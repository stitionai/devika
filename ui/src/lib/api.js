import {
  agentState,
  internet,
  modelList,
  projectList,
  messages,
  projectFiles,
  searchEngineList,
} from "./store";
import { io } from "socket.io-client";


/**
 * Retrieves the base URL for API requests.
 *
 * This function determines the appropriate base URL based on the environment.
 * If running in a browser, it checks the hostname to decide whether to use
 * 'localhost' or the current host. In non-browser environments (e.g., server-side),
 * it defaults to 'http://127.0.0.1:1337'.
 *
 * @returns {string} The base URL for API requests.
 */
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://127.0.0.1:1337';
    } else {
      return `http://${host}:1337`;
    }
  } else {
    return 'http://127.0.0.1:1337';
  }
};

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || getApiBaseUrl();
export const socket = io(API_BASE_URL, { autoConnect: false });

/**
 * Checks the server status by making an asynchronous fetch request to the API endpoint.
 *
 * @returns {Promise<boolean>} - Returns true if the server is reachable, otherwise false.
 *
 * @throws Will throw an error if the fetch operation fails for reasons other than the server being unreachable.
 */
export async function checkServerStatus() {
  try{await fetch(`${API_BASE_URL}/api/status`) ; return true;}
  catch (error) {
    return false;
  }

}

/**
 * Fetches initial data from the API and updates various lists and local storage.
 *
 * This function makes an asynchronous request to the specified API endpoint,
 * retrieves JSON data, and then populates several lists with the fetched data.
 * Additionally, it stores the entire data object in the browser's localStorage
 * under the key "defaultData".
 *
 * @returns {Promise<void>} - A promise that resolves once all operations are complete.
 *
 * @throws {Error} - Throws an error if the fetch operation fails or if there is a problem parsing the JSON data.
 */
export async function fetchInitialData() {
  const response = await fetch(`${API_BASE_URL}/api/data`);
  const data = await response.json();
  projectList.set(data.projects);
  modelList.set(data.models);
  searchEngineList.set(data.search_engines);
  localStorage.setItem("defaultData", JSON.stringify(data));
}

/**
 * Creates a new project with the specified name.
 *
 * @param {string} projectName - The name of the project to be created.
 * @returns {Promise<void>} A promise that resolves when the project creation request is completed.
 * @throws {Error} Throws an error if the fetch operation fails or encounters a network issue.
 */
export async function createProject(projectName) {
  await fetch(`${API_BASE_URL}/api/create-project`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ project_name: projectName }),
  });
  projectList.update((projects) => [...projects, projectName]);
}

/**
 * Asynchronously deletes a project by its name.
 *
 * @async
 * @function deleteProject
 * @param {string} projectName - The name of the project to be deleted.
 * @returns {Promise<void>} A Promise that resolves when the deletion is successful.
 * @throws {Error} Throws an error if the fetch operation fails or the API returns an error response.
 */
export async function deleteProject(projectName) {
  await fetch(`${API_BASE_URL}/api/delete-project`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ project_name: projectName }),
  });
}

/**
 * Fetches messages from the server for the currently selected project.
 *
 * This function retrieves messages by sending a POST request to the API endpoint `/api/messages`.
 * The request includes the currently selected project's name in the body.
 *
 * @async
 * @function fetchMessages
 *
 * @throws {Error} Throws an error if the fetch operation fails or the response is not OK.
 *
 * @returns {Promise<void>} A promise that resolves once the messages have been set.
 */
export async function fetchMessages() {
  const projectName = localStorage.getItem("selectedProject");
  const response = await fetch(`${API_BASE_URL}/api/messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ project_name: projectName }),
  });
  const data = await response.json();
  messages.set(data.messages);
}

/**
 * Fetches the agent state from the server for the currently selected project.
 *
 * This function retrieves the agent state by sending a POST request to the
 * '/api/get-agent-state' endpoint with the current project's name in the request body.
 *
 * @async
 * @function fetchAgentState
 *
 * @throws {Error} Throws an error if the API call fails or if there is an issue parsing the response.
 *
 * @returns {Promise<void>} A promise that resolves when the agent state has been successfully set.
 */
export async function fetchAgentState() {
  const projectName = localStorage.getItem("selectedProject");
  const response = await fetch(`${API_BASE_URL}/api/get-agent-state`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ project_name: projectName }),
  });
  const data = await response.json();
  agentState.set(data.state);
}

/**
 * Executes an agent with the provided prompt using the selected model and project.
 *
 * @async
 * @param {string} prompt - The input prompt to be processed by the agent.
 * @returns {Promise<void>}
 * @throws Will throw an error if the API call fails or the required data is missing.
 *
 * This function retrieves the selected model and project from local storage,
 * then makes a POST request to the execute-agent endpoint of the API with the provided prompt,
 * the selected model, and the project name. After executing the agent, it fetches messages.
 */
export async function executeAgent(prompt) {
  const projectName = localStorage.getItem("selectedProject");
  const modelId = localStorage.getItem("selectedModel");

  if (!modelId) {
    alert("Please select the LLM model first.");
    return;
  }

  await fetch(`${API_BASE_URL}/api/execute-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt: prompt,
      base_model: modelId,
      project_name: projectName,
    }),
  });

  await fetchMessages();
}

/**
 * Fetches a browser snapshot from the server.
 *
 * @param {string} snapshotPath - The path where the snapshot should be saved or retrieved from.
 * @returns {Promise<string>} A promise that resolves to the base64-encoded string of the browser snapshot image.
 * @throws {Error} Throws an error if the fetch operation fails or if the response is not in JSON format.
 */
export async function getBrowserSnapshot(snapshotPath) {
  const response = await fetch(`${API_BASE_URL}/api/browser-snapshot`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ snapshot_path: snapshotPath }),
  });
  const data = await response.json();
  return data.snapshot;
}

/**
 * Fetches project files from the server for the selected project.
 *
 * This function retrieves the list of files associated with the currently selected project
 * by making an asynchronous HTTP GET request to the API endpoint `/api/get-project-files`.
 * The `project_name` parameter is populated from the local storage under the key "selectedProject".
 *
 * @returns {Promise<Array>} A promise that resolves to an array of file objects.
 * @throws {Error} Throws an error if the fetch operation fails or if there is no selected project.
 */
export async function fetchProjectFiles() {
  const projectName = localStorage.getItem("selectedProject");
  const response = await fetch(`${API_BASE_URL}/api/get-project-files?project_name=${projectName}`)
  const data = await response.json();
  projectFiles.set(data.files);
  return data.files;
}

/**
 * Checks the current internet connection status of the browser.
 *
 * This function uses the `navigator.onLine` property to determine if the device is currently connected to the internet.
 * It sets the `internet` object's state based on the connectivity status.
 *
 * @returns {Promise<void>} - A promise that resolves once the internet connection status has been checked and updated.
 */
export async function checkInternetStatus() {
  if (navigator.onLine) {
    internet.set(true);
  } else {
    internet.set(false);
  }
}

/**
 * Fetches application settings from the server.
 *
 * This function sends an HTTP GET request to the `/api/settings` endpoint of the API_BASE_URL.
 * It then parses the JSON response and returns the settings object contained within.
 *
 * @async
 * @function fetchSettings
 * @returns {Promise<Object>} - A promise that resolves with the application settings object.
 * @throws {Error} - Throws an error if the fetch operation fails or if the response is not OK.
 */
export async function fetchSettings() {
  const response = await fetch(`${API_BASE_URL}/api/settings`);
  const data = await response.json();
  return data.settings;
}

/**
 * Updates the application settings by sending them to the server.
 *
 * @async
 * @function updateSettings
 * @param {Object} settings - An object containing the settings to be updated.
 * @returns {Promise<void>} A promise that resolves once the settings are successfully updated.
 * @throws {Error} Throws an error if the fetch operation fails or the response is not ok.
 */
export async function updateSettings(settings) {
  await fetch(`${API_BASE_URL}/api/settings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(settings),
  });
}

/**
 * Fetches logs from the server.
 *
 * @async
 * @function fetchLogs
 * @returns {Promise<Array<Object>>} - A promise that resolves to an array of log objects.
 * @throws {Error} - Throws an error if the fetch operation fails or if the response is not OK.
 */
export async function fetchLogs() {
  const response = await fetch(`${API_BASE_URL}/api/logs`);
  const data = await response.json();
  return data.logs;
}
