import { writable } from 'svelte/store';

// Helper function to get item from localStorage
function getItemFromLocalStorage(key, defaultValue) {
    const storedValue = localStorage.getItem(key);
    if (storedValue) {
        return storedValue;
    }
    localStorage.setItem(key, defaultValue);
    return defaultValue;
}

// Helper function to handle subscription and local storage setting
function subscribeAndStore(store, key, defaultValue) {
    store.set(getItemFromLocalStorage(key, defaultValue));
    store.subscribe(value => {
        localStorage.setItem(key, value);
    });
}

// Server related stores
export const serverStatus = writable(false);
export const internet = writable(true);

// Message related stores
export const messages = writable([]);
export const projectFiles = writable(null);

// Selection related stores
export const selectedProject = writable('');
export const selectedModel = writable('');
export const selectedSearchEngine = writable('');

subscribeAndStore(selectedProject, 'selectedProject', 'select project');
subscribeAndStore(selectedModel, 'selectedModel', 'select model');
subscribeAndStore(selectedSearchEngine, 'selectedSearchEngine', 'select search engine');

// List related stores
export const projectList = writable([]);
export const modelList = writable({});
export const searchEngineList = writable([]);

// Agent related stores
export const agentState = writable(null);
export const isSending = writable(false);

// Token usage store
export const tokenUsage = writable(0);
