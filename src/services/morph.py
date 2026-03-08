import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from typing import List, Dict

import requests

from src.config import Config

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
SKIP_EXTS = {".pyc", ".so", ".dll", ".exe", ".png", ".jpg", ".gif", ".pdf", ".zip"}

PROMPT = open("src/services/morph_prompt.txt", "r").read().strip()


class Morph:
    def __init__(self):
        self.api_key = Config().get_morph_api_key()

    def search(self, project_path: str, query: str) -> List[Dict]:
        if not self.api_key:
            return []
        tree = Morph._file_tree(project_path)
        if not tree:
            return []
        messages = [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": f"<repo_structure>\n{tree}\n</repo_structure>\n\n<search_string>\n{query}\n</search_string>"},
        ]
        for _ in range(4):
            response = requests.post(
                "https://api.morphllm.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "morph-warp-grep-v2", "messages": messages}, timeout=60,
            )
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": text})
            tool_calls = Morph._parse_tool_calls(text)
            if not tool_calls:
                break
            tool_responses = []
            for call in tool_calls:
                name = call.get("tool_name", "")
                if name == "finish":
                    paths = [line.strip() for line in call.get("relevant_files", "").strip().splitlines() if line.strip()]
                    return Morph._read_full_files(project_path, paths)
                if name == "ripgrep":
                    result = Morph._run_ripgrep(call.get("pattern", ""), project_path, call.get("glob", ""))
                elif name == "read":
                    valid_path = Morph._validate_path(call.get("path", ""), project_path)
                    result = Morph._read_file(valid_path, call.get("line_ranges", "")) if valid_path else "Error: path outside project root"
                elif name == "list_directory":
                    valid_path = Morph._validate_path(call.get("path", ""), project_path)
                    result = Morph._list_dir(valid_path) if valid_path else "Error: path outside project root"
                else:
                    continue
                tool_responses.append(f"<tool_response>\n<tool_name>{name}</tool_name>\n<result>\n{result}\n</result>\n</tool_response>")
            if tool_responses:
                messages.append({"role": "user", "content": "\n".join(tool_responses)})
        return []

    @staticmethod
    def _file_tree(project_path):
        if not os.path.isdir(project_path):
            return ""
        lines = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            rel = os.path.relpath(root, project_path)
            depth = 0 if rel == "." else rel.count(os.sep) + 1
            if depth > 6:
                dirs.clear()
                continue
            if rel != ".":
                lines.append(f"{'  ' * depth}{os.path.basename(root)}/")
            for file in sorted(files):
                if not any(file.endswith(ext) for ext in SKIP_EXTS):
                    lines.append(f"{'  ' * (depth + 1)}{file}")
        return "\n".join(lines[:500])

    @staticmethod
    def _run_ripgrep(pattern, path, glob=""):
        rg = shutil.which("rg")
        if not rg:
            return "(rg not found)"
        cmd = [rg, "--max-count", "20", "--line-number", "--no-heading"]
        if glob:
            cmd.extend(["--glob", glob])
        cmd.extend([pattern, path])
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout
            return (out[:8000] + "\n... (truncated)") if len(out) > 8000 else (out or "(no matches)")
        except Exception:
            return "(rg failed)"

    @staticmethod
    def _read_file(path, line_ranges=""):
        try:
            with open(path, "r", errors="ignore") as f:
                lines = f.readlines()
        except Exception as exc:
            return f"Error reading file: {exc}"
        if not line_ranges:
            content = "".join(lines[:500])
            return content + f"\n... ({len(lines)} total lines, showing first 500)" if len(lines) > 500 else content
        out = []
        for spec in line_ranges.split(","):
            spec = spec.strip()
            try:
                if "-" in spec:
                    start, end = spec.split("-", 1)
                    for i in range(max(1, int(start)) - 1, min(len(lines), int(end))):
                        out.append(f"{i + 1}: {lines[i].rstrip()}")
                else:
                    line_num = int(spec)
                    if 1 <= line_num <= len(lines):
                        out.append(f"{line_num}: {lines[line_num - 1].rstrip()}")
            except ValueError:
                out.append(f"Error: invalid range {spec}")
        return "\n".join(out)

    @staticmethod
    def _list_dir(path):
        try:
            entries = sorted(os.listdir(path))
        except Exception as exc:
            return f"Error listing directory: {exc}"
        return "\n".join(f"{entry}/" if os.path.isdir(os.path.join(path, entry)) else entry for entry in entries if entry not in SKIP_DIRS)

    @staticmethod
    def _parse_tool_calls(text):
        calls = []
        for block in re.findall(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL):
            call = {}
            try:
                root = ET.fromstring(f"<root>{block}</root>")
                for child in root:
                    call[child.tag] = (child.text or "").strip()
            except ET.ParseError:
                for tag in ("tool_name", "pattern", "glob", "path", "line_ranges", "relevant_files"):
                    m = re.search(rf"<{tag}>(.*?)</{tag}>", block, re.DOTALL)
                    if m:
                        call[tag] = m.group(1).strip()
            if call.get("tool_name"):
                calls.append(call)
        return calls

    @staticmethod
    def _validate_path(path, project_root):
        if not path:
            return ""
        full = os.path.join(project_root, path) if not os.path.isabs(path) else path
        real, rroot = os.path.realpath(full), os.path.realpath(project_root)
        return real if real == rroot or real.startswith(rroot + os.sep) else ""

    @staticmethod
    def _read_full_files(project_path, file_paths):
        results = []
        for file_path in file_paths:
            valid_path = Morph._validate_path(file_path, project_path)
            if not valid_path:
                continue
            try:
                with open(valid_path, "r", errors="ignore") as f:
                    results.append({"filename": valid_path, "code": f.read()})
            except Exception:
                continue
        return results
