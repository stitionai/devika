class DevikaEditor {
    constructor(options) {
        this.container = options.container;
        this.theme = options.theme || 'vs-dark';
        this.language = options.language || 'plaintext';
        this.value = options.value || '';
        this.settings = options.settings || {};
        
        this.editor = null;
        this.currentFile = null;
        this.isModified = false;
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error('Editor container not found');
            return;
        }
        
        // Create Monaco editor
        this.editor = monaco.editor.create(this.container, {
            value: this.value,
            language: this.language,
            theme: this.theme === 'dark' ? 'vs-dark' : 'vs',
            fontSize: this.settings.fontSize || 14,
            fontFamily: this.settings.fontFamily || 'Monaco, Menlo, "Ubuntu Mono", monospace',
            wordWrap: this.settings.wordWrap ? 'on' : 'off',
            minimap: { enabled: this.settings.minimap !== false },
            lineNumbers: this.settings.lineNumbers !== false ? 'on' : 'off',
            tabSize: this.settings.tabSize || 2,
            insertSpaces: this.settings.insertSpaces !== false,
            automaticLayout: true,
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            cursorSmoothCaretAnimation: true,
            suggest: {
                showKeywords: true,
                showSnippets: true,
                showClasses: true,
                showFunctions: true,
                showVariables: true
            },
            quickSuggestions: {
                other: true,
                comments: false,
                strings: false
            }
        });
        
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
    }
    
    setupEventListeners() {
        // Content change
        this.editor.onDidChangeModelContent(() => {
            this.isModified = true;
            this.updateTabStatus();
            
            // Auto-save if enabled
            if (this.settings.autoSave) {
                this.scheduleAutoSave();
            }
        });
        
        // Cursor position change
        this.editor.onDidChangeCursorPosition((e) => {
            this.updateCursorPosition(e.position);
        });
        
        // Selection change
        this.editor.onDidChangeCursorSelection((e) => {
            this.updateSelection(e.selection);
        });
    }
    
    setupKeyboardShortcuts() {
        // Save file
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
            this.saveFile();
        });
        
        // Save all files
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyS, () => {
            this.saveAllFiles();
        });
        
        // New file
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyN, () => {
            this.newFile();
        });
        
        // Close tab
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyW, () => {
            this.closeCurrentTab();
        });
        
        // Command palette
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyP, () => {
            window.commandPalette.show();
        });
        
        // Format document
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyI, () => {
            this.formatDocument();
        });
        
        // Toggle comment
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash, () => {
            this.editor.getAction('editor.action.commentLine').run();
        });
    }
    
    loadFile(file) {
        this.currentFile = file;
        this.isModified = false;
        
        // Create or get model
        const uri = monaco.Uri.file(file.path);
        let model = monaco.editor.getModel(uri);
        
        if (!model) {
            model = monaco.editor.createModel(file.content, file.language, uri);
        } else {
            model.setValue(file.content);
        }
        
        this.editor.setModel(model);
        this.editor.focus();
        
        // Update UI
        this.updateTabStatus();
        this.updateCursorPosition(this.editor.getPosition());
    }
    
    async saveFile() {
        if (!this.currentFile) {
            window.notifications.show('No file to save', 'warning');
            return;
        }
        
        try {
            const content = this.editor.getValue();
            
            const response = await fetch('/editor/api/file/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project: window.DEVIKA_CONFIG.currentProject,
                    path: this.currentFile.path,
                    content: content
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isModified = false;
                this.updateTabStatus();
                window.notifications.show(result.message, 'success');
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Save error:', error);
            window.notifications.show('Failed to save file', 'error');
        }
    }
    
    async saveAllFiles() {
        // Get all modified tabs and save them
        const modifiedTabs = Array.from(document.querySelectorAll('.tab'))
            .filter(tab => tab.querySelector('.animate-pulse'))
            .map(tab => tab.dataset.path);
        
        for (const path of modifiedTabs) {
            // Switch to tab and save
            await this.switchToTab(path);
            await this.saveFile();
        }
        
        window.notifications.show(`Saved ${modifiedTabs.length} files`, 'success');
    }
    
    async newFile() {
        const fileName = prompt('Enter file name:');
        if (!fileName) return;
        
        try {
            const response = await fetch('/editor/api/file/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project: window.DEVIKA_CONFIG.currentProject,
                    path: fileName,
                    content: ''
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.notifications.show(result.message, 'success');
                // Reload page to show new file
                window.location.reload();
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Create file error:', error);
            window.notifications.show('Failed to create file', 'error');
        }
    }
    
    async closeCurrentTab() {
        if (!this.currentFile) return;
        
        if (this.isModified) {
            const shouldSave = confirm(`${this.currentFile.name} has unsaved changes. Save before closing?`);
            if (shouldSave) {
                await this.saveFile();
            }
        }
        
        try {
            const response = await fetch('/editor/api/tab/close', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: this.currentFile.path
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Reload page to update tabs
                window.location.reload();
            }
        } catch (error) {
            console.error('Close tab error:', error);
        }
    }
    
    formatDocument() {
        this.editor.getAction('editor.action.formatDocument').run();
    }
    
    updateTabStatus() {
        const tab = document.querySelector(`[data-path="${this.currentFile?.path}"]`);
        if (tab) {
            const indicator = tab.querySelector('.animate-pulse');
            const closeBtn = tab.querySelector('.tab-close');
            
            if (this.isModified) {
                if (!indicator) {
                    const pulse = document.createElement('div');
                    pulse.className = 'w-2 h-2 bg-warning rounded-full ml-2 animate-pulse';
                    tab.appendChild(pulse);
                }
                if (closeBtn) closeBtn.style.display = 'none';
            } else {
                if (indicator) indicator.remove();
                if (closeBtn) closeBtn.style.display = 'flex';
            }
        }
    }
    
    updateCursorPosition(position) {
        const cursorElement = document.getElementById('cursor-position');
        if (cursorElement && position) {
            cursorElement.textContent = `Ln ${position.lineNumber}, Col ${position.column}`;
        }
    }
    
    updateSelection(selection) {
        // Update selection info if needed
    }
    
    scheduleAutoSave() {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            if (this.isModified) {
                this.saveFile();
            }
        }, this.settings.autoSaveDelay || 2000);
    }
    
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        
        // Apply settings to editor
        this.editor.updateOptions({
            fontSize: this.settings.fontSize,
            fontFamily: this.settings.fontFamily,
            wordWrap: this.settings.wordWrap ? 'on' : 'off',
            minimap: { enabled: this.settings.minimap },
            lineNumbers: this.settings.lineNumbers ? 'on' : 'off',
            tabSize: this.settings.tabSize,
            insertSpaces: this.settings.insertSpaces
        });
    }
    
    setTheme(theme) {
        this.theme = theme;
        monaco.editor.setTheme(theme === 'dark' ? 'vs-dark' : 'vs');
    }
    
    dispose() {
        if (this.editor) {
            this.editor.dispose();
        }
        clearTimeout(this.autoSaveTimeout);
    }
}

// Global functions for template usage
window.handleFileClick = async function(path, type) {
    if (type === 'folder') {
        // Toggle folder
        try {
            const response = await fetch('/editor/api/folder/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ path })
            });
            
            if (response.ok) {
                window.location.reload();
            }
        } catch (error) {
            console.error('Toggle folder error:', error);
        }
    } else {
        // Open file
        try {
            const response = await fetch('/editor/api/file/open', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project: window.DEVIKA_CONFIG.currentProject,
                    path: path
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.devikaEditor.loadFile(result.file);
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Open file error:', error);
            window.notifications.show('Failed to open file', 'error');
        }
    }
};

window.switchToTab = function(path) {
    // Implementation for switching tabs
    window.handleFileClick(path, 'file');
};

window.closeTab = async function(path) {
    try {
        const response = await fetch('/editor/api/tab/close', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ path })
        });
        
        if (response.ok) {
            window.location.reload();
        }
    } catch (error) {
        console.error('Close tab error:', error);
    }
};