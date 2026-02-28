<script>
  import { onMount, onDestroy, createEventDispatcher, tick } from 'svelte';
  import { browser } from '$app/environment';
  import { editorState, editorSettings, editorActions, notify } from '$lib/stores/editor.js';
  import { initializeMonaco, createEditorInstance } from './monaco-config.js';
  import { debounce } from '$lib/utils/debounce.js';
  import { shortcut } from '$lib/actions/shortcut.js';

  const dispatch = createEventDispatcher();

  export let height = '100%';
  export let width = '100%';

  let editorContainer;
  let monaco;
  let editor;
  let autoSaveTimer;
  let resizeObserver;

  // Reactive declarations
  $: if (editor && $editorSettings) {
    updateEditorOptions($editorSettings);
  }

  $: if (editor && $editorState.activeFile) {
    loadFileInEditor($editorState.activeFile);
  }

  // Debounced auto-save
  const debouncedAutoSave = debounce(async (content) => {
    if ($editorSettings.autoSave && $editorState.activeFile?.modified) {
      await saveCurrentFile();
    }
  }, $editorSettings.autoSaveDelay);

  onMount(async () => {
    if (!browser) return;

    try {
      monaco = await initializeMonaco();
      editor = await createEditorInstance(monaco, editorContainer, {
        theme: $editorSettings.theme,
        fontSize: $editorSettings.fontSize,
        fontFamily: $editorSettings.fontFamily,
        wordWrap: $editorSettings.wordWrap ? 'on' : 'off',
        minimap: { enabled: $editorSettings.minimap },
        lineNumbers: $editorSettings.lineNumbers ? 'on' : 'off',
        tabSize: $editorSettings.tabSize,
        insertSpaces: $editorSettings.insertSpaces,
        renderWhitespace: $editorSettings.renderWhitespace,
        cursorBlinking: $editorSettings.cursorBlinking,
        mouseWheelZoom: $editorSettings.mouseWheelZoom,
        formatOnPaste: $editorSettings.formatOnPaste,
        formatOnType: $editorSettings.formatOnType,
        automaticLayout: true,
        scrollBeyondLastLine: false,
        smoothScrolling: true,
        cursorSmoothCaretAnimation: true,
        suggest: {
          showKeywords: true,
          showSnippets: true,
          showClasses: true,
          showFunctions: true,
          showVariables: true
        },
        quickSuggestions: {
          other: true,
          comments: false,
          strings: false
        }
      });

      setupEventListeners();
      setupKeyboardShortcuts();
      setupResizeObserver();

      dispatch('ready', { editor, monaco });
      notify.success('Editor initialized successfully');

    } catch (error) {
      console.error('Failed to initialize editor:', error);
      notify.error('Failed to initialize editor');
    }
  });

  onDestroy(() => {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    if (resizeObserver) resizeObserver.disconnect();
    if (editor) {
      editor.dispose();
    }
  });

  function setupEventListeners() {
    // Content change with auto-save
    editor.onDidChangeModelContent(() => {
      const content = editor.getValue();
      
      if ($editorState.activeFile) {
        $editorState.activeFile.content = content;
        editorActions.markDirty($editorState.activeFile);
        
        if ($editorSettings.autoSave) {
          debouncedAutoSave(content);
        }
      }

      dispatch('change', { content, editor });
    });

    // Cursor position tracking
    editor.onDidChangeCursorPosition((e) => {
      editorActions.updateCursor({
        line: e.position.lineNumber,
        column: e.position.column
      });
      dispatch('cursorChange', { position: e.position, editor });
    });

    // Selection change
    editor.onDidChangeCursorSelection((e) => {
      editorState.update(state => {
        state.selection = e.selection;
        return state;
      });
    });

    // Focus events
    editor.onDidFocusEditorText(() => {
      dispatch('focus', { editor });
    });

    editor.onDidBlurEditorText(() => {
      dispatch('blur', { editor });
    });

    // Model change (when switching files)
    editor.onDidChangeModel(() => {
      dispatch('modelChange', { editor });
    });
  }

  function setupKeyboardShortcuts() {
    // Save file
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, async () => {
      await saveCurrentFile();
    });

    // Save all files
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyS, async () => {
      await saveAllFiles();
    });

    // Close current tab
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyW, () => {
      if ($editorState.activeFile) {
        editorActions.closeFile($editorState.activeFile);
      }
    });

    // Quick open
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyP, () => {
      dispatch('quickOpen');
    });

    // Command palette
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyP, () => {
      dispatch('commandPalette');
    });

    // Format document
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyI, () => {
      editor.getAction('editor.action.formatDocument').run();
    });

    // Toggle comment
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash, () => {
      editor.getAction('editor.action.commentLine').run();
    });

    // Duplicate line
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyD, () => {
      editor.getAction('editor.action.duplicateSelection').run();
    });

    // Move line up/down
    editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.UpArrow, () => {
      editor.getAction('editor.action.moveLinesUpAction').run();
    });

    editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.DownArrow, () => {
      editor.getAction('editor.action.moveLinesDownAction').run();
    });
  }

  function setupResizeObserver() {
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        if (editor) {
          editor.layout();
        }
      });
      resizeObserver.observe(editorContainer);
    }
  }

  function updateEditorOptions(settings) {
    if (!editor) return;

    editor.updateOptions({
      theme: settings.theme,
      fontSize: settings.fontSize,
      fontFamily: settings.fontFamily,
      wordWrap: settings.wordWrap ? 'on' : 'off',
      minimap: { enabled: settings.minimap },
      lineNumbers: settings.lineNumbers ? 'on' : 'off',
      tabSize: settings.tabSize,
      insertSpaces: settings.insertSpaces,
      renderWhitespace: settings.renderWhitespace,
      cursorBlinking: settings.cursorBlinking,
      mouseWheelZoom: settings.mouseWheelZoom,
      formatOnPaste: settings.formatOnPaste,
      formatOnType: settings.formatOnType
    });
  }

  async function loadFileInEditor(file) {
    if (!editor || !file) return;

    try {
      const model = monaco.editor.createModel(
        file.content || '',
        getLanguageFromFilename(file.name),
        monaco.Uri.file(file.path)
      );

      editor.setModel(model);
      editor.focus();

      // Restore cursor position if available
      if (file.cursorPosition) {
        editor.setPosition(file.cursorPosition);
      }

    } catch (error) {
      console.error('Error loading file in editor:', error);
      notify.error(`Failed to load file: ${file.name}`);
    }
  }

  async function saveCurrentFile() {
    if (!$editorState.activeFile) return;

    try {
      const content = editor.getValue();
      
      // Save cursor position
      $editorState.activeFile.cursorPosition = editor.getPosition();
      
      await dispatch('save', { 
        file: $editorState.activeFile, 
        content 
      });

      editorActions.markClean($editorState.activeFile);
      notify.success(`Saved ${$editorState.activeFile.name}`);

    } catch (error) {
      console.error('Error saving file:', error);
      notify.error(`Failed to save ${$editorState.activeFile.name}`);
    }
  }

  async function saveAllFiles() {
    const unsavedFiles = $editorState.openTabs.filter(tab => tab.modified);
    
    for (const file of unsavedFiles) {
      try {
        await dispatch('save', { file, content: file.content });
        editorActions.markClean(file);
      } catch (error) {
        console.error(`Error saving ${file.name}:`, error);
        notify.error(`Failed to save ${file.name}`);
      }
    }

    if (unsavedFiles.length > 0) {
      notify.success(`Saved ${unsavedFiles.length} files`);
    }
  }

  function getLanguageFromFilename(filename) {
    const ext = filename.split('.').pop()?.toLowerCase();
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
      'yaml': 'yaml'
    };
    return languageMap[ext] || 'plaintext';
  }

  // Public API
  export function getValue() {
    return editor ? editor.getValue() : '';
  }

  export function setValue(value) {
    if (editor) {
      editor.setValue(value || '');
    }
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

  export function getEditor() {
    return editor;
  }

  export function getMonaco() {
    return monaco;
  }
</script>

<div 
  bind:this={editorContainer}
  class="enhanced-editor"
  style="height: {height}; width: {width};"
  use:shortcut={{
    'ctrl+s': saveCurrentFile,
    'ctrl+shift+s': saveAllFiles,
    'ctrl+w': () => $editorState.activeFile && editorActions.closeFile($editorState.activeFile)
  }}
></div>

<style>
  .enhanced-editor {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    position: relative;
  }

  :global(.enhanced-editor .monaco-editor) {
    --vscode-editor-background: var(--terminal-window-background) !important;
    --vscode-editor-foreground: var(--terminal-window-foreground) !important;
  }

  :global(.enhanced-editor .monaco-editor .margin) {
    background-color: var(--secondary) !important;
  }

  :global(.enhanced-editor .monaco-scrollable-element > .scrollbar > .slider) {
    background: var(--tertiary) !important;
  }

  :global(.enhanced-editor .monaco-editor .current-line) {
    background-color: rgba(255, 255, 255, 0.05) !important;
  }

  :global(.enhanced-editor .monaco-editor .selected-text) {
    background-color: rgba(173, 214, 255, 0.3) !important;
  }
</style>