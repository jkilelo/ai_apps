/**
 * Real-time Console Streaming App - ES6 JavaScript
 * Handles WebSocket connections and real-time UI updates
 */

class ConsoleStreamer {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.outputContainer = null;
        this.connectionStatus = null;
        this.executeButton = null;
        this.clearButton = null;
        this.codeInput = null;
        this.examples = [];
        this.metrics = {
            linesReceived: 0,
            executionsRun: 0,
            startTime: Date.now()
        };

        this.init();
    }

    init() {
        this.setupDOM();
        this.setupWebSocket();
        this.setupEventListeners();
        this.loadExamples();
        this.startMetricsUpdate();
    }

    setupDOM() {
        this.outputContainer = document.getElementById('console-output');
        this.connectionStatus = document.querySelector('.status-indicator');
        this.executeButton = document.getElementById('execute-btn');
        this.clearButton = document.getElementById('clear-btn');
        this.codeInput = document.getElementById('code-input');
        this.statusDot = document.querySelector('.status-dot');

        // Add welcome message
        this.addOutput('🚀 Real-time Console Streamer initialized', 'execution-start');
        this.addOutput('Enter Python code and click Execute to see real-time output', 'output');
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addOutput('✅ WebSocket connected successfully', 'execution-complete');
                this.showToast('Connected to server', 'success');
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };

            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.addOutput('❌ WebSocket connection closed', 'error');
                this.showToast('Connection lost. Attempting to reconnect...', 'error');
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addOutput('❌ WebSocket error occurred', 'error');
                this.showToast('Connection error', 'error');
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.addOutput('❌ Failed to establish WebSocket connection', 'error');
        }
    }

    setupEventListeners() {
        // Execute button
        this.executeButton?.addEventListener('click', () => {
            this.executeCode();
        });

        // Clear button
        this.clearButton?.addEventListener('click', () => {
            this.clearOutput();
        });

        // Keyboard shortcuts
        this.codeInput?.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.executeCode();
            }
        });

        // Example items
        document.addEventListener('click', (e) => {
            if (e.target.closest('.example-item')) {
                const exampleIndex = e.target.closest('.example-item').dataset.index;
                this.loadExample(exampleIndex);
            }
        });

        // Auto-scroll toggle
        const autoScrollCheckbox = document.getElementById('auto-scroll');
        if (autoScrollCheckbox) {
            autoScrollCheckbox.addEventListener('change', (e) => {
                this.autoScroll = e.target.checked;
            });
        }
    }

    handleMessage(message) {
        const { type, content, timestamp, code, return_code } = message;

        switch (type) {
            case 'execution_start':
                this.addOutput(`🔄 Executing code...`, 'execution-start');
                this.addOutput(`📝 Code: ${code}`, 'output');
                this.executeButton.disabled = true;
                this.executeButton.innerHTML = '<span class="loading">Executing</span>';
                this.metrics.executionsRun++;
                break;

            case 'output':
                this.addOutput(content, 'output');
                this.metrics.linesReceived++;
                break;

            case 'execution_complete':
                const status = return_code === 0 ? '✅' : '❌';
                const statusText = return_code === 0 ? 'Success' : 'Error';
                this.addOutput(`${status} Execution completed with code: ${return_code} (${statusText})`, 'execution-complete');
                this.executeButton.disabled = false;
                this.executeButton.textContent = 'Execute Code';
                break;

            case 'error':
                this.addOutput(`❌ Error: ${content}`, 'error');
                this.executeButton.disabled = false;
                this.executeButton.textContent = 'Execute Code';
                break;

            case 'pong':
                // Handle ping/pong for connection health
                break;
        }

        this.scrollToBottom();
    }

    addOutput(content, type = 'output') {
        const line = document.createElement('div');
        line.className = `output-line ${type}`;

        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();

        const contentSpan = document.createElement('span');
        contentSpan.textContent = content;

        line.appendChild(timestamp);
        line.appendChild(contentSpan);

        this.outputContainer.appendChild(line);

        // Limit output lines to prevent memory issues
        if (this.outputContainer.children.length > 1000) {
            this.outputContainer.removeChild(this.outputContainer.firstChild);
        }
    }

    executeCode() {
        if (!this.isConnected) {
            this.showToast('Not connected to server', 'error');
            return;
        }

        const code = this.codeInput.value.trim();
        if (!code) {
            this.showToast('Please enter some Python code', 'error');
            return;
        }

        this.ws.send(JSON.stringify({
            type: 'execute',
            code: code
        }));
    }

    clearOutput() {
        this.outputContainer.innerHTML = '';
        this.addOutput('🧹 Console cleared', 'execution-start');
        this.metrics.linesReceived = 0;
        this.showToast('Console cleared', 'success');
    }

    scrollToBottom() {
        if (this.autoScroll !== false) {
            this.outputContainer.scrollTop = this.outputContainer.scrollHeight;
        }
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.statusDot.classList.remove('disconnected');
            this.connectionStatus.querySelector('span').textContent = 'Connected';
        } else {
            this.statusDot.classList.add('disconnected');
            this.connectionStatus.querySelector('span').textContent = 'Disconnected';
        }
    }

    attemptReconnect() {
        setTimeout(() => {
            if (!this.isConnected) {
                this.addOutput('🔄 Attempting to reconnect...', 'execution-start');
                this.setupWebSocket();
            }
        }, 3000);
    }

    async loadExamples() {
        try {
            const response = await fetch('/examples');
            this.examples = await response.json();
            this.renderExamples();
        } catch (error) {
            console.error('Failed to load examples:', error);
            this.addOutput('⚠️ Failed to load examples', 'error');
        }
    }

    renderExamples() {
        const examplesContainer = document.getElementById('examples-list');
        if (!examplesContainer) return;

        examplesContainer.innerHTML = '';

        this.examples.forEach((example, index) => {
            const item = document.createElement('div');
            item.className = 'example-item';
            item.dataset.index = index;

            item.innerHTML = `
                <div class="example-name">${example.name}</div>
                <div class="example-description">Click to load this example</div>
            `;

            examplesContainer.appendChild(item);
        });
    }

    loadExample(index) {
        const example = this.examples[index];
        if (example) {
            this.codeInput.value = example.code;
            this.showToast(`Loaded example: ${example.name}`, 'success');
            this.codeInput.focus();
        }
    }

    showToast(message, type = 'success') {
        // Remove existing toasts
        document.querySelectorAll('.toast').forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span>${type === 'success' ? '✅' : '❌'}</span>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    startMetricsUpdate() {
        setInterval(() => {
            this.updateMetrics();
        }, 1000);
    }

    updateMetrics() {
        const uptime = Math.floor((Date.now() - this.metrics.startTime) / 1000);
        const uptimeFormatted = this.formatUptime(uptime);

        const metricsContainer = document.getElementById('metrics');
        if (metricsContainer) {
            metricsContainer.innerHTML = `
                <div class="metric">
                    <div class="metric-value">${this.metrics.executionsRun}</div>
                    <div class="metric-label">Executions</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${this.metrics.linesReceived}</div>
                    <div class="metric-label">Lines Output</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${uptimeFormatted}</div>
                    <div class="metric-label">Uptime</div>
                </div>
            `;
        }
    }

    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }

    // Public API methods
    sendPing() {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }

    getMetrics() {
        return { ...this.metrics };
    }
}

// Enhanced features for syntax highlighting (simple version)
class SyntaxHighlighter {
    static highlight(code) {
        return code
            .replace(/\b(def|class|if|else|elif|for|while|import|from|return|try|except|finally|with|as)\b/g,
                '<span class="syntax-keyword">$1</span>')
            .replace(/(["'])((?:\\.|(?!\1)[^\\])*?)\1/g,
                '<span class="syntax-string">$1$2$1</span>')
            .replace(/\b(\d+\.?\d*)\b/g,
                '<span class="syntax-number">$1</span>')
            .replace(/(#.*$)/gm,
                '<span class="syntax-comment">$1</span>');
    }
}

// Theme manager
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('console-theme') || 'dark';
        this.applyTheme();
    }

    applyTheme() {
        document.body.setAttribute('data-theme', this.theme);
    }

    toggle() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('console-theme', this.theme);
        this.applyTheme();
    }
}

// Keyboard shortcuts manager
class KeyboardShortcuts {
    constructor(streamer) {
        this.streamer = streamer;
        this.setupShortcuts();
    }

    setupShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.streamer.executeCode();
                        break;
                    case 'k':
                        e.preventDefault();
                        this.streamer.clearOutput();
                        break;
                    case 'r':
                        e.preventDefault();
                        location.reload();
                        break;
                }
            }
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const streamer = new ConsoleStreamer();
    const themeManager = new ThemeManager();
    const shortcuts = new KeyboardShortcuts(streamer);

    // Make streamer globally available for debugging
    window.consoleStreamer = streamer;
    window.themeManager = themeManager;

    // Add theme toggle button functionality
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            themeManager.toggle();
        });
    }

    // Start periodic ping to keep connection alive
    setInterval(() => {
        streamer.sendPing();
    }, 30000); // Every 30 seconds
});
