import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  Database, 
  AlertTriangle, 
  CheckCircle2, 
  TrendingUp,
  Brain,
  Sparkles,
  FileSearch,
  Activity,
  Shield
} from 'lucide-react';
import { DataSourceSelector } from './DataSourceSelector';
import { ProfileResults } from './ProfileResults';
import { QualityRules } from './QualityRules';
import { MLInsights } from './MLInsights';
import { RealTimeMonitor } from './RealTimeMonitor';
import { DataCatalog } from './DataCatalog';
import { TrendAnalysis } from './TrendAnalysis';
import { useDataQualityAPI } from '@/hooks/useDataQualityAPI';
import '../../../styles/dataQuality.css';

interface DataQualityAppProps {
  onClose?: () => void;
}

export const DataQualityApp: React.FC<DataQualityAppProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState('profile');
  const [selectedDataSource, setSelectedDataSource] = useState<any>(null);
  const [isProfileRunning, setIsProfileRunning] = useState(false);
  const [profileProgress, setProfileProgress] = useState(0);
  const [profileData, setProfileData] = useState<any>(null);
  const [qualityRules, setQualityRules] = useState<any[]>([]);
  const [mlInsights, setMlInsights] = useState<any>(null);
  const [catalogData, setCatalogData] = useState<any>(null);
  
  const { 
    loading,
    error,
    profileDataSource,
    generateQualityRules,
    executeQualityRules,
    getMLInsights,
    getCatalogData,
    updateCatalogEntry
  } = useDataQualityAPI();

  const handleDataSourceSelect = async (source: any) => {
    setSelectedDataSource(source);
    setActiveTab('profile');
  };

  const handleRunProfile = async () => {
    if (!selectedDataSource) return;
    
    setIsProfileRunning(true);
    setProfileProgress(0);
    
    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProfileProgress(prev => Math.min(prev + 10, 90));
      }, 500);
      
      // Run profile
      const profile = await profileDataSource(selectedDataSource, {
        includeML: true,
        qualityDimensions: ['completeness', 'validity', 'uniqueness', 'consistency', 'timeliness']
      });
      setProfileData(profile);
      
      clearInterval(progressInterval);
      setProfileProgress(100);
      
      // Auto-generate rules after profiling
      const rules = await generateQualityRules(profile, { autoDetect: true });
      setQualityRules(rules);
      
      // Get ML insights
      const insights = await getMLInsights(selectedDataSource);
      setMlInsights(insights);
      
      // Update catalog
      const catalog = await getCatalogData();
      setCatalogData(catalog);
      
    } catch (error) {
      console.error('Profiling error:', error);
    } finally {
      setIsProfileRunning(false);
      setProfileProgress(0);
    }
  };
  
  // Load catalog data on mount
  useEffect(() => {
    loadCatalogData();
  }, []);
  
  const loadCatalogData = async () => {
    try {
      const catalog = await getCatalogData();
      setCatalogData(catalog);
    } catch (error) {
      console.error('Failed to load catalog:', error);
    }
  };

  return (
    <div className="dq-app-container">
      {/* Header */}
      <div className="dq-app-header">
        <div className="dq-container">
          <div className="dq-flex dq-justify-between dq-items-center dq-flex-wrap dq-gap-md">
            <div className="dq-flex dq-items-center dq-gap-md">
              <div className="dq-flex dq-items-center dq-justify-center" style={{
                width: '48px',
                height: '48px',
                background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
                borderRadius: 'var(--radius-xl)',
                boxShadow: 'var(--shadow-lg)'
              }}>
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="dq-text-2xl dq-font-bold" style={{ 
                  background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent'
                }}>
                  AI-Powered Data Profiler
                </h1>
                <p className="dq-text-sm dq-text-gray">
                  Comprehensive data quality analysis with ML insights
                </p>
              </div>
            </div>
            
            {selectedDataSource && (
              <div className="dq-flex dq-items-center dq-gap-md dq-flex-wrap">
                <Badge variant="secondary" className="dq-badge dq-badge-info">
                  <Database className="w-3 h-3" style={{ marginRight: '0.25rem' }} />
                  {selectedDataSource.name}
                </Badge>
                <button
                  onClick={handleRunProfile}
                  disabled={isProfileRunning}
                  className="dq-btn dq-btn-primary"
                  style={{
                    background: isProfileRunning ? 'var(--color-gray-400)' : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)'
                  }}
                >
                  {isProfileRunning ? (
                    <>
                      <Activity className="w-4 h-4 dq-spinner" />
                      Profiling...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Run Profile
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {isProfileRunning && (
        <div className="dq-container dq-mt-md">
          <div className="dq-card" style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)',
            borderLeft: '4px solid var(--color-primary)'
          }}>
            <div className="dq-flex dq-flex-col dq-gap-sm">
              <div className="dq-flex dq-justify-between dq-text-sm">
                <span>Analyzing data quality...</span>
                <span className="dq-font-semibold">{profileProgress}%</span>
              </div>
              <div className="dq-progress">
                <div className="dq-progress-bar" style={{ width: `${profileProgress}%` }} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="dq-app-main">
        <div className="dq-container">
          {!selectedDataSource ? (
            <DataSourceSelector onSelect={handleDataSourceSelect} />
          ) : (
            <div>
              <div className="dq-tabs">
                <div className="dq-tab-list">
                  <button
                    className={`dq-tab ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => setActiveTab('profile')}
                  >
                    <FileSearch className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                    <span>Profile</span>
                  </button>
                  <button
                    className={`dq-tab ${activeTab === 'rules' ? 'active' : ''}`}
                    onClick={() => setActiveTab('rules')}
                  >
                    <Shield className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                    <span>Rules</span>
                  </button>
                  <button
                    className={`dq-tab ${activeTab === 'ml-insights' ? 'active' : ''}`}
                    onClick={() => setActiveTab('ml-insights')}
                  >
                    <Brain className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                    <span>ML Insights</span>
                  </button>
                  <button
                    className={`dq-tab ${activeTab === 'monitor' ? 'active' : ''}`}
                    onClick={() => setActiveTab('monitor')}
                  >
                    <Activity className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                    <span>Monitor</span>
                  </button>
                  <button
                    className={`dq-tab ${activeTab === 'catalog' ? 'active' : ''}`}
                    onClick={() => setActiveTab('catalog')}
                  >
                    <Database className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                    <span>Catalog</span>
                  </button>
                  <button
                    className={`dq-tab ${activeTab === 'trends' ? 'active' : ''}`}
                    onClick={() => setActiveTab('trends')}
                  >
                    <TrendingUp className="w-4 h-4" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                    <span>Trends</span>
                  </button>
                </div>
              </div>

              <div className="dq-tab-content">
                {activeTab === 'profile' && (
                  profileData ? (
                    <ProfileResults data={profileData} />
                  ) : (
                    <EmptyState 
                      icon={FileSearch}
                      title="No profile data available"
                      description="Run a profile to see comprehensive data quality analysis"
                    />
                  )
                )}

                {activeTab === 'rules' && (
                  qualityRules && qualityRules.length > 0 ? (
                    <QualityRules 
                      rules={qualityRules} 
                      onExecute={(rules) => executeQualityRules(rules, selectedDataSource)}
                      profileData={profileData}
                    />
                  ) : (
                    <EmptyState 
                      icon={Shield}
                      title="No quality rules generated"
                      description="Complete profiling to generate AI-powered quality rules"
                    />
                  )
                )}

                {activeTab === 'ml-insights' && (
                  mlInsights ? (
                    <MLInsights insights={mlInsights} />
                  ) : (
                    <EmptyState 
                      icon={Brain}
                      title="No ML insights available"
                      description="Run profiling with ML analysis to discover patterns"
                    />
                  )
                )}

                {activeTab === 'monitor' && (
                  <RealTimeMonitor dataSource={selectedDataSource} />
                )}

                {activeTab === 'catalog' && (
                  <DataCatalog 
                    catalogData={catalogData}
                    dataSource={selectedDataSource}
                  />
                )}

                {activeTab === 'trends' && (
                  <TrendAnalysis dataSource={selectedDataSource} />
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Empty State Component
const EmptyState: React.FC<{
  icon: React.ElementType;
  title: string;
  description: string;
}> = ({ icon: Icon, title, description }) => (
  <div className="dq-flex dq-flex-col dq-items-center dq-justify-center dq-text-center dq-p-xl" style={{ minHeight: '400px' }}>
    <div className="dq-p-lg dq-mb-md" style={{ 
      background: 'var(--color-gray-100)', 
      borderRadius: '50%'
    }}>
      <Icon className="w-12 h-12" style={{ color: 'var(--color-gray-400)' }} />
    </div>
    <h3 className="dq-text-lg dq-font-semibold dq-mb-sm">{title}</h3>
    <p className="dq-text-sm dq-text-gray" style={{ maxWidth: '28rem' }}>{description}</p>
  </div>
);


export default DataQualityApp;