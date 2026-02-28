// Global utility functions and setup

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        const isCtrlOrCmd = event.ctrlKey || event.metaKey;
        
        if (isCtrlOrCmd) {
            switch (event.key) {
                case 'p':
                    if (event.shiftKey) {
                        event.preventDefault();
                        window.commandPalette.show();
                    }
                    break;
                    
                case 's':
                    event.preventDefault();
                    if (event.shiftKey) {
                        window.devikaEditor.saveAllFiles();
                    } else {
                        window.devikaEditor.saveFile();
                    }
                    break;
                    
                case 'n':
                    event.preventDefault();
                    window.devikaEditor.newFile();
                    break;
                    
                case 'w':
                    event.preventDefault();
                    window.devikaEditor.closeCurrentTab();
                    break;
            }
        }
        
        // Escape key
        if (event.key === 'Escape') {
            if (window.commandPalette.isVisible) {
                window.commandPalette.hide();
            }
        }
    });
}

function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', async () => {
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
        });
    }
}

function setupProjectSelector() {
    const projectSelector = document.getElementById('project-selector');
    if (projectSelector) {
        projectSelector.addEventListener('change', (e) => {
            const selectedProject = e.target.value;
            if (selectedProject) {
                window.location.href = `/editor?project=${encodeURIComponent(selectedProject)}`;
            }
        });
    }
}

// Tab drag and drop functionality
window.handleTabDragStart = function(event, path) {
    event.dataTransfer.setData('text/plain', path);
    event.dataTransfer.effectAllowed = 'move';
};

window.handleTabDragOver = function(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
};

window.handleTabDrop = function(event, targetPath) {
    event.preventDefault();
    const draggedPath = event.dataTransfer.getData('text/plain');
    
    if (draggedPath !== targetPath) {
        // Implement tab reordering logic here
        console.log('Reorder tabs:', draggedPath, 'to', targetPath);
    }
};

// Tab context menu
window.showTabContextMenu = function(event, path) {
    event.preventDefault();
    event.stopPropagation();
    
    const contextMenu = document.getElementById('context-menu');
    
    const menuItems = [
        { action: 'close', label: 'Close', icon: 'fas fa-times' },
        { action: 'closeOthers', label: 'Close Others', icon: 'fas fa-times-circle' },
        { action: 'closeAll', label: 'Close All', icon: 'fas fa-ban' },
        { action: 'copyPath', label: 'Copy Path', icon: 'fas fa-copy' }
    ];
    
    contextMenu.innerHTML = menuItems.map(item => 
        `<button class="context-menu-item flex items-center px-3 py-2 text-sm hover:bg-secondary w-full text-left" 
                 onclick="handleTabContextAction('${item.action}', '${path}')">
            <i class="${item.icon} mr-2"></i>
            ${item.label}
        </button>`
    ).join('');
    
    contextMenu.style.left = `${event.clientX}px`;
    contextMenu.style.top = `${event.clientY}px`;
    contextMenu.classList.remove('hidden');
};

window.handleTabContextAction = async function(action, path) {
    const contextMenu = document.getElementById('context-menu');
    contextMenu.classList.add('hidden');
    
    switch (action) {
        case 'close':
            await window.closeTab(path);
            break;
            
        case 'closeOthers':
            // Close all tabs except the current one
            const allTabs = document.querySelectorAll('.tab');
            for (const tab of allTabs) {
                if (tab.dataset.path !== path) {
                    await window.closeTab(tab.dataset.path);
                }
            }
            break;
            
        case 'closeAll':
            // Close all tabs
            const tabs = document.querySelectorAll('.tab');
            for (const tab of tabs) {
                await window.closeTab(tab.dataset.path);
            }
            break;
            
        case 'copyPath':
            navigator.clipboard.writeText(path);
            window.notifications.show('Path copied to clipboard', 'info');
            break;
    }
};

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const units = ['B', 'KB', 'MB', 'GB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + units[i];
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}