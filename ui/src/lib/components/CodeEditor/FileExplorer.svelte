<script>
  import { createEventDispatcher } from 'svelte';
  import { projectFiles, selectedProject } from '$lib/store';
  import { API_BASE_URL } from '$lib/api';
  import { toast } from 'svelte-sonner';

  const dispatch = createEventDispatcher();

  export let selectedFile = null;
  export let expandedFolders = new Set();

  let contextMenu = null;
  let contextMenuPosition = { x: 0, y: 0 };
  let contextMenuTarget = null;

  // File tree structure
  $: fileTree = buildFileTree($projectFiles || []);

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
            content: index === parts.length - 1 ? file.code : null
          };
        }
        current = current[part].children;
      });
    });
    
    return tree;
  }

  function toggleFolder(path) {
    if (expandedFolders.has(path)) {
      expandedFolders.delete(path);
    } else {
      expandedFolders.add(path);
    }
    expandedFolders = expandedFolders; // Trigger reactivity
  }

  function selectFile(file) {
    if (file.isFile) {
      selectedFile = file;
      dispatch('fileSelect', file);
    } else {
      toggleFolder(file.path);
    }
  }

  function getFileIcon(filename) {
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
      'sass': 'fab fa-sass text-pink-500',
      'json': 'fas fa-brackets-curly text-yellow-600',
      'md': 'fab fa-markdown text-gray-600',
      'xml': 'fas fa-code text-orange-400',
      'svg': 'fas fa-vector-square text-purple-500',
      'png': 'fas fa-image text-green-400',
      'jpg': 'fas fa-image text-green-400',
      'jpeg': 'fas fa-image text-green-400',
      'gif': 'fas fa-image text-green-400',
      'pdf': 'fas fa-file-pdf text-red-500',
      'zip': 'fas fa-file-archive text-gray-500',
      'txt': 'fas fa-file-text text-gray-400'
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
      case 'rename':
        renameFile(contextMenuTarget);
        break;
      case 'delete':
        deleteFile(contextMenuTarget);
        break;
      case 'duplicate':
        duplicateFile(contextMenuTarget);
        break;
      case 'newFile':
        createNewFile(contextMenuTarget);
        break;
      case 'newFolder':
        createNewFolder(contextMenuTarget);
        break;
    }
    
    hideContextMenu();
  }

  function renameFile(item) {
    const newName = prompt('Enter new name:', item.name);
    if (newName && newName !== item.name) {
      dispatch('rename', { oldPath: item.path, newName });
    }
  }

  function deleteFile(item) {
    if (confirm(`Are you sure you want to delete ${item.name}?`)) {
      dispatch('delete', { path: item.path });
    }
  }

  function duplicateFile(item) {
    const newName = prompt('Enter name for duplicate:', `${item.name}_copy`);
    if (newName) {
      dispatch('duplicate', { path: item.path, newName });
    }
  }

  function createNewFile(parentItem) {
    const fileName = prompt('Enter file name:');
    if (fileName) {
      const parentPath = parentItem.isFile ? parentItem.path.split('/').slice(0, -1).join('/') : parentItem.path;
      const newPath = parentPath ? `${parentPath}/${fileName}` : fileName;
      dispatch('newFile', { path: newPath });
    }
  }

  function createNewFolder(parentItem) {
    const folderName = prompt('Enter folder name:');
    if (folderName) {
      const parentPath = parentItem.isFile ? parentItem.path.split('/').slice(0, -1).join('/') : parentItem.path;
      const newPath = parentPath ? `${parentPath}/${folderName}` : folderName;
      dispatch('newFolder', { path: newPath });
    }
  }

  // Close context menu when clicking outside
  function handleDocumentClick() {
    hideContextMenu();
  }
</script>

<svelte:document on:click={handleDocumentClick} />

<div class="file-explorer h-full bg-secondary border-r border-border">
  <div class="p-3 border-b border-border">
    <h3 class="text-sm font-semibold text-foreground">Explorer</h3>
    <p class="text-xs text-tertiary">{$selectedProject || 'No project selected'}</p>
  </div>
  
  <div class="file-tree p-2 overflow-y-auto h-full">
    {#if Object.keys(fileTree).length === 0}
      <div class="text-center text-tertiary text-sm py-8">
        <i class="fas fa-folder-open text-2xl mb-2"></i>
        <p>No files in project</p>
      </div>
    {:else}
      {#each Object.values(fileTree) as item}
        <FileTreeItem 
          {item} 
          {expandedFolders} 
          {selectedFile}
          on:select={(e) => selectFile(e.detail)}
          on:contextmenu={(e) => showContextMenu(e.detail.event, e.detail.item)}
        />
      {/each}
    {/if}
  </div>
</div>

<!-- Context Menu -->
{#if contextMenu}
  <div 
    class="context-menu fixed bg-background border border-border rounded-lg shadow-lg py-1 z-50"
    style="left: {contextMenuPosition.x}px; top: {contextMenuPosition.y}px;"
  >
    {#if contextMenuTarget?.isFile}
      <button class="context-menu-item" on:click={() => handleContextAction('rename')}>
        <i class="fas fa-edit"></i> Rename
      </button>
      <button class="context-menu-item" on:click={() => handleContextAction('duplicate')}>
        <i class="fas fa-copy"></i> Duplicate
      </button>
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
      <button class="context-menu-item" on:click={() => handleContextAction('rename')}>
        <i class="fas fa-edit"></i> Rename
      </button>
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
    class="file-item flex items-center py-1 px-2 hover:bg-background cursor-pointer rounded text-sm"
    class:selected={selectedFile?.path === item.path}
    style="padding-left: {level * 16 + 8}px"
    on:click={() => selectFile(item)}
    on:contextmenu={(e) => showContextMenu(e, item)}
  >
    {#if !item.isFile}
      <i class="fas fa-chevron-{expandedFolders.has(item.path) ? 'down' : 'right'} text-xs text-tertiary mr-1"></i>
      <i class="fas fa-folder text-yellow-600 mr-2"></i>
    {:else}
      <span class="w-3 mr-1"></span>
      <i class="{getFileIcon(item.name)} mr-2"></i>
    {/if}
    <span class="truncate">{item.name}</span>
  </div>
  
  {#if !item.isFile && expandedFolders.has(item.path)}
    {#each Object.values(item.children) as child}
      <svelte:self item={child} {expandedFolders} {selectedFile} level={level + 1} on:select on:contextmenu />
    {/each}
  {/if}
</div>

<style>
  .file-explorer {
    min-width: 250px;
    max-width: 400px;
  }
  
  .file-item.selected {
    background-color: var(--primary);
    color: var(--foreground-invert);
  }
  
  .context-menu {
    min-width: 150px;
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
  }
  
  .context-menu-item:hover {
    background-color: var(--secondary);
  }
</style>