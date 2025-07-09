import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs';
import { Alert, AlertDescription } from '../../ui/alert';
import { 
  Database, 
  FileText, 
  Cloud, 
  HardDrive,
  Zap,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface DataSource {
  id: string;
  name: string;
  type: 'database' | 'file' | 'streaming' | 'api';
  connection: any;
  metadata?: any;
}

interface DataSourceSelectorProps {
  onSelect: (source: DataSource) => void;
}

export const DataSourceSelector: React.FC<DataSourceSelectorProps> = ({ onSelect }) => {
  const [sourceType, setSourceType] = useState<string>('database');
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
  
  // Synthetic data sources (pre-configured)
  const syntheticDataSources = [
    {
      id: 'retail-parquet',
      name: 'Retail Analytics Dataset',
      type: 'file' as const,
      connection: {
        path: '/workspace/generated_data',
        format: 'parquet',
        tables: ['customers', 'products', 'transactions', 'inventory']
      },
      metadata: {
        description: 'E-commerce and retail analytics data',
        records: '500K+',
        lastUpdated: '2024-02-15'
      }
    },
    {
      id: 'financial-parquet',
      name: 'Financial Services Dataset',
      type: 'file' as const,
      connection: {
        path: '/workspace/generated_data/financial',
        format: 'parquet',
        tables: ['customers', 'accounts', 'transactions', 'loans', 'fraud_cases']
      },
      metadata: {
        description: 'Banking and financial transactions data',
        records: '139K+',
        lastUpdated: '2024-02-15'
      }
    }
  ];
  
  const [formData, setFormData] = useState({
    // Database connection
    dbType: 'postgresql',
    host: 'localhost',
    port: '5432',
    database: '',
    username: '',
    password: '',
    schema: 'public',
    table: '',
    
    // File connection
    filePath: '',
    fileFormat: 'parquet',
    
    // Streaming connection
    streamType: 'kafka',
    brokers: 'localhost:9092',
    topic: '',
    
    // API connection
    apiUrl: '',
    apiKey: '',
    endpoint: ''
  });
  
  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    setConnectionStatus('idle');
    
    // Simulate connection test
    setTimeout(() => {
      setConnectionStatus('success');
      setIsTestingConnection(false);
    }, 1500);
  };
  
  const handleConnect = () => {
    const source: DataSource = {
      id: `${sourceType}-${Date.now()}`,
      name: formData.table || formData.filePath || formData.topic || 'New Data Source',
      type: sourceType as any,
      connection: { ...formData }
    };
    
    onSelect(source);
  };
  
  const handleSelectSynthetic = (source: DataSource) => {
    onSelect(source);
  };
  
  return (
    <div className="dq-container" style={{ maxWidth: '64rem', margin: '0 auto' }}>
      <div className="dq-card" style={{ borderStyle: 'dashed', borderWidth: '2px' }}>
        <div className="dq-card-header">
          <h2 className="dq-card-title dq-text-2xl">Connect to Data Source</h2>
        </div>
        <div className="dq-card-body">
          {/* Quick Start with Synthetic Data */}
          <div className="dq-mb-lg">
            <h3 className="dq-text-lg dq-font-semibold dq-flex dq-items-center dq-gap-sm dq-mb-md">
              <Zap className="w-5 h-5" style={{ color: '#f59e0b' }} />
              <span>Quick Start with Sample Data</span>
            </h3>
            <div className="dq-source-grid">
              {syntheticDataSources.map((source) => (
                <div 
                  key={source.id}
                  className="dq-source-card"
                  onClick={() => handleSelectSynthetic(source)}
                >
                  <div className="dq-flex dq-justify-between dq-items-start">
                    <div className="dq-flex-1">
                      <h4 className="dq-font-semibold dq-mb-sm">{source.name}</h4>
                      <p className="dq-text-sm dq-text-gray dq-mb-md">
                        {source.metadata.description}
                      </p>
                      <div className="dq-flex dq-items-center dq-gap-md dq-text-xs dq-text-gray">
                        <span className="dq-flex dq-items-center dq-gap-xs">
                          <Database className="w-3 h-3" />
                          {source.metadata.records} records
                        </span>
                        <span>{source.connection.tables.length} tables</span>
                      </div>
                    </div>
                    <CheckCircle className="w-5 h-5 dq-text-success" />
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="dq-flex dq-items-center dq-gap-md dq-mb-lg dq-mt-lg">
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-gray-200)' }}></div>
            <span className="dq-text-xs dq-text-gray" style={{ textTransform: 'uppercase', padding: '0 var(--space-md)' }}>
              Or connect to your data
            </span>
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-gray-200)' }}></div>
          </div>
          
          {/* Data Source Type Selection */}
          <div className="dq-tabs">
            <div className="dq-tab-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))' }}>
              <button 
                className={`dq-tab ${sourceType === 'database' ? 'active' : ''}`}
                onClick={() => setSourceType('database')}
              >
                <Database className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                <span>Database</span>
              </button>
              <button 
                className={`dq-tab ${sourceType === 'file' ? 'active' : ''}`}
                onClick={() => setSourceType('file')}
              >
                <FileText className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                <span>File</span>
              </button>
              <button 
                className={`dq-tab ${sourceType === 'streaming' ? 'active' : ''}`}
                onClick={() => setSourceType('streaming')}
              >
                <Zap className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                <span>Streaming</span>
              </button>
              <button 
                className={`dq-tab ${sourceType === 'api' ? 'active' : ''}`}
                onClick={() => setSourceType('api')}
              >
                <Cloud className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                <span>API</span>
              </button>
            </div>
            
            <div className="dq-tab-content">
              {sourceType === 'database' && (
                <div className="dq-grid dq-grid-cols-2 dq-gap-md">
                  <div className="dq-form-group">
                    <label className="dq-label">Database Type</label>
                    <select 
                      className="dq-select"
                      value={formData.dbType} 
                      onChange={(e) => setFormData({...formData, dbType: e.target.value})}
                    >
                      <option value="postgresql">PostgreSQL</option>
                      <option value="mysql">MySQL</option>
                      <option value="sqlserver">SQL Server</option>
                      <option value="oracle">Oracle</option>
                      <option value="sqlite">SQLite</option>
                    </select>
                  </div>
                
                  <div className="dq-form-group">
                    <label className="dq-label">Host</label>
                    <input 
                      className="dq-input"
                      value={formData.host}
                      onChange={(e) => setFormData({...formData, host: e.target.value})}
                      placeholder="localhost"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Port</label>
                    <input 
                      className="dq-input"
                      value={formData.port}
                      onChange={(e) => setFormData({...formData, port: e.target.value})}
                      placeholder="5432"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Database</label>
                    <input 
                      className="dq-input"
                      value={formData.database}
                      onChange={(e) => setFormData({...formData, database: e.target.value})}
                      placeholder="mydb"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Username</label>
                    <input 
                      className="dq-input"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                      placeholder="user"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Password</label>
                    <input 
                      className="dq-input"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      placeholder="••••••••"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Schema</label>
                    <input 
                      className="dq-input"
                      value={formData.schema}
                      onChange={(e) => setFormData({...formData, schema: e.target.value})}
                      placeholder="public"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Table</label>
                    <input 
                      className="dq-input"
                      value={formData.table}
                      onChange={(e) => setFormData({...formData, table: e.target.value})}
                      placeholder="customers"
                    />
                  </div>
                </div>
              )}
            
              {sourceType === 'file' && (
                <div className="dq-grid dq-gap-md">
                  <div className="dq-form-group">
                    <label className="dq-label">File Path or URL</label>
                    <input 
                      className="dq-input"
                      value={formData.filePath}
                      onChange={(e) => setFormData({...formData, filePath: e.target.value})}
                      placeholder="/path/to/data.parquet or s3://bucket/data.csv"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">File Format</label>
                    <select 
                      className="dq-select"
                      value={formData.fileFormat} 
                      onChange={(e) => setFormData({...formData, fileFormat: e.target.value})}
                    >
                      <option value="parquet">Parquet</option>
                      <option value="csv">CSV</option>
                      <option value="json">JSON</option>
                      <option value="avro">Avro</option>
                      <option value="orc">ORC</option>
                    </select>
                  </div>
                </div>
              )}
            
              {sourceType === 'streaming' && (
                <div className="dq-grid dq-gap-md">
                  <div className="dq-form-group">
                    <label className="dq-label">Stream Type</label>
                    <select 
                      className="dq-select"
                      value={formData.streamType} 
                      onChange={(e) => setFormData({...formData, streamType: e.target.value})}
                    >
                      <option value="kafka">Apache Kafka</option>
                      <option value="kinesis">AWS Kinesis</option>
                      <option value="pubsub">Google Pub/Sub</option>
                      <option value="eventhub">Azure Event Hub</option>
                    </select>
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Brokers / Endpoint</label>
                    <input 
                      className="dq-input"
                      value={formData.brokers}
                      onChange={(e) => setFormData({...formData, brokers: e.target.value})}
                      placeholder="localhost:9092"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Topic / Stream Name</label>
                    <input 
                      className="dq-input"
                      value={formData.topic}
                      onChange={(e) => setFormData({...formData, topic: e.target.value})}
                      placeholder="data-stream"
                    />
                  </div>
                </div>
              )}
            
              {sourceType === 'api' && (
                <div className="dq-grid dq-gap-md">
                  <div className="dq-form-group">
                    <label className="dq-label">API URL</label>
                    <input 
                      className="dq-input"
                      value={formData.apiUrl}
                      onChange={(e) => setFormData({...formData, apiUrl: e.target.value})}
                      placeholder="https://api.example.com"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">API Key (Optional)</label>
                    <input 
                      className="dq-input"
                      type="password"
                      value={formData.apiKey}
                      onChange={(e) => setFormData({...formData, apiKey: e.target.value})}
                      placeholder="••••••••"
                    />
                  </div>
                  
                  <div className="dq-form-group">
                    <label className="dq-label">Endpoint</label>
                    <input 
                      className="dq-input"
                      value={formData.endpoint}
                      onChange={(e) => setFormData({...formData, endpoint: e.target.value})}
                      placeholder="/v1/data"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Connection Status */}
          {connectionStatus !== 'idle' && (
            <div className={`dq-alert ${connectionStatus === 'success' ? 'dq-alert-success' : 'dq-alert-danger'} dq-mt-lg`}>
              <AlertCircle className="h-4 w-4" />
              <span>
                {connectionStatus === 'success' 
                  ? 'Connection successful! You can now proceed.'
                  : 'Connection failed. Please check your settings.'}
              </span>
            </div>
          )}
          
          {/* Action Buttons */}
          <div className="dq-flex dq-justify-end dq-gap-md dq-mt-lg">
            <button 
              className="dq-btn dq-btn-secondary" 
              onClick={handleTestConnection}
              disabled={isTestingConnection}
            >
              {isTestingConnection ? 'Testing...' : 'Test Connection'}
            </button>
            <button 
              className="dq-btn dq-btn-primary"
              onClick={handleConnect}
              disabled={connectionStatus !== 'success' && sourceType !== 'file'}
            >
              Connect & Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};