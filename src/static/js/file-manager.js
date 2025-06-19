class FileManager {
    constructor() {
        this.contextMenu = document.getElementById('context-menu');
        this.currentContextTarget = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Hide context menu on click outside
        document.addEventListener('click', (e) => {
            if (!this.contextMenu.contains(e.target)) {
                this.hideContextMenu();
            }
        });
        
        // File search
        const searchInput = document.getElementById('file-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterFiles(e.target.value);
            });
        }
        
        // New file button
        const newFileBtn = document.getElementById('new-file-btn');
        if (newFileBtn) {
            newFileBtn.addEventListener('click', () => {
                this.createNewFile();
            });
        }
        
        // New folder button
        const newFolderBtn = document.getElementById('new-folder-btn');
        if (newFolderBtn) {
            newFolderBtn.addEventListener('click', () => {
                this.createNewFolder();
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                window.location.reload();
            });
        }
    }
    
    filterFiles(query) {
        const fileItems = document.querySelectorAll('.file-tree-item');
        const searchQuery = query.toLowerCase();
        
        fileItems.forEach(item => {
            const fileName = item.querySelector('.file-item span').textContent.toLowerCase();
            const shouldShow = fileName.includes(searchQuery) || searchQuery === '';
            
            item.style.display = shouldShow ? 'block' : 'none';
        });
    }
    
    async createNewFile() {
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
                window.location.reload();
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Create file error:', error);
            window.notifications.show('Failed to create file', 'error');
        }
    }
    
    async createNewFolder() {
        const folderName = prompt('Enter folder name:');
        if (!folderName) return;
        
        try {
            const response = await fetch('/editor/api/folder/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project: window.DEVIKA_CONFIG.currentProject,
                    path: folderName
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.notifications.show(result.message, 'success');
                window.location.reload();
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Create folder error:', error);
            window.notifications.show('Failed to create folder', 'error');
        }
    }
    
    showContextMenu(event, path, type) {
        event.preventDefault();
        event.stopPropagation();
        
        this.currentContextTarget = { path, type };
        
        // Build context menu content
        const menuItems = this.getContextMenuItems(type);
        this.contextMenu.innerHTML = menuItems.map(item => 
            `<button class="context-menu-item flex items-center px-3 py-2 text-sm hover:bg-secondary w-full text-left" 
                     onclick="window.fileManager.handleContextAction('${item.action}')">
                <i class="${item.icon} mr-2"></i>
                ${item.label}
            </button>`
        ).join('');
        
        // Position and show menu
        this.contextMenu.style.left = `${event.clientX}px`;
        this.contextMenu.style.top = `${event.clientY}px`;
        this.contextMenu.classList.remove('hidden');
    }
    
    hideContextMenu() {
        this.contextMenu.classList.add('hidden');
        this.currentContextTarget = null;
    }
    
    getContextMenuItems(type) {
        const commonItems = [
            { action: 'copy', label: 'Copy', icon: 'fas fa-copy' },
            { action: 'cut', label: 'Cut', icon: 'fas fa-cut' },
            { action: 'rename', label: 'Rename', icon: 'fas fa-edit' },
            { action: 'delete', label: 'Delete', icon: 'fas fa-trash text-error' }
        ];
        
        if (type === 'file') {
            return [
                { action: 'open', label: 'Open', icon: 'fas fa-external-link-alt' },
                { action: 'duplicate', label: 'Duplicate', icon: 'fas fa-clone' },
                ...commonItems
            ];
        } else {
            return [
                { action: 'newFile', label: 'New File', icon: 'fas fa-file-plus' },
                { action: 'newFolder', label: 'New Folder', icon: 'fas fa-folder-plus' },
                ...commonItems
            ];
        }
    }
    
    async handleContextAction(action) {
        if (!this.currentContextTarget) return;
        
        const { path, type } = this.currentContextTarget;
        
        switch (action) {
            case 'open':
                window.handleFileClick(path, type);
                break;
                
            case 'newFile':
                await this.createNewFile();
                break;
                
            case 'newFolder':
                await this.createNewFolder();
                break;
                
            case 'copy':
                await this.copyItem(path);
                break;
                
            case 'cut':
                await this.cutItem(path);
                break;
                
            case 'rename':
                await this.renameItem(path);
                break;
                
            case 'duplicate':
                await this.duplicateItem(path);
                break;
                
            case 'delete':
                await this.deleteItem(path, type);
                break;
        }
        
        this.hideContextMenu();
    }
    
    async copyItem(path) {
        // Store in session storage for paste operation
        sessionStorage.setItem('clipboard', JSON.stringify({ path, action: 'copy' }));
        window.notifications.show('Copied to clipboard', 'info');
    }
    
    async cutItem(path) {
        sessionStorage.setItem('clipboard', JSON.stringify({ path, action: 'cut' }));
        window.notifications.show('Cut to clipboard', 'info');
    }
    
    async renameItem(path) {
        const newName = prompt('Enter new name:', path.split('/').pop());
        if (!newName) return;
        
        try {
            const response = await fetch('/editor/api/file/rename', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project: window.DEVIKA_CONFIG.currentProject,
                    oldPath: path,
                    newName: newName
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.notifications.show(result.message, 'success');
                window.location.reload();
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Rename error:', error);
            window.notifications.show('Failed to rename', 'error');
        }
    }
    
    async duplicateItem(path) {
        const newName = prompt('Enter name for duplicate:', `${path}_copy`);
        if (!newName) return;
        
        try {
            const response = await fetch('/editor/api/file/duplicate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    project: window.DEVIKA_CONFIG.currentProject,
                    sourcePath: path,
                    newName: newName
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.notifications.show(result.message, 'success');
                window.location.reload();
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Duplicate error:', error);
            window.notifications.show('Failed to duplicate', 'error');
        }
    }
    
    async deleteItem(path, type) {
        const itemType = type === 'folder' ? 'folder' : 'file';
        if (!confirm(`Are you sure you want to delete this ${itemType}?`)) return;
        
        try {
            const response = await fetch(`/editor/api/${itemType}/delete`, {
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
                window.notifications.show(result.message, 'success');
                window.location.reload();
            } else {
                window.notifications.show(result.error, 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
            window.notifications.show('Failed to delete', 'error');
        }
    }
}

// Global function for template usage
window.showContextMenu = function(event, path, type) {
    window.fileManager.showContextMenu(event, path, type);
};