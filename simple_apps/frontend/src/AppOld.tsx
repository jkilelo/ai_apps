import { useState, useEffect } from 'react';
import { Database, Activity, Wifi, WifiOff, Users, MessageSquare } from 'lucide-react';
import DataProfiler from './components/DataProfiler.tsx';
import Header from './components/Header';
import StatusBar from './components/StatusBar.tsx';
import { WebSocketService } from './services/api';
import { WebSocketMessage } from './types/api';

function App() {
    const [wsService] = useState(() => new WebSocketService());
    const [isConnected, setIsConnected] = useState(false);
    const [activeConnections, setActiveConnections] = useState(0);
    const [recentMessages, setRecentMessages] = useState<WebSocketMessage[]>([]);

    useEffect(() => {
        // Initialize WebSocket connection
        const initWebSocket = async () => {
            try {
                await wsService.connect();
                setIsConnected(true);

                // Set up message handlers
                wsService.onMessage('connection', (data: WebSocketMessage) => {
                    console.log('Connected to server:', data.message);
                    addMessage(data);
                });

                wsService.onMessage('stats_update', (data: WebSocketMessage) => {
                    if (data.active_connections !== undefined) {
                        setActiveConnections(data.active_connections);
                    }
                    addMessage(data);
                });

                wsService.onMessage('form_activity', (data: WebSocketMessage) => {
                    addMessage(data);
                });

                wsService.onMessage('user_disconnect', (data: WebSocketMessage) => {
                    if (data.active_connections !== undefined) {
                        setActiveConnections(data.active_connections);
                    }
                    addMessage(data);
                });

                wsService.onMessage('pong', (data: WebSocketMessage) => {
                    console.log('Pong received:', data.timestamp);
                });

                // Request initial stats
                wsService.getStats();
            } catch (error) {
                console.error('Failed to connect to WebSocket:', error);
                setIsConnected(false);
            }
        };

        initWebSocket();

        // Cleanup on unmount
        return () => {
            wsService.disconnect();
        };
    }, [wsService]);

    const addMessage = (message: WebSocketMessage) => {
        setRecentMessages(prev => {
            const newMessages = [message, ...prev].slice(0, 10); // Keep only last 10 messages
            return newMessages;
        });
    };

    const handleFormStart = (formName: string) => {
        wsService.notifyFormStart(formName);
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Header />

            <main className="container mx-auto px-4 py-8">
                <div className="mb-8">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">
                                AI-Powered Testing Platform
                            </h1>
                            <p className="text-gray-600">
                                Next-generation data profiling and testing system with AI capabilities
                            </p>
                        </div>

                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                {isConnected ? (
                                    <Wifi className="h-5 w-5 text-green-500" />
                                ) : (
                                    <WifiOff className="h-5 w-5 text-red-500" />
                                )}
                                <span className={`text-sm font-medium ${isConnected ? 'text-green-600' : 'text-red-600'
                                    }`}>
                                    {isConnected ? 'Connected' : 'Disconnected'}
                                </span>
                            </div>

                            <div className="flex items-center space-x-2">
                                <Users className="h-5 w-5 text-blue-500" />
                                <span className="text-sm font-medium text-blue-600">
                                    {activeConnections} active
                                </span>
                            </div>
                        </div>
                    </div>

                    <StatusBar
                        isConnected={isConnected}
                        activeConnections={activeConnections}
                        recentMessages={recentMessages}
                    />
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2">
                        <DataProfiler
                            wsService={wsService}
                            onFormStart={handleFormStart}
                        />
                    </div>

                    <div className="space-y-6">
                        {/* Quick Stats Card */}
                        <div className="card">
                            <h3 className="text-lg font-semibold mb-4 flex items-center">
                                <Activity className="h-5 w-5 mr-2 text-primary-600" />
                                System Status
                            </h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                                    <span className="text-sm text-gray-600">Connection Status</span>
                                    <span className={`text-sm font-medium ${isConnected ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        {isConnected ? 'Online' : 'Offline'}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                                    <span className="text-sm text-gray-600">Active Users</span>
                                    <span className="text-sm font-medium text-blue-600">
                                        {activeConnections}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center py-2">
                                    <span className="text-sm text-gray-600">Session ID</span>
                                    <span className="text-xs font-mono text-gray-500">
                                        {wsService.id.slice(-8)}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Recent Activity */}
                        <div className="card">
                            <h3 className="text-lg font-semibold mb-4 flex items-center">
                                <MessageSquare className="h-5 w-5 mr-2 text-primary-600" />
                                Recent Activity
                            </h3>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                                {recentMessages.length > 0 ? (
                                    recentMessages.map((message, index) => (
                                        <div
                                            key={`${message.timestamp}-${index}`}
                                            className="p-3 bg-gray-50 rounded-lg"
                                        >
                                            <div className="flex justify-between items-start mb-1">
                                                <span className="text-sm font-medium text-gray-900 capitalize">
                                                    {message.type.replace('_', ' ')}
                                                </span>
                                                <span className="text-xs text-gray-500">
                                                    {new Date(message.timestamp).toLocaleTimeString()}
                                                </span>
                                            </div>
                                            {message.message && (
                                                <p className="text-xs text-gray-600">
                                                    {message.message}
                                                </p>
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-sm text-gray-500 text-center py-4">
                                        No recent activity
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Feature Overview */}
                        <div className="card">
                            <h3 className="text-lg font-semibold mb-4 flex items-center">
                                <Database className="h-5 w-5 mr-2 text-primary-600" />
                                Features
                            </h3>
                            <div className="space-y-3">
                                <div className="flex items-start space-x-3">
                                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900">Data Profiling</h4>
                                        <p className="text-xs text-gray-600">
                                            Analyze database tables and columns
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-start space-x-3">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900">Real-time Updates</h4>
                                        <p className="text-xs text-gray-600">
                                            Live WebSocket connections
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-start space-x-3">
                                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900">AI-Powered</h4>
                                        <p className="text-xs text-gray-600">
                                            Intelligent testing capabilities
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
