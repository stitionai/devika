<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { initializeMonaco, createEditorInstance, disposeEditor } from './monaco-config.js';
  import { projectFiles, selectedProject } from '$lib/store';
  import { API_BASE_URL } from '$lib/api';
  import { toast } from 'svelte-sonner';

  const dispatch = createEventDispatcher();

  export let height = '100%';
  export let width = '100%';
  export let theme = 'vs-dark';
  export let language = 'javascript';
  export let value = '';
  export let readOnly = false;
  export let minimap = true;
  export let lineNumbers = true;
  export let wordWrap = 'on';

  let editorContainer;
  let monaco;
  let editor;
  let currentModel;

  // Editor configuration
  const editorOptions = {
    theme,
    language,
    value,
    readOnly,
    automaticLayout: true,
    minimap: { enabled: minimap },
    lineNumbers: lineNumbers ? 'on' : 'off',
    wordWrap,
    fontSize: 14,
    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
    scrollBeyondLastLine: false,
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
    accessibilitySupport: 'auto'
  };

  onMount(async () => {
    try {
      monaco = await initializeMonaco();
      editor = await createEditorInstance(monaco, editorContainer, editorOptions);
      
      // Set up event listeners
      setupEventListeners();
      
      // Dispatch ready event
      dispatch('ready', { editor, monaco });
      
    } catch (error) {
      console.error('Failed to initialize Monaco Editor:', error);
      toast.error('Failed to initialize code editor');
    }
  });

  onDestroy(() => {
    if (editor) {
      disposeEditor(editor);
    }
  });

  function setupEventListeners() {
    if (!editor) return;

    // Content change listener
    editor.onDidChangeModelContent(() => {
      const currentValue = editor.getValue();
      dispatch('change', { value: currentValue, editor });
    });

    // Cursor position change
    editor.onDidChangeCursorPosition((e) => {
      dispatch('cursorChange', { position: e.position, editor });
    });

    // Focus/blur events
    editor.onDidFocusEditorText(() => {
      dispatch('focus', { editor });
    });

    editor.onDidBlurEditorText(() => {
      dispatch('blur', { editor });
    });

    // Key bindings
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      dispatch('save', { value: editor.getValue(), editor });
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF, () => {
      editor.getAction('actions.find').run();
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF, () => {
      editor.getAction('editor.action.startFindReplaceAction').run();
    });
  }

  // Public methods
  export function getValue() {
    return editor ? editor.getValue() : '';
  }

  export function setValue(newValue) {
    if (editor) {
      editor.setValue(newValue || '');
    }
  }

  export function getEditor() {
    return editor;
  }

  export function getMonaco() {
    return monaco;
  }

  export function focus() {
    if (editor) {
      editor.focus();
    }
  }

  export function layout() {
    if (editor) {
      editor.layout();
    }
  }

  export function setTheme(newTheme) {
    if (monaco) {
      monaco.editor.setTheme(newTheme);
    }
  }

  export function setLanguage(newLanguage) {
    if (editor && monaco) {
      const model = editor.getModel();
      if (model) {
        monaco.editor.setModelLanguage(model, newLanguage);
      }
    }
  }

  export function insertText(text, position = null) {
    if (editor) {
      const pos = position || editor.getPosition();
      editor.executeEdits('insert-text', [{
        range: new monaco.Range(pos.lineNumber, pos.column, pos.lineNumber, pos.column),
        text: text
      }]);
    }
  }

  export function formatDocument() {
    if (editor) {
      editor.getAction('editor.action.formatDocument').run();
    }
  }

  export function findAndReplace() {
    if (editor) {
      editor.getAction('editor.action.startFindReplaceAction').run();
    }
  }

  // Reactive updates
  $: if (editor && value !== editor.getValue()) {
    setValue(value);
  }

  $: if (editor && theme) {
    setTheme(theme);
  }

  $: if (editor && language) {
    setLanguage(language);
  }
</script>

<div 
  bind:this={editorContainer} 
  class="monaco-editor-container"
  style="height: {height}; width: {width};"
></div>

<style>
  .monaco-editor-container {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }

  :global(.monaco-editor) {
    --vscode-editor-background: var(--terminal-window-background) !important;
    --vscode-editor-foreground: var(--terminal-window-foreground) !important;
  }

  :global(.monaco-editor .margin) {
    background-color: var(--secondary) !important;
  }

  :global(.monaco-editor .monaco-scrollable-element > .scrollbar > .slider) {
    background: var(--tertiary) !important;
  }
</style>