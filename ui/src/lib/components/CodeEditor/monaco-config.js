import loader from "@monaco-editor/loader";

// Language mappings
const LANGUAGE_MAP = {
  'js': 'javascript',
  'jsx': 'javascript',
  'ts': 'typescript',
  'tsx': 'typescript',
  'py': 'python',
  'html': 'html',
  'css': 'css',
  'scss': 'scss',
  'sass': 'sass',
  'less': 'less',
  'json': 'json',
  'xml': 'xml',
  'yaml': 'yaml',
  'yml': 'yaml',
  'md': 'markdown',
  'sql': 'sql',
  'sh': 'shell',
  'bash': 'shell',
  'zsh': 'shell',
  'fish': 'shell',
  'ps1': 'powershell',
  'java': 'java',
  'c': 'c',
  'cpp': 'cpp',
  'cc': 'cpp',
  'cxx': 'cpp',
  'h': 'c',
  'hpp': 'cpp',
  'cs': 'csharp',
  'php': 'php',
  'rb': 'ruby',
  'go': 'go',
  'rs': 'rust',
  'swift': 'swift',
  'kt': 'kotlin',
  'scala': 'scala',
  'r': 'r',
  'dart': 'dart',
  'lua': 'lua',
  'perl': 'perl',
  'dockerfile': 'dockerfile',
  'toml': 'toml',
  'ini': 'ini',
  'cfg': 'ini',
  'conf': 'ini'
};

// Theme configurations
const THEMES = {
  light: 'vs',
  dark: 'vs-dark',
  'high-contrast': 'hc-black'
};

export function getLanguageFromFilename(filename) {
  if (!filename) return 'plaintext';
  
  const extension = filename.split('.').pop()?.toLowerCase();
  return LANGUAGE_MAP[extension] || 'plaintext';
}

export function getTheme() {
  const savedTheme = localStorage.getItem('mode-watcher-mode');
  return THEMES[savedTheme] || THEMES.dark;
}

export async function initializeMonaco() {
  try {
    const monacoEditor = await import('monaco-editor');
    loader.config({ monaco: monacoEditor.default });
    const monaco = await loader.init();
    
    // Configure Monaco
    configureMonaco(monaco);
    
    return monaco;
  } catch (error) {
    console.error('Failed to initialize Monaco:', error);
    throw error;
  }
}

export async function createEditorInstance(monaco, container, options = {}) {
  if (!monaco || !container) {
    throw new Error('Monaco or container not available');
  }

  const defaultOptions = {
    theme: getTheme(),
    automaticLayout: true,
    fontSize: 14,
    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
    lineNumbers: 'on',
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    renderWhitespace: 'selection',
    selectOnLineNumbers: true,
    roundedSelection: false,
    cursorStyle: 'line',
    cursorBlinking: 'blink',
    folding: true,
    foldingHighlight: true,
    showFoldingControls: 'always',
    matchBrackets: 'always',
    autoIndent: 'full',
    formatOnPaste: true,
    formatOnType: true,
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on',
    tabCompletion: 'on',
    quickSuggestions: true,
    parameterHints: { enabled: true },
    hover: { enabled: true },
    contextmenu: true,
    mouseWheelZoom: true,
    multiCursorModifier: 'ctrlCmd',
    accessibilitySupport: 'auto',
    ...options
  };

  const editor = monaco.editor.create(container, defaultOptions);
  
  // Set up additional configurations
  setupEditorFeatures(monaco, editor);
  
  return editor;
}

export function createModel(monaco, content, language, uri) {
  if (!monaco) return null;
  
  try {
    // Dispose existing model if it exists
    const existingModel = monaco.editor.getModel(uri);
    if (existingModel) {
      existingModel.dispose();
    }
    
    return monaco.editor.createModel(content, language, uri);
  } catch (error) {
    console.error('Failed to create model:', error);
    return null;
  }
}

export function disposeEditor(editor) {
  if (editor) {
    try {
      editor.dispose();
    } catch (error) {
      console.error('Error disposing editor:', error);
    }
  }
}

function configureMonaco(monaco) {
  // Configure TypeScript compiler options
  monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
    target: monaco.languages.typescript.ScriptTarget.ES2020,
    allowNonTsExtensions: true,
    moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
    module: monaco.languages.typescript.ModuleKind.CommonJS,
    noEmit: true,
    esModuleInterop: true,
    jsx: monaco.languages.typescript.JsxEmit.React,
    reactNamespace: 'React',
    allowJs: true,
    typeRoots: ['node_modules/@types']
  });

  monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
    target: monaco.languages.typescript.ScriptTarget.ES2020,
    allowNonTsExtensions: true,
    moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
    module: monaco.languages.typescript.ModuleKind.CommonJS,
    noEmit: true,
    esModuleInterop: true,
    allowJs: true,
    jsx: monaco.languages.typescript.JsxEmit.React,
    reactNamespace: 'React',
    typeRoots: ['node_modules/@types']
  });

  // Configure diagnostics
  monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
    noSemanticValidation: false,
    noSyntaxValidation: false
  });

  monaco.languages.typescript.typescriptDefaults.setDiagnosticsOptions({
    noSemanticValidation: false,
    noSyntaxValidation: false
  });

  // Add custom themes
  monaco.editor.defineTheme('devika-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6A9955' },
      { token: 'keyword', foreground: '569CD6' },
      { token: 'string', foreground: 'CE9178' },
      { token: 'number', foreground: 'B5CEA8' },
      { token: 'regexp', foreground: 'D16969' },
      { token: 'type', foreground: '4EC9B0' },
      { token: 'class', foreground: '4EC9B0' },
      { token: 'function', foreground: 'DCDCAA' },
      { token: 'variable', foreground: '9CDCFE' },
      { token: 'constant', foreground: '4FC1FF' }
    ],
    colors: {
      'editor.background': '#1e1e1e',
      'editor.foreground': '#d4d4d4',
      'editor.lineHighlightBackground': '#2d2d30',
      'editor.selectionBackground': '#264f78',
      'editor.inactiveSelectionBackground': '#3a3d41'
    }
  });

  monaco.editor.defineTheme('devika-light', {
    base: 'vs',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '008000' },
      { token: 'keyword', foreground: '0000FF' },
      { token: 'string', foreground: 'A31515' },
      { token: 'number', foreground: '098658' },
      { token: 'regexp', foreground: 'D16969' },
      { token: 'type', foreground: '267F99' },
      { token: 'class', foreground: '267F99' },
      { token: 'function', foreground: '795E26' },
      { token: 'variable', foreground: '001080' },
      { token: 'constant', foreground: '0070C1' }
    ],
    colors: {
      'editor.background': '#ffffff',
      'editor.foreground': '#000000',
      'editor.lineHighlightBackground': '#f0f0f0',
      'editor.selectionBackground': '#add6ff',
      'editor.inactiveSelectionBackground': '#e5ebf1'
    }
  });
}

function setupEditorFeatures(monaco, editor) {
  // Add custom commands
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyD, () => {
    editor.getAction('editor.action.duplicateSelection').run();
  });

  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyK, () => {
    editor.getAction('editor.action.deleteLines').run();
  });

  editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.UpArrow, () => {
    editor.getAction('editor.action.moveLinesUpAction').run();
  });

  editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.DownArrow, () => {
    editor.getAction('editor.action.moveLinesDownAction').run();
  });

  // Add custom context menu items
  editor.addAction({
    id: 'format-document',
    label: 'Format Document',
    keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyI],
    contextMenuGroupId: 'modification',
    contextMenuOrder: 1,
    run: () => {
      editor.getAction('editor.action.formatDocument').run();
    }
  });

  editor.addAction({
    id: 'toggle-word-wrap',
    label: 'Toggle Word Wrap',
    keybindings: [monaco.KeyMod.Alt | monaco.KeyCode.KeyZ],
    contextMenuGroupId: 'view',
    contextMenuOrder: 1,
    run: () => {
      const currentWordWrap = editor.getOption(monaco.editor.EditorOption.wordWrap);
      editor.updateOptions({
        wordWrap: currentWordWrap === 'on' ? 'off' : 'on'
      });
    }
  });

  editor.addAction({
    id: 'toggle-minimap',
    label: 'Toggle Minimap',
    contextMenuGroupId: 'view',
    contextMenuOrder: 2,
    run: () => {
      const currentMinimap = editor.getOption(monaco.editor.EditorOption.minimap);
      editor.updateOptions({
        minimap: { enabled: !currentMinimap.enabled }
      });
    }
  });
}

export { LANGUAGE_MAP, THEMES };