import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

// Editor state management
export const editorState = writable({
  activeFile: null,
  openTabs: [],
  expandedFolders: new Set(),
  searchQuery: '',
  searchResults: [],
  isSearching: false,
  isDirty: false,
  lastSaved: null,
  cursorPosition: { line: 1, column: 1 },
  selection: null,
  theme: 'vs-dark',
  fontSize: 14,
  wordWrap: true,
  minimap: true,
  lineNumbers: true,
  autoSave: true,
  autoSaveDelay: 2000
});

// Editor settings with persistence
export const editorSettings = writable({
  theme: 'vs-dark',
  fontSize: 14,
  fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
  wordWrap: true,
  minimap: true,
  lineNumbers: true,
  autoSave: true,
  autoSaveDelay: 2000,
  tabSize: 2,
  insertSpaces: true,
  renderWhitespace: 'selection',
  cursorBlinking: 'blink',
  mouseWheelZoom: true,
  formatOnPaste: true,
  formatOnType: true
});

// Persist settings to localStorage
if (browser) {
  const savedSettings = localStorage.getItem('devika-editor-settings');
  if (savedSettings) {
    editorSettings.set(JSON.parse(savedSettings));
  }

  editorSettings.subscribe(settings => {
    localStorage.setItem('devika-editor-settings', JSON.stringify(settings));
  });
}

// File tree state
export const fileTree = writable({});
export const selectedFile = writable(null);
export const searchState = writable({
  query: '',
  results: [],
  currentIndex: 0,
  isVisible: false,
  replaceMode: false,
  replaceText: '',
  caseSensitive: false,
  wholeWord: false,
  useRegex: false
});

// Command palette state
export const commandPalette = writable({
  isOpen: false,
  query: '',
  commands: [],
  selectedIndex: 0
});

// Notifications
export const notifications = writable([]);

// Derived stores
export const hasUnsavedChanges = derived(
  editorState,
  $state => $state.openTabs.some(tab => tab.modified)
);

export const currentLanguage = derived(
  [editorState, selectedFile],
  ([$state, $selectedFile]) => {
    if (!$selectedFile) return 'plaintext';
    const ext = $selectedFile.name.split('.').pop()?.toLowerCase();
    return getLanguageFromExtension(ext);
  }
);

// Helper functions
function getLanguageFromExtension(ext) {
  const languageMap = {
    'js': 'javascript',
    'jsx': 'javascript',
    'ts': 'typescript',
    'tsx': 'typescript',
    'py': 'python',
    'html': 'html',
    'css': 'css',
    'scss': 'scss',
    'json': 'json',
    'md': 'markdown',
    'yml': 'yaml',
    'yaml': 'yaml',
    'xml': 'xml',
    'sql': 'sql',
    'sh': 'shell',
    'bash': 'shell'
  };
  return languageMap[ext] || 'plaintext';
}

// Actions
export const editorActions = {
  openFile: (file) => {
    editorState.update(state => {
      const existingTab = state.openTabs.find(tab => tab.path === file.path);
      if (existingTab) {
        state.activeFile = existingTab;
      } else {
        const newTab = { ...file, modified: false };
        state.openTabs.push(newTab);
        state.activeFile = newTab;
      }
      return state;
    });
  },

  closeFile: (file) => {
    editorState.update(state => {
      const index = state.openTabs.findIndex(tab => tab.path === file.path);
      if (index !== -1) {
        state.openTabs.splice(index, 1);
        if (state.activeFile?.path === file.path) {
          state.activeFile = state.openTabs[Math.max(0, index - 1)] || null;
        }
      }
      return state;
    });
  },

  markDirty: (file) => {
    editorState.update(state => {
      const tab = state.openTabs.find(tab => tab.path === file.path);
      if (tab) {
        tab.modified = true;
        state.isDirty = true;
      }
      return state;
    });
  },

  markClean: (file) => {
    editorState.update(state => {
      const tab = state.openTabs.find(tab => tab.path === file.path);
      if (tab) {
        tab.modified = false;
        state.lastSaved = new Date();
      }
      state.isDirty = state.openTabs.some(tab => tab.modified);
      return state;
    });
  },

  updateCursor: (position) => {
    editorState.update(state => {
      state.cursorPosition = position;
      return state;
    });
  },

  toggleFolder: (path) => {
    editorState.update(state => {
      if (state.expandedFolders.has(path)) {
        state.expandedFolders.delete(path);
      } else {
        state.expandedFolders.add(path);
      }
      return state;
    });
  }
};

// Notification system
export const notify = {
  success: (message, duration = 3000) => {
    const id = Date.now();
    notifications.update(n => [...n, { id, type: 'success', message, duration }]);
    setTimeout(() => {
      notifications.update(n => n.filter(notif => notif.id !== id));
    }, duration);
  },

  error: (message, duration = 5000) => {
    const id = Date.now();
    notifications.update(n => [...n, { id, type: 'error', message, duration }]);
    setTimeout(() => {
      notifications.update(n => n.filter(notif => notif.id !== id));
    }, duration);
  },

  info: (message, duration = 3000) => {
    const id = Date.now();
    notifications.update(n => [...n, { id, type: 'info', message, duration }]);
    setTimeout(() => {
      notifications.update(n => n.filter(notif => notif.id !== id));
    }, duration);
  }
};