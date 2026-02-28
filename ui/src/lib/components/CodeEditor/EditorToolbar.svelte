<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();

  export let currentFile = null;
  export let isModified = false;
  export let canUndo = false;
  export let canRedo = false;
  export let wordWrap = true;
  export let minimap = true;
  export let fontSize = 14;

  function handleAction(action) {
    dispatch('action', { action });
  }

  function handleFontSizeChange(delta) {
    const newSize = Math.max(10, Math.min(24, fontSize + delta));
    dispatch('fontSizeChange', { fontSize: newSize });
  }
</script>

<div class="editor-toolbar flex items-center justify-between px-3 py-2 bg-secondary border-b border-border">
  <div class="toolbar-left flex items-center gap-2">
    <!-- File Actions -->
    <div class="action-group flex items-center gap-1">
      <button 
        class="toolbar-btn"
        title="New File (Ctrl+N)"
        on:click={() => handleAction('newFile')}
      >
        <i class="fas fa-file-plus"></i>
      </button>
      <button 
        class="toolbar-btn"
        title="Open File (Ctrl+O)"
        on:click={() => handleAction('openFile')}
      >
        <i class="fas fa-folder-open"></i>
      </button>
      <button 
        class="toolbar-btn"
        title="Save (Ctrl+S)"
        disabled={!isModified}
        on:click={() => handleAction('save')}
      >
        <i class="fas fa-save"></i>
      </button>
      <button 
        class="toolbar-btn"
        title="Save All (Ctrl+Shift+S)"
        on:click={() => handleAction('saveAll')}
      >
        <i class="fas fa-save"></i>
        <i class="fas fa-plus text-xs"></i>
      </button>
    </div>

    <div class="separator"></div>

    <!-- Edit Actions -->
    <div class="action-group flex items-center gap-1">
      <button 
        class="toolbar-btn"
        title="Undo (Ctrl+Z)"
        disabled={!canUndo}
        on:click={() => handleAction('undo')}
      >
        <i class="fas fa-undo"></i>
      </button>
      <button 
        class="toolbar-btn"
        title="Redo (Ctrl+Y)"
        disabled={!canRedo}
        on:click={() => handleAction('redo')}
      >
        <i class="fas fa-redo"></i>
      </button>
    </div>

    <div class="separator"></div>

    <!-- Search Actions -->
    <div class="action-group flex items-center gap-1">
      <button 
        class="toolbar-btn"
        title="Find (Ctrl+F)"
        on:click={() => handleAction('find')}
      >
        <i class="fas fa-search"></i>
      </button>
      <button 
        class="toolbar-btn"
        title="Find and Replace (Ctrl+H)"
        on:click={() => handleAction('findReplace')}
      >
        <i class="fas fa-search-plus"></i>
      </button>
    </div>

    <div class="separator"></div>

    <!-- Format Actions -->
    <div class="action-group flex items-center gap-1">
      <button 
        class="toolbar-btn"
        title="Format Document (Shift+Alt+F)"
        on:click={() => handleAction('format')}
      >
        <i class="fas fa-code"></i>
      </button>
      <button 
        class="toolbar-btn"
        title="Toggle Comment (Ctrl+/)"
        on:click={() => handleAction('toggleComment')}
      >
        <i class="fas fa-comment"></i>
      </button>
    </div>
  </div>

  <div class="toolbar-right flex items-center gap-2">
    <!-- View Options -->
    <div class="action-group flex items-center gap-1">
      <button 
        class="toolbar-btn"
        class:active={wordWrap}
        title="Toggle Word Wrap (Alt+Z)"
        on:click={() => handleAction('toggleWordWrap')}
      >
        <i class="fas fa-text-width"></i>
      </button>
      <button 
        class="toolbar-btn"
        class:active={minimap}
        title="Toggle Minimap"
        on:click={() => handleAction('toggleMinimap')}
      >
        <i class="fas fa-map"></i>
      </button>
    </div>

    <div class="separator"></div>

    <!-- Font Size Controls -->
    <div class="action-group flex items-center gap-1">
      <button 
        class="toolbar-btn"
        title="Decrease Font Size"
        on:click={() => handleFontSizeChange(-1)}
      >
        <i class="fas fa-minus"></i>
      </button>
      <span class="font-size-display text-sm px-2">{fontSize}px</span>
      <button 
        class="toolbar-btn"
        title="Increase Font Size"
        on:click={() => handleFontSizeChange(1)}
      >
        <i class="fas fa-plus"></i>
      </button>
    </div>

    <div class="separator"></div>

    <!-- File Info -->
    {#if currentFile}
      <div class="file-info text-sm text-tertiary">
        <span class="file-name">{currentFile.name}</span>
        {#if isModified}
          <span class="modified-indicator">●</span>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .toolbar-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: none;
    color: var(--tertiary);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .toolbar-btn:hover:not(:disabled) {
    background-color: var(--background);
    color: var(--foreground);
  }
  
  .toolbar-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .toolbar-btn.active {
    background-color: var(--primary);
    color: var(--foreground-invert);
  }
  
  .separator {
    width: 1px;
    height: 20px;
    background-color: var(--border);
    margin: 0 4px;
  }
  
  .font-size-display {
    min-width: 40px;
    text-align: center;
    color: var(--foreground);
  }
  
  .file-info {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .modified-indicator {
    color: var(--orange-500);
    font-weight: bold;
  }
</style>