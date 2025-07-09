// LLM Query Web Component
import { AIAppsAPI } from '../js/modules/api.js';
import { NotificationManager } from '../js/modules/notifications.js';
import { Utils } from '../js/modules/utils.js';

class LLMQueryComponent extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        
        // Initialize services
        this.api = new AIAppsAPI();
        this.notifications = new NotificationManager();
        
        // State
        this.isLoading = false;
        this.history = [];
    }
    
    connectedCallback() {
        this.render();
        this.setupEventListeners();
        this.loadHistory();
    }
    
    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: 100%;
                    max-width: 800px;
                    margin: 0 auto;
                }
                
                .llm-container {
                    display: grid;
                    gap: var(--space-lg);
                }
                
                .query-form {
                    background: var(--bg-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    box-shadow: var(--shadow-md);
                }
                
                .form-group {
                    margin-bottom: var(--space-md);
                }
                
                .form-label {
                    display: block;
                    font-weight: var(--font-weight-medium);
                    margin-bottom: var(--space-xs);
                    color: var(--text-primary);
                }
                
                .form-textarea {
                    width: 100%;
                    min-height: 120px;
                    padding: var(--space-sm);
                    border: 2px solid var(--border-color);
                    border-radius: var(--radius-md);
                    font-family: inherit;
                    font-size: var(--font-size-base);
                    resize: vertical;
                    transition: border-color var(--transition-fast);
                }
                
                .form-textarea:focus {
                    outline: none;
                    border-color: var(--primary-color);
                }
                
                .char-count {
                    text-align: right;
                    font-size: var(--font-size-sm);
                    color: var(--text-secondary);
                    margin-top: var(--space-xs);
                }
                
                .form-actions {
                    display: flex;
                    gap: var(--space-sm);
                    justify-content: flex-end;
                }
                
                .button {
                    padding: var(--space-sm) var(--space-lg);
                    border: none;
                    border-radius: var(--radius-md);
                    font-weight: var(--font-weight-medium);
                    cursor: pointer;
                    transition: all var(--transition-fast);
                }
                
                .button.primary {
                    background: var(--primary-color);
                    color: white;
                }
                
                .button.primary:hover {
                    background: var(--primary-dark);
                    transform: translateY(-1px);
                    box-shadow: var(--shadow-md);
                }
                
                .button.primary:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .button.secondary {
                    background: var(--bg-secondary);
                    color: var(--text-primary);
                }
                
                .button.secondary:hover {
                    background: var(--bg-tertiary);
                }
                
                .response-section {
                    background: var(--bg-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    box-shadow: var(--shadow-md);
                }
                
                .response-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--space-md);
                }
                
                .response-title {
                    font-size: var(--font-size-lg);
                    font-weight: var(--font-weight-semibold);
                }
                
                .response-content {
                    background: var(--bg-secondary);
                    border-radius: var(--radius-md);
                    padding: var(--space-md);
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    line-height: var(--line-height-relaxed);
                }
                
                .loading {
                    display: flex;
                    align-items: center;
                    gap: var(--space-sm);
                    color: var(--text-secondary);
                }
                
                .loading-spinner {
                    width: 20px;
                    height: 20px;
                    border: 2px solid var(--border-color);
                    border-top-color: var(--primary-color);
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                
                .history-section {
                    background: var(--bg-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    box-shadow: var(--shadow-md);
                }
                
                .history-item {
                    padding: var(--space-sm);
                    border-radius: var(--radius-md);
                    cursor: pointer;
                    transition: background var(--transition-fast);
                }
                
                .history-item:hover {
                    background: var(--bg-secondary);
                }
                
                .history-prompt {
                    font-weight: var(--font-weight-medium);
                    margin-bottom: var(--space-xs);
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }
                
                .history-time {
                    font-size: var(--font-size-sm);
                    color: var(--text-tertiary);
                }
                
                /* Import global styles */
                @import url('/css/variables.css');
            </style>
            
            <div class="llm-container">
                <form class="query-form" id="queryForm">
                    <div class="form-group">
                        <label class="form-label" for="prompt">Enter your prompt</label>
                        <textarea 
                            class="form-textarea" 
                            id="prompt" 
                            name="prompt" 
                            placeholder="Ask me anything..."
                            maxlength="4000"
                            required
                        ></textarea>
                        <div class="char-count">
                            <span id="charCount">0</span> / 4000
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="button secondary" id="clearBtn">
                            Clear
                        </button>
                        <button type="submit" class="button primary" id="submitBtn">
                            <span id="submitText">Send Query</span>
                        </button>
                    </div>
                </form>
                
                <div class="response-section" id="responseSection" style="display: none;">
                    <div class="response-header">
                        <h3 class="response-title">Response</h3>
                        <button class="button secondary" id="copyBtn">Copy</button>
                    </div>
                    <div class="response-content" id="responseContent">
                        <div class="loading" id="loadingIndicator">
                            <div class="loading-spinner"></div>
                            <span>Generating response...</span>
                        </div>
                    </div>
                </div>
                
                <div class="history-section" id="historySection" style="display: none;">
                    <h3 class="response-title">Recent Queries</h3>
                    <div id="historyList"></div>
                </div>
            </div>
        `;
    }
    
    setupEventListeners() {
        const form = this.shadowRoot.getElementById('queryForm');
        const prompt = this.shadowRoot.getElementById('prompt');
        const charCount = this.shadowRoot.getElementById('charCount');
        const clearBtn = this.shadowRoot.getElementById('clearBtn');
        const copyBtn = this.shadowRoot.getElementById('copyBtn');
        
        // Form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // Character count
        prompt.addEventListener('input', (e) => {
            charCount.textContent = e.target.value.length;
        });
        
        // Clear button
        clearBtn.addEventListener('click', () => {
            prompt.value = '';
            charCount.textContent = '0';
            prompt.focus();
        });
        
        // Copy button
        copyBtn.addEventListener('click', () => {
            this.copyResponse();
        });
        
        // Keyboard shortcuts
        prompt.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.handleSubmit();
            }
        });
    }
    
    async handleSubmit() {
        if (this.isLoading) return;
        
        const prompt = this.shadowRoot.getElementById('prompt');
        const submitBtn = this.shadowRoot.getElementById('submitBtn');
        const submitText = this.shadowRoot.getElementById('submitText');
        const responseSection = this.shadowRoot.getElementById('responseSection');
        const responseContent = this.shadowRoot.getElementById('responseContent');
        const loadingIndicator = this.shadowRoot.getElementById('loadingIndicator');
        
        const query = prompt.value.trim();
        if (!query) return;
        
        this.isLoading = true;
        submitBtn.disabled = true;
        submitText.textContent = 'Sending...';
        
        // Show response section with loading
        responseSection.style.display = 'block';
        loadingIndicator.style.display = 'flex';
        responseContent.textContent = '';
        
        try {
            const response = await this.api.queryLLM(query);
            
            // Display response
            loadingIndicator.style.display = 'none';
            responseContent.textContent = response.response || 'No response received';
            
            // Add to history
            this.addToHistory(query, response.response);
            
            // Clear input
            prompt.value = '';
            this.shadowRoot.getElementById('charCount').textContent = '0';
            
        } catch (error) {
            console.error('LLM query error:', error);
            loadingIndicator.style.display = 'none';
            responseContent.innerHTML = `
                <div style="color: var(--error-color);">
                    Error: ${error.message || 'Failed to get response'}
                </div>
            `;
            this.notifications.error('Failed to get response from LLM');
        } finally {
            this.isLoading = false;
            submitBtn.disabled = false;
            submitText.textContent = 'Send Query';
        }
    }
    
    async copyResponse() {
        const responseContent = this.shadowRoot.getElementById('responseContent');
        const text = responseContent.textContent;
        
        const success = await Utils.copyToClipboard(text);
        if (success) {
            this.notifications.success('Response copied to clipboard');
        } else {
            this.notifications.error('Failed to copy response');
        }
    }
    
    addToHistory(prompt, response) {
        const item = {
            id: Utils.generateUUID(),
            prompt,
            response,
            timestamp: Date.now()
        };
        
        this.history.unshift(item);
        if (this.history.length > 10) {
            this.history = this.history.slice(0, 10);
        }
        
        this.saveHistory();
        this.renderHistory();
    }
    
    renderHistory() {
        const historySection = this.shadowRoot.getElementById('historySection');
        const historyList = this.shadowRoot.getElementById('historyList');
        
        if (this.history.length === 0) {
            historySection.style.display = 'none';
            return;
        }
        
        historySection.style.display = 'block';
        
        historyList.innerHTML = this.history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-prompt">${Utils.escapeHtml(item.prompt)}</div>
                <div class="history-time">${Utils.formatRelativeTime(item.timestamp)}</div>
            </div>
        `).join('');
        
        // Add click handlers
        historyList.querySelectorAll('.history-item').forEach(el => {
            el.addEventListener('click', () => {
                const id = el.dataset.id;
                const item = this.history.find(h => h.id === id);
                if (item) {
                    this.loadHistoryItem(item);
                }
            });
        });
    }
    
    loadHistoryItem(item) {
        const prompt = this.shadowRoot.getElementById('prompt');
        const responseSection = this.shadowRoot.getElementById('responseSection');
        const responseContent = this.shadowRoot.getElementById('responseContent');
        const loadingIndicator = this.shadowRoot.getElementById('loadingIndicator');
        
        prompt.value = item.prompt;
        this.shadowRoot.getElementById('charCount').textContent = item.prompt.length;
        
        responseSection.style.display = 'block';
        loadingIndicator.style.display = 'none';
        responseContent.textContent = item.response;
    }
    
    saveHistory() {
        localStorage.setItem('llm-history', JSON.stringify(this.history));
    }
    
    loadHistory() {
        try {
            const saved = localStorage.getItem('llm-history');
            if (saved) {
                this.history = JSON.parse(saved);
                this.renderHistory();
            }
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }
}

// Define custom element
customElements.define('llm-query-component', LLMQueryComponent);