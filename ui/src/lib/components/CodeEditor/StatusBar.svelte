<script>
  export let currentFile = null;
  export let cursorPosition = { lineNumber: 1, column: 1 };
  export let selection = null;
  export let language = 'plaintext';
  export let encoding = 'UTF-8';
  export let lineEnding = 'LF';
  export let fileSize = 0;
  export let isConnected = true;

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function getSelectionText() {
    if (!selection) return '';
    const { startLineNumber, startColumn, endLineNumber, endColumn } = selection;
    if (startLineNumber === endLineNumber && startColumn === endColumn) return '';
    
    const lines = Math.abs(endLineNumber - startLineNumber) + 1;
    const chars = selection.selectionLength || 0;
    
    return `(${lines} lines, ${chars} chars selected)`;
  }
</script>

<div class="status-bar flex items-center justify-between px-3 py-1 bg-secondary border-t border-border text-xs">
  <div class="status-left flex items-center gap-4">
    <!-- Connection Status -->
    <div class="status-item flex items-center gap-1">
      <div class="connection-indicator w-2 h-2 rounded-full" class:connected={isConnected} class:disconnected={!isConnected}></div>
      <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
    </div>

    <!-- File Info -->
    {#if currentFile}
      <div class="status-item">
        <i class="fas fa-file mr-1"></i>
        {currentFile.name}
      </div>
      
      <div class="status-item">
        {formatFileSize(fileSize)}
      </div>
    {/if}

    <!-- Git Status (placeholder) -->
    <div class="status-item">
      <i class="fab fa-git-alt mr-1"></i>
      main
    </div>
  </div>

  <div class="status-right flex items-center gap-4">
    <!-- Selection Info -->
    {#if selection}
      <div class="status-item">
        {getSelectionText()}
      </div>
    {/if}

    <!-- Cursor Position -->
    <div class="status-item cursor-position">
      Ln {cursorPosition.lineNumber}, Col {cursorPosition.column}
    </div>

    <!-- Language -->
    <div class="status-item language-selector cursor-pointer hover:bg-background px-2 py-1 rounded">
      <i class="fas fa-code mr-1"></i>
      {language.toUpperCase()}
    </div>

    <!-- Encoding -->
    <div class="status-item encoding-selector cursor-pointer hover:bg-background px-2 py-1 rounded">
      {encoding}
    </div>

    <!-- Line Ending -->
    <div class="status-item line-ending-selector cursor-pointer hover:bg-background px-2 py-1 rounded">
      {lineEnding}
    </div>

    <!-- Notifications -->
    <div class="status-item">
      <button class="notification-btn" title="Notifications">
        <i class="fas fa-bell"></i>
      </button>
    </div>
  </div>
</div>

<style>
  .status-bar {
    height: 24px;
    font-size: 11px;
    color: var(--tertiary);
  }
  
  .status-item {
    display: flex;
    align-items: center;
    white-space: nowrap;
  }
  
  .connection-indicator.connected {
    background-color: #22c55e;
  }
  
  .connection-indicator.disconnected {
    background-color: #ef4444;
  }
  
  .cursor-position {
    font-family: 'Monaco', 'Menlo', monospace;
  }
  
  .language-selector,
  .encoding-selector,
  .line-ending-selector {
    transition: background-color 0.2s;
  }
  
  .notification-btn {
    background: none;
    border: none;
    color: var(--tertiary);
    cursor: pointer;
    padding: 2px;
    border-radius: 2px;
  }
  
  .notification-btn:hover {
    color: var(--foreground);
    background-color: var(--background);
  }
</style>