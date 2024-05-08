import loader from "@monaco-editor/loader";
import { Icons } from "../icons";
import { updateSettings, fetchSettings } from "$lib/api";

let settings = {};
let original = {};

const getSettings = async () => {
  settings = await fetchSettings();
  original = JSON.parse(JSON.stringify(settings));
}

await getSettings();

const save = async () => {
  let updated = {};
  for (let key in settings) {
    for (let subkey in settings[key]) {
      if (settings[key][subkey] !== original[key][subkey]) {
        if (!updated[key]) {
          updated[key] = {};
        }
        updated[key][subkey] = settings[key][subkey];
      }
    }
  }

  await updateSettings(updated);
};

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

export async function initializeEditorRef(monaco, container) {
  const editor = monaco.editor.create(container, {
    theme: getTheme(),
    readOnly: false,
    automaticLayout: true,
  });
  return editor;
}

export function createModel(monaco, file) {
  const model = monaco.editor.createModel(
    file.code,
    getFileLanguage(file.file.split(".").pop())
  );
  return model;
}

export function disposeEditor(editor) {
  if(editor) editor.dispose();
}

export function enableTabSwitching(editor, models, tabContainer) {
  tabContainer.innerHTML = "";
  Object.keys(models).forEach((filename, index) => {
    const tabElement = document.createElement("div");
    tabElement.textContent = filename.split("/").pop();
    tabElement.className = "tab p-2 me-2 rounded-lg text-sm cursor-pointer hover:bg-secondary text-primary whitespace-nowrap";
    tabElement.setAttribute("data-filename", filename);
    tabElement.addEventListener("click", () =>
      switchTab(editor, models, filename, tabElement)
    );
    if (index === Object.keys(models).length - 1) {
      tabElement.classList.add("bg-secondary");
    }
    tabContainer.appendChild(tabElement);
  });
}

function switchTab(editor, models, filename, tabElement) {
  Object.entries(models).forEach(([file, model]) => {
    if (file === filename) {
      editor.setModel(model);
    }
  });

  const allTabElements = tabElement?.parentElement?.children;
  for (let i = 0; i < allTabElements?.length; i++) {
    allTabElements[i].classList.remove("bg-secondary");
  }

  tabElement.classList.add("bg-secondary");
}

export function sidebar(editor, models, sidebarContainer) {
  sidebarContainer.innerHTML = "";

  const createSidebarElement = (filename, isFolder, isAIContext) => {
    const sidebarElement = document.createElement("div");
    const icon = isAIContext ? Icons.ContextOff : Icons.ContextOn;
    const state = isAIContext ? "inactive" : "active";

    if (isFolder) {
      sidebarElement.classList.add("mx-3", "p-1", "px-2", "cursor-pointer");
      sidebarElement.innerHTML = `<div class="align-container"><p class="flex items-center gap-2">${Icons.FolderEditor}${" "}${filename}</p><p data-state="${state}" title="Activate/Deactivate as context for AI">${icon}</p></div>`;
      // TODO implement folder collapse/expand to the element sidebarElement
    } else {
      sidebarElement.classList.add("mx-3", "p-1", "px-2", "cursor-pointer", "align-container");
      sidebarElement.innerHTML = `<p class="flex items-center gap-2">${Icons.File}${" "}${filename}</p><p data-state="${state}" title="Activate/Deactivate as context for AI">${icon}</p>`;
    }

    return sidebarElement;
  };

  const changeTabColor = (index) => {
    const allTabElements = document.querySelectorAll("#tabContainer")[0].children;
    for (let i = 0; i < allTabElements?.length; i++) {
      allTabElements[i].classList.remove("bg-secondary");
    }
    allTabElements[index].classList.add("bg-secondary");
  }

  const contextToggle = (elementParagraph, name) => {
    const state = elementParagraph.getAttribute('data-state');

    if (state === "inactive") {
      elementParagraph.setAttribute('data-state', 'active');
      elementParagraph.innerHTML = `${Icons.ContextOn}`;

      const nameIndex = settings["CUSTOM"]["BLACKLIST_FOLDER"].indexOf(name);
      if (nameIndex !== -1) {
          settings["CUSTOM"]["BLACKLIST_FOLDER"] = settings["CUSTOM"]["BLACKLIST_FOLDER"].split(', ').filter(item => item !== name).join(', ');
      }
    } else {
      elementParagraph.setAttribute('data-state', 'inactive');
      elementParagraph.innerHTML = `${Icons.ContextOff}`;

      settings["CUSTOM"]["BLACKLIST_FOLDER"] += `, ${name}`;
    }

    console.log(settings["CUSTOM"]["BLACKLIST_FOLDER"]);
    save();
  }

  const expandFolder = (folder, expand) => {
    const elements = document.querySelectorAll(`[id="${folder}"]`);
    elements.forEach(element => {
      element.style.display = (element.style.display === "none") ? "" : "none";
    });
  }

  const folders = {};
  const blacklistDir = settings["CUSTOM"]["BLACKLIST_FOLDER"];
  const blacklistDirs = blacklistDir.split(', ').map(dir => dir.trim());

  Object.entries(models).forEach(([filename, model], modelIndex) => {
    const parts = filename.split(/[\/\\]/);
    let currentFolder = sidebarContainer;
    let folderID = ""

    parts.forEach((part, index) => {
      const contextEnable = blacklistDirs.some(dir => part.includes(dir));
      const parentFolder = index !== 0 ? `FOLDER::${parts.slice(0, index).join("/")}` : ""
      const actualFile = `FOLDER::${parts.slice(0, index + 1).join("/")}`

      if (index === parts.length - 1) {
        const fileElement = createSidebarElement(part, false, contextEnable);
        const fileElementParagraphs = fileElement.querySelectorAll('p');

        // What folder is the parent of this file
        fileElement.setAttribute("id", parentFolder);

        // Collapse every folder/file
          if (index !== 0) {
            fileElement.style.display = "none"
          }

        fileElementParagraphs[0].addEventListener("click", () => {
          editor.setModel(model);
          changeTabColor(modelIndex);
        });

        fileElementParagraphs[1].addEventListener("click", () => {
          contextToggle(fileElementParagraphs[1], part);
        });
        currentFolder.appendChild(fileElement);
      } else {
        // We get the path of the actual folder with the parent directory, otherwise duplicate folder name will glitch out
        const folderName = actualFile;

        if (!folders[folderName]) {
          const folderElement = createSidebarElement(part, true, contextEnable);
          const folderElementParagraphs = folderElement.querySelectorAll('p');

          // If it's a sub-directory (Not the first index), we set the id to the previous folder name
          folderElement.setAttribute("id", parentFolder);

          // Collapse every folder/file
          if (index !== 0) {
            folderElement.style.display = "none"
          }

          folderElementParagraphs[0].addEventListener("click", () => {
            expandFolder(actualFile);
          });

          folderElementParagraphs[1].addEventListener("click", () => {
            contextToggle(folderElementParagraphs[1], part);
          });

          currentFolder.appendChild(folderElement);
          folders[folderName] = folderElement;
          currentFolder = folderElement;
        } else {
          currentFolder = folders[folderName];
        }
      }
    });
  });
}