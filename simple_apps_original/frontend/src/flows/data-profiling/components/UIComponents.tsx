import React from 'react';
import { motion } from 'framer-motion';
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';

interface TooltipProps {
    content: string;
    children: React.ReactNode;
    position?: 'top' | 'bottom' | 'left' | 'right';
}

export const Tooltip: React.FC<TooltipProps> = ({
    content,
    children,
    position = 'top'
}) => {
    const [isVisible, setIsVisible] = React.useState(false);

    const positionClasses = {
        top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
        bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
        left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
        right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
    };

    return (
        <div
            className="relative inline-block"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
        >
            {children}
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className={`
                        absolute z-[100] px-3 py-2 text-sm text-white bg-slate-900 dark:bg-slate-700 
                        rounded-lg shadow-lg whitespace-nowrap max-w-xs
                        ${positionClasses[position]}
                    `}
                >
                    {content}
                    <div className="absolute w-2 h-2 bg-slate-900 dark:bg-slate-700 transform rotate-45 
                        top-full left-1/2 -translate-x-1/2 -translate-y-1"></div>
                </motion.div>
            )}
        </div>
    );
};

interface HelpTooltipProps {
    content: string;
    className?: string;
}

export const HelpTooltip: React.FC<HelpTooltipProps> = ({ content, className = '' }) => (
    <Tooltip content={content}>
        <HelpCircle className={`h-4 w-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 cursor-help transition-colors ${className}`} />
    </Tooltip>
);

interface CollapsibleSectionProps {
    title: string;
    children: React.ReactNode;
    defaultOpen?: boolean;
    icon?: React.ReactNode;
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
    title,
    children,
    defaultOpen = false,
    icon
}) => {
    const [isOpen, setIsOpen] = React.useState(defaultOpen);

    return (
        <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
            <motion.button
                whileHover={{ backgroundColor: 'rgba(59, 130, 246, 0.05)' }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 text-left transition-colors"
            >
                <div className="flex items-center space-x-3">
                    {icon}
                    <span className="font-medium text-slate-900 dark:text-white">{title}</span>
                </div>
                <motion.div
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                >
                    <ChevronDown className="h-5 w-5 text-slate-500" />
                </motion.div>
            </motion.button>

            <motion.div
                initial={false}
                animate={{
                    height: isOpen ? 'auto' : 0,
                    opacity: isOpen ? 1 : 0
                }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className="overflow-hidden"
            >
                <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                    {children}
                </div>
            </motion.div>
        </div>
    );
};

// Enhanced focus ring for accessibility
export const FocusRing: React.FC<{ children: React.ReactNode; className?: string }> = ({
    children,
    className = ''
}) => (
    <div className={`
        focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 
        focus-within:ring-offset-white dark:focus-within:ring-offset-slate-900 
        rounded-lg transition-all duration-200
        ${className}
    `}>
        {children}
    </div>
);

// Keyboard navigation indicator
export const KeyboardHint: React.FC<{ keys: string[] }> = ({ keys }) => (
    <div className="inline-flex items-center space-x-1 text-xs text-slate-500 dark:text-slate-400">
        {keys.map((key, index) => (
            <React.Fragment key={key}>
                {index > 0 && <span className="text-slate-300">+</span>}
                <kbd className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded text-slate-700 dark:text-slate-300 font-mono text-xs">
                    {key}
                </kbd>
            </React.Fragment>
        ))}
    </div>
);
