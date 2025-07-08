import React, { useState } from 'react';
import { Database, BarChart3, CheckCircle, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';

interface StepStatus {
  notStarted: boolean;
  inProgress: boolean;
  completed: boolean;
  error: boolean;
}

const DataProfiling: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Form inputs
  const [databaseName, setDatabaseName] = useState('');
  const [tableName, setTableName] = useState('');
  const [columns, setColumns] = useState('');
  
  // Outputs for each step
  const [outputs, setOutputs] = useState<{[key: number]: any}>({});

  const steps = [
    { number: 1, title: 'Profiling Suggestions', icon: Sparkles },
    { number: 2, title: 'Test Cases', icon: CheckCircle },
    { number: 3, title: 'Generate PySpark', icon: Database },
    { number: 4, title: 'Execute Profiling', icon: BarChart3 },
    { number: 5, title: 'DQ Suggestions', icon: AlertCircle },
    { number: 6, title: 'DQ Tests', icon: CheckCircle },
    { number: 7, title: 'DQ PySpark Code', icon: Database },
    { number: 8, title: 'Execute DQ Tests', icon: BarChart3 },
  ];

  const executeStep = async (stepNumber: number) => {
    setLoading(true);
    
    try {
      let response: any;
      const endpoints = [
        'generate_profiling_suggestions',
        'generate_profiling_testcases',
        'generate_pyspark_code',
        'execute_pyspark_code',
        'generate_dq_suggestions',
        'generate_dq_tests',
        'generate_pyspark_dq_code',
        'execute_pyspark_dq_code'
      ];

      if (stepNumber === 1) {
        response = await axios.post(`/api/data_profiling/${endpoints[0]}`, {
          database_name: databaseName,
          table_name: tableName,
          columns: columns.split(',').map(c => c.trim()).filter(c => c)
        });
        setSessionId(response.data.session_id);
      } else {
        const input = outputs[stepNumber - 1];
        response = await axios.post(`/api/data_profiling/${endpoints[stepNumber - 1]}`, {
          input: input,
          session_id: sessionId
        });
      }

      setOutputs(prev => ({ ...prev, [stepNumber]: response.data.output }));
      
      if (stepNumber < 8) {
        setCurrentStep(stepNumber + 1);
      }
    } catch (error) {
      console.error('Error:', error);
      alert(`Failed to execute step ${stepNumber}`);
    } finally {
      setLoading(false);
    }
  };

  const getStepStatus = (stepNumber: number): string => {
    if (currentStep === stepNumber && loading) return 'status-in-progress';
    if (outputs[stepNumber]) return 'status-completed';
    if (currentStep === stepNumber) return 'status-in-progress';
    return 'status-not-started';
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <Database className="w-6 h-6 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Data Profiling</h1>
          </div>
          <p className="text-gray-600">
            Analyze data quality and generate comprehensive profiling insights with PySpark
          </p>
        </div>

        {/* Initial Input Form */}
        {!sessionId && (
          <div className="card mb-8">
            <div className="p-8">
              <h3 className="text-xl font-semibold mb-6">Configure Data Source</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="form-label">Database Name</label>
                  <input
                    type="text"
                    value={databaseName}
                    onChange={(e) => setDatabaseName(e.target.value)}
                    placeholder="e.g., sales_db"
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="form-label">Table Name</label>
                  <input
                    type="text"
                    value={tableName}
                    onChange={(e) => setTableName(e.target.value)}
                    placeholder="e.g., customers"
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="form-label">Columns (comma-separated)</label>
                  <input
                    type="text"
                    value={columns}
                    onChange={(e) => setColumns(e.target.value)}
                    placeholder="e.g., id, name, email, age"
                    className="form-input"
                  />
                </div>
              </div>
              <button
                onClick={() => executeStep(1)}
                className="btn btn-primary mt-6"
                disabled={loading || !databaseName || !tableName || !columns}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Starting Analysis...
                  </span>
                ) : (
                  'Start Data Profiling'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Progress Steps */}
        {sessionId && (
          <div className="mb-8">
            <div className="grid grid-cols-4 gap-4">
              {steps.map((step) => (
                <div
                  key={step.number}
                  className={`card p-4 cursor-pointer transition-all ${
                    currentStep === step.number ? 'ring-2 ring-primary shadow-lg' : ''
                  }`}
                  onClick={() => currentStep === step.number && !loading && executeStep(step.number)}
                >
                  <div className="flex items-center gap-3">
                    <div className={`step-indicator ${
                      outputs[step.number] ? 'step-completed' :
                      currentStep === step.number ? 'step-active' : 'step-pending'
                    }`}>
                      {outputs[step.number] ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <step.icon className="w-5 h-5" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Step {step.number}</p>
                      <p className="text-xs text-gray-500">{step.title}</p>
                    </div>
                    <span className={`status-badge ${getStepStatus(step.number)}`}>
                      {loading && currentStep === step.number ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : outputs[step.number] ? (
                        <CheckCircle className="w-3 h-3" />
                      ) : (
                        <span className="w-2 h-2 rounded-full bg-current" />
                      )}
                      {loading && currentStep === step.number ? 'Processing' :
                       outputs[step.number] ? 'Complete' :
                       currentStep === step.number ? 'Ready' : 'Pending'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results Display */}
        {Object.entries(outputs).length > 0 && (
          <div className="space-y-6">
            {/* Step 1: Profiling Suggestions */}
            {outputs[1] && (
              <div className="card animate-slide-in">
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Profiling Suggestions</h3>
                  <div className="grid gap-4">
                    {outputs[1].map((suggestion: any, idx: number) => (
                      <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium">{suggestion.description}</h4>
                          <span className={`status-badge ${
                            suggestion.priority === 'high' ? 'bg-red-100 text-red-700' :
                            suggestion.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-green-100 text-green-700'
                          }`}>
                            {suggestion.priority}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Type: {suggestion.suggestion_type}</p>
                        <div className="flex flex-wrap gap-2">
                          {suggestion.columns_involved.map((col: string) => (
                            <span key={col} className="px-2 py-1 bg-white rounded text-xs">
                              {col}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Test Cases */}
            {outputs[2] && (
              <div className="card animate-slide-in">
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Generated Test Cases</h3>
                  <div className="grid gap-3">
                    {outputs[2].slice(0, 5).map((test: any, idx: number) => (
                      <div key={idx} className="p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900">{test.test_name}</h4>
                        <p className="text-sm text-blue-700 mt-1">{test.test_logic}</p>
                        <div className="mt-2 flex items-center gap-4 text-xs">
                          <span className="text-gray-600">ID: {test.test_id}</span>
                          <span className={`status-badge ${
                            test.severity === 'critical' ? 'bg-red-100 text-red-700' :
                            test.severity === 'major' ? 'bg-orange-100 text-orange-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {test.severity}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3 & 7: PySpark Code */}
            {(outputs[3] || outputs[7]) && (
              <div className="card animate-slide-in">
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">
                    {outputs[7] ? 'DQ PySpark Code' : 'Profiling PySpark Code'}
                  </h3>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm max-h-96">
                    {outputs[7] || outputs[3]}
                  </pre>
                </div>
              </div>
            )}

            {/* Step 4 & 8: Execution Results */}
            {(outputs[4] || outputs[8]) && (
              <div className="card animate-slide-in">
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">
                    {outputs[8] ? 'DQ Test Results' : 'Profiling Results'}
                  </h3>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm max-h-96">
                    {outputs[8] || outputs[4]}
                  </pre>
                </div>
              </div>
            )}

            {/* Step 5: DQ Suggestions */}
            {outputs[5] && (
              <div className="card animate-slide-in">
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Data Quality Suggestions</h3>
                  <div className="grid gap-4">
                    {outputs[5].map((suggestion: any, idx: number) => (
                      <div key={idx} className="p-4 bg-yellow-50 rounded-lg">
                        <h4 className="font-medium text-yellow-900">{suggestion.title}</h4>
                        <p className="text-sm text-yellow-700 mt-1">{suggestion.description}</p>
                        <p className="text-sm text-yellow-600 mt-2">{suggestion.recommendation}</p>
                        <div className="mt-3 flex items-center gap-2">
                          <span className={`status-badge ${
                            suggestion.impact === 'high' ? 'bg-red-100 text-red-700' :
                            suggestion.impact === 'medium' ? 'bg-orange-100 text-orange-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {suggestion.impact} impact
                          </span>
                          <span className="text-xs text-gray-500">
                            Category: {suggestion.category}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataProfiling;