// Data Profiling Web Component
import { AIAppsAPI } from '../js/modules/api.js';
import { NotificationManager } from '../js/modules/notifications.js';
import { Utils } from '../js/modules/utils.js';

class DataProfilingComponent extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        
        // Initialize services
        this.api = new AIAppsAPI();
        this.notifications = new NotificationManager();
        
        // State for 8-step process
        this.currentStep = 1;
        this.profilingData = {
            dataSample: '',
            dataDescription: '',
            profilingSuggestions: null,
            profilingTestcases: null,
            pysparkCode: null,
            profilingResults: null,
            dqSuggestions: null,
            dqTests: null,
            dqPysparkCode: null,
            dqResults: null
        };
    }
    
    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }
    
    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: 100%;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .profiling-container {
                    display: grid;
                    gap: var(--space-xl);
                }
                
                .steps-overview {
                    background: var(--bg-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    box-shadow: var(--shadow-md);
                }
                
                .steps-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: var(--space-sm);
                    margin-top: var(--space-md);
                }
                
                .step-card {
                    background: var(--bg-secondary);
                    border-radius: var(--radius-md);
                    padding: var(--space-md);
                    text-align: center;
                    cursor: pointer;
                    transition: all var(--transition-fast);
                    position: relative;
                    overflow: hidden;
                }
                
                .step-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: var(--border-color);
                    transition: background var(--transition-fast);
                }
                
                .step-card.active {
                    background: var(--primary-color);
                    color: white;
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-md);
                }
                
                .step-card.active::before {
                    background: white;
                }
                
                .step-card.completed {
                    background: var(--success-color);
                    color: white;
                }
                
                .step-card.completed::before {
                    background: white;
                }
                
                .step-number {
                    font-size: var(--font-size-2xl);
                    font-weight: var(--font-weight-bold);
                    margin-bottom: var(--space-xs);
                }
                
                .step-name {
                    font-size: var(--font-size-xs);
                    line-height: 1.2;
                }
                
                .main-content {
                    background: var(--bg-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-xl);
                    box-shadow: var(--shadow-md);
                }
                
                .content-header {
                    margin-bottom: var(--space-lg);
                    padding-bottom: var(--space-lg);
                    border-bottom: 1px solid var(--border-color);
                }
                
                .content-title {
                    font-size: var(--font-size-2xl);
                    font-weight: var(--font-weight-bold);
                    margin-bottom: var(--space-sm);
                }
                
                .content-description {
                    color: var(--text-secondary);
                    line-height: var(--line-height-relaxed);
                }
                
                .form-group {
                    margin-bottom: var(--space-lg);
                }
                
                .form-label {
                    display: block;
                    font-weight: var(--font-weight-medium);
                    margin-bottom: var(--space-sm);
                    color: var(--text-primary);
                }
                
                .form-help {
                    font-size: var(--font-size-sm);
                    color: var(--text-secondary);
                    margin-top: var(--space-xs);
                }
                
                .form-textarea {
                    width: 100%;
                    min-height: 150px;
                    padding: var(--space-sm);
                    border: 2px solid var(--border-color);
                    border-radius: var(--radius-md);
                    font-family: var(--font-mono);
                    font-size: var(--font-size-sm);
                    resize: vertical;
                    transition: border-color var(--transition-fast);
                }
                
                .form-textarea:focus {
                    outline: none;
                    border-color: var(--primary-color);
                }
                
                .form-input {
                    width: 100%;
                    padding: var(--space-sm);
                    border: 2px solid var(--border-color);
                    border-radius: var(--radius-md);
                    font-size: var(--font-size-base);
                    transition: border-color var(--transition-fast);
                }
                
                .form-input:focus {
                    outline: none;
                    border-color: var(--primary-color);
                }
                
                .button {
                    padding: var(--space-sm) var(--space-lg);
                    border: none;
                    border-radius: var(--radius-md);
                    font-weight: var(--font-weight-medium);
                    cursor: pointer;
                    transition: all var(--transition-fast);
                    display: inline-flex;
                    align-items: center;
                    gap: var(--space-xs);
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
                    background: var(--bg-tertiary);
                    color: var(--text-primary);
                }
                
                .button-group {
                    display: flex;
                    gap: var(--space-sm);
                    justify-content: space-between;
                    margin-top: var(--space-xl);
                }
                
                .result-panel {
                    background: var(--bg-secondary);
                    border-radius: var(--radius-md);
                    padding: var(--space-lg);
                    margin-top: var(--space-lg);
                }
                
                .result-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--space-md);
                }
                
                .result-title {
                    font-weight: var(--font-weight-semibold);
                    font-size: var(--font-size-lg);
                }
                
                .code-viewer {
                    background: var(--bg-primary);
                    border-radius: var(--radius-sm);
                    padding: var(--space-md);
                    font-family: var(--font-mono);
                    font-size: var(--font-size-sm);
                    white-space: pre-wrap;
                    word-break: break-all;
                    line-height: 1.6;
                    max-height: 400px;
                    overflow-y: auto;
                }
                
                .loading {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: var(--space-sm);
                    padding: var(--space-xl);
                    color: var(--text-secondary);
                }
                
                .loading-spinner {
                    width: 24px;
                    height: 24px;
                    border: 3px solid var(--border-color);
                    border-top-color: var(--primary-color);
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                
                .status-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: var(--space-xs);
                    padding: var(--space-xs) var(--space-sm);
                    border-radius: var(--radius-full);
                    font-size: var(--font-size-sm);
                    font-weight: var(--font-weight-medium);
                }
                
                .status-badge.success {
                    background: var(--success-color);
                    color: white;
                }
                
                .status-badge.error {
                    background: var(--error-color);
                    color: white;
                }
                
                .status-badge.pending {
                    background: var(--warning-color);
                    color: white;
                }
                
                /* Import global styles */
                @import url('/css/variables.css');
                
                @media (max-width: 768px) {
                    .steps-grid {
                        grid-template-columns: repeat(2, 1fr);
                    }
                    
                    .button-group {
                        flex-direction: column-reverse;
                    }
                }
            </style>
            
            <div class="profiling-container">
                <div class="steps-overview">
                    <h2 style="margin-bottom: var(--space-sm);">Data Profiling Process</h2>
                    <p style="color: var(--text-secondary); margin-bottom: var(--space-md);">
                        Complete 8-step process for comprehensive data quality analysis
                    </p>
                    <div class="steps-grid">
                        ${this.renderStepCards()}
                    </div>
                </div>
                
                <div class="main-content">
                    ${this.renderStepContent()}
                </div>
            </div>
        `;
    }
    
    renderStepCards() {
        const steps = [
            { num: 1, name: 'Profiling Suggestions' },
            { num: 2, name: 'Test Cases' },
            { num: 3, name: 'PySpark Code' },
            { num: 4, name: 'Execute Profiling' },
            { num: 5, name: 'DQ Suggestions' },
            { num: 6, name: 'DQ Tests' },
            { num: 7, name: 'DQ PySpark' },
            { num: 8, name: 'Execute DQ' }
        ];
        
        return steps.map(step => `
            <div class="step-card ${step.num === this.currentStep ? 'active' : ''} ${step.num < this.currentStep ? 'completed' : ''}" 
                 data-step="${step.num}">
                <div class="step-number">${step.num < this.currentStep ? '✓' : step.num}</div>
                <div class="step-name">${step.name}</div>
            </div>
        `).join('');
    }
    
    renderStepContent() {
        const stepContents = {
            1: this.renderStep1(),
            2: this.renderStep2(),
            3: this.renderStep3(),
            4: this.renderStep4(),
            5: this.renderStep5(),
            6: this.renderStep6(),
            7: this.renderStep7(),
            8: this.renderStep8()
        };
        
        return stepContents[this.currentStep] || '';
    }
    
    renderStep1() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 1: Generate Profiling Suggestions</h3>
                <p class="content-description">
                    Provide a sample of your data and description to generate intelligent profiling suggestions
                </p>
            </div>
            
            <form id="step1Form">
                <div class="form-group">
                    <label class="form-label" for="dataSample">Data Sample (CSV, JSON, or SQL)</label>
                    <textarea 
                        class="form-textarea" 
                        id="dataSample" 
                        placeholder="id,name,email,age&#10;1,John Doe,john@example.com,30&#10;2,Jane Smith,jane@example.com,25"
                        required
                    >${this.profilingData.dataSample}</textarea>
                    <p class="form-help">Paste a sample of your data (first 5-10 rows)</p>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="dataDescription">Data Description</label>
                    <input 
                        type="text" 
                        class="form-input" 
                        id="dataDescription" 
                        placeholder="Customer data with personal information and demographics"
                        value="${this.profilingData.dataDescription}"
                        required
                    />
                    <p class="form-help">Brief description of what this data represents</p>
                </div>
                
                <div class="button-group">
                    <div></div>
                    <button type="submit" class="button primary" id="generateSuggestionsBtn">
                        Generate Suggestions
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M3 8h10m0 0l-3-3m3 3l-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
            </form>
        `;
    }
    
    renderStep2() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 2: Generate Profiling Test Cases</h3>
                <p class="content-description">
                    Create comprehensive test cases based on the profiling suggestions
                </p>
            </div>
            
            <div class="result-panel">
                <div class="result-header">
                    <span class="result-title">Profiling Suggestions</span>
                    <button class="button secondary" id="copySuggestionsBtn">Copy</button>
                </div>
                <div class="code-viewer" id="suggestionsViewer">
                    ${Utils.escapeHtml(this.profilingData.profilingSuggestions || 'No suggestions generated')}
                </div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backBtn1">
                    Back to Step 1
                </button>
                <button type="button" class="button primary" id="generateTestcasesBtn">
                    Generate Test Cases
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8h10m0 0l-3-3m3 3l-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
    }
    
    renderStep3() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 3: Generate PySpark Code</h3>
                <p class="content-description">
                    Convert test cases into executable PySpark code for data profiling
                </p>
            </div>
            
            <div class="result-panel">
                <div class="result-header">
                    <span class="result-title">Test Cases</span>
                    <button class="button secondary" id="copyTestcasesBtn">Copy</button>
                </div>
                <div class="code-viewer" id="testcasesViewer">
                    ${Utils.escapeHtml(this.profilingData.profilingTestcases || 'No test cases generated')}
                </div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backBtn2">
                    Back to Step 2
                </button>
                <button type="button" class="button primary" id="generatePysparkBtn">
                    Generate PySpark Code
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8h10m0 0l-3-3m3 3l-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
    }
    
    renderStep4() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 4: Execute PySpark Profiling</h3>
                <p class="content-description">
                    Run the generated PySpark code to profile your data
                </p>
            </div>
            
            <div class="result-panel">
                <div class="result-header">
                    <span class="result-title">PySpark Code</span>
                    <button class="button secondary" id="copyPysparkBtn">Copy</button>
                </div>
                <div class="code-viewer" id="pysparkViewer">
                    ${Utils.escapeHtml(this.profilingData.pysparkCode || 'No code generated')}
                </div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backBtn3">
                    Back to Step 3
                </button>
                <button type="button" class="button primary" id="executePysparkBtn">
                    Execute Code
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 5v6m0 0l3-3m-3 3l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
            
            <div id="executionResults" style="display: none;"></div>
        `;
    }
    
    renderStep5() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 5: Generate DQ Suggestions</h3>
                <p class="content-description">
                    Analyze profiling results to generate data quality improvement suggestions
                </p>
            </div>
            
            <div class="result-panel">
                <div class="result-header">
                    <span class="result-title">Profiling Results</span>
                    <span class="status-badge success">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 0a8 8 0 100 16A8 8 0 008 0zm3.707 6.293l-4 4a1 1 0 01-1.414 0l-2-2a1 1 0 111.414-1.414L7 8.172l3.293-3.293a1 1 0 111.414 1.414z"/>
                        </svg>
                        Completed
                    </span>
                </div>
                <div class="code-viewer" id="profilingResultsViewer">
                    ${Utils.escapeHtml(this.profilingData.profilingResults || 'No results available')}
                </div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backBtn4">
                    Back to Step 4
                </button>
                <button type="button" class="button primary" id="generateDqSuggestionsBtn">
                    Generate DQ Suggestions
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8h10m0 0l-3-3m3 3l-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
    }
    
    renderStep6() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 6: Generate DQ Test Cases</h3>
                <p class="content-description">
                    Create data quality test cases based on the suggestions
                </p>
            </div>
            
            <div class="result-panel">
                <div class="result-header">
                    <span class="result-title">DQ Suggestions</span>
                    <button class="button secondary" id="copyDqSuggestionsBtn">Copy</button>
                </div>
                <div class="code-viewer" id="dqSuggestionsViewer">
                    ${Utils.escapeHtml(this.profilingData.dqSuggestions || 'No suggestions generated')}
                </div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backBtn5">
                    Back to Step 5
                </button>
                <button type="button" class="button primary" id="generateDqTestsBtn">
                    Generate DQ Tests
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8h10m0 0l-3-3m3 3l-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
    }
    
    renderStep7() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 7: Generate DQ PySpark Code</h3>
                <p class="content-description">
                    Convert DQ test cases into executable PySpark code
                </p>
            </div>
            
            <div class="result-panel">
                <div class="result-header">
                    <span class="result-title">DQ Test Cases</span>
                    <button class="button secondary" id="copyDqTestsBtn">Copy</button>
                </div>
                <div class="code-viewer" id="dqTestsViewer">
                    ${Utils.escapeHtml(this.profilingData.dqTests || 'No tests generated')}
                </div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backBtn6">
                    Back to Step 6
                </button>
                <button type="button" class="button primary" id="generateDqPysparkBtn">
                    Generate DQ PySpark
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8h10m0 0l-3-3m3 3l-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
    }
    
    renderStep8() {
        return `
            <div class="content-header">
                <h3 class="content-title">Step 8: Execute DQ Analysis</h3>
                <p class="content-description">
                    Run the final data quality analysis and view results
                </p>
            </div>
            
            <div class="result-panel">
                <div class="result-header">
                    <span class="result-title">DQ PySpark Code</span>
                    <button class="button secondary" id="copyDqPysparkBtn">Copy</button>
                </div>
                <div class="code-viewer" id="dqPysparkViewer">
                    ${Utils.escapeHtml(this.profilingData.dqPysparkCode || 'No code generated')}
                </div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backBtn7">
                    Back to Step 7
                </button>
                <button type="button" class="button primary" id="executeDqBtn">
                    Execute DQ Analysis
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 5v6m0 0l3-3m-3 3l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
            
            <div id="dqResults" style="display: none;"></div>
        `;
    }
    
    setupEventListeners() {
        this.shadowRoot.addEventListener('click', async (e) => {
            const target = e.target.closest('button, .step-card');
            if (!target) return;
            
            // Step navigation
            if (target.classList.contains('step-card')) {
                const step = parseInt(target.dataset.step);
                if (step < this.currentStep) {
                    this.goToStep(step);
                }
                return;
            }
            
            // Button actions
            const handlers = {
                'generateSuggestionsBtn': () => this.generateSuggestions(e),
                'generateTestcasesBtn': () => this.generateTestcases(),
                'generatePysparkBtn': () => this.generatePyspark(),
                'executePysparkBtn': () => this.executePyspark(),
                'generateDqSuggestionsBtn': () => this.generateDqSuggestions(),
                'generateDqTestsBtn': () => this.generateDqTests(),
                'generateDqPysparkBtn': () => this.generateDqPyspark(),
                'executeDqBtn': () => this.executeDq(),
                
                // Copy buttons
                'copySuggestionsBtn': () => this.copyToClipboard(this.profilingData.profilingSuggestions),
                'copyTestcasesBtn': () => this.copyToClipboard(this.profilingData.profilingTestcases),
                'copyPysparkBtn': () => this.copyToClipboard(this.profilingData.pysparkCode),
                'copyDqSuggestionsBtn': () => this.copyToClipboard(this.profilingData.dqSuggestions),
                'copyDqTestsBtn': () => this.copyToClipboard(this.profilingData.dqTests),
                'copyDqPysparkBtn': () => this.copyToClipboard(this.profilingData.dqPysparkCode),
                
                // Back buttons
                'backBtn1': () => this.goToStep(1),
                'backBtn2': () => this.goToStep(2),
                'backBtn3': () => this.goToStep(3),
                'backBtn4': () => this.goToStep(4),
                'backBtn5': () => this.goToStep(5),
                'backBtn6': () => this.goToStep(6),
                'backBtn7': () => this.goToStep(7)
            };
            
            const handler = handlers[target.id];
            if (handler) {
                await handler();
            }
        });
        
        // Form submission
        this.shadowRoot.addEventListener('submit', (e) => {
            e.preventDefault();
        });
    }
    
    async generateSuggestions(e) {
        e.preventDefault();
        
        const dataSample = this.shadowRoot.getElementById('dataSample').value;
        const dataDescription = this.shadowRoot.getElementById('dataDescription').value;
        
        if (!dataSample || !dataDescription) {
            this.notifications.error('Please provide both data sample and description');
            return;
        }
        
        this.profilingData.dataSample = dataSample;
        this.profilingData.dataDescription = dataDescription;
        
        const button = this.shadowRoot.getElementById('generateSuggestionsBtn');
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<div class="loading-spinner" style="width: 16px; height: 16px;"></div> Generating...';
        
        try {
            const response = await this.api.generateProfilingSuggestions(dataSample, dataDescription);
            this.profilingData.profilingSuggestions = response.profiling_suggestions;
            this.notifications.success('Profiling suggestions generated');
            this.goToStep(2);
        } catch (error) {
            console.error('Error generating suggestions:', error);
            this.notifications.error('Failed to generate suggestions');
        } finally {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }
    
    async generateTestcases() {
        const button = this.shadowRoot.getElementById('generateTestcasesBtn');
        this.setButtonLoading(button, true);
        
        try {
            const response = await this.api.generateProfilingTestcases(this.profilingData.profilingSuggestions);
            this.profilingData.profilingTestcases = response.testcases;
            this.notifications.success('Test cases generated');
            this.goToStep(3);
        } catch (error) {
            console.error('Error generating test cases:', error);
            this.notifications.error('Failed to generate test cases');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async generatePyspark() {
        const button = this.shadowRoot.getElementById('generatePysparkBtn');
        this.setButtonLoading(button, true);
        
        try {
            const response = await this.api.generatePySparkCode(this.profilingData.profilingTestcases);
            this.profilingData.pysparkCode = response.pyspark_code;
            this.notifications.success('PySpark code generated');
            this.goToStep(4);
        } catch (error) {
            console.error('Error generating PySpark code:', error);
            this.notifications.error('Failed to generate PySpark code');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async executePyspark() {
        const button = this.shadowRoot.getElementById('executePysparkBtn');
        const resultsDiv = this.shadowRoot.getElementById('executionResults');
        
        this.setButtonLoading(button, true);
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading"><div class="loading-spinner"></div><span>Executing PySpark code...</span></div>';
        
        try {
            const response = await this.api.executePySparkCode(this.profilingData.pysparkCode);
            this.profilingData.profilingResults = response.results || response.output;
            
            resultsDiv.innerHTML = `
                <div class="result-panel" style="margin-top: var(--space-lg);">
                    <div class="result-header">
                        <span class="result-title">Execution Results</span>
                        <span class="status-badge ${response.success ? 'success' : 'error'}">
                            ${response.success ? 'Success' : 'Failed'}
                        </span>
                    </div>
                    <div class="code-viewer">${Utils.escapeHtml(this.profilingData.profilingResults)}</div>
                </div>
            `;
            
            if (response.success) {
                this.notifications.success('Profiling completed successfully');
                setTimeout(() => this.goToStep(5), 2000);
            } else {
                this.notifications.error('Profiling execution failed');
            }
        } catch (error) {
            console.error('Error executing PySpark:', error);
            resultsDiv.innerHTML = `<div style="color: var(--error-color); margin-top: var(--space-md);">Error: ${error.message}</div>`;
            this.notifications.error('Failed to execute PySpark code');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async generateDqSuggestions() {
        const button = this.shadowRoot.getElementById('generateDqSuggestionsBtn');
        this.setButtonLoading(button, true);
        
        try {
            const response = await this.api.generateDQSuggestions(this.profilingData.profilingResults);
            this.profilingData.dqSuggestions = response.dq_suggestions;
            this.notifications.success('DQ suggestions generated');
            this.goToStep(6);
        } catch (error) {
            console.error('Error generating DQ suggestions:', error);
            this.notifications.error('Failed to generate DQ suggestions');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async generateDqTests() {
        const button = this.shadowRoot.getElementById('generateDqTestsBtn');
        this.setButtonLoading(button, true);
        
        try {
            const response = await this.api.generateDQTests(this.profilingData.dqSuggestions);
            this.profilingData.dqTests = response.dq_tests;
            this.notifications.success('DQ tests generated');
            this.goToStep(7);
        } catch (error) {
            console.error('Error generating DQ tests:', error);
            this.notifications.error('Failed to generate DQ tests');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async generateDqPyspark() {
        const button = this.shadowRoot.getElementById('generateDqPysparkBtn');
        this.setButtonLoading(button, true);
        
        try {
            const response = await this.api.generatePySparkDQCode(this.profilingData.dqTests);
            this.profilingData.dqPysparkCode = response.pyspark_code;
            this.notifications.success('DQ PySpark code generated');
            this.goToStep(8);
        } catch (error) {
            console.error('Error generating DQ PySpark code:', error);
            this.notifications.error('Failed to generate DQ PySpark code');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    async executeDq() {
        const button = this.shadowRoot.getElementById('executeDqBtn');
        const resultsDiv = this.shadowRoot.getElementById('dqResults');
        
        this.setButtonLoading(button, true);
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading"><div class="loading-spinner"></div><span>Executing DQ analysis...</span></div>';
        
        try {
            const response = await this.api.executePySparkDQCode(this.profilingData.dqPysparkCode);
            this.profilingData.dqResults = response.results || response.output;
            
            resultsDiv.innerHTML = `
                <div class="result-panel" style="margin-top: var(--space-lg);">
                    <div class="result-header">
                        <span class="result-title">DQ Analysis Results</span>
                        <span class="status-badge ${response.success ? 'success' : 'error'}">
                            ${response.success ? 'Complete' : 'Failed'}
                        </span>
                    </div>
                    <div class="code-viewer">${Utils.escapeHtml(this.profilingData.dqResults)}</div>
                </div>
                
                <div style="text-align: center; margin-top: var(--space-xl);">
                    <h3 style="color: var(--success-color); margin-bottom: var(--space-sm);">
                        🎉 Data Profiling Complete!
                    </h3>
                    <p style="color: var(--text-secondary); margin-bottom: var(--space-lg);">
                        All 8 steps have been successfully completed.
                    </p>
                    <button class="button primary" onclick="location.reload()">
                        Start New Profiling
                    </button>
                </div>
            `;
            
            if (response.success) {
                this.notifications.success('Data quality analysis completed!');
            }
        } catch (error) {
            console.error('Error executing DQ analysis:', error);
            resultsDiv.innerHTML = `<div style="color: var(--error-color); margin-top: var(--space-md);">Error: ${error.message}</div>`;
            this.notifications.error('Failed to execute DQ analysis');
        } finally {
            this.setButtonLoading(button, false);
        }
    }
    
    goToStep(step) {
        this.currentStep = step;
        this.render();
        this.setupEventListeners();
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.dataset.originalHtml = button.innerHTML;
            button.innerHTML = '<div class="loading-spinner" style="width: 16px; height: 16px;"></div> Processing...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalHtml || button.innerHTML;
        }
    }
    
    async copyToClipboard(text) {
        if (!text) {
            this.notifications.warning('No content to copy');
            return;
        }
        
        const success = await Utils.copyToClipboard(text);
        if (success) {
            this.notifications.success('Copied to clipboard');
        } else {
            this.notifications.error('Failed to copy to clipboard');
        }
    }
}

// Define custom element
customElements.define('data-profiling-component', DataProfilingComponent);