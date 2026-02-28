<script>
  import { onMount, onDestroy } from 'svelte';
  import { projectFiles, selectedProject } from '$lib/store';
  import { API_BASE_URL } from '$lib/api';
  import { toast } from 'svelte-sonner';
  
  // Monaco editor imports
  import loader from "@monaco-editor/loader";
  
  let editorContainer;
  let monaco;
  let editor;
  let currentFile = null;
  let openFiles = [];
  let fileTree = {};
  
  // Editor settings
  let theme = 'vs-dark';
  let fontSize = 14;
  let wordWrap = true;
  let minimap = true;
  
  onMount(async () => {
    try {
      // Initialize Monaco editor
      const monacoEditor = await import('monaco-editor');
      loader.config({ monaco: monacoEditor.default });
      monaco = await loader.init();
      
      // Create editor instance
      createEditor();
      
      // Build file tree from project files
      if ($projectFiles) {
        buildFileTree($projectFiles);
      }
      
      // Listen for theme changes
      const observer = new MutationObserver(() => {
        const isDark = document.documentElement.classList.contains('dark');
        theme = isDark ? 'vs-dark' : 'vs';
        if (editor) {
          monaco.editor.setTheme(theme);
        }
      });
      
      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      });
      
      return () => observer.disconnect();
    } catch (error) {
      console.error('Failed to initialize Monaco editor:', error);
      toast.error('Failed to initialize code editor');
    }
  });
  
  onDestroy(() => {
    if (editor) {
      editor.dispose();
    }
  });
  
  function createEditor() {
    if (!monaco || !editorContainer) return;
    
    editor = monaco.editor.create(editorContainer, {
      value: '',
      language: 'javascript',
      theme,
      fontSize,
      fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
      wordWrap: wordWrap ? 'on' : 'off',
      minimap: { enabled: minimap },
      lineNumbers: 'on',
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 2,
      insertSpaces: true
    });
    
    // Set up event listeners
    editor.onDidChangeModelContent(() => {
      if (currentFile) {
        currentFile.modified = true;
        updateOpenFile(currentFile);
      }
    });
    
    // Set up keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      if (currentFile) {
        saveFile(currentFile);
      }
    });
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
            content: index === parts.length - 1 ? file.code : null
          };
        }
        
        if (!current[part].isFile) {
          current = current[part].children;
        }
      });
    });
    
    fileTree = tree;
  }
  
  function getFileLanguage(filename) {
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
  
  function openFile(file) {
    if (!editor || !monaco) return;
    
    // Check if file is already open
    const existingFile = openFiles.find(f => f.path === file.path);
    
    if (existingFile) {
      currentFile = existingFile;
    } else {
      currentFile = { ...file, modified: false };
      openFiles = [...openFiles, currentFile];
    }
    
    // Create or get model for the file
    const uri = monaco.Uri.file(file.path);
    let model = monaco.editor.getModel(uri);
    
    if (!model) {
      model = monaco.editor.createModel(
        file.content || '',
        getFileLanguage(file.name),
        uri
      );
    }
    
    editor.setModel(model);
  }
  
  function updateOpenFile(file) {
    const index = openFiles.findIndex(f => f.path === file.path);
    if (index !== -1) {
      openFiles[index] = { ...file };
      openFiles = [...openFiles]; // Trigger reactivity
    }
  }
  
  async function saveFile(file) {
    if (!file) return;
    
    try {
      const content = editor.getValue();
      
      const response = await fetch(`${API_BASE_URL}/api/save-file`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_name: $selectedProject,
          file_path: file.path,
          content
        })
      });
      
      if (response.ok) {
        file.modified = false;
        updateOpenFile(file);
        toast.success(`Saved ${file.name}`);
      } else {
        throw new Error('Failed to save file');
      }
    } catch (error) {
      console.error('Error saving file:', error);
      toast.error(`Failed to save ${file.name}`);
    }
  }
  
  function closeFile(file) {
    const index = openFiles.findIndex(f => f.path === file.path);
    if (index !== -1) {
      openFiles.splice(index, 1);
      openFiles = [...openFiles]; // Trigger reactivity
      
      if (currentFile?.path === file.path) {
        currentFile = openFiles[0] || null;
        
        if (currentFile) {
          openFile(currentFile);
        } else {
          editor.setModel(null);
        }
      }
    }
  }
  
  function handleFileClick(file) {
    if (file.isFile) {
      openFile(file);
    }
  }
  
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
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
      'json': 'fas fa-code text-yellow-600',
      'md': 'fas fa-file-alt text-gray-600'
    };
    
    return iconMap[ext] || 'fas fa-file text-gray-400';
  }
  
  // Recursive component for file tree
  function FileTreeItem({ item, level = 0 }) {
    const isExpanded = true; // For simplicity, all folders are expanded
    
    return {
      item,
      level,
      isExpanded,
      handleFileClick
    };
  }
</script>

<div class="web-code-editor h-full flex flex-col border-[3px] rounded-xl overflow-hidden border-window-outline bg-background">
  <!-- Editor Header -->
  <div class="flex items-center p-2 border-b bg-secondary">
    <div class="flex ml-2 mr-4 space-x-2">
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
      <div class="w-3 h-3 rounded-full bg-terminal-window-dots"></div>
    </div>
    <span class="text-tertiary text-sm">Web Code Editor</span>
    
    <!-- Tabs -->
    <div class="flex ml-4 overflow-x-auto">
      {#each openFiles as file}
        <div 
          class="tab flex items-center px-3 py-1 border-r border-border cursor-pointer hover:bg-background transition-colors"
          class:active={currentFile?.path === file.path}
          on:click={() => openFile(file)}
        >
          <i class="{getFileIcon(file.name)} mr-2 text-xs"></i>
          <span class="text-sm">{file.name}</span>
          {#if file.modified}
            <div class="w-2 h-2 bg-orange-500 rounded-full ml-2"></div>
          {:else}
            <button 
              class="ml-2 text-tertiary hover:text-foreground"
              on:click|stopPropagation={() => closeFile(file)}
            >
              <i class="fas fa-times text-xs"></i>
            </button>
          {/if}
        </div>
      {/each}
    </div>
  </div>
  
  <!-- Main Content -->
  <div class="flex flex-1 overflow-hidden">
    <!-- File Explorer -->
    <div class="w-64 bg-secondary border-r border-border overflow-y-auto p-2">
      <div class="text-sm font-semibold mb-2">Explorer</div>
      
      <!-- File Tree -->
      {#if Object.keys(fileTree).length === 0}
        <div class="text-center text-tertiary text-sm py-8">
          <i class="fas fa-folder-open text-2xl mb-2"></i>
          <p>No files in project</p>
        </div>
      {:else}
        {#each Object.values(fileTree) as item}
          <div class="file-tree-item">
            <div 
              class="file-item flex items-center py-1 px-2 hover:bg-background cursor-pointer rounded text-sm"
              style="padding-left: 8px"
              on:click={() => handleFileClick(item)}
            >
              {#if !item.isFile}
                <i class="fas fa-folder text-yellow-600 mr-2"></i>
              {:else}
                <i class="{getFileIcon(item.name)} mr-2"></i>
              {/if}
              <span class="truncate">{item.name}</span>
            </div>
            
            {#if !item.isFile}
              <div class="pl-4">
                {#each Object.values(item.children) as child}
                  <div 
                    class="file-item flex items-center py-1 px-2 hover:bg-background cursor-pointer rounded text-sm"
                    on:click={() => handleFileClick(child)}
                  >
                    {#if !child.isFile}
                      <i class="fas fa-folder text-yellow-600 mr-2"></i>
                    {:else}
                      <i class="{getFileIcon(child.name)} mr-2"></i>
                    {/if}
                    <span class="truncate">{child.name}</span>
                  </div>
                  
                  {#if !child.isFile && Object.keys(child.children).length > 0}
                    <!-- Recursive rendering would go here -->
                  {/if}
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      {/if}
    </div>
    
    <!-- Editor -->
    <div class="flex-1 overflow-hidden" bind:this={editorContainer}>
      {#if !currentFile}
        <div class="flex items-center justify-center h-full text-tertiary">
          <div class="text-center">
            <i class="fas fa-code text-4xl mb-4"></i>
            <p class="text-lg mb-2">Select a file to edit</p>
            <p class="text-sm">Or create a new file to get started</p>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Status Bar -->
  <div class="flex items-center justify-between px-3 py-1 text-xs bg-secondary border-t border-border">
    <div class="flex items-center space-x-4">
      {#if currentFile}
        <span>{currentFile.path}</span>
        <span>{getFileLanguage(currentFile.name).toUpperCase()}</span>
      {/if}
    </div>
    <div class="flex items-center space-x-4">
      <span>Ln 1, Col 1</span>
      <span>UTF-8</span>
      <span>LF</span>
    </div>
  </div>
</div>

<style>
  .web-code-editor {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }
  
  .tab.active {
    background-color: var(--background);
    border-bottom: 2px solid var(--primary);
  }
  
  /* Hide scrollbar for tabs */
  .overflow-x-auto::-webkit-scrollbar {
    height: 0;
    width: 0;
  }
</style>