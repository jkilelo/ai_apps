import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, Info, X, ExternalLink } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
    id: string;
    type: ToastType;
    title: string;
    message?: string;
    action?: {
        label: string;
        onClick: () => void;
    };
    duration?: number;
}

interface ToastProps extends Toast {
    onRemove: (id: string) => void;
}

const ToastComponent: React.FC<ToastProps> = ({
    id,
    type,
    title,
    message,
    action,
    onRemove
}) => {
    const icons = {
        success: CheckCircle,
        error: AlertCircle,
        info: Info,
        warning: AlertCircle
    };

    const colors = {
        success: 'from-emerald-500 to-green-600',
        error: 'from-red-500 to-red-600',
        info: 'from-blue-500 to-indigo-600',
        warning: 'from-amber-500 to-orange-600'
    };

    const bgColors = {
        success: 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800',
        error: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
        info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
        warning: 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
    };

    const Icon = icons[type];

    return (
        <motion.div
            initial={{ opacity: 0, x: 300, scale: 0.3 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.5 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className={`
                relative w-full max-w-md p-4 rounded-xl border shadow-lg backdrop-blur-sm
                ${bgColors[type]}
            `}
        >
            <div className="flex items-start space-x-3">
                <div className={`flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-r ${colors[type]} flex items-center justify-center`}>
                    <Icon className="w-4 h-4 text-white" />
                </div>

                <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium text-slate-900 dark:text-white">
                            {title}
                        </h4>
                        <button
                            onClick={() => onRemove(id)}
                            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>

                    {message && (
                        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                            {message}
                        </p>
                    )}

                    {action && (
                        <button
                            onClick={action.onClick}
                            className={`
                                mt-2 inline-flex items-center space-x-1 text-sm font-medium transition-colors
                                ${type === 'success' ? 'text-emerald-700 hover:text-emerald-800 dark:text-emerald-300' :
                                    type === 'error' ? 'text-red-700 hover:text-red-800 dark:text-red-300' :
                                        type === 'warning' ? 'text-amber-700 hover:text-amber-800 dark:text-amber-300' :
                                            'text-blue-700 hover:text-blue-800 dark:text-blue-300'}
                            `}
                        >
                            <span>{action.label}</span>
                            <ExternalLink className="w-3 h-3" />
                        </button>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

interface ToastContainerProps {
    toasts: Toast[];
    onRemove: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
    return (
        <div className="fixed top-4 right-4 z-50 space-y-2">
            <AnimatePresence>
                {toasts.map((toast) => (
                    <ToastComponent
                        key={toast.id}
                        {...toast}
                        onRemove={onRemove}
                    />
                ))}
            </AnimatePresence>
        </div>
    );
};

// Hook for managing toasts
export const useToast = () => {
    const [toasts, setToasts] = React.useState<Toast[]>([]);

    const addToast = React.useCallback((toast: Omit<Toast, 'id'>) => {
        const id = Date.now().toString();
        const newToast = { ...toast, id };

        // Check for duplicate toasts with same title and message to prevent spam
        const isDuplicate = toasts.some(existingToast =>
            existingToast.title === toast.title &&
            existingToast.message === toast.message &&
            existingToast.type === toast.type
        );

        if (isDuplicate) {
            return id;
        }

        setToasts(prev => [...prev, newToast]);

        // Auto remove after duration
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id));
        }, toast.duration || 5000);

        return id;
    }, [toasts]);

    const removeToast = React.useCallback((id: string) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    }, []);

    const success = React.useCallback((title: string, message?: string, action?: Toast['action']) => {
        return addToast({ type: 'success', title, message, action });
    }, [addToast]);

    const error = React.useCallback((title: string, message?: string, action?: Toast['action']) => {
        return addToast({ type: 'error', title, message, action });
    }, [addToast]);

    const info = React.useCallback((title: string, message?: string, action?: Toast['action']) => {
        return addToast({ type: 'info', title, message, action });
    }, [addToast]);

    const warning = React.useCallback((title: string, message?: string, action?: Toast['action']) => {
        return addToast({ type: 'warning', title, message, action });
    }, [addToast]);

    return {
        toasts,
        addToast,
        removeToast,
        success,
        error,
        info,
        warning
    };
};
