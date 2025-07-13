import axios from 'axios';
import { GetMetadataRequest, GetMetadataResponse, APIEndpoint } from '../types/api';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: import.meta.env.PROD ? '' : 'http://localhost:8210',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// API service functions
export const apiService = {
    // Get metadata for a database table
    async getMetadata(request: GetMetadataRequest): Promise<GetMetadataResponse> {
        const response = await api.post('/api/metadata', request);
        return response.data;
    },

    // Get available API endpoints
    async getEndpoints(): Promise<Record<string, APIEndpoint>> {
        const response = await api.get('/api/endpoints');
        return response.data;
    },

    // Health check
    async healthCheck(): Promise<{ status: string }> {
        await api.get('/');
        return { status: 'ok' };
    },

    // Get form schema for dynamic form generation (optional - for future use)
    async getMetadataSchema(): Promise<any> {
        const response = await api.get('/api/metadata/schema');
        return response.data;
    },

    // Get example request payload (optional - for future use)
    async getMetadataExample(): Promise<GetMetadataRequest> {
        const response = await api.get('/api/metadata/example');
        return response.data;
    },

    // Generic POST method for all endpoints
    async post(endpoint: string, data: any): Promise<any> {
        const response = await api.post(endpoint, data);
        return response.data;
    },

    // Data Profiling endpoints
    async getProfilingSuggestions(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/profiling/suggestions', request);
        return response.data;
    },

    async getProfilingTestCases(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/profiling/testcases', request);
        return response.data;
    },

    async getProfilingCode(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/profiling/pyspark_code', request);
        return response.data;
    },

    async executeProfilingCode(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/profiling/code_execution', request);
        return response.data;
    },

    // Data Quality endpoints
    async getDQSuggestions(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/dq/suggestions', request);
        return response.data;
    },

    async getDQTestCases(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/dq/testcases', request);
        return response.data;
    },

    async getDQCode(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/dq/pyspark_code', request);
        return response.data;
    },

    async executeDQCode(request: GetMetadataRequest): Promise<any> {
        const response = await api.post('/api/dq/code_execution', request);
        return response.data;
    },

    // Web Automation endpoints
    async extractElements(url: string): Promise<any> {
        const response = await api.post('/api/ui/url', { url });
        return response.data;
    },

    async getUITestCases(url: string): Promise<any> {
        const response = await api.post('/api/ui/testcases', { url });
        return response.data;
    },

    async getUIPythonCode(url: string): Promise<any> {
        const response = await api.post('/api/ui/python_code', { url });
        return response.data;
    },

    async executeUICode(url: string): Promise<any> {
        const response = await api.post('/api/ui/code_execution', { url });
        return response.data;
    },

    // Session Management
    async getProfilingSession(database: string, table: string, freshData: boolean = false): Promise<any> {
        const response = await api.post('/api/session/profiling', {
            database,
            table,
            fresh_data: freshData
        });
        return response.data;
    },

    async getDQSession(database: string, table: string, freshData: boolean = false): Promise<any> {
        const response = await api.post('/api/session/dq', {
            database,
            table,
            fresh_data: freshData
        });
        return response.data;
    },

    async getUISession(url: string, freshData: boolean = false): Promise<any> {
        const response = await api.post('/api/session/ui', {
            url,
            fresh_data: freshData
        });
        return response.data;
    },

    async clearProfilingSession(database: string, table: string): Promise<any> {
        const response = await api.delete('/api/session/profiling', {
            data: { database, table }
        });
        return response.data;
    },

    async clearDQSession(database: string, table: string): Promise<any> {
        const response = await api.delete('/api/session/dq', {
            data: { database, table }
        });
        return response.data;
    },

    async clearUISession(url: string): Promise<any> {
        const response = await api.delete('/api/session/ui', {
            data: { url }
        });
        return response.data;
    },

    async getSessionSummary(): Promise<any> {
        const response = await api.get('/api/session/summary');
        return response.data;
    },

    async clearAllSessions(): Promise<any> {
        const response = await api.delete('/api/session/all');
        return response.data;
    }
};

// WebSocket service
export class WebSocketService {
    private ws: WebSocket | null = null;
    private clientId: string;
    private messageHandlers: Map<string, (data: any) => void> = new Map();
    private isConnected = false;

    constructor() {
        this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                const wsUrl = import.meta.env.PROD
                    ? `wss://${window.location.host}/ws/${this.clientId}`
                    : `ws://localhost:8210/ws/${this.clientId}`;

                this.ws = new WebSocket(wsUrl);

                this.ws.onopen = () => {
                    this.isConnected = true;
                    console.log('WebSocket connected');
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        const handler = this.messageHandlers.get(data.type);
                        if (handler) {
                            handler(data);
                        }
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                    }
                };

                this.ws.onclose = () => {
                    this.isConnected = false;
                    console.log('WebSocket disconnected');
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }

    send(message: any) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(message));
        }
    }

    onMessage(type: string, handler: (data: any) => void) {
        this.messageHandlers.set(type, handler);
    }

    removeMessageHandler(type: string) {
        this.messageHandlers.delete(type);
    }

    ping() {
        this.send({ type: 'ping' });
    }

    getStats() {
        this.send({ type: 'get_stats' });
    }

    notifyFormStart(formName: string) {
        this.send({ type: 'form_start', form_name: formName });
    }

    get connected() {
        return this.isConnected;
    }

    get id() {
        return this.clientId;
    }
}
