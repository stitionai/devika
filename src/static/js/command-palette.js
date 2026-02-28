class CommandPalette {
    constructor() {
        this.modal = document.getElementById('command-palette');
        this.searchInput = document.getElementById('command-search');
        this.commandList = document.getElementById('command-list');
        this.commandCount = document.getElementById('command-count');
        
        this.commands = [];
        this.filteredCommands = [];
        this.selectedIndex = 0;
        this.isVisible = false;
        
        this.init();
    }
    
    init() {
        this.loadCommands();
        this.setupEventListeners();
    }
    
    loadCommands() {
        // Get commands from template data or define them here
        this.commands = [
            {
                id: 'file.new',
                title: 'New File',
                description: 'Create a new file',
                icon: 'fas fa-file-plus',
                shortcut: 'Ctrl+N',
                action: () => window.devikaEditor.newFile()
            },
            {
                id: 'file.save',
                title: 'Save File',
                description: 'Save the current file',
                icon: 'fas fa-save',
                shortcut: 'Ctrl+S',
                action: () => window.devikaEditor.saveFile()
            },
            {
                id: 'file.saveAll',
                title: 'Save All Files',
                description: 'Save all modified files',
                icon: 'fas fa-save',
                shortcut: 'Ctrl+Shift+S',
                action: () => window.devikaEditor.saveAllFiles()
            },
            {
                id: 'edit.find',
                title: 'Find',
                description: 'Find text in current file',
                icon: 'fas fa-search',
                shortcut: 'Ctrl+F',
                action: () => window.devikaEditor.editor.getAction('actions.find').run()
            },
            {
                id: 'edit.replace',
                title: 'Find and Replace',
                description: 'Find and replace text',
                icon: 'fas fa-search-plus',
                shortcut: 'Ctrl+H',
                action: () => window.devikaEditor.editor.getAction('editor.action.startFindReplaceAction').run()
            },
            {
                id: 'edit.format',
                title: 'Format Document',
                description: 'Format the current document',
                icon: 'fas fa-code',
                shortcut: 'Shift+Alt+F',
                action: () => window.devikaEditor.formatDocument()
            },
            {
                id: 'view.toggleMinimap',
                title: 'Toggle Minimap',
                description: 'Show or hide the minimap',
                icon: 'fas fa-map',
                action: () => this.toggleMinimap()
            },
            {
                id: 'view.toggleWordWrap',
                title: 'Toggle Word Wrap',
                description: 'Enable or disable word wrapping',
                icon: 'fas fa-text-width',
                action: () => this.toggleWordWrap()
            },
            {
                id: 'view.zoomIn',
                title: 'Zoom In',
                description: 'Increase font size',
                icon: 'fas fa-plus',
                action: () => this.zoomIn()
            },
            {
                id: 'view.zoomOut',
                title: 'Zoom Out',
                description: 'Decrease font size',
                icon: 'fas fa-minus',
                action: () => this.zoomOut()
            },
            {
                id: 'theme.toggle',
                title: 'Toggle Theme',
                description: 'Switch between light and dark theme',
                icon: 'fas fa-palette',
                action: () => this.toggleTheme()
            }
        ];
        
        this.filteredCommands = [...this.commands];
    }
    
    setupEventListeners() {
        // Search input
        this.searchInput.addEventListener('input', (e) => {
            this.filterCommands(e.target.value);
        });
        
        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
        
        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });
        
        // Command item clicks
        this.commandList.addEventListener('click', (e) => {
            const commandItem = e.target.closest('.command-item');
            if (commandItem) {
                const commandId = commandItem.dataset.command;
                this.executeCommand(commandId);
            }
        });
    }
    
    show() {
        this.isVisible = true;
        this.modal.classList.remove('hidden');
        this.searchInput.focus();
        this.searchInput.value = '';
        this.selectedIndex = 0;
        this.filterCommands('');
    }
    
    hide() {
        this.isVisible = false;
        this.modal.classList.add('hidden');
        this.searchInput.value = '';
    }
    
    filterCommands(query) {
        const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
        
        if (searchTerms.length === 0) {
            this.filteredCommands = [...this.commands];
        } else {
            this.filteredCommands = this.commands.filter(command => {
                const searchableText = [
                    command.title,
                    command.description,
                    command.id
                ].join(' ').toLowerCase();
                
                return searchTerms.every(term => searchableText.includes(term));
            });
        }
        
        this.selectedIndex = 0;
        this.renderCommands();
        this.updateCommandCount();
    }
    
    renderCommands() {
        this.commandList.innerHTML = this.filteredCommands.map((command, index) => `
            <div class="command-item flex items-center p-4 hover:bg-secondary cursor-pointer ${index === this.selectedIndex ? 'bg-primary text-background' : ''}"
                 data-command="${command.id}">
                <div class="flex items-center justify-center w-8 h-8 bg-primary rounded mr-3">
                    <i class="${command.icon} text-background text-sm"></i>
                </div>
                <div class="flex-1">
                    <div class="font-medium">${command.title}</div>
                    <div class="text-sm text-tertiary">${command.description}</div>
                </div>
                ${command.shortcut ? `<div class="text-xs text-tertiary bg-secondary px-2 py-1 rounded">${command.shortcut}</div>` : ''}
            </div>
        `).join('');
    }
    
    updateCommandCount() {
        this.commandCount.textContent = `${this.filteredCommands.length} command${this.filteredCommands.length !== 1 ? 's' : ''}`;
    }
    
    handleKeydown(event) {
        switch (event.key) {
            case 'Escape':
                event.preventDefault();
                this.hide();
                break;
                
            case 'ArrowDown':
                event.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredCommands.length - 1);
                this.renderCommands();
                this.scrollToSelected();
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                this.renderCommands();
                this.scrollToSelected();
                break;
                
            case 'Enter':
                event.preventDefault();
                if (this.filteredCommands[this.selectedIndex]) {
                    this.executeCommand(this.filteredCommands[this.selectedIndex].id);
                }
                break;
        }
    }
    
    scrollToSelected() {
        const selectedElement = this.commandList.children[this.selectedIndex];
        if (selectedElement) {
            selectedElement.scrollIntoView({ block: 'nearest' });
        }
    }
    
    executeCommand(commandId) {
        const command = this.commands.find(cmd => cmd.id === commandId);
        if (command && command.action) {
            command.action();
            this.hide();
        }
    }
    
    // Command implementations
    toggleMinimap() {
        const currentSettings = window.DEVIKA_CONFIG.settings;
        const newSettings = { ...currentSettings, minimap: !currentSettings.minimap };
        this.updateSettings(newSettings);
    }
    
    toggleWordWrap() {
        const currentSettings = window.DEVIKA_CONFIG.settings;
        const newSettings = { ...currentSettings, wordWrap: !currentSettings.wordWrap };
        this.updateSettings(newSettings);
    }
    
    zoomIn() {
        const currentSettings = window.DEVIKA_CONFIG.settings;
        const newSettings = { ...currentSettings, fontSize: Math.min(24, currentSettings.fontSize + 1) };
        this.updateSettings(newSettings);
    }
    
    zoomOut() {
        const currentSettings = window.DEVIKA_CONFIG.settings;
        const newSettings = { ...currentSettings, fontSize: Math.max(10, currentSettings.fontSize - 1) };
        this.updateSettings(newSettings);
    }
    
    async toggleTheme() {
        try {
            const response = await fetch('/editor/api/theme/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.location.reload();
            }
        } catch (error) {
            console.error('Theme toggle error:', error);
        }
    }
    
    async updateSettings(newSettings) {
        try {
            const response = await fetch('/editor/api/settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newSettings)
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.DEVIKA_CONFIG.settings = result.settings;
                window.devikaEditor.updateSettings(result.settings);
                window.notifications.show('Settings updated', 'success');
            }
        } catch (error) {
            console.error('Settings update error:', error);
            window.notifications.show('Failed to update settings', 'error');
        }
    }
}