import React, { useState } from 'react';
import { Brain, Send, Loader2, Copy, Check } from 'lucide-react';
import axios from 'axios';

const LLMQuery: React.FC = () => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setOutput('');

    try {
      const response = await axios.post('/api/llm_query', {
        input: input
      });
      setOutput(response.data.output);
    } catch (error) {
      console.error('Error:', error);
      setOutput('Error: Failed to get response from LLM');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">LLM Query</h1>
          </div>
          <p className="text-gray-600">
            Ask questions and get AI-powered responses for web automation and data analysis tasks
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="card mb-6">
          <div className="p-6">
            <label className="form-label">Your Question</label>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about web automation, data profiling, or general AI tasks..."
              className="form-input min-h-[120px] resize-y"
              disabled={loading}
            />
            <div className="mt-4 flex justify-end">
              <button
                type="submit"
                className="btn btn-primary flex items-center gap-2"
                disabled={loading || !input.trim()}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Send Query
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Output */}
        {output && (
          <div className="card animate-fade-in">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Response</h3>
                <button
                  onClick={handleCopy}
                  className="btn btn-secondary py-2 px-4 flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </button>
              </div>
              <div className="prose prose-gray max-w-none">
                <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-lg text-sm">
                  {output}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* Examples */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Example Queries</h3>
          <div className="grid gap-3">
            {[
              "How can I automate form filling on a website?",
              "What are the best practices for data quality assessment?",
              "Generate a Python script to scrape product prices",
              "Explain how to detect anomalies in a dataset"
            ].map((example, idx) => (
              <button
                key={idx}
                onClick={() => setInput(example)}
                className="text-left p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all"
              >
                <p className="text-sm text-gray-700">{example}</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMQuery;