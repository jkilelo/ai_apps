import { Link } from 'react-router-dom';
import { ChartBarIcon, ComputerDesktopIcon, SparklesIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { useState, useEffect } from 'react';

export function HomePage() {
    const [isVisible, setIsVisible] = useState(false);
    const [hoveredCard, setHoveredCard] = useState<number | null>(null);
    
    useEffect(() => {
        setIsVisible(true);
    }, []);
    const features = [
        {
            title: 'AI-Driven Data Quality Test',
            description: 'Comprehensive data analysis with automated quality assessment, statistical profiling, and detailed reporting.',
            icon: ChartBarIcon,
            href: '/data-profiling',
            color: 'from-blue-500 to-blue-600',
            steps: [
                'Provide Table Details',
                'Perform Profiling',
                'Execute Generated Code',
                'Generate DQ Rules',
                'Perform DQ Checks',
                'Review Results'
            ]
        },
        {
            title: 'Next-Gen UI Automation with AI',
            subtitle: 'Smarter UI, Smarter Testing',
            description: 'Automated UI Testing and interaction workflow with intelligent element detection and validation.',
            icon: ComputerDesktopIcon,
            href: '/web-automation',
            color: 'from-indigo-500 to-indigo-600',
            steps: [
                'Web URL',
                'Extract Elements',
                'Generate Test Cases',
                'Execute Tests',
                'Review Results'
            ]
        }
    ];

    return (
        <div className="h-[calc(100vh-49px)] sm:h-[calc(100vh-57px)] overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
            <div className="h-full flex flex-col">
                {/* Hero Section with Fade Animation */}
                <div className={`text-center px-4 pt-4 sm:pt-6 pb-2 sm:pb-4 transition-all duration-700 transform ${
                    isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'
                }`}>
                    <div className="flex justify-center mb-2">
                        <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg shadow-lg transform hover:scale-110 transition-transform duration-300">
                            <SparklesIcon className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
                        </div>
                    </div>
                    <div className="mb-2">
                        <h1 className="text-lg sm:text-xl lg:text-2xl font-medium text-slate-600 mb-1">
                            AI-Powered
                        </h1>
                        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Smart Testing Framework</span>
                        </h2>
                    </div>
                    <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto">
                        Transform your quality assurance with intelligent automation and AI-driven insights
                    </p>
                </div>

                {/* Feature Cards with Animation */}
                <div className="flex-1 px-4 pb-4 overflow-auto">
                    <div className={`grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 max-w-6xl mx-auto transition-all duration-700 transform ${
                        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                    }`}>
                        {features.map((feature, index) => {
                            const Icon = feature.icon;
                            return (
                                <Link
                                    key={feature.title}
                                    to={feature.href}
                                    onMouseEnter={() => setHoveredCard(index)}
                                    onMouseLeave={() => setHoveredCard(null)}
                                    className="group bg-white rounded-xl p-5 sm:p-6 shadow-md hover:shadow-xl transition-all duration-300 border border-slate-200 flex flex-col transform hover:-translate-y-1"
                                >
                                    {/* Header */}
                                    <div className="flex items-start space-x-3 mb-4">
                                        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${feature.color} flex-shrink-0 shadow-md group-hover:shadow-lg transition-shadow duration-300`}>
                                            <Icon className="h-6 w-6 text-white" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="text-lg sm:text-xl font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                                                {feature.title}
                                            </h3>
                                            {feature.subtitle && (
                                                <p className="text-sm font-medium text-indigo-600 mt-0.5">
                                                    {feature.subtitle}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    
                                    {/* Description */}
                                    <p className="text-sm sm:text-base text-slate-600 mb-4">
                                        {feature.description}
                                    </p>
                                    
                                    {/* Workflow Steps */}
                                    <div className="flex-1">
                                        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                                            Workflow Steps
                                        </h4>
                                        <div className="space-y-2">
                                            {feature.steps.map((step, stepIndex) => {
                                                const isCardHovered = hoveredCard === index;
                                                return (
                                                    <div 
                                                        key={stepIndex} 
                                                        className={`flex items-center space-x-2 p-1 rounded transition-all duration-300 ${
                                                            isCardHovered ? 'bg-slate-50 translate-x-1' : ''
                                                        }`}
                                                    >
                                                        <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                                                            isCardHovered 
                                                                ? `bg-gradient-to-br ${feature.color} shadow-sm` 
                                                                : 'bg-slate-100'
                                                        }`}>
                                                            <span className={`text-xs font-semibold ${
                                                                isCardHovered ? 'text-white' : 'text-slate-600'
                                                            }`}>
                                                                {stepIndex + 1}
                                                            </span>
                                                        </div>
                                                        <span className="text-sm text-slate-700">{step}</span>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                    
                                    {/* CTA */}
                                    <div className="flex items-center justify-between mt-5 pt-4 border-t border-slate-100">
                                        <div className="flex items-center space-x-2">
                                            <div className="flex -space-x-1">
                                                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                                <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                                            </div>
                                            <span className="text-xs text-green-600 font-medium">Ready</span>
                                        </div>
                                        <span className="text-sm font-medium text-blue-600 group-hover:translate-x-1 transition-transform flex items-center space-x-2">
                                            <span>Get Started</span>
                                            <ArrowRightIcon className="h-4 w-4" />
                                        </span>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}