<script>
  import { onMount, onDestroy } from 'svelte';
  import { projectFiles, selectedProject } from '$lib/store';
  import { editorState, editorSettings, editorActions, commandPalette, notify } from '$lib/stores/editor.js';
  import { API_BASE_URL } from '$lib/api';
  import { toast } from 'svelte-sonner';
  
  import EnhancedEditor from './EnhancedEditor.svelte';
  import SmartFileExplorer from './SmartFileExplorer.svelte';
  import AdvancedTabManager from './AdvancedTabManager.svelte';
  import EditorToolbar from './EditorToolbar.svelte';
  import StatusBar from './StatusBar.svelte';
  import CommandPalette from './CommandPalette.svelte';
  import NotificationSystem from './NotificationSystem.svelte';

  let editorComponent;
  let unsavedChangesBeforeUnload = false;

  // Auto-save functionality
  $: if ($editorSettings.autoSave && $editorState.isDirty) {
    scheduleAutoSave();
  }

  let autoSaveTimeout;
  function scheduleAutoSave() {
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(async () => {
      const unsavedTabs = $editorState.openTabs.filter(tab => tab.modified);
      for (const tab of unsavedTabs) {
        await saveFile(tab);
      }
    }, $editorSettings.autoSaveDelay);
  }

  // File operations
  async function saveFile(file) {
    if (!file) return;
    
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
        editorActions.markClean(file);
        notify.success(`Saved ${file.name}`);
        return true;
      } else {
        throw new Error('Failed to save file');
      }
    } catch (error) {
      console.error('Save error:', error);
      notify.error(`Failed to save ${file.name}`);
      return false;
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
        await refreshProjectFiles();
        notify.success(`Created ${path}`);
        
        // Open the new file
        const newFile = {
          name: path.split('/').pop(),
          path: path,
          content: '',
          isFile: true
        };
        editorActions.openFile(newFile);
      } else {
        throw new Error('Failed to create file');
      }
    } catch (error) {
      console.error('Create file error:', error);
      notify.error(`Failed to create ${path}`);
    }
  }

  async function deleteFile(path, isFile = true) {
    try {
      const endpoint = isFile ? '/api/delete-file' : '/api/delete-folder';
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: $selectedProject,
          file_path: path
        })
      });
      
      if (response.ok) {
        // Close tab if open
        if (isFile) {
          const tab = $editorState.openTabs.find(tab => tab.path === path);
          if (tab) {
            editorActions.closeFile(tab);
          }
        }
        
        await refreshProjectFiles();
        notify.success(`Deleted ${path}`);
      } else {
        throw new Error('Failed to delete');
      }
    } catch (error) {
      console.error('Delete error:', error);
      notify.error(`Failed to delete ${path}`);
    }
  }

  async function refreshProjectFiles() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/get-project-files?project_name=${$selectedProject}`);
      const data = await response.json();
      projectFiles.set(data.files);
    } catch (error) {
      console.error('Refresh files error:', error);
      notify.error('Failed to refresh project files');
    }
  }

  // Editor event handlers
  function handleEditorReady(event) {
    console.log('Enhanced editor ready');
  }

  function handleEditorChange(event) {
    // Content changes are handled automatically by the enhanced editor
  }

  function handleEditorSave(event) {
    const { file } = event.detail;
    saveFile(file);
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
        if ($editorState.activeFile) {
          saveFile($editorState.activeFile);
        }
        break;
        
      case 'saveAll':
        $editorState.openTabs.filter(tab => tab.modified).forEach(tab => saveFile(tab));
        break;
        
      case 'find':
        if (editorComponent) {
          const editor = editorComponent.getEditor();
          if (editor) {
            editor.getAction('actions.find').run();
          }
        }
        break;
        
      case 'findReplace':
        if (editorComponent) {
          const editor = editorComponent.getEditor();
          if (editor) {
            editor.getAction('editor.action.startFindReplaceAction').run();
          }
        }
        break;
        
      case 'format':
        if (editorComponent) {
          const editor = editorComponent.getEditor();
          if (editor) {
            editor.getAction('editor.action.formatDocument').run();
          }
        }
        break;
        
      case 'toggleWordWrap':
        editorSettings.update(settings => ({
          ...settings,
          wordWrap: !settings.wordWrap
        }));
        break;
        
      case 'toggleMinimap':
        editorSettings.update(settings => ({
          ...settings,
          minimap: !settings.minimap
        }));
        break;
    }
  }

  function handleFontSizeChange(event) {
    const { fontSize } = event.detail;
    editorSettings.update(settings => ({
      ...settings,
      fontSize
    }));
  }

  // File explorer events
  function handleFileSelect(event) {
    const file = event.detail;
    editorActions.openFile(file);
  }

  function handleFileCreate(event) {
    createNewFile(event.detail.path);
  }

  function handleFileDelete(event) {
    deleteFile(event.detail.path, event.detail.isFile);
  }

  function handleFileRename(event) {
    // Implement rename functionality
    console.log('Rename file:', event.detail);
  }

  // Command palette
  function openCommandPalette() {
    commandPalette.update(state => ({
      ...state,
      isOpen: true
    }));
  }

  function handleCommandPaletteAction(event) {
    // Handle command palette actions
    console.log('Command palette action:', event.type);
  }

  // Keyboard shortcuts
  function handleKeydown(event) {
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case 'p':
          if (event.shiftKey) {
            event.preventDefault();
            openCommandPalette();
          }
          break;
          
        case 's':
          event.preventDefault();
          if (event.shiftKey) {
            // Save all
            $editorState.openTabs.filter(tab => tab.modified).forEach(tab => saveFile(tab));
          } else if ($editorState.activeFile) {
            saveFile($editorState.activeFile);
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
          if ($editorState.activeFile) {
            editorActions.closeFile($editorState.activeFile);
          }
          break;
      }
    }
  }

  // Prevent data loss
  function handleBeforeUnload(event) {
    if ($editorState.openTabs.some(tab => tab.modified)) {
      event.preventDefault();
      event.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
      return event.returnValue;
    }
  }

  onMount(() => {
    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('keydown', handleKeydown);
  });

  onDestroy(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
    document.removeEventListener('keydown', handleKeydown);
    clearTimeout(autoSaveTimeout);
  });

  // Theme handling
  $: if (typeof window !== 'undefined') {
    const theme = document.documentElement.classList.contains('dark') ? 'vs-dark' : 'vs';
    editorSettings.update(settings => ({
      ...settings,
      theme
    }));
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="enhanced-web-code-editor h-full flex flex-col bg-background">
  <!-- Toolbar -->
  <EditorToolbar
    currentFile={$editorState.activeFile}
    isModified={$editorState.isDirty}
    canUndo={false}
    canRedo={false}
    wordWrap={$editorSettings.wordWrap}
    minimap={$editorSettings.minimap}
    fontSize={$editorSettings.fontSize}
    on:action={handleToolbarAction}
    on:fontSizeChange={handleFontSizeChange}
  />
  
  <!-- Main Content -->
  <div class="editor-content flex flex-1 overflow-hidden">
    <!-- File Explorer -->
    <SmartFileExplorer
      on:fileSelect={handleFileSelect}
      on:newFile={handleFileCreate}
      on:delete={handleFileDelete}
      on:rename={handleFileRename}
      on:refresh={refreshProjectFiles}
    />
    
    <!-- Editor Area -->
    <div class="editor-area flex flex-col flex-1 min-w-0">
      <!-- Tab Manager -->
      <AdvancedTabManager
        on:save={handleEditorSave}
        on:revealInExplorer={(e) => console.log('Reveal in explorer:', e.detail)}
      />
      
      <!-- Editor -->
      <div class="editor-container flex-1 min-h-0">
        {#if $editorState.activeFile}
          <EnhancedEditor
            bind:this={editorComponent}
            height="100%"
            on:ready={handleEditorReady}
            on:change={handleEditorChange}
            on:save={handleEditorSave}
            on:quickOpen={openCommandPalette}
            on:commandPalette={openCommandPalette}
          />
        {:else}
          <div class="empty-editor flex items-center justify-center h-full text-tertiary">
            <div class="text-center">
              <i class="fas fa-code text-6xl mb-4 opacity-50"></i>
              <h2 class="text-2xl mb-2 font-light">Welcome to Devika Code Editor</h2>
              <p class="text-lg mb-4 opacity-75">Enhanced with Svelte for the best coding experience</p>
              <div class="space-y-2 text-sm">
                <p><kbd class="kbd">Ctrl+P</kbd> Quick Open</p>
                <p><kbd class="kbd">Ctrl+Shift+P</kbd> Command Palette</p>
                <p><kbd class="kbd">Ctrl+N</kbd> New File</p>
                <p><kbd class="kbd">Ctrl+S</kbd> Save File</p>
              </div>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
  
  <!-- Status Bar -->
  <StatusBar
    currentFile={$editorState.activeFile}
    cursorPosition={$editorState.cursorPosition}
    selection={$editorState.selection}
    language={$editorState.activeFile ? 'javascript' : 'plaintext'}
    fileSize={$editorState.activeFile ? new Blob([$editorState.activeFile.content || '']).size : 0}
    isConnected={true}
  />
</div>

<!-- Command Palette -->
<CommandPalette
  on:newFile={() => {
    const fileName = prompt('Enter file name:');
    if (fileName) createNewFile(fileName);
  }}
  on:save={() => $editorState.activeFile && saveFile($editorState.activeFile)}
  on:saveAll={() => $editorState.openTabs.filter(tab => tab.modified).forEach(tab => saveFile(tab))}
  on:find={() => {
    if (editorComponent) {
      const editor = editorComponent.getEditor();
      if (editor) editor.getAction('actions.find').run();
    }
  }}
  on:replace={() => {
    if (editorComponent) {
      const editor = editorComponent.getEditor();
      if (editor) editor.getAction('editor.action.startFindReplaceAction').run();
    }
  }}
  on:format={() => {
    if (editorComponent) {
      const editor = editorComponent.getEditor();
      if (editor) editor.getAction('editor.action.formatDocument').run();
    }
  }}
  on:toggleMinimap={() => {
    editorSettings.update(settings => ({ ...settings, minimap: !settings.minimap }));
  }}
  on:toggleWordWrap={() => {
    editorSettings.update(settings => ({ ...settings, wordWrap: !settings.wordWrap }));
  }}
  on:zoomIn={() => {
    editorSettings.update(settings => ({ ...settings, fontSize: Math.min(24, settings.fontSize + 1) }));
  }}
  on:zoomOut={() => {
    editorSettings.update(settings => ({ ...settings, fontSize: Math.max(10, settings.fontSize - 1) }));
  }}
  on:closeAllTabs={() => {
    $editorState.openTabs.forEach(tab => editorActions.closeFile(tab));
  }}
/>

<!-- Notification System -->
<NotificationSystem />

<style>
  .enhanced-web-code-editor {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
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
    background: linear-gradient(135deg, var(--terminal-window-background) 0%, var(--secondary) 100%);
  }
  
  .kbd {
    background-color: var(--secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2px 6px;
    font-family: monospace;
    font-size: 12px;
    margin: 0 2px;
  }
</style>