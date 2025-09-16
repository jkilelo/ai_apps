import React from 'react';
import { Link } from 'react-router-dom';
import { Monitor, BarChart3, ArrowRight } from 'lucide-react';

export function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="text-center mb-16">
                    <h1 className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-white mb-6">
                        AI Testing Apps
                    </h1>
                    <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
                        Powerful AI-driven tools for web automation, data profiling, and testing workflows.
                        Streamline your development process with intelligent automation.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                    <Link
                        to="/web-automation"
                        className="group bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600"
                    >
                        <div className="flex items-center mb-4">
                            <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded-lg">
                                <Monitor className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900 dark:text-white ml-4">
                                Web Automation
                            </h2>
                        </div>
                        <p className="text-slate-600 dark:text-slate-300 mb-6">
                            Extract elements from web pages, generate test scenarios, and create automation scripts
                            with AI-powered analysis and code generation.
                        </p>
                        <div className="flex items-center text-blue-600 dark:text-blue-400 font-medium group-hover:translate-x-1 transition-transform">
                            Get Started
                            <ArrowRight className="h-4 w-4 ml-2" />
                        </div>
                    </Link>

                    <Link
                        to="/data-profiling"
                        className="group bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-slate-200 dark:border-slate-700 hover:border-purple-300 dark:hover:border-purple-600"
                    >
                        <div className="flex items-center mb-4">
                            <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-lg">
                                <BarChart3 className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900 dark:text-white ml-4">
                                Data Profiling
                            </h2>
                        </div>
                        <p className="text-slate-600 dark:text-slate-300 mb-6">
                            Analyze data structures, detect patterns, and generate insights with advanced
                            AI-powered data profiling and visualization tools.
                        </p>
                        <div className="flex items-center text-purple-600 dark:text-purple-400 font-medium group-hover:translate-x-1 transition-transform">
                            Explore Data
                            <ArrowRight className="h-4 w-4 ml-2" />
                        </div>
                    </Link>
                </div>

                <div className="text-center mt-16">
                    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-2xl mx-auto shadow-lg border border-slate-200 dark:border-slate-700">
                        <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                            Ready to Automate?
                        </h3>
                        <p className="text-slate-600 dark:text-slate-300">
                            Choose a tool above to start building intelligent automation workflows powered by AI.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}