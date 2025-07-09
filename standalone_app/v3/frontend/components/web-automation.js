// Web Automation Web Component
import { AIAppsAPI } from '../js/modules/api.js';
import { NotificationManager } from '../js/modules/notifications.js';
import { Utils } from '../js/modules/utils.js';

class WebAutomationComponent extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        
        // Initialize services
        this.api = new AIAppsAPI();
        this.notifications = new NotificationManager();
        
        // State
        this.currentStep = 1;
        this.stepData = {
            url: '',
            elements: null,
            gherkinTests: null,
            pythonCode: null,
            executionResult: null
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
                    max-width: 1000px;
                    margin: 0 auto;
                }
                
                .automation-container {
                    display: grid;
                    gap: var(--space-xl);
                }
                
                .progress-tracker {
                    background: var(--bg-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    box-shadow: var(--shadow-md);
                }
                
                .progress-steps {
                    display: flex;
                    justify-content: space-between;
                    position: relative;
                    margin-bottom: var(--space-lg);
                }
                
                .progress-line {
                    position: absolute;
                    top: 20px;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: var(--border-color);
                    z-index: 0;
                }
                
                .progress-line-fill {
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    background: var(--primary-color);
                    transition: width var(--transition-slow);
                    width: 0%;
                }
                
                .step {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: var(--space-xs);
                    position: relative;
                    z-index: 1;
                }
                
                .step-number {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: var(--bg-secondary);
                    border: 2px solid var(--border-color);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: var(--font-weight-semibold);
                    transition: all var(--transition-base);
                }
                
                .step.active .step-number {
                    background: var(--primary-color);
                    color: white;
                    border-color: var(--primary-color);
                    transform: scale(1.1);
                }
                
                .step.completed .step-number {
                    background: var(--success-color);
                    color: white;
                    border-color: var(--success-color);
                }
                
                .step-label {
                    font-size: var(--font-size-sm);
                    color: var(--text-secondary);
                    text-align: center;
                    max-width: 100px;
                }
                
                .step-content {
                    background: var(--bg-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-lg);
                    box-shadow: var(--shadow-md);
                }
                
                .step-header {
                    margin-bottom: var(--space-lg);
                }
                
                .step-title {
                    font-size: var(--font-size-xl);
                    font-weight: var(--font-weight-semibold);
                    margin-bottom: var(--space-xs);
                }
                
                .step-description {
                    color: var(--text-secondary);
                }
                
                .form-group {
                    margin-bottom: var(--space-md);
                }
                
                .form-label {
                    display: block;
                    font-weight: var(--font-weight-medium);
                    margin-bottom: var(--space-xs);
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
                    justify-content: flex-end;
                    margin-top: var(--space-lg);
                }
                
                .result-container {
                    background: var(--bg-secondary);
                    border-radius: var(--radius-md);
                    padding: var(--space-md);
                    margin-top: var(--space-md);
                    max-height: 400px;
                    overflow-y: auto;
                }
                
                .result-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--space-sm);
                }
                
                .result-title {
                    font-weight: var(--font-weight-medium);
                }
                
                .code-block {
                    background: var(--bg-primary);
                    border-radius: var(--radius-sm);
                    padding: var(--space-sm);
                    font-family: var(--font-mono);
                    font-size: var(--font-size-sm);
                    white-space: pre-wrap;
                    word-break: break-all;
                    line-height: 1.5;
                }
                
                .elements-grid {
                    display: grid;
                    gap: var(--space-sm);
                }
                
                .element-item {
                    background: var(--bg-primary);
                    border-radius: var(--radius-md);
                    padding: var(--space-sm);
                    display: grid;
                    grid-template-columns: auto 1fr;
                    gap: var(--space-sm);
                    align-items: start;
                }
                
                .element-type {
                    background: var(--primary-color);
                    color: white;
                    padding: 2px 8px;
                    border-radius: var(--radius-sm);
                    font-size: var(--font-size-xs);
                    font-weight: var(--font-weight-medium);
                }
                
                .element-details {
                    font-size: var(--font-size-sm);
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
                
                /* Import global styles */
                @import url('/css/variables.css');
                
                @media (max-width: 768px) {
                    .step-label {
                        display: none;
                    }
                    
                    .progress-steps {
                        justify-content: space-around;
                    }
                }
            </style>
            
            <div class="automation-container">
                <div class="progress-tracker">
                    <div class="progress-steps">
                        <div class="progress-line">
                            <div class="progress-line-fill" id="progressFill"></div>
                        </div>
                        ${this.renderSteps()}
                    </div>
                </div>
                
                <div class="step-content">
                    ${this.renderStepContent()}
                </div>
            </div>
        `;
    }
    
    renderSteps() {
        const steps = [
            { number: 1, label: 'Extract Elements' },
            { number: 2, label: 'Generate Tests' },
            { number: 3, label: 'Generate Code' },
            { number: 4, label: 'Execute Code' }
        ];
        
        return steps.map(step => `
            <div class="step ${step.number === this.currentStep ? 'active' : ''} ${step.number < this.currentStep ? 'completed' : ''}" data-step="${step.number}">
                <div class="step-number">${step.number < this.currentStep ? '✓' : step.number}</div>
                <div class="step-label">${step.label}</div>
            </div>
        `).join('');
    }
    
    renderStepContent() {
        switch (this.currentStep) {
            case 1:
                return this.renderStep1();
            case 2:
                return this.renderStep2();
            case 3:
                return this.renderStep3();
            case 4:
                return this.renderStep4();
            default:
                return '';
        }
    }
    
    renderStep1() {
        return `
            <div class="step-header">
                <h2 class="step-title">Step 1: Extract Elements</h2>
                <p class="step-description">Enter a URL to extract interactive elements from the webpage</p>
            </div>
            
            <form id="step1Form">
                <div class="form-group">
                    <label class="form-label" for="url">Website URL</label>
                    <input 
                        type="url" 
                        class="form-input" 
                        id="url" 
                        placeholder="https://example.com"
                        value="${this.stepData.url}"
                        required
                    />
                </div>
                
                <div class="button-group">
                    <button type="submit" class="button primary" id="extractBtn">
                        Extract Elements
                    </button>
                </div>
            </form>
            
            <div id="step1Result" style="display: none;"></div>
        `;
    }
    
    renderStep2() {
        return `
            <div class="step-header">
                <h2 class="step-title">Step 2: Generate Test Scenarios</h2>
                <p class="step-description">Generate Gherkin test scenarios based on extracted elements</p>
            </div>
            
            <div class="result-container">
                <div class="result-header">
                    <span class="result-title">Extracted Elements</span>
                    <span>${this.stepData.elements?.length || 0} elements</span>
                </div>
                <div class="elements-grid" id="elementsPreview"></div>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backToStep1">
                    Back
                </button>
                <button type="button" class="button primary" id="generateTestsBtn">
                    Generate Tests
                </button>
            </div>
            
            <div id="step2Result" style="display: none;"></div>
        `;
    }
    
    renderStep3() {
        return `
            <div class="step-header">
                <h2 class="step-title">Step 3: Generate Python Code</h2>
                <p class="step-description">Convert Gherkin tests to executable Python code</p>
            </div>
            
            <div class="result-container">
                <div class="result-header">
                    <span class="result-title">Gherkin Tests</span>
                    <button class="button secondary" id="copyGherkinBtn">Copy</button>
                </div>
                <pre class="code-block" id="gherkinPreview"></pre>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backToStep2">
                    Back
                </button>
                <button type="button" class="button primary" id="generateCodeBtn">
                    Generate Python Code
                </button>
            </div>
            
            <div id="step3Result" style="display: none;"></div>
        `;
    }
    
    renderStep4() {
        return `
            <div class="step-header">
                <h2 class="step-title">Step 4: Execute Code</h2>
                <p class="step-description">Run the generated automation code</p>
            </div>
            
            <div class="result-container">
                <div class="result-header">
                    <span class="result-title">Python Code</span>
                    <button class="button secondary" id="copyPythonBtn">Copy</button>
                </div>
                <pre class="code-block" id="pythonPreview"></pre>
            </div>
            
            <div class="button-group">
                <button type="button" class="button secondary" id="backToStep3">
                    Back
                </button>
                <button type="button" class="button primary" id="executeBtn">
                    Execute Code
                </button>
            </div>
            
            <div id="step4Result" style="display: none;"></div>
        `;
    }
    
    setupEventListeners() {
        // Re-render and setup listeners when step changes
        this.shadowRoot.addEventListener('click', async (e) => {
            const target = e.target;
            
            // Step 1
            if (target.id === 'extractBtn') {
                e.preventDefault();
                await this.extractElements();
            }
            
            // Step 2
            if (target.id === 'backToStep1') {
                this.goToStep(1);
            }
            if (target.id === 'generateTestsBtn') {
                await this.generateTests();
            }
            
            // Step 3
            if (target.id === 'backToStep2') {
                this.goToStep(2);
            }
            if (target.id === 'generateCodeBtn') {
                await this.generateCode();
            }
            if (target.id === 'copyGherkinBtn') {
                this.copyGherkinTests();
            }
            
            // Step 4
            if (target.id === 'backToStep3') {
                this.goToStep(3);
            }
            if (target.id === 'executeBtn') {
                await this.executeCode();
            }
            if (target.id === 'copyPythonBtn') {
                this.copyPythonCode();
            }
        });
        
        // Form submission
        this.shadowRoot.addEventListener('submit', (e) => {
            if (e.target.id === 'step1Form') {
                e.preventDefault();
            }
        });
    }
    
    async extractElements() {
        const urlInput = this.shadowRoot.getElementById('url');
        const url = urlInput.value.trim();
        
        if (!Utils.isValidURL(url)) {
            this.notifications.error('Please enter a valid URL');
            return;
        }
        
        const resultDiv = this.shadowRoot.getElementById('step1Result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div class="loading"><div class="loading-spinner"></div><span>Extracting elements...</span></div>';
        
        try {
            const response = await this.api.extractElements(url);
            this.stepData.url = url;
            this.stepData.elements = response.elements;
            
            this.notifications.success(`Extracted ${response.elements.length} elements`);
            this.goToStep(2);
            
        } catch (error) {
            console.error('Element extraction error:', error);
            resultDiv.innerHTML = `<div style="color: var(--error-color); margin-top: var(--space-md);">Error: ${error.message}</div>`;
            this.notifications.error('Failed to extract elements');
        }
    }
    
    async generateTests() {
        const resultDiv = this.shadowRoot.getElementById('step2Result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div class="loading"><div class="loading-spinner"></div><span>Generating tests...</span></div>';
        
        try {
            const response = await this.api.generateGherkinTests(this.stepData.elements, this.stepData.url);
            this.stepData.gherkinTests = response.gherkin_tests;
            
            this.notifications.success('Test scenarios generated successfully');
            this.goToStep(3);
            
        } catch (error) {
            console.error('Test generation error:', error);
            resultDiv.innerHTML = `<div style="color: var(--error-color); margin-top: var(--space-md);">Error: ${error.message}</div>`;
            this.notifications.error('Failed to generate tests');
        }
    }
    
    async generateCode() {
        const resultDiv = this.shadowRoot.getElementById('step3Result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div class="loading"><div class="loading-spinner"></div><span>Generating Python code...</span></div>';
        
        try {
            const response = await this.api.generatePythonCode(this.stepData.gherkinTests);
            this.stepData.pythonCode = response.python_code;
            
            this.notifications.success('Python code generated successfully');
            this.goToStep(4);
            
        } catch (error) {
            console.error('Code generation error:', error);
            resultDiv.innerHTML = `<div style="color: var(--error-color); margin-top: var(--space-md);">Error: ${error.message}</div>`;
            this.notifications.error('Failed to generate code');
        }
    }
    
    async executeCode() {
        const resultDiv = this.shadowRoot.getElementById('step4Result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div class="loading"><div class="loading-spinner"></div><span>Executing code...</span></div>';
        
        try {
            const response = await this.api.executePythonCode(this.stepData.pythonCode);
            this.stepData.executionResult = response;
            
            resultDiv.innerHTML = `
                <div class="result-container" style="margin-top: var(--space-md);">
                    <div class="result-header">
                        <span class="result-title">Execution Result</span>
                        <span style="color: ${response.success ? 'var(--success-color)' : 'var(--error-color)'}">
                            ${response.success ? 'Success' : 'Failed'}
                        </span>
                    </div>
                    <pre class="code-block">${Utils.escapeHtml(response.output || response.error || 'No output')}</pre>
                </div>
            `;
            
            if (response.success) {
                this.notifications.success('Code executed successfully');
            } else {
                this.notifications.error('Code execution failed');
            }
            
        } catch (error) {
            console.error('Code execution error:', error);
            resultDiv.innerHTML = `<div style="color: var(--error-color); margin-top: var(--space-md);">Error: ${error.message}</div>`;
            this.notifications.error('Failed to execute code');
        }
    }
    
    goToStep(step) {
        this.currentStep = step;
        this.render();
        this.setupEventListeners();
        this.updateProgress();
        
        // Populate data for current step
        if (step === 2 && this.stepData.elements) {
            this.renderElementsPreview();
        } else if (step === 3 && this.stepData.gherkinTests) {
            this.shadowRoot.getElementById('gherkinPreview').textContent = this.stepData.gherkinTests;
        } else if (step === 4 && this.stepData.pythonCode) {
            this.shadowRoot.getElementById('pythonPreview').textContent = this.stepData.pythonCode;
        }
    }
    
    updateProgress() {
        const progressFill = this.shadowRoot.getElementById('progressFill');
        const progress = ((this.currentStep - 1) / 3) * 100;
        progressFill.style.width = `${progress}%`;
    }
    
    renderElementsPreview() {
        const preview = this.shadowRoot.getElementById('elementsPreview');
        if (!preview || !this.stepData.elements) return;
        
        const elementsToShow = this.stepData.elements.slice(0, 5);
        preview.innerHTML = elementsToShow.map(el => `
            <div class="element-item">
                <span class="element-type">${el.type}</span>
                <div class="element-details">
                    ${el.text || el.name || el.selector || 'No text'}
                </div>
            </div>
        `).join('');
        
        if (this.stepData.elements.length > 5) {
            preview.innerHTML += `<div style="text-align: center; color: var(--text-secondary); padding: var(--space-sm);">
                ... and ${this.stepData.elements.length - 5} more elements
            </div>`;
        }
    }
    
    async copyGherkinTests() {
        const success = await Utils.copyToClipboard(this.stepData.gherkinTests);
        if (success) {
            this.notifications.success('Gherkin tests copied to clipboard');
        }
    }
    
    async copyPythonCode() {
        const success = await Utils.copyToClipboard(this.stepData.pythonCode);
        if (success) {
            this.notifications.success('Python code copied to clipboard');
        }
    }
}

// Define custom element
customElements.define('web-automation-component', WebAutomationComponent);