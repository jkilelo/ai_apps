/**
 * Dynamic Forms Application - ES6 JavaScript Client
 * Real-time form generation with WebSocket streaming
 */

class DynamicFormsApp {
    constructor() {
        this.endpoints = {};
        this.currentEndpoint = null;
        this.websocket = null;
        this.updateCount = 0;
        this.formData = {};
        this.validationErrors = {};

        this.init();
    }

    async init() {
        console.log('🚀 Initializing Dynamic Forms App...');

        // Initialize WebSocket connection
        this.initWebSocket();

        // Load endpoints
        await this.loadEndpoints();

        // Set up event listeners
        this.setupEventListeners();

        console.log('✅ App initialized successfully');
    }

    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('🔌 WebSocket connected');
                this.updateConnectionStatus(true);
                this.showToast('Connected', 'Real-time updates are now active', 'success');
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };

            this.websocket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.showToast('Disconnected', 'Attempting to reconnect...', 'warning');

                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.initWebSocket(), 3000);
            };

            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('❌ Failed to initialize WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');

        if (connected) {
            statusIndicator.className = 'status-indicator connected';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Disconnected';
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message:', data);

        switch (data.type) {
            case 'connection':
                this.addUpdate(data.message, 'info', data.timestamp);
                break;
            case 'submission':
                this.addUpdate(data.message, 'success', data.timestamp);
                this.showToast('New Submission', data.message, 'success');
                break;
            case 'form_activity':
                this.addUpdate(data.message, 'info', data.timestamp);
                break;
            case 'pong':
                // Handle ping/pong for connection keepalive
                break;
            default:
                this.addUpdate(data.message || 'Unknown update', 'info', data.timestamp);
        }
    }

    addUpdate(message, type = 'info', timestamp = null) {
        const updatesList = document.getElementById('updates-list');
        const updateItem = document.createElement('div');
        updateItem.className = `update-item ${type}`;

        const time = timestamp ? new Date(timestamp) : new Date();
        const timeString = time.toLocaleTimeString();

        updateItem.innerHTML = `
            <div class="update-message">${message}</div>
            <div class="update-time">${timeString}</div>
        `;

        // Add to top of list
        updatesList.insertBefore(updateItem, updatesList.firstChild);

        // Update counter
        this.updateCount++;
        document.getElementById('updates-count').textContent = this.updateCount;

        // Limit to 50 updates
        const updates = updatesList.children;
        if (updates.length > 50) {
            updatesList.removeChild(updates[updates.length - 1]);
        }

        // Auto-scroll to top
        updatesList.scrollTop = 0;
    }

    async loadEndpoints() {
        try {
            console.log('📡 Loading endpoints...');
            const response = await fetch('/api/endpoints');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.endpoints = await response.json();
            this.renderEndpoints();

            console.log('✅ Endpoints loaded:', Object.keys(this.endpoints));
        } catch (error) {
            console.error('❌ Failed to load endpoints:', error);
            this.showToast('Error', 'Failed to load API endpoints', 'error');
        }
    }

    renderEndpoints() {
        const container = document.getElementById('endpoints-container');
        container.innerHTML = '';

        Object.entries(this.endpoints).forEach(([path, config]) => {
            const endpointItem = document.createElement('div');
            endpointItem.className = 'endpoint-item';
            endpointItem.dataset.endpoint = path;

            endpointItem.innerHTML = `
                <i data-feather="${config.icon || 'edit'}" class="endpoint-icon"></i>
                <div class="endpoint-info">
                    <h3>${config.title}</h3>
                    <p>${config.description}</p>
                </div>
            `;

            endpointItem.addEventListener('click', () => this.selectEndpoint(path, config));
            container.appendChild(endpointItem);
        });

        // Re-initialize feather icons
        feather.replace();
    }

    selectEndpoint(path, config) {
        // Update active state
        document.querySelectorAll('.endpoint-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-endpoint="${path}"]`).classList.add('active');

        // Store current endpoint
        this.currentEndpoint = { path, config };

        // Update page header
        document.getElementById('page-title').textContent = config.title;
        document.getElementById('page-description').textContent = config.description;

        // Hide welcome screen and show form
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('form-container').style.display = 'block';

        // Generate and render form
        this.generateForm(config.schema);

        // Notify WebSocket about form start
        this.sendWebSocketMessage({
            type: 'form_start',
            form_name: config.title,
            endpoint: path
        });

        console.log(`📝 Selected endpoint: ${path}`);
    }

    generateForm(schema) {
        const formTitle = document.getElementById('form-title');
        const formFields = document.getElementById('form-fields');

        // Update form title
        formTitle.innerHTML = `
            <i data-feather="${this.currentEndpoint.config.icon || 'edit'}" class="form-title-icon"></i>
            ${schema.title}
        `;

        // Clear existing fields
        formFields.innerHTML = '';
        this.formData = {};
        this.validationErrors = {};

        // Generate fields
        schema.fields.forEach(field => {
            const fieldElement = this.createFormField(field);
            formFields.appendChild(fieldElement);
        });

        // Re-initialize feather icons
        feather.replace();

        console.log('🎨 Form generated for:', schema.title);
    }

    createFormField(field) {
        const fieldDiv = document.createElement('div');
        fieldDiv.className = `form-field ${field.type === 'textarea' ? 'full-width' : ''}`;
        fieldDiv.dataset.fieldName = field.name;

        const label = document.createElement('label');
        label.className = `form-label ${field.required ? 'required' : ''}`;
        label.textContent = field.label;
        label.setAttribute('for', field.name);

        let inputElement;

        switch (field.type) {
            case 'select':
                inputElement = this.createSelectField(field);
                break;
            case 'checkbox':
                inputElement = this.createCheckboxField(field);
                break;
            case 'textarea':
                inputElement = this.createTextareaField(field);
                break;
            case 'range':
                inputElement = this.createRangeField(field);
                break;
            case 'tags':
                inputElement = this.createTagsField(field);
                break;
            default:
                inputElement = this.createInputField(field);
        }

        fieldDiv.appendChild(label);
        fieldDiv.appendChild(inputElement);

        return fieldDiv;
    }

    createInputField(field) {
        const input = document.createElement('input');
        input.className = 'form-input';
        input.type = field.type;
        input.name = field.name;
        input.id = field.name;
        input.placeholder = field.placeholder || '';

        if (field.required) input.required = true;
        if (field.validation) {
            if (field.validation.min !== undefined) input.min = field.validation.min;
            if (field.validation.max !== undefined) input.max = field.validation.max;
            if (field.validation.minLength !== undefined) input.minLength = field.validation.minLength;
            if (field.validation.maxLength !== undefined) input.maxLength = field.validation.maxLength;
            if (field.validation.pattern) input.pattern = field.validation.pattern;
        }

        input.addEventListener('input', (e) => this.handleFieldChange(field.name, e.target.value));
        input.addEventListener('blur', (e) => this.validateField(field, e.target.value));

        return input;
    }

    createSelectField(field) {
        const select = document.createElement('select');
        select.className = 'form-select';
        select.name = field.name;
        select.id = field.name;

        if (field.required) select.required = true;

        // Add placeholder option
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = `Select ${field.label}...`;
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        select.appendChild(placeholderOption);

        // Add options
        field.options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option.charAt(0).toUpperCase() + option.slice(1);
            select.appendChild(optionElement);
        });

        select.addEventListener('change', (e) => this.handleFieldChange(field.name, e.target.value));

        return select;
    }

    createCheckboxField(field) {
        const wrapper = document.createElement('div');
        wrapper.className = 'form-checkbox-wrapper';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'form-checkbox';
        checkbox.name = field.name;
        checkbox.id = field.name;

        if (field.required) checkbox.required = true;

        const checkboxLabel = document.createElement('label');
        checkboxLabel.setAttribute('for', field.name);
        checkboxLabel.textContent = field.placeholder || 'Check this box';

        checkbox.addEventListener('change', (e) => this.handleFieldChange(field.name, e.target.checked));

        wrapper.appendChild(checkbox);
        wrapper.appendChild(checkboxLabel);

        return wrapper;
    }

    createTextareaField(field) {
        const textarea = document.createElement('textarea');
        textarea.className = 'form-textarea';
        textarea.name = field.name;
        textarea.id = field.name;
        textarea.placeholder = field.placeholder || '';

        if (field.required) textarea.required = true;
        if (field.validation) {
            if (field.validation.minLength !== undefined) textarea.minLength = field.validation.minLength;
            if (field.validation.maxLength !== undefined) textarea.maxLength = field.validation.maxLength;
        }

        textarea.addEventListener('input', (e) => this.handleFieldChange(field.name, e.target.value));
        textarea.addEventListener('blur', (e) => this.validateField(field, e.target.value));

        return textarea;
    }

    createRangeField(field) {
        const wrapper = document.createElement('div');

        const range = document.createElement('input');
        range.type = 'range';
        range.className = 'form-range';
        range.name = field.name;
        range.id = field.name;
        range.min = field.min || 1;
        range.max = field.max || 5;
        range.value = field.min || 1;

        const labels = document.createElement('div');
        labels.className = 'range-labels';
        labels.innerHTML = `
            <span>${field.min || 1}</span>
            <span id="${field.name}-value">${field.min || 1}</span>
            <span>${field.max || 5}</span>
        `;

        range.addEventListener('input', (e) => {
            document.getElementById(`${field.name}-value`).textContent = e.target.value;
            this.handleFieldChange(field.name, parseInt(e.target.value));
        });

        wrapper.appendChild(range);
        wrapper.appendChild(labels);

        return wrapper;
    }

    createTagsField(field) {
        const wrapper = document.createElement('div');
        wrapper.className = 'tags-input';
        wrapper.dataset.fieldName = field.name;

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'tag-input';
        input.placeholder = 'Type and press Enter to add tags...';

        const tags = [];

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                e.preventDefault();
                const tag = input.value.trim();
                if (!tags.includes(tag)) {
                    tags.push(tag);
                    this.addTag(wrapper, tag, tags, field.name);
                    input.value = '';
                    this.handleFieldChange(field.name, tags);
                }
            } else if (e.key === 'Backspace' && !input.value && tags.length > 0) {
                const lastTag = tags.pop();
                this.removeTagElement(wrapper, lastTag);
                this.handleFieldChange(field.name, tags);
            }
        });

        wrapper.appendChild(input);

        return wrapper;
    }

    addTag(wrapper, tag, tags, fieldName) {
        const tagElement = document.createElement('div');
        tagElement.className = 'tag';
        tagElement.dataset.tag = tag;

        tagElement.innerHTML = `
            <span>${tag}</span>
            <button type="button" class="tag-remove" aria-label="Remove tag">&times;</button>
        `;

        tagElement.querySelector('.tag-remove').addEventListener('click', () => {
            const index = tags.indexOf(tag);
            if (index > -1) {
                tags.splice(index, 1);
                tagElement.remove();
                this.handleFieldChange(fieldName, tags);
            }
        });

        // Insert before the input
        const input = wrapper.querySelector('.tag-input');
        wrapper.insertBefore(tagElement, input);
    }

    removeTagElement(wrapper, tag) {
        const tagElement = wrapper.querySelector(`[data-tag="${tag}"]`);
        if (tagElement) {
            tagElement.remove();
        }
    }

    handleFieldChange(fieldName, value) {
        this.formData[fieldName] = value;

        // Clear validation error if field is valid
        if (this.validationErrors[fieldName]) {
            this.clearFieldError(fieldName);
        }

        console.log(`📝 Field changed: ${fieldName} =`, value);
    }

    validateField(field, value) {
        const errors = [];

        // Required validation
        if (field.required && (!value || (Array.isArray(value) && value.length === 0))) {
            errors.push(`${field.label} is required`);
        }

        // Type-specific validation
        if (value && field.validation) {
            const validation = field.validation;

            if (validation.minLength && value.length < validation.minLength) {
                errors.push(`${field.label} must be at least ${validation.minLength} characters`);
            }

            if (validation.maxLength && value.length > validation.maxLength) {
                errors.push(`${field.label} must not exceed ${validation.maxLength} characters`);
            }

            if (validation.min !== undefined && value < validation.min) {
                errors.push(`${field.label} must be at least ${validation.min}`);
            }

            if (validation.max !== undefined && value > validation.max) {
                errors.push(`${field.label} must not exceed ${validation.max}`);
            }

            if (validation.pattern && !new RegExp(validation.pattern).test(value)) {
                errors.push(`${field.label} format is invalid`);
            }
        }

        if (errors.length > 0) {
            this.showFieldError(field.name, errors[0]);
            this.validationErrors[field.name] = errors;
        } else {
            this.clearFieldError(field.name);
            delete this.validationErrors[field.name];
        }

        return errors.length === 0;
    }

    showFieldError(fieldName, message) {
        const fieldDiv = document.querySelector(`[data-field-name="${fieldName}"]`);
        if (!fieldDiv) return;

        fieldDiv.classList.add('error');

        // Remove existing error message
        const existingError = fieldDiv.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const template = document.getElementById('error-message-template');
        const errorElement = template.content.cloneNode(true);
        errorElement.querySelector('span').textContent = message;

        fieldDiv.appendChild(errorElement);

        // Re-initialize feather icons
        feather.replace();
    }

    clearFieldError(fieldName) {
        const fieldDiv = document.querySelector(`[data-field-name="${fieldName}"]`);
        if (!fieldDiv) return;

        fieldDiv.classList.remove('error');
        fieldDiv.classList.add('success');

        const errorMessage = fieldDiv.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }

        // Remove success class after animation
        setTimeout(() => {
            fieldDiv.classList.remove('success');
        }, 2000);
    }

    setupEventListeners() {
        // Form submission
        document.getElementById('dynamic-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });

        // Reset button
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetForm();
        });

        // Toast close buttons (event delegation)
        document.getElementById('toast-container').addEventListener('click', (e) => {
            if (e.target.classList.contains('toast-close')) {
                e.target.closest('.toast').remove();
            }
        });

        // Keep WebSocket alive with periodic pings
        setInterval(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.sendWebSocketMessage({ type: 'ping' });
            }
        }, 30000);
    }

    async submitForm() {
        if (!this.currentEndpoint) {
            this.showToast('Error', 'No endpoint selected', 'error');
            return;
        }

        // Validate all fields
        const schema = this.currentEndpoint.config.schema;
        let hasErrors = false;

        schema.fields.forEach(field => {
            const value = this.formData[field.name];
            if (!this.validateField(field, value)) {
                hasErrors = true;
            }
        });

        if (hasErrors) {
            this.showToast('Validation Error', 'Please fix the errors in the form', 'error');
            return;
        }

        // Show loading state
        this.setFormLoading(true);

        try {
            console.log('📤 Submitting form to:', this.currentEndpoint.path);
            console.log('📋 Form data:', this.formData);

            const response = await fetch(this.currentEndpoint.path, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.formData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showInFormResponse(result, 'success');
                this.showToast('Success', result.message || 'Form submitted successfully', 'success');

                // Don't auto-reset form so users can see the response
                // setTimeout(() => this.resetForm(), 5000);
            } else {
                throw new Error(result.detail || 'Submission failed');
            }

        } catch (error) {
            console.error('❌ Form submission error:', error);
            this.showToast('Error', error.message || 'Failed to submit form', 'error');
            this.showInFormResponse({ error: error.message }, 'error');
        } finally {
            this.setFormLoading(false);
        }
    }

    setFormLoading(loading) {
        const submitBtn = document.getElementById('submit-btn');
        const form = document.getElementById('dynamic-form');

        if (loading) {
            submitBtn.disabled = true;
            submitBtn.classList.add('btn-loading');

            // Add loading overlay to form
            const template = document.getElementById('loading-overlay-template');
            const overlay = template.content.cloneNode(true);
            form.style.position = 'relative';
            form.appendChild(overlay);
        } else {
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-loading');

            // Remove loading overlay
            const overlay = form.querySelector('.loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    }

    showInFormResponse(data, type = 'success') {
        // Remove any existing response
        const existingResponse = document.querySelector('.form-response');
        if (existingResponse) {
            existingResponse.remove();
        }

        // Create response container
        const responseContainer = document.createElement('div');
        responseContainer.className = `form-response ${type}`;

        // Format the response data for display
        const formattedData = this.formatResponseData(data);

        responseContainer.innerHTML = `
            <div class="form-response-header">
                <i data-feather="${type === 'success' ? 'check-circle' : 'alert-circle'}" class="response-icon"></i>
                <h3 class="response-title">${type === 'success' ? 'Submission Successful' : 'Submission Error'}</h3>
            </div>
            <div class="form-response-content">
                ${formattedData}
            </div>
            <div class="form-response-actions">
                <button type="button" class="btn btn-secondary" id="view-full-response">View Full Response</button>
                <button type="button" class="btn btn-primary" id="new-submission">New Submission</button>
            </div>
        `;

        // Insert after form fields, before form actions
        const formActions = document.querySelector('.form-actions');
        formActions.parentNode.insertBefore(responseContainer, formActions);

        // Set up event listeners
        document.getElementById('view-full-response').addEventListener('click', () => {
            this.showDetailedResponse(data);
        });

        document.getElementById('new-submission').addEventListener('click', () => {
            this.resetForm();
        });

        // Re-initialize feather icons
        feather.replace();

        // Scroll to response
        responseContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });

        console.log('✅ Response displayed in form:', data);
    }

    formatResponseData(data) {
        if (data.error) {
            return `
                <div class="response-field">
                    <strong>Error:</strong> ${data.error}
                </div>
            `;
        }

        let html = '';

        // Show success message prominently
        if (data.message) {
            html += `
                <div class="response-field highlight">
                    <i data-feather="info" class="field-icon"></i>
                    <div>
                        <strong>Message:</strong>
                        <span>${data.message}</span>
                    </div>
                </div>
            `;
        }

        // Show ID if available
        if (data.id) {
            html += `
                <div class="response-field">
                    <i data-feather="hash" class="field-icon"></i>
                    <div>
                        <strong>Record ID:</strong>
                        <span class="response-id">${data.id}</span>
                    </div>
                </div>
            `;
        }

        // Show timestamp if available
        if (data.created_at) {
            const date = new Date(data.created_at);
            html += `
                <div class="response-field">
                    <i data-feather="calendar" class="field-icon"></i>
                    <div>
                        <strong>Created:</strong>
                        <span>${date.toLocaleString()}</span>
                    </div>
                </div>
            `;
        }

        // Show success status
        if (data.success) {
            html += `
                <div class="response-field">
                    <i data-feather="check" class="field-icon"></i>
                    <div>
                        <strong>Status:</strong>
                        <span class="status-success">Successful</span>
                    </div>
                </div>
            `;
        }

        // Show any additional fields (excluding standard ones)
        const standardFields = ['success', 'message', 'id', 'created_at', 'error'];
        Object.entries(data).forEach(([key, value]) => {
            if (!standardFields.includes(key)) {
                html += `
                    <div class="response-field">
                        <div>
                            <strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                            <span>${typeof value === 'object' ? JSON.stringify(value) : value}</span>
                        </div>
                    </div>
                `;
            }
        });

        return html || '<div class="response-field">No additional data returned</div>';
    }

    showDetailedResponse(data) {
        // Show the original response area with full JSON
        const responseArea = document.getElementById('response-area');
        const responseContent = document.getElementById('response-content');

        responseContent.textContent = JSON.stringify(data, null, 2);
        responseArea.style.display = 'block';

        // Scroll to response
        responseArea.scrollIntoView({ behavior: 'smooth' });
    }

    showResponse(data) {
        const responseArea = document.getElementById('response-area');
        const responseContent = document.getElementById('response-content');

        responseContent.textContent = JSON.stringify(data, null, 2);
        responseArea.style.display = 'block';

        // Scroll to response
        responseArea.scrollIntoView({ behavior: 'smooth' });
    }

    resetForm() {
        const form = document.getElementById('dynamic-form');
        const responseArea = document.getElementById('response-area');

        // Reset form data
        this.formData = {};
        this.validationErrors = {};

        // Reset form elements
        form.reset();

        // Remove in-form response
        const formResponse = document.querySelector('.form-response');
        if (formResponse) {
            formResponse.remove();
        }

        // Clear error states
        document.querySelectorAll('.form-field').forEach(field => {
            field.classList.remove('error', 'success');
            const errorMessage = field.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.remove();
            }
        });

        // Reset range value displays
        document.querySelectorAll('.form-range').forEach(range => {
            const valueDisplay = document.getElementById(`${range.name}-value`);
            if (valueDisplay) {
                valueDisplay.textContent = range.value;
            }
        });

        // Clear tags
        document.querySelectorAll('.tags-input').forEach(tagsInput => {
            const tags = tagsInput.querySelectorAll('.tag');
            tags.forEach(tag => tag.remove());
        });

        // Hide response area
        responseArea.style.display = 'none';

        this.showToast('Reset', 'Form has been reset', 'info');
        console.log('🔄 Form reset');
    }

    showToast(title, message, type = 'info') {
        const container = document.getElementById('toast-container');
        const template = document.getElementById('toast-template');
        const toast = template.content.cloneNode(true);

        const toastElement = toast.querySelector('.toast');
        toastElement.classList.add(type);

        toast.querySelector('.toast-title').textContent = title;
        toast.querySelector('.toast-message').textContent = message;

        container.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            const toastToRemove = container.querySelector('.toast');
            if (toastToRemove) {
                toastToRemove.remove();
            }
        }, 5000);
    }

    sendWebSocketMessage(data) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(data));
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dynamicFormsApp = new DynamicFormsApp();
});

// Handle page visibility for WebSocket management
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('🛌 Page hidden, reducing WebSocket activity');
    } else {
        console.log('👀 Page visible, resuming WebSocket activity');
        // Reconnect if needed
        if (window.dynamicFormsApp &&
            (!window.dynamicFormsApp.websocket ||
                window.dynamicFormsApp.websocket.readyState !== WebSocket.OPEN)) {
            window.dynamicFormsApp.initWebSocket();
        }
    }
});
