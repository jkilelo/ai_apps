// Router Module - Pure JS implementation without framework

export class Router {
    constructor() {
        this.routes = new Map();
        this.currentPage = null;
        this.beforeRoute = null;
        this.afterRoute = null;
    }
    
    init() {
        // Get initial page from URL hash
        const initialPage = window.location.hash.slice(1) || 'home';
        this.showPage(initialPage);
    }
    
    // Register route handler
    on(path, handler) {
        this.routes.set(path, handler);
        return this;
    }
    
    // Set before route hook
    before(handler) {
        this.beforeRoute = handler;
        return this;
    }
    
    // Set after route hook
    after(handler) {
        this.afterRoute = handler;
        return this;
    }
    
    // Navigate to a page
    async navigate(page) {
        // Run before route hook
        if (this.beforeRoute) {
            const proceed = await this.beforeRoute(this.currentPage, page);
            if (!proceed) return;
        }
        
        // Update URL
        window.location.hash = page;
        
        // Show page
        await this.showPage(page);
        
        // Run after route hook
        if (this.afterRoute) {
            await this.afterRoute(page);
        }
    }
    
    // Show specific page
    async showPage(page) {
        // Hide all pages
        document.querySelectorAll('.page-content').forEach(p => {
            p.hidden = true;
            p.classList.remove('active');
        });
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === page) {
                link.classList.add('active');
            }
        });
        
        // Close mobile menu if open
        const menuToggle = document.querySelector('.menu-toggle');
        const mainNav = document.querySelector('.main-nav');
        if (menuToggle && mainNav && mainNav.classList.contains('active')) {
            menuToggle.setAttribute('aria-expanded', 'false');
            mainNav.classList.remove('active');
        }
        
        // Show target page
        const targetPage = document.getElementById(`${page}-page`);
        if (targetPage) {
            targetPage.hidden = false;
            targetPage.classList.add('active');
            
            // Run route handler if exists
            if (this.routes.has(page)) {
                await this.routes.get(page)();
            }
            
            // Update page title
            const pageTitle = this.getPageTitle(page);
            document.title = `${pageTitle} - AI Apps v2`;
            
            // Announce page change for screen readers
            this.announcePageChange(pageTitle);
            
            // Scroll to top
            window.scrollTo(0, 0);
            
            this.currentPage = page;
        } else {
            // 404 - Page not found
            this.show404();
        }
    }
    
    // Get page title
    getPageTitle(page) {
        const titles = {
            'home': 'Home',
            'llm': 'LLM Query',
            'automation': 'Web Automation',
            'profiling': 'Data Profiling'
        };
        return titles[page] || 'Page';
    }
    
    // Announce page change for accessibility
    announcePageChange(title) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'visually-hidden';
        announcement.textContent = `Navigated to ${title}`;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    // Show 404 page
    show404() {
        const mainContent = document.querySelector('.content-wrapper');
        mainContent.innerHTML = `
            <div class="error-page">
                <h1 class="error-title">404</h1>
                <p class="error-message">Page not found</p>
                <button class="button primary" onclick="window.app.router.navigate('home')">
                    Go to Home
                </button>
            </div>
        `;
    }
    
    // Get current route
    getCurrentRoute() {
        return this.currentPage;
    }
    
    // Check if route exists
    hasRoute(path) {
        return document.getElementById(`${path}-page`) !== null;
    }
}

// Route Parameter Parser
export class RouteParams {
    static parse(route) {
        const params = {};
        const queryString = route.split('?')[1];
        
        if (queryString) {
            const pairs = queryString.split('&');
            pairs.forEach(pair => {
                const [key, value] = pair.split('=');
                params[decodeURIComponent(key)] = decodeURIComponent(value || '');
            });
        }
        
        return params;
    }
    
    static stringify(params) {
        return Object.keys(params)
            .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
            .join('&');
    }
}