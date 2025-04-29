import loader from "@monaco-editor/loader";
import { Icons } from "../icons";

/**
 * Retrieves the programming language associated with a given file type.
 *
 * @param {string} fileType - The file extension or type for which to determine the language.
 * @returns {string | undefined} - The corresponding programming language as a string,
 *                                or `undefined` if the file type is not recognized.
 */
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

/**
 * Retrieves the current theme mode from local storage and returns the corresponding editor theme.
 *
 * The function checks the value of "mode-watcher-mode" in local storage.
 * If the value is "light", it returns "vs-light"; otherwise, it returns "vs-dark".
 *
 * @returns {string} - The editor theme based on the current mode ("vs-light" or "vs-dark").
 */
const getTheme = () => {
  const theme = localStorage.getItem("mode-watcher-mode");
  return theme === "light" ? "vs-light" : "vs-dark";
};

/**
 * Initializes the Monaco editor by importing it and configuring the loader.
 *
 * @returns {Promise<any>} A promise that resolves to the result of the loader initialization.
 * @throws Will throw an error if there is an issue during the import or initialization process.
 */
export async function initializeMonaco() {
  const monacoEditor = await import("monaco-editor");
  loader.config({ monaco: monacoEditor.default });
  return loader.init();
}

/**
 * Initializes an editor instance within the specified container using Monaco Editor.
 *
 * @param {Object} monaco - The Monaco Editor module to use for creating the editor instance.
 * @param {HTMLElement} container - The HTML element where the editor will be initialized.
 * @returns {Promise<Object>} A promise that resolves with the created editor instance.
 * @throws Will throw an error if the editor cannot be initialized properly.
 */
export async function initializeEditorRef(monaco, container) {
  const editor = monaco.editor.create(container, {
    theme: getTheme(),
    readOnly: false,
    automaticLayout: true,
  });
  return editor;
}

/**
 * Creates a model for the given file using Monaco Editor.
 *
 * @param {object} monaco - The Monaco Editor instance.
 * @param {object} file - The file object containing the code and filename.
 * @param {string} file.code - The source code of the file.
 * @param {string} file.file - The full name of the file, including its extension.
 *
 * @returns {Model} A model created by Monaco Editor for the given file.
 */
export function createModel(monaco, file) {
  const model = monaco.editor.createModel(
    file.code,
    getFileLanguage(file.file.split(".").pop())
  );
  return model;
}

/**
 * Disposes of the given editor instance if it exists.
 *
 * @param {Object} editor - The editor instance to be disposed. It should have a `dispose` method.
 */
export function disposeEditor(editor) {
  if(editor) editor.dispose();
}

/**
 * Enables tab switching functionality for an editor by creating tabs based on provided models.
 *
 * @param {any} editor - The editor instance to switch tabs for.
 * @param {Object} models - An object containing model data where keys are filenames and values are associated models.
 * @param {HTMLElement} tabContainer - The HTML element that will contain the tabs.
 */
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

/**
 * Switches the active tab in an editor to display the model associated with a given filename.
 *
 * @param {Editor} editor - The editor instance where the model will be set.
 * @param {Object.<string, Model>} models - An object containing filenames as keys and their corresponding models as values.
 * @param {string} filename - The name of the file whose model should be displayed in the editor.
 * @param {HTMLElement} tabElement - The DOM element representing the tab that was clicked or activated.
 */
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

/**
 * Initializes and updates the sidebar with file and folder elements based on the provided models.
 *
 * @param {Editor} editor - The code editor instance to which models will be set.
 * @param {Object.<string, Model>} models - An object where keys are filenames and values are corresponding model objects.
 * @param {HTMLElement} sidebarContainer - The DOM element that will contain the sidebar items.
 */
export function sidebar(editor, models, sidebarContainer) {
  sidebarContainer.innerHTML = "";
  /**
   * Creates a sidebar element based on the provided filename and whether it represents a folder or not.
   *
   * @param {string} filename - The name of the file or folder to be displayed in the sidebar.
   * @param {boolean} isFolder - A boolean indicating whether the element represents a folder (true) or a file (false).
   * @returns {HTMLElement} - The created sidebar element with appropriate styling and content.
   *
   * @throws {TypeError} - Throws an error if filename is not a string or if isFolder is not a boolean.
   */
  const createSidebarElement = (filename, isFolder) => {
    const sidebarElement = document.createElement("div");
    sidebarElement.classList.add("mx-3", "p-1", "px-2", "cursor-pointer");
    if (isFolder) {
      sidebarElement.innerHTML = `<p class="flex items-center gap-2">${Icons.Folder}${" "}${filename}</p>`;
      // TODO implement folder collapse/expand to the element sidebarElement
    } else {
      sidebarElement.innerHTML = `<p class="flex items-center gap-2">${Icons.File}${" "}${filename}</p>`;
    }
    return sidebarElement;
  };

  /**
   * Changes the background color of a tab by adding the 'bg-secondary' class to it
   * and removing it from all other tabs.
   *
   * @param {number} index - The zero-based index of the tab to be highlighted.
   */
  const changeTabColor = (index) => {
    const allTabElements = document.querySelectorAll("#tabContainer")[0].children;
    for (let i = 0; i < allTabElements?.length; i++) {
      allTabElements[i].classList.remove("bg-secondary");
    }
    allTabElements[index].classList.add("bg-secondary");
  }

  const folders = {};

  Object.entries(models).forEach(([filename, model], modelIndex) => {
    const parts = filename.split('/');
    let currentFolder = sidebarContainer;

    parts.forEach((part, index) => {
      if (index === parts.length - 1) {
        const fileElement = createSidebarElement(part, false);
        fileElement.addEventListener("click", () => {
          editor.setModel(model);
          changeTabColor(modelIndex);
        });
        currentFolder.appendChild(fileElement);
      } else {
        const folderName = part;
        if (!folders[folderName]) {
          const folderElement = createSidebarElement(part, true);
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