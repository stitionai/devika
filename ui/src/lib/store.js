import { writable } from 'svelte/store';

// Helper function to get item from localStorage
/**
 * Retrieves an item from local storage. If the item does not exist,
 * sets it with a default value and returns that value.
 *
 * @param {string} key - The key under which the value is stored in local storage.
 * @param {*} defaultValue - The default value to be set if the key does not exist.
 * @returns {*} - The retrieved value from local storage or the default value if the key was not found.
 */
function getItemFromLocalStorage(key, defaultValue) {
    const storedValue = localStorage.getItem(key);
    if (storedValue) {
        return storedValue;
    }
    localStorage.setItem(key, defaultValue);
    return defaultValue;
}

// Helper function to handle subscription and local storage setting
/**
 * Subscribes to changes in the provided store and synchronizes its value with localStorage.
 *
 * @param {Object} store - The store object that provides `set` and `subscribe` methods.
 * @param {string} key - The localStorage key under which the value will be stored.
 * @param {*} defaultValue - The default value to use if no value is found in localStorage.
 */
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
