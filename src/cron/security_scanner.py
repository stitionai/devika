#!/usr/bin/env python3
"""
Security Scanner Cron Job for Bambu Agent System
Scans all repositories for security vulnerabilities
"""

import os
import json
import re
import subprocess
from datetime import datetime
from typing import Dict, Any, List


class SecurityScanner:
    """Scan repositories for security issues"""
    
    # Patterns to detect potential secrets
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*=\s*["\']?[a-zA-Z0-9_\-]{20,}', 'API Key'),
        (r'(?i)(secret[_-]?key|secretkey)\s*=\s*["\']?[a-zA-Z0-9_\-]{20,}', 'Secret Key'),
        (r'(?i)(password|passwd|pwd)\s*=\s*["\']?[a-zA-Z0-9_\-]{8,}', 'Password'),
        (r'(?i)(token|auth[_-]?token)\s*=\s*["\']?[a-zA-Z0-9_\-]{20,}', 'Token'),
        (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key'),
        (r'sk-ant-[a-zA-Z0-9\-]{20,}', 'Anthropic API Key'),
        (r'ghp_[a-zA-Z0-9]{36}', 'GitHub PAT'),
        (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth'),
        (r'ghu_[a-zA-Z0-9]{36}', 'GitHub User Token'),
        (r'ghs_[a-zA-Z0-9]{36}', 'GitHub Server Token'),
        (r'ghr_[a-zA-Z0-9]{36}', 'GitHub Refresh Token'),
        (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
        (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\']?[a-zA-Z0-9/+=]{40}', 'AWS Secret'),
        (r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----', 'Private Key'),
        (r'(?i)(mongodb\+srv://|mongodb://)[^\s"\']+', 'MongoDB URI'),
        (r'(?i)(postgres://|postgresql://)[^\s"\']+', 'PostgreSQL URI'),
        (r'(?i)(mysql://)[^\s"\']+', 'MySQL URI'),
        (r'(?i)(redis://)[^\s"\']+', 'Redis URI'),
        (r'sbp_[a-zA-Z0-9]{32,}', 'Supabase Key'),
        (r'eyJ[a-zA-Z0-9_\-]*\.eyJ[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-]*', 'JWT Token'),
    ]
    
    def __init__(self):
        self.log_file = "logs/security_scans.jsonl"
        self.ignored_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
        self.ignored_files = {'.env', '.env.local', '.env.example'}
        
    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file for secrets"""
        findings = []
        
        # Skip ignored files
        if os.path.basename(file_path) in self.ignored_files:
            return findings
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern, secret_type in self.SECRET_PATTERNS:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Get line number
                    line_num = content[:match.start()].count('\n') + 1
                    findings.append({
                        "file": file_path,
                        "line": line_num,
                        "type": secret_type,
                        "match": match.group()[:20] + "..." if len(match.group()) > 20 else match.group()
                    })
                    
        except Exception as e:
            pass  # Skip files that can't be read
            
        return findings
    
    def scan_directory(self, directory: str) -> Dict[str, Any]:
        """Recursively scan a directory for security issues"""
        all_findings = []
        files_scanned = 0
        
        for root, dirs, files in os.walk(directory):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                findings = self.scan_file(file_path)
                all_findings.extend(findings)
                files_scanned += 1
                
        return {
            "directory": directory,
            "files_scanned": files_scanned,
            "findings_count": len(all_findings),
            "findings": all_findings
        }
    
    def check_gitignore(self, directory: str) -> Dict[str, Any]:
        """Check if .gitignore properly excludes sensitive files"""
        gitignore_path = os.path.join(directory, '.gitignore')
        issues = []
        
        required_patterns = [
            '.env',
            '*.pem',
            '*.key',
            'secrets/',
            '.secrets/'
        ]
        
        if not os.path.exists(gitignore_path):
            return {
                "has_gitignore": False,
                "issues": ["No .gitignore file found"]
            }
            
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                issues.append(f"Missing pattern: {pattern}")
                
        return {
            "has_gitignore": True,
            "issues": issues
        }
    
    def check_env_exposure(self, directory: str) -> List[Dict[str, Any]]:
        """Check for exposed .env files"""
        exposed = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                if file.startswith('.env') and not file.endswith('.example'):
                    file_path = os.path.join(root, file)
                    # Check if it's tracked by git
                    try:
                        result = subprocess.run(
                            ['git', 'ls-files', '--error-unmatch', file_path],
                            cwd=directory,
                            capture_output=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            exposed.append({
                                "file": file_path,
                                "issue": "Tracked by git"
                            })
                    except:
                        pass
                        
        return exposed
    
    def run_full_scan(self, directories: List[str] = None) -> Dict[str, Any]:
        """Run a full security scan"""
        if directories is None:
            directories = ['.', 'repos', 'memory', 'src']
            
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "scan_type": "security_scanner",
            "directories": {},
            "summary": {
                "total_files": 0,
                "total_findings": 0,
                "critical_issues": 0
            }
        }
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
                
            print(f"Scanning {directory}...")
            
            dir_results = self.scan_directory(directory)
            gitignore_check = self.check_gitignore(directory)
            env_check = self.check_env_exposure(directory)
            
            results["directories"][directory] = {
                **dir_results,
                "gitignore_check": gitignore_check,
                "env_exposure": env_check
            }
            
            results["summary"]["total_files"] += dir_results["files_scanned"]
            results["summary"]["total_findings"] += dir_results["findings_count"]
            
            if gitignore_check.get("issues"):
                results["summary"]["critical_issues"] += len(gitignore_check["issues"])
            if env_check:
                results["summary"]["critical_issues"] += len(env_check)
        
        # Log results
        self.log_scan(results)
        
        return results
    
    def log_scan(self, results: Dict[str, Any]):
        """Log scan results"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(results) + "\n")


def main():
    """Main entry point for security scan"""
    scanner = SecurityScanner()
    results = scanner.run_full_scan()
    
    print(f"\nSecurity Scan Complete:")
    print(f"  Files scanned: {results['summary']['total_files']}")
    print(f"  Findings: {results['summary']['total_findings']}")
    print(f"  Critical issues: {results['summary']['critical_issues']}")
    
    if results['summary']['critical_issues'] > 0:
        print("\n⚠️  CRITICAL ISSUES FOUND - Review logs/security_scans.jsonl")
    
    return results


if __name__ == "__main__":
    main()
