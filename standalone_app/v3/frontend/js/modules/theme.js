// Theme Manager Module using localStorage and CSS custom properties

export class ThemeManager {
    constructor() {
        this.storageKey = 'ai-apps-theme';
        this.defaultTheme = 'light';
        this.currentTheme = null;
    }
    
    init() {
        // Get saved theme or detect system preference
        const savedTheme = localStorage.getItem(this.storageKey);
        const systemTheme = this.getSystemTheme();
        
        this.currentTheme = savedTheme || systemTheme || this.defaultTheme;
        this.apply(this.currentTheme);
        
        // Listen for system theme changes
        this.watchSystemTheme();
    }
    
    // Get system theme preference
    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }
    
    // Watch for system theme changes
    watchSystemTheme() {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            darkModeQuery.addEventListener('change', (e) => {
                // Only auto-switch if user hasn't set a preference
                if (!localStorage.getItem(this.storageKey)) {
                    this.apply(e.matches ? 'dark' : 'light');
                }
            });
        }
    }
    
    // Apply theme
    apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        
        // Update meta theme-color
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            const color = theme === 'dark' ? '#1a1a2e' : '#ffffff';
            metaThemeColor.setAttribute('content', color);
        }
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themechange', { 
            detail: { theme } 
        }));
    }
    
    // Toggle between themes
    toggle() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.set(newTheme);
    }
    
    // Set specific theme
    set(theme) {
        this.apply(theme);
        localStorage.setItem(this.storageKey, theme);
    }
    
    // Get current theme
    get() {
        return this.currentTheme;
    }
    
    // Check if dark mode
    isDark() {
        return this.currentTheme === 'dark';
    }
    
    // Clear saved preference
    clear() {
        localStorage.removeItem(this.storageKey);
        const systemTheme = this.getSystemTheme();
        this.apply(systemTheme);
    }
}

// Advanced theme features
export class ThemeCustomizer {
    constructor() {
        this.customProperties = new Map();
    }
    
    // Set custom CSS property
    setProperty(property, value) {
        document.documentElement.style.setProperty(property, value);
        this.customProperties.set(property, value);
    }
    
    // Get custom CSS property
    getProperty(property) {
        return getComputedStyle(document.documentElement).getPropertyValue(property);
    }
    
    // Set primary color with auto-generated shades
    setPrimaryColor(color) {
        const hsl = this.hexToHSL(color);
        
        this.setProperty('--primary-hue', hsl.h);
        this.setProperty('--primary-saturation', `${hsl.s}%`);
        this.setProperty('--primary-lightness', `${hsl.l}%`);
    }
    
    // Convert hex to HSL
    hexToHSL(hex) {
        // Remove #
        hex = hex.replace('#', '');
        
        // Convert to RGB
        const r = parseInt(hex.substr(0, 2), 16) / 255;
        const g = parseInt(hex.substr(2, 2), 16) / 255;
        const b = parseInt(hex.substr(4, 2), 16) / 255;
        
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const diff = max - min;
        
        let h = 0;
        let s = 0;
        let l = (max + min) / 2;
        
        if (diff !== 0) {
            s = l > 0.5 ? diff / (2 - max - min) : diff / (max + min);
            
            switch (max) {
                case r:
                    h = ((g - b) / diff + (g < b ? 6 : 0)) / 6;
                    break;
                case g:
                    h = ((b - r) / diff + 2) / 6;
                    break;
                case b:
                    h = ((r - g) / diff + 4) / 6;
                    break;
            }
        }
        
        return {
            h: Math.round(h * 360),
            s: Math.round(s * 100),
            l: Math.round(l * 100)
        };
    }
    
    // Save custom theme
    saveCustomTheme(name) {
        const theme = {
            name,
            properties: Object.fromEntries(this.customProperties)
        };
        
        const savedThemes = JSON.parse(localStorage.getItem('custom-themes') || '[]');
        savedThemes.push(theme);
        localStorage.setItem('custom-themes', JSON.stringify(savedThemes));
    }
    
    // Load custom theme
    loadCustomTheme(name) {
        const savedThemes = JSON.parse(localStorage.getItem('custom-themes') || '[]');
        const theme = savedThemes.find(t => t.name === name);
        
        if (theme) {
            Object.entries(theme.properties).forEach(([property, value]) => {
                this.setProperty(property, value);
            });
        }
    }
    
    // Reset to defaults
    reset() {
        this.customProperties.forEach((_, property) => {
            document.documentElement.style.removeProperty(property);
        });
        this.customProperties.clear();
    }
}