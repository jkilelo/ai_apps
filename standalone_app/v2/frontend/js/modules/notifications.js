// Notification Manager Module - Toast notifications without dependencies

export class NotificationManager {
    constructor() {
        this.container = null;
        this.queue = [];
        this.activeNotifications = new Map();
        this.init();
    }
    
    init() {
        // Get or create container
        this.container = document.querySelector('.toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            this.container.setAttribute('role', 'status');
            this.container.setAttribute('aria-live', 'polite');
            document.body.appendChild(this.container);
        }
    }
    
    // Show notification
    show(message, type = 'info', duration = 5000, options = {}) {
        const id = this.generateId();
        const notification = this.create(id, message, type, options);
        
        // Add to queue if too many active
        if (this.activeNotifications.size >= 3) {
            this.queue.push({ id, message, type, duration, options });
            return id;
        }
        
        // Show notification
        this.container.appendChild(notification);
        this.activeNotifications.set(id, notification);
        
        // Trigger animation
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });
        
        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => this.dismiss(id), duration);
        }
        
        return id;
    }
    
    // Create notification element
    create(id, message, type, options = {}) {
        const notification = document.createElement('div');
        notification.className = `toast ${type} animate-slide-in`;
        notification.id = `notification-${id}`;
        
        // Icon
        const icon = this.getIcon(type);
        
        // Title
        const title = options.title || this.getDefaultTitle(type);
        
        // Build HTML
        notification.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${this.escapeHtml(title)}</div>` : ''}
                <div class="toast-message">${this.escapeHtml(message)}</div>
            </div>
            <button class="toast-close" aria-label="Close notification">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"/>
                </svg>
            </button>
        `;
        
        // Add actions if provided
        if (options.actions && options.actions.length > 0) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'toast-actions';
            
            options.actions.forEach(action => {
                const button = document.createElement('button');
                button.className = 'button small ghost';
                button.textContent = action.label;
                button.addEventListener('click', () => {
                    action.handler();
                    this.dismiss(id);
                });
                actionsDiv.appendChild(button);
            });
            
            notification.querySelector('.toast-content').appendChild(actionsDiv);
        }
        
        // Close button handler
        notification.querySelector('.toast-close').addEventListener('click', () => {
            this.dismiss(id);
        });
        
        return notification;
    }
    
    // Dismiss notification
    dismiss(id) {
        const notification = this.activeNotifications.get(id);
        if (!notification) return;
        
        // Add exit animation
        notification.classList.remove('show');
        notification.classList.add('animate-slide-out');
        
        // Remove after animation
        notification.addEventListener('animationend', () => {
            notification.remove();
            this.activeNotifications.delete(id);
            
            // Process queue
            if (this.queue.length > 0) {
                const next = this.queue.shift();
                this.show(next.message, next.type, next.duration, next.options);
            }
        }, { once: true });
    }
    
    // Dismiss all notifications
    dismissAll() {
        this.activeNotifications.forEach((_, id) => this.dismiss(id));
        this.queue = [];
    }
    
    // Get icon for notification type
    getIcon(type) {
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
            </svg>`,
            warning: `<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
            </svg>`
        };
        
        return icons[type] || icons.info;
    }
    
    // Get default title for type
    getDefaultTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info'
        };
        
        return titles[type] || '';
    }
    
    // Generate unique ID
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Convenience methods
    success(message, options = {}) {
        return this.show(message, 'success', 5000, options);
    }
    
    error(message, options = {}) {
        return this.show(message, 'error', 0, options); // No auto-dismiss for errors
    }
    
    warning(message, options = {}) {
        return this.show(message, 'warning', 7000, options);
    }
    
    info(message, options = {}) {
        return this.show(message, 'info', 5000, options);
    }
}

// Global notification helper
export function notify(message, type = 'info', duration = 5000) {
    if (!window.notificationManager) {
        window.notificationManager = new NotificationManager();
    }
    return window.notificationManager.show(message, type, duration);
}