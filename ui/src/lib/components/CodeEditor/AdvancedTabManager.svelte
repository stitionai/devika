<script>
  import { createEventDispatcher } from 'svelte';
  import { editorState, editorActions } from '$lib/stores/editor.js';
  import { slide, fade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { clickOutside } from '$lib/actions/clickOutside.js';
  import { shortcut } from '$lib/actions/shortcut.js';

  const dispatch = createEventDispatcher();

  let draggedTab = null;
  let dragOverTab = null;
  let tabContextMenu = null;
  let contextMenuPosition = { x: 0, y: 0 };
  let contextMenuTarget = null;

  function selectTab(tab) {
    editorActions.openFile(tab);
    dispatch('tabSelect', tab);
  }

  function closeTab(tab, event) {
    event.stopPropagation();
    
    if (tab.modified) {
      const shouldSave = confirm(`${tab.name} has unsaved changes. Save before closing?`);
      if (shouldSave) {
        dispatch('save', { file: tab });
      }
    }
    
    editorActions.closeFile(tab);
    dispatch('tabClose', tab);
  }

  function closeOtherTabs(targetTab) {
    const otherTabs = $editorState.openTabs.filter(tab => tab.path !== targetTab.path);
    otherTabs.forEach(tab => {
      if (tab.modified) {
        const shouldSave = confirm(`${tab.name} has unsaved changes. Save before closing?`);
        if (shouldSave) {
          dispatch('save', { file: tab });
        }
      }
      editorActions.closeFile(tab);
    });
  }

  function closeTabsToRight(targetTab) {
    const targetIndex = $editorState.openTabs.findIndex(tab => tab.path === targetTab.path);
    const tabsToClose = $editorState.openTabs.slice(targetIndex + 1);
    
    tabsToClose.forEach(tab => {
      if (tab.modified) {
        const shouldSave = confirm(`${tab.name} has unsaved changes. Save before closing?`);
        if (shouldSave) {
          dispatch('save', { file: tab });
        }
      }
      editorActions.closeFile(tab);
    });
  }

  function closeAllTabs() {
    const unsavedTabs = $editorState.openTabs.filter(tab => tab.modified);
    
    if (unsavedTabs.length > 0) {
      const shouldSave = confirm(`${unsavedTabs.length} files have unsaved changes. Save all before closing?`);
      if (shouldSave) {
        unsavedTabs.forEach(tab => {
          dispatch('save', { file: tab });
        });
      }
    }
    
    $editorState.openTabs.forEach(tab => {
      editorActions.closeFile(tab);
    });
  }

  function getTabIcon(filename) {
    const ext = filename.split('.').pop()?.toLowerCase();
    const iconMap = {
      'js': 'fab fa-js-square text-yellow-500',
      'jsx': 'fab fa-react text-blue-400',
      'ts': 'fab fa-js-square text-blue-600',
      'tsx': 'fab fa-react text-blue-600',
      'py': 'fab fa-python text-green-500',
      'html': 'fab fa-html5 text-orange-500',
      'css': 'fab fa-css3-alt text-blue-500',
      'scss': 'fab fa-sass text-pink-500',
      'json': 'fas fa-brackets-curly text-yellow-600',
      'md': 'fab fa-markdown text-gray-600'
    };
    
    return iconMap[ext] || 'fas fa-file text-gray-400';
  }

  function handleTabDragStart(event, tab) {
    draggedTab = tab;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', JSON.stringify(tab));
  }

  function handleTabDragOver(event, tab) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    dragOverTab = tab;
  }

  function handleTabDragLeave() {
    dragOverTab = null;
  }

  function handleTabDrop(event, targetTab) {
    event.preventDefault();
    
    if (draggedTab && draggedTab.path !== targetTab.path) {
      // Reorder tabs
      const draggedIndex = $editorState.openTabs.findIndex(tab => tab.path === draggedTab.path);
      const targetIndex = $editorState.openTabs.findIndex(tab => tab.path === targetTab.path);
      
      if (draggedIndex !== -1 && targetIndex !== -1) {
        const newTabs = [...$editorState.openTabs];
        const [removed] = newTabs.splice(draggedIndex, 1);
        newTabs.splice(targetIndex, 0, removed);
        
        editorState.update(state => {
          state.openTabs = newTabs;
          return state;
        });
        
        dispatch('tabReorder', { draggedTab, targetTab });
      }
    }
    
    draggedTab = null;
    dragOverTab = null;
  }

  function handleTabDragEnd() {
    draggedTab = null;
    dragOverTab = null;
  }

  function showTabContextMenu(event, tab) {
    event.preventDefault();
    event.stopPropagation();
    
    contextMenuPosition = { x: event.clientX, y: event.clientY };
    contextMenuTarget = tab;
    tabContextMenu = true;
  }

  function hideTabContextMenu() {
    tabContextMenu = false;
    contextMenuTarget = null;
  }

  function handleTabContextAction(action) {
    if (!contextMenuTarget) return;
    
    switch (action) {
      case 'close':
        closeTab(contextMenuTarget, { stopPropagation: () => {} });
        break;
      case 'closeOthers':
        closeOtherTabs(contextMenuTarget);
        break;
      case 'closeToRight':
        closeTabsToRight(contextMenuTarget);
        break;
      case 'closeAll':
        closeAllTabs();
        break;
      case 'copyPath':
        navigator.clipboard.writeText(contextMenuTarget.path);
        break;
      case 'revealInExplorer':
        dispatch('revealInExplorer', contextMenuTarget);
        break;
    }
    
    hideTabContextMenu();
  }

  function getTabTitle(tab) {
    let title = tab.name;
    if (tab.modified) title += ' (modified)';
    title += `\nPath: ${tab.path}`;
    if (tab.size) title += `\nSize: ${formatFileSize(tab.size)}`;
    return title;
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
</script>

<div class="advanced-tab-manager flex items-center bg-secondary border-b border-border overflow-x-auto">
  {#if $editorState.openTabs.length === 0}
    <div class="flex items-center px-4 py-2 text-tertiary text-sm">
      <i class="fas fa-code mr-2"></i>
      No files open
    </div>
  {:else}
    <div class="flex items-center flex-1 min-w-0">
      {#each $editorState.openTabs as tab (tab.path)}
        <div 
          class="tab flex items-center px-3 py-2 border-r border-border cursor-pointer hover:bg-background transition-all duration-200 group relative"
          class:active={$editorState.activeFile?.path === tab.path}
          class:drag-over={dragOverTab?.path === tab.path}
          class:modified={tab.modified}
          draggable="true"
          title={getTabTitle(tab)}
          on:click={() => selectTab(tab)}
          on:contextmenu={(e) => showTabContextMenu(e, tab)}
          on:dragstart={(e) => handleTabDragStart(e, tab)}
          on:dragover={(e) => handleTabDragOver(e, tab)}
          on:dragleave={handleTabDragLeave}
          on:drop={(e) => handleTabDrop(e, tab)}
          on:dragend={handleTabDragEnd}
          transition:slide={{ duration: 200, easing: quintOut }}
          use:shortcut={{
            'ctrl+w': () => closeTab(tab, { stopPropagation: () => {} })
          }}
        >
          <i class="{getTabIcon(tab.name)} mr-2 text-xs"></i>
          
          <span class="tab-name text-sm truncate max-w-32 flex-1">
            {tab.name}
          </span>
          
          {#if tab.modified}
            <div class="w-2 h-2 bg-orange-500 rounded-full ml-2 animate-pulse"></div>
          {:else}
            <button 
              class="tab-close ml-2 w-4 h-4 flex items-center justify-center rounded hover:bg-red-500 hover:text-white transition-all duration-200 opacity-0 group-hover:opacity-100"
              on:click={(e) => closeTab(tab, e)}
              title="Close tab"
            >
              <i class="fas fa-times text-xs"></i>
            </button>
          {/if}
          
          <!-- Active tab indicator -->
          {#if $editorState.activeFile?.path === tab.path}
            <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
  
  <!-- Tab Actions -->
  <div class="tab-actions flex items-center ml-auto px-2 border-l border-border">
    <button 
      class="action-btn p-1 rounded hover:bg-background transition-colors"
      title="Close All Tabs"
      on:click={closeAllTabs}
    >
      <i class="fas fa-times-circle text-sm"></i>
    </button>
    
    <button 
      class="action-btn p-1 rounded hover:bg-background transition-colors ml-1"
      title="Split Editor"
      on:click={() => dispatch('splitEditor')}
    >
      <i class="fas fa-columns text-sm"></i>
    </button>
    
    <button 
      class="action-btn p-1 rounded hover:bg-background transition-colors ml-1"
      title="More Actions"
      on:click={() => dispatch('moreActions')}
    >
      <i class="fas fa-ellipsis-h text-sm"></i>
    </button>
  </div>
</div>

<!-- Tab Context Menu -->
{#if tabContextMenu}
  <div 
    class="tab-context-menu fixed bg-background border border-border rounded-lg shadow-lg py-1 z-50 min-w-48"
    style="left: {contextMenuPosition.x}px; top: {contextMenuPosition.y}px;"
    use:clickOutside={hideTabContextMenu}
    transition:fade={{ duration: 150 }}
  >
    <button class="context-menu-item" on:click={() => handleTabContextAction('close')}>
      <i class="fas fa-times"></i> Close
    </button>
    
    <button class="context-menu-item" on:click={() => handleTabContextAction('closeOthers')}>
      <i class="fas fa-times-circle"></i> Close Others
    </button>
    
    <button class="context-menu-item" on:click={() => handleTabContextAction('closeToRight')}>
      <i class="fas fa-arrow-right"></i> Close to the Right
    </button>
    
    <button class="context-menu-item" on:click={() => handleTabContextAction('closeAll')}>
      <i class="fas fa-ban"></i> Close All
    </button>
    
    <div class="context-menu-separator"></div>
    
    <button class="context-menu-item" on:click={() => handleTabContextAction('copyPath')}>
      <i class="fas fa-copy"></i> Copy Path
    </button>
    
    <button class="context-menu-item" on:click={() => handleTabContextAction('revealInExplorer')}>
      <i class="fas fa-search"></i> Reveal in Explorer
    </button>
  </div>
{/if}

<style>
  .advanced-tab-manager {
    min-height: 40px;
  }
  
  .tab {
    min-width: 120px;
    max-width: 200px;
    position: relative;
    user-select: none;
  }
  
  .tab.active {
    background-color: var(--background);
    z-index: 1;
  }
  
  .tab.drag-over {
    background-color: var(--primary);
    color: var(--foreground-invert);
  }
  
  .tab.modified {
    font-style: italic;
  }
  
  .tab-name {
    flex: 1;
  }
  
  .action-btn {
    color: var(--tertiary);
    transition: all 0.2s;
  }
  
  .action-btn:hover {
    color: var(--foreground);
  }
  
  .tab-context-menu {
    animation: contextMenuAppear 0.15s ease-out;
  }
  
  @keyframes contextMenuAppear {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
  
  .context-menu-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 8px 12px;
    text-align: left;
    font-size: 14px;
    border: none;
    background: none;
    color: var(--foreground);
    cursor: pointer;
    transition: background-color 0.15s;
  }
  
  .context-menu-item:hover {
    background-color: var(--secondary);
  }
  
  .context-menu-separator {
    height: 1px;
    background-color: var(--border);
    margin: 4px 0;
  }
  
  /* Scrollbar styling for tab overflow */
  .advanced-tab-manager::-webkit-scrollbar {
    height: 4px;
  }
  
  .advanced-tab-manager::-webkit-scrollbar-track {
    background: var(--secondary);
  }
  
  .advanced-tab-manager::-webkit-scrollbar-thumb {
    background: var(--tertiary);
    border-radius: 2px;
  }
  
  .advanced-tab-manager::-webkit-scrollbar-thumb:hover {
    background: var(--foreground);
  }
</style>