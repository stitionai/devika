<script>
  import { createEventDispatcher, onMount, tick } from 'svelte';
  import { commandPalette, editorState, editorActions } from '$lib/stores/editor.js';
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { clickOutside } from '$lib/actions/clickOutside.js';

  const dispatch = createEventDispatcher();

  let searchInput;
  let commandList;

  const commands = [
    {
      id: 'file.new',
      title: 'New File',
      description: 'Create a new file',
      icon: 'fas fa-file-plus',
      action: () => dispatch('newFile'),
      keywords: ['new', 'create', 'file']
    },
    {
      id: 'file.save',
      title: 'Save File',
      description: 'Save the current file',
      icon: 'fas fa-save',
      action: () => dispatch('save'),
      keywords: ['save', 'write']
    },
    {
      id: 'file.saveAll',
      title: 'Save All Files',
      description: 'Save all modified files',
      icon: 'fas fa-save',
      action: () => dispatch('saveAll'),
      keywords: ['save', 'all', 'write']
    },
    {
      id: 'edit.find',
      title: 'Find',
      description: 'Find text in current file',
      icon: 'fas fa-search',
      action: () => dispatch('find'),
      keywords: ['find', 'search']
    },
    {
      id: 'edit.replace',
      title: 'Find and Replace',
      description: 'Find and replace text',
      icon: 'fas fa-search-plus',
      action: () => dispatch('replace'),
      keywords: ['find', 'replace', 'search']
    },
    {
      id: 'edit.format',
      title: 'Format Document',
      description: 'Format the current document',
      icon: 'fas fa-code',
      action: () => dispatch('format'),
      keywords: ['format', 'beautify', 'pretty']
    },
    {
      id: 'view.toggleMinimap',
      title: 'Toggle Minimap',
      description: 'Show or hide the minimap',
      icon: 'fas fa-map',
      action: () => dispatch('toggleMinimap'),
      keywords: ['minimap', 'toggle', 'view']
    },
    {
      id: 'view.toggleWordWrap',
      title: 'Toggle Word Wrap',
      description: 'Enable or disable word wrapping',
      icon: 'fas fa-text-width',
      action: () => dispatch('toggleWordWrap'),
      keywords: ['wrap', 'word', 'toggle']
    },
    {
      id: 'view.zoomIn',
      title: 'Zoom In',
      description: 'Increase font size',
      icon: 'fas fa-plus',
      action: () => dispatch('zoomIn'),
      keywords: ['zoom', 'font', 'bigger', 'increase']
    },
    {
      id: 'view.zoomOut',
      title: 'Zoom Out',
      description: 'Decrease font size',
      icon: 'fas fa-minus',
      action: () => dispatch('zoomOut'),
      keywords: ['zoom', 'font', 'smaller', 'decrease']
    },
    {
      id: 'editor.closeTab',
      title: 'Close Tab',
      description: 'Close the current tab',
      icon: 'fas fa-times',
      action: () => {
        if ($editorState.activeFile) {
          editorActions.closeFile($editorState.activeFile);
        }
      },
      keywords: ['close', 'tab']
    },
    {
      id: 'editor.closeAllTabs',
      title: 'Close All Tabs',
      description: 'Close all open tabs',
      icon: 'fas fa-times-circle',
      action: () => dispatch('closeAllTabs'),
      keywords: ['close', 'all', 'tabs']
    }
  ];

  $: filteredCommands = filterCommands($commandPalette.query);

  function filterCommands(query) {
    if (!query.trim()) return commands;
    
    const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
    
    return commands.filter(command => {
      const searchableText = [
        command.title,
        command.description,
        ...command.keywords
      ].join(' ').toLowerCase();
      
      return searchTerms.every(term => searchableText.includes(term));
    }).sort((a, b) => {
      // Prioritize title matches over description/keyword matches
      const aTitle = a.title.toLowerCase().includes(query.toLowerCase());
      const bTitle = b.title.toLowerCase().includes(query.toLowerCase());
      
      if (aTitle && !bTitle) return -1;
      if (!aTitle && bTitle) return 1;
      
      return a.title.localeCompare(b.title);
    });
  }

  function executeCommand(command) {
    command.action();
    closePalette();
  }

  function closePalette() {
    commandPalette.update(state => ({
      ...state,
      isOpen: false,
      query: '',
      selectedIndex: 0
    }));
  }

  function handleKeydown(event) {
    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        closePalette();
        break;
        
      case 'ArrowDown':
        event.preventDefault();
        commandPalette.update(state => ({
          ...state,
          selectedIndex: Math.min(state.selectedIndex + 1, filteredCommands.length - 1)
        }));
        scrollToSelected();
        break;
        
      case 'ArrowUp':
        event.preventDefault();
        commandPalette.update(state => ({
          ...state,
          selectedIndex: Math.max(state.selectedIndex - 1, 0)
        }));
        scrollToSelected();
        break;
        
      case 'Enter':
        event.preventDefault();
        if (filteredCommands[$commandPalette.selectedIndex]) {
          executeCommand(filteredCommands[$commandPalette.selectedIndex]);
        }
        break;
    }
  }

  async function scrollToSelected() {
    await tick();
    const selectedElement = commandList?.querySelector('.command-item.selected');
    if (selectedElement) {
      selectedElement.scrollIntoView({ block: 'nearest' });
    }
  }

  onMount(async () => {
    if ($commandPalette.isOpen) {
      await tick();
      searchInput?.focus();
    }
  });

  $: if ($commandPalette.isOpen && searchInput) {
    searchInput.focus();
  }

  $: if ($commandPalette.query) {
    commandPalette.update(state => ({ ...state, selectedIndex: 0 }));
  }
</script>

{#if $commandPalette.isOpen}
  <div 
    class="command-palette-overlay fixed inset-0 bg-black bg-opacity-50 z-50 flex items-start justify-center pt-20"
    transition:fade={{ duration: 200 }}
    use:clickOutside={closePalette}
  >
    <div 
      class="command-palette bg-background border border-border rounded-lg shadow-2xl w-full max-w-2xl mx-4"
      transition:fly={{ y: -20, duration: 300, easing: quintOut }}
      on:keydown={handleKeydown}
    >
      <!-- Search Input -->
      <div class="p-4 border-b border-border">
        <div class="relative">
          <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-tertiary"></i>
          <input
            bind:this={searchInput}
            bind:value={$commandPalette.query}
            type="text"
            placeholder="Type a command or search..."
            class="w-full pl-10 pr-4 py-3 bg-secondary border border-border rounded-lg focus:outline-none focus:border-primary text-foreground placeholder-tertiary"
          />
        </div>
      </div>
      
      <!-- Command List -->
      <div 
        bind:this={commandList}
        class="command-list max-h-96 overflow-y-auto"
      >
        {#if filteredCommands.length === 0}
          <div class="p-8 text-center text-tertiary">
            <i class="fas fa-search text-2xl mb-2"></i>
            <p>No commands found</p>
          </div>
        {:else}
          {#each filteredCommands as command, index}
            <button
              class="command-item w-full flex items-center p-4 hover:bg-secondary transition-colors text-left"
              class:selected={index === $commandPalette.selectedIndex}
              on:click={() => executeCommand(command)}
            >
              <div class="flex items-center justify-center w-8 h-8 bg-primary rounded mr-3">
                <i class="{command.icon} text-foreground-invert text-sm"></i>
              </div>
              
              <div class="flex-1 min-w-0">
                <div class="font-medium text-foreground">{command.title}</div>
                <div class="text-sm text-tertiary truncate">{command.description}</div>
              </div>
              
              {#if command.shortcut}
                <div class="text-xs text-tertiary bg-secondary px-2 py-1 rounded">
                  {command.shortcut}
                </div>
              {/if}
            </button>
          {/each}
        {/if}
      </div>
      
      <!-- Footer -->
      <div class="p-3 border-t border-border bg-secondary text-xs text-tertiary flex items-center justify-between">
        <div class="flex items-center gap-4">
          <span><kbd class="kbd">↑↓</kbd> to navigate</span>
          <span><kbd class="kbd">Enter</kbd> to select</span>
          <span><kbd class="kbd">Esc</kbd> to close</span>
        </div>
        <div>
          {filteredCommands.length} command{filteredCommands.length !== 1 ? 's' : ''}
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .command-palette {
    animation: commandPaletteAppear 0.3s ease-out;
  }
  
  @keyframes commandPaletteAppear {
    from {
      opacity: 0;
      transform: translateY(-20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
  
  .command-item.selected {
    background-color: var(--primary);
    color: var(--foreground-invert);
  }
  
  .command-item.selected .text-tertiary {
    color: rgba(255, 255, 255, 0.7);
  }
  
  .kbd {
    background-color: var(--background);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 2px 4px;
    font-family: monospace;
    font-size: 10px;
  }
  
  .command-list::-webkit-scrollbar {
    width: 6px;
  }
  
  .command-list::-webkit-scrollbar-track {
    background: var(--secondary);
  }
  
  .command-list::-webkit-scrollbar-thumb {
    background: var(--tertiary);
    border-radius: 3px;
  }
  
  .command-list::-webkit-scrollbar-thumb:hover {
    background: var(--foreground);
  }
</style>