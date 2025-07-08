import React, { useState, useEffect } from 'react';
import { Globe, Play, CheckCircle, AlertCircle, Loader2, ChevronRight } from 'lucide-react';
import axios from 'axios';

interface StepData {
  step1: { input: string; output: any[] | null };
  step2: { input: string; output: any[] | null };
  step3: { input: string; output: string | null };
  step4: { input: string; output: string | null };
}

const WebAutomation: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [stepData, setStepData] = useState<StepData>({
    step1: { input: '', output: null },
    step2: { input: '', output: null },
    step3: { input: '', output: null },
    step4: { input: '', output: null },
  });

  const steps = [
    { number: 1, title: 'Extract Elements', description: 'Enter URL to extract page elements' },
    { number: 2, title: 'Generate Tests', description: 'Describe test scenarios' },
    { number: 3, title: 'Generate Code', description: 'Create Python automation code' },
    { number: 4, title: 'Execute Code', description: 'Run the automation script' },
  ];

  const handleStep1Submit = async () => {
    if (!stepData.step1.input.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.post('/api/web_automation/extract_elements', {
        input: stepData.step1.input
      });
      
      setStepData(prev => ({
        ...prev,
        step1: { ...prev.step1, output: response.data.output }
      }));
      setSessionId(response.data.session_id);
      setCurrentStep(2);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to extract elements');
    } finally {
      setLoading(false);
    }
  };

  const handleStep2Submit = async () => {
    if (!stepData.step2.input.trim() || !sessionId) return;
    
    setLoading(true);
    try {
      const response = await axios.post('/api/web_automation/generate_gherkin_tests', {
        input: stepData.step2.input,
        session_id: sessionId
      });
      
      setStepData(prev => ({
        ...prev,
        step2: { ...prev.step2, output: response.data.output }
      }));
      setCurrentStep(3);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate tests');
    } finally {
      setLoading(false);
    }
  };

  const handleStep3Submit = async () => {
    if (!stepData.step3.input.trim() || !sessionId) return;
    
    setLoading(true);
    try {
      const response = await axios.post('/api/web_automation/generate_python_code', {
        input: stepData.step3.input,
        session_id: sessionId
      });
      
      setStepData(prev => ({
        ...prev,
        step3: { ...prev.step3, output: response.data.output },
        step4: { input: response.data.output, output: null }
      }));
      setCurrentStep(4);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate code');
    } finally {
      setLoading(false);
    }
  };

  const handleStep4Submit = async () => {
    if (!stepData.step4.input.trim() || !sessionId) return;
    
    setLoading(true);
    try {
      const response = await axios.post('/api/web_automation/execute_python_code', {
        input: stepData.step4.input,
        session_id: sessionId
      });
      
      setStepData(prev => ({
        ...prev,
        step4: { ...prev.step4, output: response.data.output }
      }));
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to execute code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <Globe className="w-6 h-6 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Web Automation</h1>
          </div>
          <p className="text-gray-600">
            Create automated web tests with AI-powered code generation
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, idx) => (
              <React.Fragment key={step.number}>
                <div className="flex flex-col items-center">
                  <div className={`step-indicator ${
                    currentStep === step.number ? 'step-active' : 
                    currentStep > step.number ? 'step-completed' : 'step-pending'
                  }`}>
                    {currentStep > step.number ? (
                      <CheckCircle className="w-6 h-6" />
                    ) : (
                      step.number
                    )}
                  </div>
                  <div className="mt-2 text-center">
                    <p className="text-sm font-medium text-gray-900">{step.title}</p>
                    <p className="text-xs text-gray-500 mt-1 max-w-[120px]">{step.description}</p>
                  </div>
                </div>
                {idx < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-4 ${
                    currentStep > step.number ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Step Forms */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Column */}
          <div>
            {/* Step 1: Extract Elements */}
            {currentStep >= 1 && (
              <div className={`card mb-6 ${currentStep === 1 ? 'ring-2 ring-primary' : ''}`}>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Step 1: Extract Elements</h3>
                  <label className="form-label">Website URL</label>
                  <input
                    type="url"
                    value={stepData.step1.input}
                    onChange={(e) => setStepData(prev => ({
                      ...prev,
                      step1: { ...prev.step1, input: e.target.value }
                    }))}
                    placeholder="https://example.com"
                    className="form-input"
                    disabled={currentStep !== 1 || loading}
                  />
                  {currentStep === 1 && (
                    <button
                      onClick={handleStep1Submit}
                      className="btn btn-primary mt-4 w-full"
                      disabled={loading || !stepData.step1.input.trim()}
                    >
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Extracting...
                        </span>
                      ) : (
                        'Extract Elements'
                      )}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Step 2: Generate Tests */}
            {currentStep >= 2 && (
              <div className={`card mb-6 ${currentStep === 2 ? 'ring-2 ring-primary' : ''}`}>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Step 2: Generate Tests</h3>
                  <label className="form-label">Test Scenario Description</label>
                  <textarea
                    value={stepData.step2.input}
                    onChange={(e) => setStepData(prev => ({
                      ...prev,
                      step2: { ...prev.step2, input: e.target.value }
                    }))}
                    placeholder="Describe what you want to test (e.g., Login flow, form submission, navigation)"
                    className="form-input min-h-[100px]"
                    disabled={currentStep !== 2 || loading}
                  />
                  {currentStep === 2 && (
                    <button
                      onClick={handleStep2Submit}
                      className="btn btn-primary mt-4 w-full"
                      disabled={loading || !stepData.step2.input.trim()}
                    >
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Generating...
                        </span>
                      ) : (
                        'Generate Tests'
                      )}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Step 3: Generate Code */}
            {currentStep >= 3 && (
              <div className={`card mb-6 ${currentStep === 3 ? 'ring-2 ring-primary' : ''}`}>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Step 3: Generate Code</h3>
                  <label className="form-label">Additional Instructions (Optional)</label>
                  <textarea
                    value={stepData.step3.input}
                    onChange={(e) => setStepData(prev => ({
                      ...prev,
                      step3: { ...prev.step3, input: e.target.value }
                    }))}
                    placeholder="Any specific requirements for the Python code?"
                    className="form-input min-h-[80px]"
                    disabled={currentStep !== 3 || loading}
                  />
                  {currentStep === 3 && (
                    <button
                      onClick={handleStep3Submit}
                      className="btn btn-primary mt-4 w-full"
                      disabled={loading}
                    >
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Generating...
                        </span>
                      ) : (
                        'Generate Python Code'
                      )}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Step 4: Execute Code */}
            {currentStep >= 4 && (
              <div className={`card ${currentStep === 4 ? 'ring-2 ring-primary' : ''}`}>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Step 4: Execute Code</h3>
                  <label className="form-label">Python Code</label>
                  <textarea
                    value={stepData.step4.input}
                    onChange={(e) => setStepData(prev => ({
                      ...prev,
                      step4: { ...prev.step4, input: e.target.value }
                    }))}
                    className="form-input min-h-[200px] font-mono text-sm"
                    disabled={loading}
                  />
                  <button
                    onClick={handleStep4Submit}
                    className="btn btn-primary mt-4 w-full"
                    disabled={loading || !stepData.step4.input.trim()}
                  >
                    {loading ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Executing...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-2">
                        <Play className="w-5 h-5" />
                        Execute Code
                      </span>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Output Column */}
          <div>
            {/* Step 1 Output */}
            {stepData.step1.output && (
              <div className="card mb-6 animate-slide-in">
                <div className="p-6">
                  <h4 className="font-semibold mb-3">Extracted Elements</h4>
                  <div className="max-h-[300px] overflow-y-auto space-y-2">
                    {stepData.step1.output.slice(0, 10).map((elem: any, idx: number) => (
                      <div key={idx} className="p-3 bg-gray-50 rounded-lg text-sm">
                        <span className={`status-badge ${
                          elem.type === 'button' ? 'bg-blue-100 text-blue-700' :
                          elem.type === 'input' ? 'bg-green-100 text-green-700' :
                          elem.type === 'link' ? 'bg-purple-100 text-purple-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {elem.type}
                        </span>
                        <p className="mt-1 text-gray-700">{elem.text || elem.placeholder || elem.href || 'No text'}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 2 Output */}
            {stepData.step2.output && (
              <div className="card mb-6 animate-slide-in">
                <div className="p-6">
                  <h4 className="font-semibold mb-3">Generated Tests</h4>
                  <div className="space-y-3 max-h-[400px] overflow-y-auto">
                    {stepData.step2.output.map((test: any, idx: number) => (
                      <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                        <h5 className="font-medium text-sm mb-2">{test.scenario}</h5>
                        <div className="space-y-1 text-xs">
                          {test.given?.map((g: string, i: number) => (
                            <p key={i} className="text-gray-600">Given {g}</p>
                          ))}
                          {test.when?.map((w: string, i: number) => (
                            <p key={i} className="text-blue-600">When {w}</p>
                          ))}
                          {test.then?.map((t: string, i: number) => (
                            <p key={i} className="text-green-600">Then {t}</p>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 4 Output */}
            {stepData.step4.output && (
              <div className="card animate-slide-in">
                <div className="p-6">
                  <h4 className="font-semibold mb-3">Execution Results</h4>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {stepData.step4.output}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebAutomation;