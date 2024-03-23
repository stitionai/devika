import {
  messages,
  projectList,
  modelList,
  agentState,
  internet,
} from "./store";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:1337";

export async function fetchProjectList() {
  const response = await fetch(`${API_BASE_URL}/api/project-list`);
  const data = await response.json();
  projectList.set(data.projects);
}

export async function createProject(projectName) {
  await fetch(`${API_BASE_URL}/api/create-project`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ project_name: projectName }),
  });
}

export async function fetchModelList() {
  const response = await fetch(`${API_BASE_URL}/api/model-list`);
  const data = await response.json();
  modelList.set(data.models);
}

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

export async function fetchMessages() {
  const projectName = localStorage.getItem("selectedProject");
  const response = await fetch(`${API_BASE_URL}/api/get-messages`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ project_name: projectName }),
  });
  const data = await response.json();
  messages.set(data.messages);
}

export async function sendMessage(message) {
  const projectName = localStorage.getItem("selectedProject");
  const modelId = localStorage.getItem("selectedModel");

  if (!modelId) {
    alert("Please select the LLM model first.");
    return;
  }

  await fetch(`${API_BASE_URL}/api/send-message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      project_name: projectName,
      base_model: modelId,
    }),
  });
  await fetchMessages();
}

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

export async function getTokenUsage() {
  const response = await fetch(`${API_BASE_URL}/api/token-usage`);
  const data = await response.json();
  return data.token_usage;
}

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

export async function checkInternetStatus() {
  if (navigator.onLine) {
    internet.set(true);
  } else {
    internet.set(false);
  }
}
