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
