<script>
  import { createEventDispatcher } from 'svelte';
  import { getLanguageFromFilename } from './monaco-config.js';

  const dispatch = createEventDispatcher();

  export let tabs = [];
  export let activeTab = null;

  function selectTab(tab) {
    activeTab = tab;
    dispatch('tabSelect', tab);
  }

  function closeTab(tab, event) {
    event.stopPropagation();
    dispatch('tabClose', tab);
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
    event.dataTransfer.setData('text/plain', JSON.stringify(tab));
    event.dataTransfer.effectAllowed = 'move';
  }

  function handleTabDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }

  function handleTabDrop(event, targetTab) {
    event.preventDefault();
    const draggedTab = JSON.parse(event.dataTransfer.getData('text/plain'));
    
    if (draggedTab.path !== targetTab.path) {
      dispatch('tabReorder', { draggedTab, targetTab });
    }
  }
</script>

<div class="tab-manager flex items-center bg-secondary border-b border-border overflow-x-auto">
  {#if tabs.length === 0}
    <div class="flex items-center px-4 py-2 text-tertiary text-sm">
      <i class="fas fa-code mr-2"></i>
      No files open
    </div>
  {:else}
    {#each tabs as tab}
      <div 
        class="tab flex items-center px-3 py-2 border-r border-border cursor-pointer hover:bg-background transition-colors"
        class:active={activeTab?.path === tab.path}
        draggable="true"
        on:click={() => selectTab(tab)}
        on:dragstart={(e) => handleTabDragStart(e, tab)}
        on:dragover={handleTabDragOver}
        on:drop={(e) => handleTabDrop(e, tab)}
      >
        <i class="{getTabIcon(tab.name)} mr-2 text-xs"></i>
        <span class="tab-name text-sm truncate max-w-32">{tab.name}</span>
        {#if tab.modified}
          <div class="w-2 h-2 bg-orange-500 rounded-full ml-2"></div>
        {:else}
          <button 
            class="tab-close ml-2 w-4 h-4 flex items-center justify-center rounded hover:bg-red-500 hover:text-white transition-colors"
            on:click={(e) => closeTab(tab, e)}
          >
            <i class="fas fa-times text-xs"></i>
          </button>
        {/if}
      </div>
    {/each}
  {/if}
  
  <!-- Tab Actions -->
  <div class="tab-actions flex items-center ml-auto px-2">
    <button 
      class="action-btn p-1 rounded hover:bg-background transition-colors"
      title="Close All Tabs"
      on:click={() => dispatch('closeAllTabs')}
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
  </div>
</div>

<style>
  .tab-manager {
    min-height: 40px;
  }
  
  .tab {
    min-width: 120px;
    max-width: 200px;
    position: relative;
  }
  
  .tab.active {
    background-color: var(--background);
    border-bottom: 2px solid var(--primary);
  }
  
  .tab-name {
    flex: 1;
  }
  
  .tab-close {
    opacity: 0;
    transition: opacity 0.2s;
  }
  
  .tab:hover .tab-close {
    opacity: 1;
  }
  
  .action-btn {
    color: var(--tertiary);
  }
  
  .action-btn:hover {
    color: var(--foreground);
  }
</style>