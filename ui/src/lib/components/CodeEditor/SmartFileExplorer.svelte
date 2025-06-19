<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { projectFiles, selectedProject } from '$lib/store';
  import { editorState, editorActions, fileTree } from '$lib/stores/editor.js';
  import { slide, fade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { clickOutside } from '$lib/actions/clickOutside.js';
  import { shortcut } from '$lib/actions/shortcut.js';

  const dispatch = createEventDispatcher();

  let contextMenu = null;
  let contextMenuPosition = { x: 0, y: 0 };
  let contextMenuTarget = null;
  let searchQuery = '';
  let filteredFiles = [];
  let isSearching = false;

  // Build file tree from flat file list
  $: if ($projectFiles) {
    buildFileTree($projectFiles);
    filterFiles();
  }

  $: if (searchQuery) {
    filterFiles();
  }

  function buildFileTree(files) {
    const tree = {};
    
    files.forEach(file => {
      const parts = file.file.split('/');
      let current = tree;
      
      parts.forEach((part, index) => {
        if (!current[part]) {
          current[part] = {
            name: part,
            path: parts.slice(0, index + 1).join('/'),
            isFile: index === parts.length - 1,
            children: {},
            content: index === parts.length - 1 ? file.code : null,
            size: index === parts.length - 1 ? new Blob([file.code || '']).size : 0,
            modified: false,
            lastModified: new Date()
          };
        }
        current = current[part].children;
      });
    });
    
    fileTree.set(tree);
  }

  function filterFiles() {
    if (!searchQuery.trim()) {
      filteredFiles = [];
      isSearching = false;
      return;
    }

    isSearching = true;
    const query = searchQuery.toLowerCase();
    
    filteredFiles = ($projectFiles || [])
      .filter(file => 
        file.file.toLowerCase().includes(query) ||
        (file.code && file.code.toLowerCase().includes(query))
      )
      .map(file => ({
        ...file,
        matchType: file.file.toLowerCase().includes(query) ? 'filename' : 'content'
      }))
      .sort((a, b) => {
        // Prioritize filename matches over content matches
        if (a.matchType !== b.matchType) {
          return a.matchType === 'filename' ? -1 : 1;
        }
        return a.file.localeCompare(b.file);
      });
  }

  function selectFile(file) {
    if (file.isFile) {
      editorActions.openFile(file);
      dispatch('fileSelect', file);
    } else {
      editorActions.toggleFolder(file.path);
    }
  }

  function getFileIcon(filename, isFolder = false) {
    if (isFolder) {
      return 'fas fa-folder text-yellow-600';
    }

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
      'md': 'fab fa-markdown text-gray-600',
      'xml': 'fas fa-code text-orange-400',
      'svg': 'fas fa-vector-square text-purple-500',
      'png': 'fas fa-image text-green-400',
      'jpg': 'fas fa-image text-green-400',
      'gif': 'fas fa-image text-green-400',
      'pdf': 'fas fa-file-pdf text-red-500',
      'zip': 'fas fa-file-archive text-gray-500'
    };
    
    return iconMap[ext] || 'fas fa-file text-gray-400';
  }

  function showContextMenu(event, item) {
    event.preventDefault();
    event.stopPropagation();
    
    contextMenuPosition = { x: event.clientX, y: event.clientY };
    contextMenuTarget = item;
    contextMenu = true;
  }

  function hideContextMenu() {
    contextMenu = false;
    contextMenuTarget = null;
  }

  function handleContextAction(action) {
    if (!contextMenuTarget) return;
    
    switch (action) {
      case 'open':
        selectFile(contextMenuTarget);
        break;
      case 'rename':
        renameItem(contextMenuTarget);
        break;
      case 'delete':
        deleteItem(contextMenuTarget);
        break;
      case 'duplicate':
        duplicateItem(contextMenuTarget);
        break;
      case 'newFile':
        createNewFile(contextMenuTarget);
        break;
      case 'newFolder':
        createNewFolder(contextMenuTarget);
        break;
      case 'copy':
        copyItem(contextMenuTarget);
        break;
      case 'cut':
        cutItem(contextMenuTarget);
        break;
    }
    
    hideContextMenu();
  }

  function renameItem(item) {
    const newName = prompt('Enter new name:', item.name);
    if (newName && newName !== item.name) {
      dispatch('rename', { oldPath: item.path, newName });
    }
  }

  function deleteItem(item) {
    if (confirm(`Are you sure you want to delete ${item.name}?`)) {
      dispatch('delete', { path: item.path, isFile: item.isFile });
    }
  }

  function duplicateItem(item) {
    const newName = prompt('Enter name for duplicate:', `${item.name}_copy`);
    if (newName) {
      dispatch('duplicate', { path: item.path, newName });
    }
  }

  function createNewFile(parentItem) {
    const fileName = prompt('Enter file name:');
    if (fileName) {
      const parentPath = parentItem.isFile 
        ? parentItem.path.split('/').slice(0, -1).join('/') 
        : parentItem.path;
      const newPath = parentPath ? `${parentPath}/${fileName}` : fileName;
      dispatch('newFile', { path: newPath });
    }
  }

  function createNewFolder(parentItem) {
    const folderName = prompt('Enter folder name:');
    if (folderName) {
      const parentPath = parentItem.isFile 
        ? parentItem.path.split('/').slice(0, -1).join('/') 
        : parentItem.path;
      const newPath = parentPath ? `${parentPath}/${folderName}` : folderName;
      dispatch('newFolder', { path: newPath });
    }
  }

  function copyItem(item) {
    // Implement copy functionality
    navigator.clipboard.writeText(JSON.stringify(item));
  }

  function cutItem(item) {
    // Implement cut functionality
    copyItem(item);
    // Mark for deletion after paste
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function clearSearch() {
    searchQuery = '';
    isSearching = false;
  }
</script>

<div class="smart-file-explorer h-full bg-secondary border-r border-border flex flex-col">
  <!-- Header -->
  <div class="p-3 border-b border-border">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-semibold text-foreground">Explorer</h3>
      <div class="flex gap-1">
        <button 
          class="p-1 hover:bg-background rounded text-tertiary hover:text-foreground transition-colors"
          title="New File"
          on:click={() => createNewFile({ path: '', isFile: false })}
        >
          <i class="fas fa-file-plus text-xs"></i>
        </button>
        <button 
          class="p-1 hover:bg-background rounded text-tertiary hover:text-foreground transition-colors"
          title="New Folder"
          on:click={() => createNewFolder({ path: '', isFile: false })}
        >
          <i class="fas fa-folder-plus text-xs"></i>
        </button>
        <button 
          class="p-1 hover:bg-background rounded text-tertiary hover:text-foreground transition-colors"
          title="Refresh"
          on:click={() => dispatch('refresh')}
        >
          <i class="fas fa-sync text-xs"></i>
        </button>
      </div>
    </div>
    
    <p class="text-xs text-tertiary mb-2">{$selectedProject || 'No project selected'}</p>
    
    <!-- Search -->
    <div class="relative">
      <input
        type="text"
        placeholder="Search files..."
        bind:value={searchQuery}
        class="w-full px-3 py-1 text-xs bg-background border border-border rounded focus:outline-none focus:border-primary"
        use:shortcut={{
          'escape': clearSearch
        }}
      />
      {#if searchQuery}
        <button
          class="absolute right-2 top-1/2 transform -translate-y-1/2 text-tertiary hover:text-foreground"
          on:click={clearSearch}
        >
          <i class="fas fa-times text-xs"></i>
        </button>
      {/if}
    </div>
  </div>
  
  <!-- File Tree / Search Results -->
  <div class="flex-1 overflow-y-auto p-2">
    {#if isSearching}
      <!-- Search Results -->
      <div class="space-y-1">
        <div class="text-xs text-tertiary mb-2">
          {filteredFiles.length} result{filteredFiles.length !== 1 ? 's' : ''}
        </div>
        {#each filteredFiles as file}
          <div 
            class="file-item flex items-center py-1 px-2 hover:bg-background cursor-pointer rounded text-sm group"
            class:selected={$editorState.activeFile?.path === file.file}
            on:click={() => selectFile({ ...file, path: file.file, name: file.file.split('/').pop(), isFile: true })}
            on:contextmenu={(e) => showContextMenu(e, { ...file, path: file.file, name: file.file.split('/').pop(), isFile: true })}
            transition:fade={{ duration: 150 }}
          >
            <i class="{getFileIcon(file.file)} mr-2 text-xs"></i>
            <div class="flex-1 min-w-0">
              <div class="truncate">{file.file}</div>
              {#if file.matchType === 'content'}
                <div class="text-xs text-tertiary">Content match</div>
              {/if}
            </div>
            <div class="text-xs text-tertiary opacity-0 group-hover:opacity-100 transition-opacity">
              {formatFileSize(new Blob([file.code || '']).size)}
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <!-- File Tree -->
      {#if Object.keys($fileTree).length === 0}
        <div class="text-center text-tertiary text-sm py-8">
          <i class="fas fa-folder-open text-2xl mb-2"></i>
          <p>No files in project</p>
        </div>
      {:else}
        {#each Object.values($fileTree) as item}
          <FileTreeItem 
            {item} 
            expandedFolders={$editorState.expandedFolders}
            selectedFile={$editorState.activeFile}
            on:select={(e) => selectFile(e.detail)}
            on:contextmenu={(e) => showContextMenu(e.detail.event, e.detail.item)}
          />
        {/each}
      {/if}
    {/if}
  </div>
</div>

<!-- Context Menu -->
{#if contextMenu}
  <div 
    class="context-menu fixed bg-background border border-border rounded-lg shadow-lg py-1 z-50 min-w-40"
    style="left: {contextMenuPosition.x}px; top: {contextMenuPosition.y}px;"
    use:clickOutside={hideContextMenu}
    transition:fade={{ duration: 150 }}
  >
    {#if contextMenuTarget?.isFile}
      <button class="context-menu-item" on:click={() => handleContextAction('open')}>
        <i class="fas fa-external-link-alt"></i> Open
      </button>
      <div class="context-menu-separator"></div>
      <button class="context-menu-item" on:click={() => handleContextAction('copy')}>
        <i class="fas fa-copy"></i> Copy
      </button>
      <button class="context-menu-item" on:click={() => handleContextAction('cut')}>
        <i class="fas fa-cut"></i> Cut
      </button>
      <div class="context-menu-separator"></div>
      <button class="context-menu-item" on:click={() => handleContextAction('rename')}>
        <i class="fas fa-edit"></i> Rename
      </button>
      <button class="context-menu-item" on:click={() => handleContextAction('duplicate')}>
        <i class="fas fa-clone"></i> Duplicate
      </button>
      <div class="context-menu-separator"></div>
      <button class="context-menu-item text-red-500" on:click={() => handleContextAction('delete')}>
        <i class="fas fa-trash"></i> Delete
      </button>
    {:else}
      <button class="context-menu-item" on:click={() => handleContextAction('newFile')}>
        <i class="fas fa-file-plus"></i> New File
      </button>
      <button class="context-menu-item" on:click={() => handleContextAction('newFolder')}>
        <i class="fas fa-folder-plus"></i> New Folder
      </button>
      <div class="context-menu-separator"></div>
      <button class="context-menu-item" on:click={() => handleContextAction('copy')}>
        <i class="fas fa-copy"></i> Copy
      </button>
      <button class="context-menu-item" on:click={() => handleContextAction('cut')}>
        <i class="fas fa-cut"></i> Cut
      </button>
      <div class="context-menu-separator"></div>
      <button class="context-menu-item" on:click={() => handleContextAction('rename')}>
        <i class="fas fa-edit"></i> Rename
      </button>
      <div class="context-menu-separator"></div>
      <button class="context-menu-item text-red-500" on:click={() => handleContextAction('delete')}>
        <i class="fas fa-trash"></i> Delete
      </button>
    {/if}
  </div>
{/if}

<!-- File Tree Item Component -->
<script context="module">
  import { createEventDispatcher } from 'svelte';
  
  export function FileTreeItem({ item, expandedFolders, selectedFile, level = 0 }) {
    const dispatch = createEventDispatcher();
    
    function handleSelect() {
      dispatch('select', item);
    }
    
    function handleContextMenu(event) {
      dispatch('contextmenu', { event, item });
    }
    
    const isExpanded = expandedFolders.has(item.path);
    const isSelected = selectedFile?.path === item.path;
    
    return {
      item,
      level,
      isExpanded,
      isSelected,
      handleSelect,
      handleContextMenu
    };
  }
</script>

<div class="file-tree-item">
  <div 
    class="file-item flex items-center py-1 px-2 hover:bg-background cursor-pointer rounded text-sm group"
    class:selected={selectedFile?.path === item.path}
    style="padding-left: {level * 16 + 8}px"
    on:click={() => selectFile(item)}
    on:contextmenu={(e) => showContextMenu(e, item)}
    transition:slide={{ duration: 200, easing: quintOut }}
  >
    {#if !item.isFile}
      <i class="fas fa-chevron-{expandedFolders.has(item.path) ? 'down' : 'right'} text-xs text-tertiary mr-1 transition-transform"></i>
      <i class="fas fa-folder text-yellow-600 mr-2"></i>
    {:else}
      <span class="w-3 mr-1"></span>
      <i class="{getFileIcon(item.name)} mr-2"></i>
    {/if}
    
    <span class="truncate flex-1">{item.name}</span>
    
    {#if item.isFile}
      <div class="text-xs text-tertiary opacity-0 group-hover:opacity-100 transition-opacity">
        {formatFileSize(item.size)}
      </div>
    {/if}
    
    {#if item.modified}
      <div class="w-2 h-2 bg-orange-500 rounded-full ml-1"></div>
    {/if}
  </div>
  
  {#if !item.isFile && expandedFolders.has(item.path)}
    <div transition:slide={{ duration: 200, easing: quintOut }}>
      {#each Object.values(item.children) as child}
        <svelte:self 
          item={child} 
          {expandedFolders} 
          {selectedFile} 
          level={level + 1} 
          on:select 
          on:contextmenu 
        />
      {/each}
    </div>
  {/if}
</div>

<style>
  .smart-file-explorer {
    min-width: 250px;
    max-width: 400px;
  }
  
  .file-item.selected {
    background-color: var(--primary);
    color: var(--foreground-invert);
  }
  
  .context-menu {
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
</style>