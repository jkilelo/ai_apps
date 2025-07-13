import { AlertCircle, CheckCircle, Clock, Wifi } from 'lucide-react';
import { WebSocketMessage } from '../types/api';

interface StatusBarProps {
    isConnected: boolean;
    activeConnections: number;
    recentMessages: WebSocketMessage[];
}

const StatusBar = ({ isConnected, activeConnections, recentMessages }: StatusBarProps) => {
    const lastMessage = recentMessages[0];

    return (
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                    <div className="flex items-center space-x-2">
                        {isConnected ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                            <AlertCircle className="h-5 w-5 text-red-500" />
                        )}
                        <span className={`font-medium ${isConnected ? 'text-green-700' : 'text-red-700'
                            }`}>
                            {isConnected ? 'System Online' : 'System Offline'}
                        </span>
                    </div>

                    <div className="flex items-center space-x-2">
                        <Wifi className="h-4 w-4 text-blue-500" />
                        <span className="text-sm text-gray-600">
                            {activeConnections} active connection{activeConnections !== 1 ? 's' : ''}
                        </span>
                    </div>

                    {lastMessage && (
                        <div className="flex items-center space-x-2">
                            <Clock className="h-4 w-4 text-gray-400" />
                            <span className="text-sm text-gray-600">
                                Last activity: {new Date(lastMessage.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                    )}
                </div>

                <div className="text-sm text-gray-500">
                    React 19.1 • Tailwind 4.1 • FastAPI
                </div>
            </div>
        </div>
    );
};

export default StatusBar;
