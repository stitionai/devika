<script>
  import { onMount, onDestroy } from 'svelte';
  import { projectFiles, selectedProject } from '$lib/store';
  import { API_BASE_URL } from '$lib/api';
  import { toast } from 'svelte-sonner';
  
  import EditorCore from './EditorCore.svelte';
  import FileExplorer from './FileExplorer.svelte';
  import TabManager from './TabManager.svelte';
  import EditorToolbar from './EditorToolbar.svelte';
  import StatusBar from './StatusBar.svelte';
  import { getLanguageFromFilename, getTheme } from './monaco-config.js';

  // Editor state
  let editorCore;
  let monaco;
  let editor;
  
  // File management
  let openTabs = [];
  let activeTab = null;
  let selectedFile = null;
  let expandedFolders = new Set(['']);
  
  // Editor settings
  let editorTheme = getTheme();
  let fontSize = 14;
  let wordWrap = true;
  let minimap = true;
  let lineNumbers = true;
  
  // Status
  let cursorPosition = { lineNumber: 1, column: 1 };
  let selection = null;
  let isModified = false;
  let canUndo = false;
  let canRedo = false;
  let fileSize = 0;

  // File operations
  async function saveFile(file) {
    if (!file || !file.content) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/save-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: $selectedProject,
          file_path: file.path,
          content: file.content
        })
      });
      
      if (response.ok) {
        file.modified = false;
        updateTab(file);
        toast.success(`Saved ${file.name}`);
      } else {
        throw new Error('Failed to save file');
      }
    } catch (error) {
      console.error('Save error:', error);
      toast.error(`Failed to save ${file.name}`);
    }
  }

  async function createNewFile(path) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/create-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: $selectedProject,
          file_path: path,
          content: ''
        })
      });
      
      if (response.ok) {
        // Refresh project files
        await refreshProjectFiles();
        toast.success(`Created ${path}`);
      } else {
        throw new Error('Failed to create file');
      }
    } catch (error) {
      console.error('Create file error:', error);
      toast.error(`Failed to create ${path}`);
    }
  }

  async function deleteFile(path) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/delete-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: $selectedProject,
          file_path: path
        })
      });
      
      if (response.ok) {
        // Close tab if open
        const tabIndex = openTabs.findIndex(tab => tab.path === path);
        if (tabIndex !== -1) {
          closeTab(openTabs[tabIndex]);
        }
        
        // Refresh project files
        await refreshProjectFiles();
        toast.success(`Deleted ${path}`);
      } else {
        throw new Error('Failed to delete file');
      }
    } catch (error) {
      console.error('Delete file error:', error);
      toast.error(`Failed to delete ${path}`);
    }
  }

  async function refreshProjectFiles() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-project-files?project_name=${$selectedProject}`);
      const data = await response.json();
      projectFiles.set(data.files);
    } catch (error) {
      console.error('Refresh files error:', error);
    }
  }

  // Tab management
  function openFileInTab(file) {
    const existingTab = openTabs.find(tab => tab.path === file.path);
    
    if (existingTab) {
      activeTab = existingTab;
    } else {
      const newTab = {
        ...file,
        modified: false,
        content: file.content || ''
      };
      openTabs = [...openTabs, newTab];
      activeTab = newTab;
    }
    
    // Update editor content
    if (editorCore) {
      editorCore.setValue(activeTab.content);
      editorCore.setLanguage(getLanguageFromFilename(activeTab.name));
    }
  }

  function closeTab(tab) {
    if (tab.modified) {
      const shouldSave = confirm(`${tab.name} has unsaved changes. Save before closing?`);
      if (shouldSave) {
        saveFile(tab);
      }
    }
    
    const tabIndex = openTabs.findIndex(t => t.path === tab.path);
    if (tabIndex !== -1) {
      openTabs.splice(tabIndex, 1);
      openTabs = openTabs;
      
      if (activeTab?.path === tab.path) {
        activeTab = openTabs[Math.max(0, tabIndex - 1)] || null;
        
        if (activeTab && editorCore) {
          editorCore.setValue(activeTab.content);
          editorCore.setLanguage(getLanguageFromFilename(activeTab.name));
        }
      }
    }
  }

  function updateTab(updatedTab) {
    const tabIndex = openTabs.findIndex(tab => tab.path === updatedTab.path);
    if (tabIndex !== -1) {
      openTabs[tabIndex] = { ...openTabs[tabIndex], ...updatedTab };
      openTabs = openTabs;
    }
  }

  // Editor event handlers
  function handleEditorReady(event) {
    editor = event.detail.editor;
    monaco = event.detail.monaco;
  }

  function handleEditorChange(event) {
    if (activeTab) {
      activeTab.content = event.detail.value;
      activeTab.modified = true;
      updateTab(activeTab);
      
      // Update file size
      fileSize = new Blob([event.detail.value]).size;
    }
  }

  function handleCursorChange(event) {
    cursorPosition = event.detail.position;
  }

  function handleEditorSave() {
    if (activeTab) {
      saveFile(activeTab);
    }
  }

  // Toolbar actions
  function handleToolbarAction(event) {
    const { action } = event.detail;
    
    switch (action) {
      case 'newFile':
        const fileName = prompt('Enter file name:');
        if (fileName) {
          createNewFile(fileName);
        }
        break;
        
      case 'save':
        if (activeTab) {
          saveFile(activeTab);
        }
        break;
        
      case 'saveAll':
        openTabs.filter(tab => tab.modified).forEach(tab => saveFile(tab));
        break;
        
      case 'undo':
        if (editor) {
          editor.trigger('keyboard', 'undo', null);
        }
        break;
        
      case 'redo':
        if (editor) {
          editor.trigger('keyboard', 'redo', null);
        }
        break;
        
      case 'find':
        if (editor) {
          editor.getAction('actions.find').run();
        }
        break;
        
      case 'findReplace':
        if (editor) {
          editor.getAction('editor.action.startFindReplaceAction').run();
        }
        break;
        
      case 'format':
        if (editorCore) {
          editorCore.formatDocument();
        }
        break;
        
      case 'toggleComment':
        if (editor) {
          editor.getAction('editor.action.commentLine').run();
        }
        break;
        
      case 'toggleWordWrap':
        wordWrap = !wordWrap;
        if (editor) {
          editor.updateOptions({ wordWrap: wordWrap ? 'on' : 'off' });
        }
        break;
        
      case 'toggleMinimap':
        minimap = !minimap;
        if (editor) {
          editor.updateOptions({ minimap: { enabled: minimap } });
        }
        break;
    }
  }

  function handleFontSizeChange(event) {
    fontSize = event.detail.fontSize;
    if (editor) {
      editor.updateOptions({ fontSize });
    }
  }

  // File explorer events
  function handleFileSelect(event) {
    selectedFile = event.detail;
    openFileInTab(selectedFile);
  }

  function handleFileCreate(event) {
    createNewFile(event.detail.path);
  }

  function handleFileDelete(event) {
    deleteFile(event.detail.path);
  }

  // Keyboard shortcuts
  function handleKeydown(event) {
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case 's':
          event.preventDefault();
          if (event.shiftKey) {
            // Save all
            openTabs.filter(tab => tab.modified).forEach(tab => saveFile(tab));
          } else if (activeTab) {
            saveFile(activeTab);
          }
          break;
          
        case 'n':
          event.preventDefault();
          const fileName = prompt('Enter file name:');
          if (fileName) {
            createNewFile(fileName);
          }
          break;
          
        case 'w':
          event.preventDefault();
          if (activeTab) {
            closeTab(activeTab);
          }
          break;
      }
    }
  }

  // Theme handling
  function updateTheme() {
    editorTheme = getTheme();
    if (editorCore) {
      editorCore.setTheme(editorTheme);
    }
  }

  // Watch for theme changes
  onMount(() => {
    const observer = new MutationObserver(updateTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    });
    
    return () => observer.disconnect();
  });

  // Update editor state
  $: if (editor) {
    canUndo = editor.getModel()?.canUndo() || false;
    canRedo = editor.getModel()?.canRedo() || false;
  }

  $: if (activeTab) {
    fileSize = new Blob([activeTab.content || '']).size;
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="web-code-editor h-full flex flex-col bg-background">
  <!-- Toolbar -->
  <EditorToolbar
    currentFile={activeTab}
    {isModified}
    {canUndo}
    {canRedo}
    {wordWrap}
    {minimap}
    {fontSize}
    on:action={handleToolbarAction}
    on:fontSizeChange={handleFontSizeChange}
  />
  
  <!-- Main Content -->
  <div class="editor-content flex flex-1 overflow-hidden">
    <!-- File Explorer -->
    <FileExplorer
      {selectedFile}
      {expandedFolders}
      on:fileSelect={handleFileSelect}
      on:newFile={handleFileCreate}
      on:delete={handleFileDelete}
    />
    
    <!-- Editor Area -->
    <div class="editor-area flex flex-col flex-1">
      <!-- Tab Manager -->
      <TabManager
        tabs={openTabs}
        {activeTab}
        on:tabSelect={(e) => { activeTab = e.detail; openFileInTab(activeTab); }}
        on:tabClose={(e) => closeTab(e.detail)}
        on:closeAllTabs={() => { openTabs = []; activeTab = null; }}
      />
      
      <!-- Editor -->
      <div class="editor-container flex-1">
        {#if activeTab}
          <EditorCore
            bind:this={editorCore}
            value={activeTab.content}
            language={getLanguageFromFilename(activeTab.name)}
            theme={editorTheme}
            {fontSize}
            {wordWrap}
            {minimap}
            {lineNumbers}
            on:ready={handleEditorReady}
            on:change={handleEditorChange}
            on:cursorChange={handleCursorChange}
            on:save={handleEditorSave}
          />
        {:else}
          <div class="empty-editor flex items-center justify-center h-full text-tertiary">
            <div class="text-center">
              <i class="fas fa-code text-4xl mb-4"></i>
              <p class="text-lg mb-2">Welcome to Devika Code Editor</p>
              <p class="text-sm">Select a file from the explorer or create a new one to start coding</p>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
  
  <!-- Status Bar -->
  <StatusBar
    currentFile={activeTab}
    {cursorPosition}
    {selection}
    language={activeTab ? getLanguageFromFilename(activeTab.name) : 'plaintext'}
    {fileSize}
    isConnected={true}
  />
</div>

<style>
  .web-code-editor {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }
  
  .editor-content {
    min-height: 0; /* Allow flex child to shrink */
  }
  
  .editor-area {
    min-width: 0; /* Allow flex child to shrink */
  }
  
  .editor-container {
    min-height: 0; /* Allow flex child to shrink */
  }
  
  .empty-editor {
    background-color: var(--terminal-window-background);
  }
</style>