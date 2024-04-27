import loader from "@monaco-editor/loader";

function getFileLanguage(fileType) {
  const fileTypeToLanguage = {
    js: "javascript",
    jsx: "javascript",
    ts: "typescript",
    tsx: "typescript",
    html: "html",
    css: "css",
    py: "python",
    java: "java",
    rb: "ruby",
    php: "php",
    cpp: "c++",
    c: "c",
    swift: "swift",
    kt: "kotlin",
    json: "json",
    xml: "xml",
    sql: "sql",
    sh: "shell",
  };
  const language = fileTypeToLanguage[fileType.toLowerCase()];
  return language;
}

const getTheme = () => {
  const theme = localStorage.getItem("mode-watcher-mode");
  return theme === "light" ? "vs-light" : "vs-dark";
};

export async function initializeMonaco() {
  const monacoEditor = await import("monaco-editor");
  loader.config({ monaco: monacoEditor.default });
  return loader.init();
}

export function createEditors(container, monaco, file) {
  const editor = monaco.editor.create(container, {
    theme: getTheme(),
    readOnly: false,
    automaticLayout: true,
  });
  const model = monaco.editor.createModel(
    file.code,
    getFileLanguage(file.file.split(".").pop())
  );
  editor.setModel(model);
  return editor;
}

export function disposeEditors(editors) {
  Object.values(editors).forEach((editor) => editor.dispose());
}

export function enableTabSwitching(editors, tabContainer) {
  tabContainer.innerHTML = "";
  Object.keys(editors).forEach((filename, index) => {
    const tabElement = document.createElement("div");
    tabElement.textContent = filename;
    tabElement.className =
      "tab p-2 me-2 rounded-lg text-sm cursor-pointer hover:bg-secondary text-primary";
    if (index === 0) {
      tabElement.classList.add("bg-secondary");
    }
    tabElement.setAttribute("data-filename", filename);
    tabElement.addEventListener("click", () =>
      switchTab(editors, filename, tabElement)
    );
    tabContainer.appendChild(tabElement);
  });
}

function switchTab(editors, filename, tabElement) {
  Object.entries(editors).forEach((editor) => {
    if (editor[0] === filename) {
      const domNode = editor[1].getDomNode();
      if (domNode) {
        domNode.style.display = "block";
      }
      // editor[1].updateOptions({ readOnly: false });
    } else {
      // editor[1].updateOptions({ readOnly: true });
      const domNode = editor[1].getDomNode();
      if (domNode) {
        domNode.style.display = "none";
      }
    }
  });

  const allTabElements = tabElement.parentElement.children;
  for (let i = 0; i < allTabElements.length; i++) {
    allTabElements[i].classList.remove("bg-secondary");
  }

  tabElement.classList.add("bg-secondary");
}
