import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs';
import { Progress } from '../../ui/progress';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { 
  BarChart, 
  PieChart, 
  LineChart,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Info,
  Download,
  Eye,
  Filter
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../../ui/tooltip';

interface ProfileResultsProps {
  data: any;
}

export const ProfileResults: React.FC<ProfileResultsProps> = ({ data }) => {
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'detailed'>('overview');
  
  const getQualityScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getQualityBadge = (score: number) => {
    if (score >= 90) return { label: 'Excellent', variant: 'success' as const };
    if (score >= 70) return { label: 'Good', variant: 'warning' as const };
    if (score >= 50) return { label: 'Fair', variant: 'secondary' as const };
    return { label: 'Poor', variant: 'destructive' as const };
  };
  
  const overallScore = data.overall_quality_score || 0;
  const qualityBadge = getQualityBadge(overallScore);
  
  return (
    <div className="dq-container">
      {/* Overall Summary */}
      <div className="dq-card dq-mb-lg">
        <div className="dq-card-header">
          <div className="dq-flex dq-justify-between dq-items-center dq-flex-wrap dq-gap-md">
            <h3 className="dq-card-title">Profile Summary</h3>
            <div className="dq-flex dq-gap-sm">
              <button
                className="dq-btn dq-btn-secondary dq-btn-sm"
                onClick={() => setViewMode(viewMode === 'overview' ? 'detailed' : 'overview')}
              >
                <Eye className="w-4 h-4" />
                {viewMode === 'overview' ? 'Detailed View' : 'Overview'}
              </button>
              <button className="dq-btn dq-btn-secondary dq-btn-sm">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>
        <div className="dq-card-body">
          <div className="dq-profile-summary">
            {/* Overall Quality Score */}
            <div className="dq-metric-card">
              <div className={`dq-metric-value ${getQualityScoreColor(overallScore)}`}>
                {overallScore.toFixed(1)}%
              </div>
              <div className="dq-metric-label">Overall Quality</div>
              <Badge variant={qualityBadge.variant} className="dq-badge dq-mt-sm">
                {qualityBadge.label}
              </Badge>
            </div>
            
            {/* Key Metrics */}
            <div className="dq-metric-card">
              <div className="dq-metric-value">{data.total_rows?.toLocaleString() || '0'}</div>
              <div className="dq-metric-label">Total Records</div>
            </div>
            <div className="dq-metric-card">
              <div className="dq-metric-value">{data.total_columns || '0'}</div>
              <div className="dq-metric-label">Total Columns</div>
            </div>
            <div className="dq-metric-card">
              <div className="dq-metric-value">{formatBytes(data.data_size_bytes || 0)}</div>
              <div className="dq-metric-label">Data Size</div>
            </div>
          </div>
          
          {/* Quality Dimensions */}
          <div className="dq-mt-lg">
            <h4 className="dq-text-sm dq-font-semibold dq-text-gray dq-mb-md">Quality Dimensions</h4>
            {Object.entries(data.quality_dimensions || {}).map(([dimension, score]: [string, any]) => (
              <div key={dimension} className="dq-mb-md">
                <div className="dq-flex dq-justify-between dq-text-sm dq-mb-sm">
                  <span className="dq-capitalize">{dimension.replace('_', ' ')}</span>
                  <span className={`dq-font-semibold ${getQualityScoreColor(score)}`}>{score.toFixed(1)}%</span>
                </div>
                <div className="dq-progress">
                  <div className="dq-progress-bar" style={{ width: `${score}%` }} />
                </div>
              </div>
            ))}
          </div>
          
          {/* Critical Issues */}
          {data.critical_issues && data.critical_issues.length > 0 && (
            <div className="dq-mt-lg">
              <h4 className="dq-text-sm dq-font-semibold dq-text-gray dq-mb-md">Critical Issues</h4>
              <div className="dq-grid dq-gap-sm">
                {data.critical_issues.slice(0, 3).map((issue: string, idx: number) => (
                  <div key={idx} className="dq-alert dq-alert-danger">
                    <AlertTriangle className="w-4 h-4" style={{ flexShrink: 0 }} />
                    <span className="dq-text-sm">{issue}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Column Profiles */}
      <div className="dq-card">
        <div className="dq-card-header">
          <h3 className="dq-card-title">Column Analysis</h3>
        </div>
        <div className="dq-card-body">
          <div className="dq-tabs">
            <div className="dq-tab-list dq-mb-lg">
              <button className="dq-tab active">Grid View</button>
              <button className="dq-tab">Detailed View</button>
              <button className="dq-tab">Correlations</button>
              <button className="dq-tab">Patterns</button>
            </div>
            
            <div className="dq-tab-content">
              {/* Grid View */}
              <div className="dq-grid dq-grid-cols-3 dq-gap-md">
                {data.column_profiles?.map((profile: any) => (
                  <ColumnCard
                    key={profile.column_name}
                    profile={profile}
                    onClick={() => setSelectedColumn(profile.column_name)}
                    isSelected={selectedColumn === profile.column_name}
                  />
                ))}
              </div>
            
              {/* Note: Tab switching logic would be implemented with state management */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  title: string;
  value: string;
  icon: React.ElementType;
  trend: 'up' | 'down' | null;
}> = ({ title, value, icon: Icon, trend }) => (
  <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
    <div className="flex items-center justify-between mb-2">
      <Icon className="w-5 h-5 text-muted-foreground" />
      {trend && (
        trend === 'up' ? 
          <TrendingUp className="w-4 h-4 text-green-500" /> :
          <TrendingDown className="w-4 h-4 text-red-500" />
      )}
    </div>
    <div className="text-2xl font-semibold">{value}</div>
    <div className="text-sm text-muted-foreground">{title}</div>
  </div>
);

// Column Card Component
const ColumnCard: React.FC<{
  profile: any;
  onClick: () => void;
  isSelected: boolean;
}> = ({ profile, onClick, isSelected }) => {
  const qualityScore = (
    profile.completeness_score * 0.4 +
    profile.validity_score * 0.3 +
    profile.consistency_score * 0.3
  ) * 100;
  
  return (
    <div 
      className={`dq-card dq-transition ${isSelected ? 'dq-source-card selected' : ''}`}
      style={{ cursor: 'pointer' }}
      onClick={onClick}
    >
      <div className="dq-flex dq-justify-between dq-items-start dq-mb-md">
        <div className="dq-flex-1" style={{ minWidth: 0 }}>
          <h4 className="dq-font-semibold dq-text-sm dq-truncate">{profile.column_name}</h4>
          <Badge variant="outline" className="dq-badge dq-mt-sm dq-text-xs">
            {profile.data_type}
          </Badge>
        </div>
        <div className={`dq-text-lg dq-font-bold ${getQualityScoreColor(qualityScore)}`}>
          {qualityScore.toFixed(0)}%
        </div>
      </div>
      
      <div className="dq-mt-md">
        <div className="dq-flex dq-justify-between dq-text-xs dq-mb-sm">
          <span className="dq-text-gray">Completeness</span>
          <span>{(profile.completeness_score * 100).toFixed(1)}%</span>
        </div>
        <div className="dq-progress" style={{ height: '4px' }}>
          <div className="dq-progress-bar" style={{ width: `${profile.completeness_score * 100}%` }} />
        </div>
        
        <div className="dq-flex dq-justify-between dq-text-xs dq-mt-sm">
          <span className="dq-text-gray">Unique values</span>
          <span>{profile.unique_count?.toLocaleString() || 0}</span>
        </div>
        
        {profile.quality_issues && profile.quality_issues.length > 0 && (
          <div className="dq-flex dq-items-center dq-gap-xs dq-text-xs dq-text-danger dq-mt-sm">
            <AlertTriangle className="w-3 h-3" />
            <span>{profile.quality_issues.length} issues</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Column Detail View Component
const ColumnDetailView: React.FC<{ profile: any }> = ({ profile }) => {
  if (!profile) return null;
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-2">
              {profile.min_value !== undefined && (
                <>
                  <StatRow label="Min" value={profile.min_value} />
                  <StatRow label="Max" value={profile.max_value} />
                  <StatRow label="Mean" value={profile.mean?.toFixed(2)} />
                  <StatRow label="Median" value={profile.median?.toFixed(2)} />
                  <StatRow label="Std Dev" value={profile.std_dev?.toFixed(2)} />
                </>
              )}
              {profile.min_length !== undefined && (
                <>
                  <StatRow label="Min Length" value={profile.min_length} />
                  <StatRow label="Max Length" value={profile.max_length} />
                  <StatRow label="Avg Length" value={profile.avg_length?.toFixed(1)} />
                </>
              )}
              <StatRow label="Null Count" value={profile.null_count} />
              <StatRow label="Unique Count" value={profile.unique_count} />
              <StatRow label="Duplicate Count" value={profile.duplicate_count} />
            </dl>
          </CardContent>
        </Card>
        
        {/* Value Distribution */}
        {profile.top_values && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Top Values</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {profile.top_values.slice(0, 10).map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="truncate max-w-[200px]">{item.value}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-muted-foreground">{item.count}</span>
                      <span className="text-xs text-muted-foreground">
                        ({item.percentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
      
      {/* Patterns */}
      {profile.common_patterns && profile.common_patterns.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Detected Patterns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {profile.common_patterns.map((pattern: any, idx: number) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <code className="text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                      {pattern.pattern}
                    </code>
                    <span className="text-sm text-muted-foreground">
                      {pattern.count} ({pattern.percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Example: {pattern.example}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Stat Row Component
const StatRow: React.FC<{ label: string; value: any }> = ({ label, value }) => (
  <div className="flex justify-between text-sm">
    <dt className="text-muted-foreground">{label}</dt>
    <dd className="font-medium">{value?.toLocaleString() || 'N/A'}</dd>
  </div>
);

// Correlation Matrix Component
const CorrelationMatrix: React.FC<{ correlations: any }> = ({ correlations }) => {
  if (!correlations || Object.keys(correlations).length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No correlations found in the data
      </div>
    );
  }
  
  // Simplified correlation display
  const significantCorrelations: any[] = [];
  Object.entries(correlations).forEach(([col1, corrDict]: [string, any]) => {
    Object.entries(corrDict).forEach(([col2, value]: [string, any]) => {
      if (Math.abs(value) > 0.5 && col1 < col2) {
        significantCorrelations.push({ col1, col2, value });
      }
    });
  });
  
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Significant Correlations</h3>
      {significantCorrelations.length > 0 ? (
        <div className="space-y-2">
          {significantCorrelations.map((corr, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="font-medium">{corr.col1}</span>
                <span className="text-muted-foreground">↔</span>
                <span className="font-medium">{corr.col2}</span>
              </div>
              <div className={`font-semibold ${corr.value > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {corr.value.toFixed(3)}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground">No significant correlations found (threshold: |r| {'>'} 0.5)</p>
      )}
    </div>
  );
};

// Pattern Analysis Component
const PatternAnalysis: React.FC<{ patterns: any }> = ({ patterns }) => {
  if (!patterns) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No pattern analysis available
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {Object.entries(patterns).map(([column, columnPatterns]: [string, any]) => (
        <Card key={column}>
          <CardHeader>
            <CardTitle className="text-lg">{column}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {columnPatterns.map((pattern: any, idx: number) => (
                <div key={idx} className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="outline">{pattern.pattern}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {pattern.count} occurrences
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Confidence: {(pattern.confidence * 100).toFixed(1)}%
                  </div>
                  {pattern.examples && (
                    <div className="mt-2 text-xs">
                      Examples: {pattern.examples.slice(0, 3).join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

// Utility function
const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Helper function for score color
const getQualityScoreColor = (score: number) => {
  if (score >= 90) return 'dq-text-success';
  if (score >= 70) return 'dq-text-warning';
  return 'dq-text-danger';
};