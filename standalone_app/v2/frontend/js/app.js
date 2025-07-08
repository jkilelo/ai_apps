// Main App Module - ES6+ with modern features
import { Router } from './modules/router.js';
import { ThemeManager } from './modules/theme.js';
import { ApiClient } from './modules/api.js';
import { NotificationManager } from './modules/notifications.js';
import { StateManager } from './modules/state.js';
import { Utils } from './modules/utils.js';

// App Class using ES6 Classes
class App {
    constructor() {
        this.router = new Router();
        this.theme = new ThemeManager();
        this.api = new ApiClient('/api');
        this.notifications = new NotificationManager();
        this.state = new StateManager();
        
        // Bind methods
        this.init = this.init.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        this.handleNavigation = this.handleNavigation.bind(this);
    }
    
    async init() {
        try {
            // Initialize theme
            this.theme.init();
            
            // Initialize router
            this.router.init();
            
            // Setup global event listeners
            this.setupEventListeners();
            
            // Check API health
            await this.checkApiHealth();
            
            // Register service worker for PWA
            if ('serviceWorker' in navigator) {
                this.registerServiceWorker();
            }
            
            // Initialize Web Components
            await this.loadWebComponents();
            
            // Show welcome notification
            this.notifications.show('Welcome to AI Apps v2!', 'success', 3000);
            
            console.log('App initialized successfully');
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.notifications.show('Failed to initialize app', 'error');
        }
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', this.handleNavigation);
        });
        
        // Theme toggle
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.theme.toggle());
        }
        
        // Mobile menu
        const menuToggle = document.querySelector('.menu-toggle');
        const mainNav = document.querySelector('.main-nav');
        if (menuToggle && mainNav) {
            menuToggle.addEventListener('click', () => {
                const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
                menuToggle.setAttribute('aria-expanded', !isExpanded);
                mainNav.classList.toggle('active');
            });
        }
        
        // Get Started button
        const getStartedBtn = document.querySelector('[data-action="get-started"]');
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', () => {
                this.router.navigate('llm');
            });
        }
        
        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            const page = window.location.hash.slice(1) || 'home';
            this.router.showPage(page);
        });
        
        // Handle online/offline
        window.addEventListener('online', () => {
            this.notifications.show('Connection restored', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.notifications.show('No internet connection', 'warning');
        });
    }
    
    handleNavigation(event) {
        event.preventDefault();
        const page = event.currentTarget.dataset.page;
        this.router.navigate(page);
    }
    
    async checkApiHealth() {
        try {
            const response = await this.api.get('/health');
            if (response.status === 'healthy') {
                console.log('API is healthy');
            } else {
                throw new Error('API is not healthy');
            }
        } catch (error) {
            console.error('API health check failed:', error);
            this.notifications.show('API connection failed', 'error');
        }
    }
    
    async registerServiceWorker() {
        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('Service Worker registered:', registration);
            
            // Listen for updates
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        this.notifications.show('New version available! Refresh to update.', 'info');
                    }
                });
            });
        } catch (error) {
            console.log('Service Worker registration failed:', error);
        }
    }
    
    async loadWebComponents() {
        // Web Components are already loaded via script tags in HTML
        // Just verify they're registered
        const componentsToCheck = [
            'llm-query-component',
            'web-automation-component',
            'data-profiling-component'
        ];
        
        const allRegistered = componentsToCheck.every(name => 
            customElements.get(name) !== undefined
        );
        
        if (allRegistered) {
            console.log('All Web Components are registered');
        } else {
            console.warn('Some Web Components are not yet registered');
        }
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.app = new App();
        window.app.init();
    });
} else {
    window.app = new App();
    window.app.init();
}

// Export for use in other modules
export { App };