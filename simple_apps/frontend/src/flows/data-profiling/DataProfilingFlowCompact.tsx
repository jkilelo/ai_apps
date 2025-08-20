import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Database, BarChart3, CheckCircle, Code, Play, ArrowLeft, Menu, X, ChevronRight } from 'lucide-react';
import { SimpleProfileForm } from './components/SimpleProfileForm';
import { useTheme } from '../../contexts/ThemeContext';
import './styles/scrollbar.css';

const steps = [
    { id: 'input', title: 'Data Input', icon: Database },
    { id: 'metadata', title: 'Metadata', icon: BarChart3 },
    { id: 'profiling_suggestions', title: 'Suggestions', icon: CheckCircle },
    { id: 'profiling_code', title: 'Code', icon: Code },
    { id: 'profiling_execution', title: 'Execute', icon: Play }
];

export const DataProfilingFlowCompact: React.FC = () => {
    const { viewMode } = useTheme();
    const [currentStep, setCurrentStep] = useState(0);
    const [profileData, setProfileData] = useState<any>(null);
    const [stepResults, setStepResults] = useState<{ [key: string]: any }>({});
    const [isLoadingStep, setIsLoadingStep] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const handleFormSubmit = async (data: any) => {
        setProfileData(data);
        setCurrentStep(1);
        // Auto-close sidebar on mobile after action
        if (window.innerWidth < 768) {
            setSidebarOpen(false);
        }
    };

    const executeStep = async (stepIndex: number) => {
        if (stepIndex === 0 || !profileData) return;
        
        setIsLoadingStep(true);
        // Simulate API call
        setTimeout(() => {
            setStepResults({
                ...stepResults,
                [steps[stepIndex].id]: { success: true, data: 'Sample result' }
            });
            setIsLoadingStep(false);
            if (stepIndex < steps.length - 1) {
                setCurrentStep(stepIndex + 1);
            }
        }, 1000);
    };

    const renderStepContent = () => {
        const step = steps[currentStep];
        
        if (currentStep === 0) {
            return (
                <div className="h-full overflow-auto p-4">
                    <h2 className="text-lg font-semibold mb-3">Configure Data Source</h2>
                    <SimpleProfileForm onSubmit={handleFormSubmit} />
                </div>
            );
        }

        return (
            <div className="h-full overflow-auto p-4">
                <h2 className="text-lg font-semibold mb-3">{step.title}</h2>
                
                {isLoadingStep ? (
                    <div className="flex items-center justify-center h-32">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {stepResults[step.id] ? (
                            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                <p className="text-sm text-green-800">Step completed successfully</p>
                            </div>
                        ) : (
                            <button
                                onClick={() => executeStep(currentStep)}
                                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                            >
                                Execute {step.title}
                            </button>
                        )}
                        
                        {currentStep < steps.length - 1 && stepResults[step.id] && (
                            <button
                                onClick={() => setCurrentStep(currentStep + 1)}
                                className="w-full bg-slate-100 text-slate-700 py-2 px-4 rounded-lg hover:bg-slate-200 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                            >
                                <span>Next Step</span>
                                <ChevronRight className="h-4 w-4" />
                            </button>
                        )}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="h-[calc(100vh-49px)] sm:h-[calc(100vh-57px)] flex relative bg-slate-50">
            {/* Mobile Menu Button */}
            <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden absolute top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-slate-200"
            >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            {/* Sidebar - Collapsible on Mobile */}
            <div className={`
                ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
                md:translate-x-0 transition-transform duration-300
                fixed md:relative w-64 md:w-72 h-full bg-white border-r border-slate-200 z-40
                flex flex-col
            `}>
                {/* Header */}
                <div className="p-4 border-b border-slate-200">
                    <Link to="/" className="flex items-center space-x-2 text-sm text-slate-600 hover:text-slate-900 mb-3">
                        <ArrowLeft className="h-4 w-4" />
                        <span>Back</span>
                    </Link>
                    <h1 className="text-lg font-semibold text-slate-900">Data Profiling</h1>
                    <div className="mt-2 text-xs text-slate-500">
                        Step {currentStep + 1} of {steps.length}
                    </div>
                </div>

                {/* Steps List */}
                <div className="flex-1 overflow-y-auto p-3">
                    {steps.map((step, index) => {
                        const StepIcon = step.icon;
                        const isActive = currentStep === index;
                        const isCompleted = stepResults[step.id];
                        
                        return (
                            <button
                                key={step.id}
                                onClick={() => {
                                    if (index === 0 || profileData) {
                                        setCurrentStep(index);
                                        if (window.innerWidth < 768) {
                                            setSidebarOpen(false);
                                        }
                                    }
                                }}
                                disabled={index > 0 && !profileData}
                                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg mb-1 transition-all text-sm ${
                                    isActive
                                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                                        : isCompleted
                                        ? 'bg-green-50 text-green-700 hover:bg-green-100'
                                        : 'hover:bg-slate-50 text-slate-600'
                                } ${index > 0 && !profileData ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                <StepIcon className="h-4 w-4 flex-shrink-0" />
                                <span className="text-left flex-1">{step.title}</span>
                                {isCompleted && <CheckCircle className="h-3 w-3 text-green-600" />}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Overlay for mobile */}
            {sidebarOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-black bg-opacity-25 z-30"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                {/* Content */}
                <div className="flex-1 bg-white m-4 rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                    {renderStepContent()}
                </div>
            </div>
        </div>
    );
};