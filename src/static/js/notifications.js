class NotificationSystem {
    constructor() {
        this.container = document.getElementById('notifications');
        this.notifications = new Map();
        this.nextId = 1;
    }
    
    show(message, type = 'info', title = null, duration = 5000) {
        const id = this.nextId++;
        
        const notification = this.createNotification(id, message, type, title);
        this.container.appendChild(notification);
        this.notifications.set(id, notification);
        
        // Auto-dismiss after duration
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(id);
            }, duration);
        }
        
        return id;
    }
    
    createNotification(id, message, type, title) {
        const notificationClass = {
            'success': 'border-success bg-green-50 dark:bg-green-900/20',
            'error': 'border-error bg-red-50 dark:bg-red-900/20',
            'warning': 'border-warning bg-yellow-50 dark:bg-yellow-900/20',
            'info': 'border-primary bg-blue-50 dark:bg-blue-900/20'
        }[type] || 'border-primary bg-blue-50 dark:bg-blue-900/20';
        
        const notificationIcon = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-error',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-primary'
        }[type] || 'fas fa-info-circle text-primary';
        
        const notification = document.createElement('div');
        notification.className = `notification flex items-center p-4 rounded-lg border-l-4 shadow-lg max-w-sm ${notificationClass}`;
        notification.dataset.id = id;
        
        notification.innerHTML = `
            <i class="${notificationIcon} mr-3"></i>
            <div class="flex-1 min-w-0">
                ${title ? `<p class="text-sm font-medium text-foreground">${title}</p>` : ''}
                <p class="text-sm ${title ? 'text-tertiary' : 'font-medium text-foreground'}">${message}</p>
            </div>
            <button class="ml-3 text-tertiary hover:text-foreground transition-colors" onclick="window.notifications.dismiss(${id})">
                <i class="fas fa-times text-xs"></i>
            </button>
        `;
        
        return notification;
    }
    
    dismiss(id) {
        const notification = this.notifications.get(id);
        if (notification) {
            notification.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.notifications.delete(id);
            }, 300);
        }
    }
    
    clear() {
        this.notifications.forEach((notification, id) => {
            this.dismiss(id);
        });
    }
    
    success(message, title = null, duration = 3000) {
        return this.show(message, 'success', title, duration);
    }
    
    error(message, title = null, duration = 5000) {
        return this.show(message, 'error', title, duration);
    }
    
    warning(message, title = null, duration = 4000) {
        return this.show(message, 'warning', title, duration);
    }
    
    info(message, title = null, duration = 3000) {
        return this.show(message, 'info', title, duration);
    }
}

// Add CSS for slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);