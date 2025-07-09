// WebSocket service for real-time data quality monitoring

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export interface WebSocketMessage {
  type: 'metric' | 'alert' | 'status' | 'error';
  data: any;
  timestamp: string;
}

export class DataQualityWebSocket {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  
  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      ...config
    };
  }
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }
      
      if (this.isConnecting) {
        reject(new Error('Already connecting'));
        return;
      }
      
      this.isConnecting = true;
      
      try {
        this.ws = new WebSocket(this.config.url);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected to data quality monitor');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.isConnecting = false;
          this.handleReconnect();
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }
  
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.messageHandlers.clear();
  }
  
  send(type: string, data: any): void {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected');
      return;
    }
    
    const message = {
      type,
      data,
      timestamp: new Date().toISOString()
    };
    
    this.ws.send(JSON.stringify(message));
  }
  
  on(event: string, handler: (data: any) => void): void {
    this.messageHandlers.set(event, handler);
  }
  
  off(event: string): void {
    this.messageHandlers.delete(event);
  }
  
  private handleMessage(message: WebSocketMessage): void {
    // Handle specific message types
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message.data);
    }
    
    // Also handle wildcard
    const wildcardHandler = this.messageHandlers.get('*');
    if (wildcardHandler) {
      wildcardHandler(message);
    }
  }
  
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts!) {
      console.error('Max reconnection attempts reached');
      return;
    }
    
    this.reconnectAttempts++;
    
    this.reconnectTimer = setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`);
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, this.config.reconnectInterval);
  }
  
  getState(): 'connecting' | 'open' | 'closing' | 'closed' {
    if (this.isConnecting) return 'connecting';
    
    switch (this.ws?.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'open';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'closed';
      default: return 'closed';
    }
  }
}

// Singleton instance for the app
let wsInstance: DataQualityWebSocket | null = null;

export const getDataQualityWebSocket = (config?: WebSocketConfig): DataQualityWebSocket => {
  if (!wsInstance && config) {
    wsInstance = new DataQualityWebSocket(config);
  }
  
  if (!wsInstance) {
    throw new Error('WebSocket not initialized. Provide config on first call.');
  }
  
  return wsInstance;
};

export const closeDataQualityWebSocket = (): void => {
  if (wsInstance) {
    wsInstance.disconnect();
    wsInstance = null;
  }
};