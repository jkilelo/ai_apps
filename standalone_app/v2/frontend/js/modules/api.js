// API Client Module using Fetch API and Async/Await

export class ApiClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
        
        // AbortController for canceling requests
        this.controllers = new Map();
    }
    
    // Generic request method with modern features
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const requestId = `${options.method || 'GET'}-${endpoint}`;
        
        // Cancel previous request to same endpoint
        if (this.controllers.has(requestId)) {
            this.controllers.get(requestId).abort();
        }
        
        // Create new AbortController
        const controller = new AbortController();
        this.controllers.set(requestId, controller);
        
        const config = {
            method: options.method || 'GET',
            headers: {
                ...this.defaultHeaders,
                ...options.headers,
            },
            signal: controller.signal,
            ...options,
        };
        
        // Add body for non-GET requests
        if (options.body && config.method !== 'GET') {
            config.body = JSON.stringify(options.body);
        }
        
        try {
            const response = await fetch(url, config);
            
            // Clean up controller
            this.controllers.delete(requestId);
            
            // Handle response
            if (!response.ok) {
                throw new ApiError(response.status, response.statusText, await response.text());
            }
            
            // Parse response based on content type
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else if (contentType && contentType.includes('text/')) {
                return await response.text();
            } else {
                return await response.blob();
            }
        } catch (error) {
            // Clean up controller
            this.controllers.delete(requestId);
            
            if (error.name === 'AbortError') {
                console.log('Request was cancelled:', requestId);
                return null;
            }
            
            throw error;
        }
    }
    
    // HTTP method shortcuts
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }
    
    async post(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', body });
    }
    
    async put(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', body });
    }
    
    async patch(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'PATCH', body });
    }
    
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
    
    // Upload file with progress
    async uploadFile(endpoint, file, onProgress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const formData = new FormData();
            formData.append('file', file);
            
            // Progress tracking
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }
            
            // Handle completion
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        resolve(xhr.responseText);
                    }
                } else {
                    reject(new ApiError(xhr.status, xhr.statusText, xhr.responseText));
                }
            });
            
            // Handle errors
            xhr.addEventListener('error', () => {
                reject(new Error('Network error'));
            });
            
            // Send request
            xhr.open('POST', `${this.baseURL}${endpoint}`);
            xhr.send(formData);
        });
    }
    
    // Stream response using ReadableStream
    async stream(endpoint, onChunk) {
        const response = await fetch(`${this.baseURL}${endpoint}`);
        
        if (!response.ok) {
            throw new ApiError(response.status, response.statusText);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        try {
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                onChunk(chunk);
            }
        } finally {
            reader.releaseLock();
        }
    }
    
    // Cancel all pending requests
    cancelAll() {
        this.controllers.forEach(controller => controller.abort());
        this.controllers.clear();
    }
}

// Custom Error class for API errors
class ApiError extends Error {
    constructor(status, statusText, response) {
        super(`API Error: ${status} ${statusText}`);
        this.name = 'ApiError';
        this.status = status;
        this.statusText = statusText;
        this.response = response;
    }
}

// Specific API endpoints
export class AIAppsAPI extends ApiClient {
    constructor() {
        super('/api');
    }
    
    // LLM endpoints
    async queryLLM(prompt, options = {}) {
        return this.post('/llm_query', { prompt, ...options });
    }
    
    // Web Automation endpoints
    async extractElements(url) {
        return this.post('/web_automation/extract_elements', { url });
    }
    
    async generateGherkinTests(elements, url) {
        return this.post('/web_automation/generate_gherkin_tests', { elements, url });
    }
    
    async generatePythonCode(gherkin_tests) {
        return this.post('/web_automation/generate_python_code', { gherkin_tests });
    }
    
    async executePythonCode(python_code) {
        return this.post('/web_automation/execute_python_code', { python_code });
    }
    
    // Data Profiling endpoints
    async generateProfilingSuggestions(data_sample, data_description) {
        return this.post('/data_profiling/generate_profiling_suggestions', { 
            data_sample, 
            data_description 
        });
    }
    
    async generateProfilingTestcases(profiling_suggestions) {
        return this.post('/data_profiling/generate_profiling_testcases', { 
            profiling_suggestions 
        });
    }
    
    async generatePySparkCode(testcases) {
        return this.post('/data_profiling/generate_pyspark_code', { testcases });
    }
    
    async executePySparkCode(pyspark_code) {
        return this.post('/data_profiling/execute_pyspark_code', { pyspark_code });
    }
    
    async generateDQSuggestions(profiling_results) {
        return this.post('/data_profiling/generate_dq_suggestions', { profiling_results });
    }
    
    async generateDQTests(dq_suggestions) {
        return this.post('/data_profiling/generate_dq_tests', { dq_suggestions });
    }
    
    async generatePySparkDQCode(dq_tests) {
        return this.post('/data_profiling/generate_pyspark_dq_code', { dq_tests });
    }
    
    async executePySparkDQCode(pyspark_code) {
        return this.post('/data_profiling/execute_pyspark_dq_code', { pyspark_code });
    }
}