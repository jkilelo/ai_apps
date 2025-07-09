import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { Alert, AlertDescription, AlertTitle } from '../../ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs';
import { Progress } from '../../ui/progress';
import {
  Brain,
  AlertTriangle,
  TrendingUp,
  Eye,
  Lightbulb,
  Activity,
  BarChart3,
  Sparkles,
  Info,
  ChevronRight,
  Target,
  Layers,
  ChevronDown
} from 'lucide-react';

interface MLInsight {
  insight_type: string;
  severity: string;
  affected_columns: string[];
  description: string;
  recommendation: string;
  ml_confidence: number;
  supporting_evidence: any;
}

interface MLInsightsProps {
  insights: {
    anomalies?: any;
    patterns?: any;
    correlations?: any;
    clusters?: any;
    time_series?: any;
    text_insights?: any;
    advanced_insights?: MLInsight[];
  };
}

export const MLInsights: React.FC<MLInsightsProps> = ({ insights }) => {
  const [selectedInsight, setSelectedInsight] = useState<string>('overview');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['anomalies']));
  
  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };
  
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'dq-text-danger';
      case 'high': return 'dq-text-danger';
      case 'medium': return 'dq-text-warning';
      case 'low': return 'dq-text-info';
      default: return 'dq-text-gray';
    }
  };
  
  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'warning';
      case 'low': return 'secondary';
      default: return 'default';
    }
  };
  
  return (
    <div className="dq-container">
      {/* Advanced Insights Summary */}
      {insights.advanced_insights && insights.advanced_insights.length > 0 && (
        <div className="dq-card dq-mb-lg" style={{ borderColor: 'var(--color-primary)', borderWidth: '2px' }}>
          <div className="dq-card-header">
            <h3 className="dq-card-title dq-flex dq-items-center dq-gap-sm">
              <Sparkles className="w-5 h-5" style={{ color: 'var(--color-primary)' }} />
              <span>AI-Powered Insights</span>
            </h3>
          </div>
          <div className="dq-card-body">
            <div className="dq-grid dq-gap-md">
              {insights.advanced_insights.map((insight, idx) => (
                <div 
                  key={idx} 
                  className={`dq-alert ${
                    insight.severity === 'critical' ? 'dq-alert-danger' :
                    insight.severity === 'high' ? 'dq-alert-danger' :
                    insight.severity === 'medium' ? 'dq-alert-warning' :
                    'dq-alert-info'
                  }`}
                >
                  <Lightbulb className="h-4 w-4" style={{ flexShrink: 0 }} />
                  <div className="dq-w-full">
                    <div className="dq-flex dq-justify-between dq-items-start dq-flex-wrap dq-gap-sm dq-mb-sm">
                      <span className="dq-font-semibold">{insight.description}</span>
                      <div className="dq-flex dq-gap-sm">
                        <Badge variant={getSeverityBadge(insight.severity)} className="dq-badge">
                          {insight.severity}
                        </Badge>
                        <Badge variant="outline" className="dq-badge">
                          {(insight.ml_confidence * 100).toFixed(0)}% confidence
                        </Badge>
                      </div>
                    </div>
                    <p className="dq-text-sm dq-mb-sm">{insight.recommendation}</p>
                    <div className="dq-flex dq-flex-wrap dq-gap-xs">
                      {insight.affected_columns.map((col) => (
                        <Badge key={col} variant="secondary" className="dq-badge dq-text-xs">
                          {col}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* ML Analysis Tabs */}
      <div className="dq-tabs">
        <div className="dq-tab-list dq-scrollbar" style={{ overflowX: 'auto' }}>
          <button 
            className={`dq-tab ${selectedInsight === 'overview' ? 'active' : ''}`}
            onClick={() => setSelectedInsight('overview')}
          >
            Overview
          </button>
          <button 
            className={`dq-tab ${selectedInsight === 'anomalies' ? 'active' : ''}`}
            onClick={() => setSelectedInsight('anomalies')}
          >
            Anomalies
          </button>
          <button 
            className={`dq-tab ${selectedInsight === 'patterns' ? 'active' : ''}`}
            onClick={() => setSelectedInsight('patterns')}
          >
            Patterns
          </button>
          <button 
            className={`dq-tab ${selectedInsight === 'correlations' ? 'active' : ''}`}
            onClick={() => setSelectedInsight('correlations')}
          >
            Correlations
          </button>
          <button 
            className={`dq-tab ${selectedInsight === 'clusters' ? 'active' : ''}`}
            onClick={() => setSelectedInsight('clusters')}
          >
            Clusters
          </button>
          <button 
            className={`dq-tab ${selectedInsight === 'predictions' ? 'active' : ''}`}
            onClick={() => setSelectedInsight('predictions')}
          >
            Predictions
          </button>
        </div>
        
        <div className="dq-tab-content">
          {selectedInsight === 'overview' && (
            <MLOverview insights={insights} />
          )}
          
          {selectedInsight === 'anomalies' && (
            <AnomalyAnalysis anomalies={insights.anomalies} />
          )}
          
          {selectedInsight === 'patterns' && (
            <PatternAnalysis patterns={insights.patterns} />
          )}
          
          {selectedInsight === 'correlations' && (
            <CorrelationAnalysis correlations={insights.correlations} />
          )}
          
          {selectedInsight === 'clusters' && (
            <ClusterAnalysis clusters={insights.clusters} />
          )}
          
          {selectedInsight === 'predictions' && (
            <PredictiveAnalysis insights={insights} />
          )}
        </div>
      </div>
    </div>
  );
};

// ML Overview Component
const MLOverview: React.FC<{ insights: any }> = ({ insights }) => {
  const metrics = [
    {
      label: 'Anomalies Detected',
      value: Object.values(insights.anomalies || {}).flat().length,
      icon: AlertTriangle,
      color: 'var(--color-danger)'
    },
    {
      label: 'Patterns Found',
      value: Object.keys(insights.patterns || {}).length,
      icon: Layers,
      color: 'var(--color-info)'
    },
    {
      label: 'Correlations',
      value: insights.correlations?.significant_correlations?.length || 0,
      icon: Activity,
      color: 'var(--color-primary)'
    },
    {
      label: 'Data Clusters',
      value: insights.clusters?.optimal_clusters || 0,
      icon: Target,
      color: 'var(--color-success)'
    }
  ];
  
  return (
    <div className="dq-grid dq-gap-lg">
      <div className="dq-grid dq-grid-cols-4 dq-gap-md">
        {metrics.map((metric, idx) => (
          <div key={idx} className="dq-metric-card">
            <div className="dq-flex dq-items-center dq-justify-between dq-mb-sm">
              <metric.icon className="w-5 h-5" style={{ color: metric.color }} />
            </div>
            <div className="dq-metric-value">{metric.value}</div>
            <div className="dq-metric-label">{metric.label}</div>
          </div>
        ))}
      </div>
      
      {/* Key Findings */}
      <div className="dq-card">
        <div className="dq-card-header">
          <h4 className="dq-card-title dq-text-lg">Key ML Findings</h4>
        </div>
        <div className="dq-card-body">
          <div className="dq-grid dq-gap-md">
            {insights.anomalies && Object.keys(insights.anomalies).length > 0 && (
              <FindingItem
                icon={AlertTriangle}
                title="Anomaly Detection"
                description={`Found anomalies in ${Object.keys(insights.anomalies).length} columns using multiple ML algorithms`}
                severity="high"
              />
            )}
            
            {insights.patterns && Object.keys(insights.patterns).length > 0 && (
              <FindingItem
                icon={Layers}
                title="Pattern Discovery"
                description={`Discovered ${Object.values(insights.patterns).flat().length} distinct patterns across string columns`}
                severity="medium"
              />
            )}
            
            {insights.clusters && insights.clusters.optimal_clusters > 0 && (
              <FindingItem
                icon={Target}
                title="Data Segmentation"
                description={`Data naturally segments into ${insights.clusters.optimal_clusters} clusters with ${(insights.clusters.silhouette_score * 100).toFixed(1)}% separation quality`}
                severity="low"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Finding Item Component
const FindingItem: React.FC<{
  icon: React.ElementType;
  title: string;
  description: string;
  severity: string;
}> = ({ icon: Icon, title, description, severity }) => (
  <div className="dq-flex dq-gap-md dq-p-md" style={{
    background: 'var(--color-gray-50)',
    borderRadius: 'var(--radius-lg)'
  }}>
    <div className="dq-p-sm" style={{
      background: severity === 'high' ? 'rgba(239, 68, 68, 0.1)' :
                  severity === 'medium' ? 'rgba(245, 158, 11, 0.1)' :
                  'rgba(59, 130, 246, 0.1)',
      borderRadius: 'var(--radius-lg)',
      flexShrink: 0
    }}>
      <Icon className="w-4 h-4" style={{
        color: severity === 'high' ? 'var(--color-danger)' :
               severity === 'medium' ? 'var(--color-warning)' :
               'var(--color-info)'
      }} />
    </div>
    <div className="dq-flex-1">
      <h4 className="dq-font-semibold dq-text-sm dq-mb-xs">{title}</h4>
      <p className="dq-text-sm dq-text-gray">{description}</p>
    </div>
  </div>
);

// Anomaly Analysis Component
const AnomalyAnalysis: React.FC<{ anomalies: any }> = ({ anomalies }) => {
  if (!anomalies || Object.keys(anomalies).length === 0) {
    return (
      <div className="dq-card">
        <div className="dq-card-body dq-text-center dq-p-xl dq-text-gray">
          No anomalies detected in the dataset
        </div>
      </div>
    );
  }
  
  return (
    <div className="dq-grid dq-gap-lg">
      {Object.entries(anomalies).map(([column, results]: [string, any]) => (
        <div key={column} className="dq-card">
          <div className="dq-card-header">
            <div className="dq-flex dq-justify-between dq-items-center dq-flex-wrap dq-gap-sm">
              <h4 className="dq-card-title dq-text-lg">{column}</h4>
              <Badge variant="destructive" className="dq-badge">
                {Array.isArray(results) ? results[0]?.anomaly_indices?.length || 0 : 0} anomalies
              </Badge>
            </div>
          </div>
          <div className="dq-card-body">
            {Array.isArray(results) && results.map((result, idx) => (
              <div key={idx} className="dq-mb-md dq-pb-md" style={{ borderBottom: idx < results.length - 1 ? '1px solid var(--color-gray-200)' : 'none' }}>
                <div className="dq-flex dq-justify-between dq-items-center dq-mb-sm dq-flex-wrap dq-gap-sm">
                  <div className="dq-flex dq-items-center dq-gap-sm">
                    <Badge variant="outline" className="dq-badge">{result.algorithm}</Badge>
                    <span className="dq-text-sm dq-text-gray">
                      Confidence: {(result.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <span className="dq-text-sm">
                    Contamination: {(result.contamination_rate * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="dq-text-sm dq-text-gray">{result.explanation}</p>
                
                {result.anomaly_scores && result.anomaly_scores.length > 0 && (
                  <div className="dq-mt-sm dq-p-sm" style={{
                    background: 'var(--color-gray-50)',
                    borderRadius: 'var(--radius-md)'
                  }}>
                    <span className="dq-text-xs dq-text-gray">
                      Anomaly scores range: [{Math.min(...result.anomaly_scores).toFixed(3)}, {Math.max(...result.anomaly_scores).toFixed(3)}]
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// Pattern Analysis Component
const PatternAnalysis: React.FC<{ patterns: any }> = ({ patterns }) => {
  const [expandedPattern, setExpandedPattern] = useState<string | null>(null);
  
  if (!patterns || Object.keys(patterns).length === 0) {
    return (
      <div className="dq-card">
        <div className="dq-card-body dq-text-center dq-p-xl dq-text-gray">
          No patterns discovered in the dataset
        </div>
      </div>
    );
  }
  
  return (
    <div className="dq-grid dq-gap-lg">
      {Object.entries(patterns).map(([column, columnPatterns]: [string, any]) => (
        <div key={column} className="dq-card">
          <div className="dq-card-header">
            <h4 className="dq-card-title dq-text-lg">{column}</h4>
          </div>
          <div className="dq-card-body">
            <div className="dq-grid dq-gap-md">
              {columnPatterns.map((pattern: any, idx: number) => {
                const isExpanded = expandedPattern === `${column}-${idx}`;
                return (
                  <div key={idx} className="dq-p-md" style={{
                    background: 'var(--color-gray-50)',
                    borderRadius: 'var(--radius-lg)'
                  }}>
                    <div className="dq-flex dq-justify-between dq-items-center dq-mb-sm dq-flex-wrap dq-gap-sm">
                      <Badge variant="outline" className="dq-badge" style={{ fontFamily: 'monospace' }}>
                        {pattern.pattern}
                      </Badge>
                      <div className="dq-flex dq-items-center dq-gap-sm">
                        <span className="dq-text-sm dq-text-gray">
                          {pattern.count} occurrences
                        </span>
                        <Badge variant="secondary" className="dq-badge">
                          {(pattern.confidence * 100).toFixed(0)}% confidence
                        </Badge>
                      </div>
                    </div>
                    
                    {pattern.examples && (
                      <div className="dq-mt-sm">
                        <button 
                          className="dq-text-xs dq-text-primary dq-flex dq-items-center dq-gap-xs"
                          onClick={() => setExpandedPattern(isExpanded ? null : `${column}-${idx}`)}
                        >
                          Examples 
                          <ChevronDown className={`w-3 h-3 dq-transition ${isExpanded ? 'rotate-180' : ''}`} />
                        </button>
                        {isExpanded && (
                          <div className="dq-flex dq-flex-wrap dq-gap-xs dq-mt-sm">
                            {pattern.examples.slice(0, 5).map((ex: string, i: number) => (
                              <code key={i} className="dq-text-xs dq-p-xs" style={{
                                background: 'var(--color-gray-200)',
                                borderRadius: 'var(--radius-sm)'
                              }}>
                                {ex}
                              </code>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {pattern.anomaly_score > 0 && (
                      <div className="dq-mt-sm dq-flex dq-items-center dq-gap-xs">
                        <AlertTriangle className="w-3 h-3 dq-text-warning" />
                        <span className="dq-text-xs dq-text-gray">
                          Anomaly score: {pattern.anomaly_score.toFixed(3)}
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Correlation Analysis Component
const CorrelationAnalysis: React.FC<{ correlations: any }> = ({ correlations }) => {
  if (!correlations) {
    return (
      <div className="dq-card">
        <div className="dq-card-body dq-text-center dq-p-xl dq-text-gray">
          No correlation analysis available
        </div>
      </div>
    );
  }
  
  return (
    <div className="dq-grid dq-gap-lg">
      {/* Linear Correlations */}
      {correlations.linear && (
        <div className="dq-card">
          <div className="dq-card-header">
            <h4 className="dq-card-title dq-text-lg">Linear Correlations (Pearson)</h4>
          </div>
          <div className="dq-card-body">
            <CorrelationHeatmap data={correlations.linear} />
          </div>
        </div>
      )}
      
      {/* Non-linear Correlations */}
      {correlations.non_linear && (
        <div className="dq-card">
          <div className="dq-card-header">
            <h4 className="dq-card-title dq-text-lg">Non-linear Correlations (Spearman)</h4>
          </div>
          <div className="dq-card-body">
            <CorrelationHeatmap data={correlations.non_linear} />
          </div>
        </div>
      )}
      
      {/* Categorical Correlations */}
      {correlations.categorical && Object.keys(correlations.categorical).length > 0 && (
        <div className="dq-card">
          <div className="dq-card-header">
            <h4 className="dq-card-title dq-text-lg">Categorical-Numeric Relationships</h4>
          </div>
          <div className="dq-card-body">
            <div className="dq-grid dq-gap-md">
              {Object.entries(correlations.categorical).map(([catCol, scores]: [string, any]) => (
                <div key={catCol}>
                  <h5 className="dq-font-semibold dq-text-sm dq-mb-sm">{catCol}</h5>
                  <div className="dq-grid dq-grid-cols-2 dq-gap-sm">
                    {Object.entries(scores).map(([numCol, score]: [string, any]) => (
                      <div key={numCol} className="dq-flex dq-justify-between dq-items-center dq-p-sm" style={{
                        background: 'var(--color-gray-50)',
                        borderRadius: 'var(--radius-md)'
                      }}>
                        <span className="dq-text-sm">{numCol}</span>
                        <Badge variant={score > 0.5 ? 'default' : 'secondary'} className="dq-badge">
                          {score.toFixed(3)}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Correlation Heatmap Component (responsive)
const CorrelationHeatmap: React.FC<{ data: any }> = ({ data }) => {
  const columns = Object.keys(data);
  
  const getCorrelationColor = (value: number) => {
    const absValue = Math.abs(value);
    if (absValue > 0.8) return '#ef4444';
    if (absValue > 0.6) return '#f97316';
    if (absValue > 0.4) return '#eab308';
    if (absValue > 0.2) return '#3b82f6';
    return '#d1d5db';
  };
  
  return (
    <div className="dq-overflow-container">
      <div style={{ minWidth: '600px' }}>
        <table className="dq-text-xs" style={{ width: '100%' }}>
          <thead>
            <tr>
              <th className="dq-p-xs"></th>
              {columns.map(col => (
                <th key={col} className="dq-p-xs dq-text-left">
                  <div style={{ 
                    transform: 'rotate(-45deg)', 
                    transformOrigin: 'left',
                    whiteSpace: 'nowrap',
                    marginTop: '2rem'
                  }}>
                    {col}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {columns.map(row => (
              <tr key={row}>
                <td className="dq-p-xs dq-font-semibold">{row}</td>
                {columns.map(col => {
                  const value = data[row]?.[col] || 0;
                  return (
                    <td key={col} className="dq-p-xs">
                      <div
                        className="dq-flex dq-items-center dq-justify-center dq-text-xs"
                        style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: 'var(--radius-sm)',
                          background: row === col ? 'var(--color-gray-400)' : getCorrelationColor(value),
                          color: 'white'
                        }}
                        title={`${row} vs ${col}: ${value.toFixed(3)}`}
                      >
                        {row !== col && Math.abs(value) > 0.5 ? value.toFixed(2) : ''}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Cluster Analysis Component
const ClusterAnalysis: React.FC<{ clusters: any }> = ({ clusters }) => {
  const [expandedCluster, setExpandedCluster] = useState<number | null>(null);
  
  if (!clusters || !clusters.clusters) {
    return (
      <div className="dq-card">
        <div className="dq-card-body dq-text-center dq-p-xl dq-text-gray">
          No clustering analysis available
        </div>
      </div>
    );
  }
  
  return (
    <div className="dq-grid dq-gap-lg">
      <div className="dq-card">
        <div className="dq-card-header">
          <div className="dq-flex dq-justify-between dq-items-center dq-flex-wrap dq-gap-sm">
            <h4 className="dq-card-title dq-text-lg">Data Segmentation Analysis</h4>
            <div className="dq-flex dq-items-center dq-gap-sm">
              <Badge variant="outline" className="dq-badge">
                {clusters.algorithm}
              </Badge>
              <Badge className="dq-badge">
                {clusters.optimal_clusters} clusters
              </Badge>
            </div>
          </div>
        </div>
        <div className="dq-card-body">
          <div className="dq-mb-lg">
            <div className="dq-flex dq-justify-between dq-text-sm dq-mb-sm">
              <span>Silhouette Score (Quality)</span>
              <span className="dq-font-semibold">{(clusters.silhouette_score * 100).toFixed(1)}%</span>
            </div>
            <div className="dq-progress">
              <div className="dq-progress-bar" style={{ width: `${clusters.silhouette_score * 100}%` }} />
            </div>
          </div>
          
          <div className="dq-grid dq-gap-md">
            {clusters.clusters.map((cluster: any) => {
              const isExpanded = expandedCluster === cluster.cluster_id;
              return (
                <div key={cluster.cluster_id} className="dq-p-md" style={{
                  background: 'var(--color-gray-50)',
                  borderRadius: 'var(--radius-lg)'
                }}>
                  <div className="dq-flex dq-justify-between dq-items-center dq-mb-sm">
                    <h5 className="dq-font-semibold">Cluster {cluster.cluster_id}</h5>
                    <div className="dq-flex dq-items-center dq-gap-sm">
                      <Badge variant="secondary" className="dq-badge">
                        {cluster.size} records
                      </Badge>
                      <span className="dq-text-sm dq-text-gray">
                        {cluster.percentage.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  
                  <button
                    className="dq-flex dq-items-center dq-gap-xs dq-text-sm dq-text-primary"
                    onClick={() => setExpandedCluster(isExpanded ? null : cluster.cluster_id)}
                  >
                    <span>View characteristics</span>
                    <ChevronRight className={`w-3 h-3 dq-transition ${isExpanded ? 'rotate-90' : ''}`} />
                  </button>
                  
                  {isExpanded && (
                    <div className="dq-mt-sm dq-grid dq-gap-xs">
                      {Object.entries(cluster.characteristics).slice(0, 5).map(([col, stats]: [string, any]) => (
                        <div key={col} className="dq-text-xs dq-text-gray">
                          <span className="dq-font-semibold">{col}:</span> μ={stats.mean.toFixed(2)}, σ={stats.std.toFixed(2)}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

// Predictive Analysis Component
const PredictiveAnalysis: React.FC<{ insights: any }> = ({ insights }) => {
  return (
    <div className="dq-grid dq-gap-lg">
      <div className="dq-card">
        <div className="dq-card-header">
          <h4 className="dq-card-title dq-text-lg dq-flex dq-items-center dq-gap-sm">
            <TrendingUp className="w-5 h-5" />
            <span>Predictive Insights</span>
          </h4>
        </div>
        <div className="dq-card-body">
          <div className="dq-alert dq-alert-info dq-mb-lg">
            <Info className="h-4 w-4" />
            <span className="dq-text-sm">
              Based on the ML analysis, here are predictive insights for your data:
            </span>
          </div>
          
          <div className="dq-grid dq-gap-md">
            {/* Data Quality Prediction */}
            <div className="dq-p-md" style={{
              background: 'rgba(59, 130, 246, 0.05)',
              borderRadius: 'var(--radius-lg)',
              borderLeft: '4px solid var(--color-info)'
            }}>
              <h5 className="dq-font-semibold dq-mb-sm">Data Quality Trend</h5>
              <p className="dq-text-sm dq-text-gray">
                Based on detected patterns, data quality is expected to remain stable 
                with potential improvements in completeness if current trends continue.
              </p>
            </div>
            
            {/* Anomaly Prediction */}
            {insights.anomalies && Object.keys(insights.anomalies).length > 0 && (
              <div className="dq-p-md" style={{
                background: 'rgba(245, 158, 11, 0.05)',
                borderRadius: 'var(--radius-lg)',
                borderLeft: '4px solid var(--color-warning)'
              }}>
                <h5 className="dq-font-semibold dq-mb-sm">Anomaly Forecast</h5>
                <p className="dq-text-sm dq-text-gray">
                  Current anomaly rate suggests {Object.keys(insights.anomalies).length} columns 
                  require monitoring. Implement automated detection to prevent quality degradation.
                </p>
              </div>
            )}
            
            {/* Pattern Evolution */}
            {insights.patterns && Object.keys(insights.patterns).length > 0 && (
              <div className="dq-p-md" style={{
                background: 'rgba(139, 92, 246, 0.05)',
                borderRadius: 'var(--radius-lg)',
                borderLeft: '4px solid var(--color-primary)'
              }}>
                <h5 className="dq-font-semibold dq-mb-sm">Pattern Evolution</h5>
                <p className="dq-text-sm dq-text-gray">
                  Discovered patterns indicate structured data entry. Consider implementing 
                  validation rules based on the top {Object.keys(insights.patterns).length} patterns.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};