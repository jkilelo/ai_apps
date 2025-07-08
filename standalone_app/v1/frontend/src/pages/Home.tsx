import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Globe, Database, ArrowRight, Sparkles } from 'lucide-react';

const Home: React.FC = () => {
  const features = [
    {
      icon: Brain,
      title: 'LLM Query',
      description: 'Interact with AI language models for various tasks',
      path: '/llm-query',
      color: 'bg-purple-500',
      lightColor: 'bg-purple-100',
    },
    {
      icon: Globe,
      title: 'Web Automation',
      description: 'Automate web interactions and generate test scripts',
      path: '/web-automation',
      color: 'bg-blue-500',
      lightColor: 'bg-blue-100',
    },
    {
      icon: Database,
      title: 'Data Profiling',
      description: 'Analyze data quality and generate insights',
      path: '/data-profiling',
      color: 'bg-green-500',
      lightColor: 'bg-green-100',
    },
  ];

  return (
    <div className="min-h-screen p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-12">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary rounded-2xl mb-6">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI Apps Standalone
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            A powerful suite of AI-powered tools for web automation and data profiling
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature) => (
            <Link
              key={feature.path}
              to={feature.path}
              className="card group hover:scale-105 transition-transform duration-300"
            >
              <div className="p-8">
                <div className={`inline-flex items-center justify-center w-16 h-16 ${feature.lightColor} rounded-xl mb-6 group-hover:scale-110 transition-transform`}>
                  <feature.icon className={`w-8 h-8 ${feature.color.replace('bg-', 'text-')}`} />
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-6">
                  {feature.description}
                </p>
                <div className="flex items-center text-primary font-medium">
                  <span>Get Started</span>
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-4xl mx-auto mt-16">
        <div className="card">
          <div className="p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              Key Features
            </h2>
            <div className="grid grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-primary mb-2">8+</div>
                <div className="text-gray-600">API Endpoints</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary mb-2">100%</div>
                <div className="text-gray-600">Open Source</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary mb-2">Real-time</div>
                <div className="text-gray-600">Processing</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;