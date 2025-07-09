import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  PlayCircle,
  PauseCircle,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Zap,
  Clock,
  RefreshCw
} from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useDataQualityAPI } from '@/hooks/useDataQualityAPI';
import { DataQualityWebSocket } from '@/services/websocket';

interface RealTimeMonitorProps {
  dataSource: any;
}

export const RealTimeMonitor: React.FC<RealTimeMonitorProps> = ({ dataSource }) => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [metrics, setMetrics] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [updateInterval, setUpdateInterval] = useState(30); // seconds
  const [enabledRules, setEnabledRules] = useState({
    completeness: true,
    validity: true,
    freshness: true,
    anomalies: true
  });
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<DataQualityWebSocket | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  
  const { startMonitoring: startMonitoringAPI, stopMonitoring: stopMonitoringAPI, connectWebSocket } = useDataQualityAPI();
  
  useEffect(() => {
    if (isMonitoring) {
      startMonitoring();
    } else {
      stopMonitoring();
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, [isMonitoring, updateInterval]);
  
  const startMonitoring = async () => {
    try {
      // Start monitoring session via API
      const sessionId = await startMonitoringAPI(
        dataSource,
        Object.entries(enabledRules)
          .filter(([_, enabled]) => enabled)
          .map(([type]) => ({ 
            rule_id: type, 
            rule_name: type,
            rule_type: type,
            dimension: type,
            column_name: '*',
            description: `Monitor ${type}`,
            sql_expression: '',
            pyspark_code: '',
            python_code: '',
            severity: 'MEDIUM',
            enabled: true
          })),
        updateInterval
      );
      
      sessionIdRef.current = sessionId;
      
      // Connect WebSocket for real-time updates
      const ws = connectWebSocket(sessionId, (data) => {
        if (data.type === 'metric') {
          setMetrics(prev => [...prev.slice(-19), data.metric]);
        } else if (data.type === 'alert') {
          setAlerts(prev => [data.alert, ...prev].slice(0, 10));
        }
      });
      
      wsRef.current = ws;
      
      // Initial fetch
      fetchMetrics();
      
      // Set up fallback interval
      intervalRef.current = setInterval(() => {
        fetchMetrics();
      }, updateInterval * 1000);
    } catch (error) {
      console.error('Failed to start monitoring:', error);
      setIsMonitoring(false);
    }
  };
  
  const stopMonitoring = async () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }
    
    if (sessionIdRef.current) {
      try {
        await stopMonitoringAPI(sessionIdRef.current);
      } catch (error) {
        console.error('Failed to stop monitoring:', error);
      }
      sessionIdRef.current = null;
    }
  };
  
  const fetchMetrics = async () => {
    // Simulate fetching real-time metrics
    const newMetric = {
      timestamp: new Date().toISOString(),
      completeness: 95 + Math.random() * 5,
      validity: 92 + Math.random() * 8,
      uniqueness: 98 + Math.random() * 2,
      consistency: 94 + Math.random() * 6,
      rowCount: Math.floor(100000 + Math.random() * 10000),
      anomalyCount: Math.floor(Math.random() * 50),
      processingTime: Math.floor(100 + Math.random() * 500)
    };
    
    setMetrics(prev => [...prev.slice(-19), newMetric]);
    
    // Check for alerts
    checkAlerts(newMetric);
  };
  
  const checkAlerts = (metric: any) => {
    const newAlerts: any[] = [];
    
    if (enabledRules.completeness && metric.completeness < 95) {
      newAlerts.push({
        type: 'completeness',
        severity: 'warning',
        message: `Completeness dropped to ${metric.completeness.toFixed(1)}%`,
        timestamp: metric.timestamp
      });
    }
    
    if (enabledRules.validity && metric.validity < 90) {
      newAlerts.push({
        type: 'validity',
        severity: 'error',
        message: `Validity below threshold: ${metric.validity.toFixed(1)}%`,
        timestamp: metric.timestamp
      });
    }
    
    if (enabledRules.anomalies && metric.anomalyCount > 30) {
      newAlerts.push({
        type: 'anomaly',
        severity: 'warning',
        message: `High anomaly count detected: ${metric.anomalyCount}`,
        timestamp: metric.timestamp
      });
    }
    
    if (newAlerts.length > 0) {
      setAlerts(prev => [...newAlerts, ...prev].slice(0, 10));
    }
  };
  
  const getLatestMetric = () => metrics[metrics.length - 1];
  const getPreviousMetric = () => metrics[metrics.length - 2];
  
  const getTrend = (current: number, previous: number) => {
    if (!previous) return null;
    return current > previous ? 'up' : current < previous ? 'down' : 'stable';
  };
  
  const latestMetric = getLatestMetric();
  const previousMetric = getPreviousMetric();
  
  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Real-Time Quality Monitor</span>
            </CardTitle>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Label>Interval:</Label>
                <Select 
                  value={updateInterval.toString()} 
                  onValueChange={(v) => setUpdateInterval(parseInt(v))}
                >
                  <SelectTrigger className="w-24">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5">5s</SelectItem>
                    <SelectItem value="10">10s</SelectItem>
                    <SelectItem value="30">30s</SelectItem>
                    <SelectItem value="60">1m</SelectItem>
                    <SelectItem value="300">5m</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => setIsMonitoring(!isMonitoring)}
                variant={isMonitoring ? "destructive" : "default"}
              >
                {isMonitoring ? (
                  <>
                    <PauseCircle className="w-4 h-4 mr-2" />
                    Stop
                  </>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4 mr-2" />
                    Start
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">Completeness</span>
              <Switch 
                checked={enabledRules.completeness}
                onCheckedChange={(checked) => 
                  setEnabledRules({...enabledRules, completeness: checked})
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Validity</span>
              <Switch 
                checked={enabledRules.validity}
                onCheckedChange={(checked) => 
                  setEnabledRules({...enabledRules, validity: checked})
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Freshness</span>
              <Switch 
                checked={enabledRules.freshness}
                onCheckedChange={(checked) => 
                  setEnabledRules({...enabledRules, freshness: checked})
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Anomalies</span>
              <Switch 
                checked={enabledRules.anomalies}
                onCheckedChange={(checked) => 
                  setEnabledRules({...enabledRules, anomalies: checked})
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Live Metrics */}
      {latestMetric && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricCard
            title="Completeness"
            value={latestMetric.completeness}
            unit="%"
            trend={getTrend(latestMetric.completeness, previousMetric?.completeness)}
            threshold={95}
            format="percentage"
          />
          <MetricCard
            title="Validity"
            value={latestMetric.validity}
            unit="%"
            trend={getTrend(latestMetric.validity, previousMetric?.validity)}
            threshold={90}
            format="percentage"
          />
          <MetricCard
            title="Row Count"
            value={latestMetric.rowCount}
            unit=""
            trend={getTrend(latestMetric.rowCount, previousMetric?.rowCount)}
            format="number"
          />
          <MetricCard
            title="Anomalies"
            value={latestMetric.anomalyCount}
            unit=""
            trend={getTrend(latestMetric.anomalyCount, previousMetric?.anomalyCount)}
            threshold={30}
            thresholdType="max"
            format="number"
          />
        </div>
      )}
      
      {/* Quality Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quality Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-48 relative">
            {metrics.length > 1 ? (
              <QualityTrendChart metrics={metrics} />
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                {isMonitoring ? 'Collecting data...' : 'Start monitoring to see trends'}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      {/* Alerts */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5" />
              <span>Recent Alerts</span>
            </CardTitle>
            {alerts.length > 0 && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setAlerts([])}
              >
                Clear All
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {alerts.length > 0 ? (
            <div className="space-y-2">
              {alerts.map((alert, idx) => (
                <Alert 
                  key={idx}
                  className={alert.severity === 'error' ? 'border-red-500' : 'border-yellow-500'}
                >
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="flex items-center justify-between">
                      <span>{alert.message}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-4">
              No alerts triggered
            </p>
          )}
        </CardContent>
      </Card>
      
      {/* Performance Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Performance Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">
                {isMonitoring ? (
                  <span className="flex items-center justify-center">
                    <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
                    Live
                  </span>
                ) : (
                  'Stopped'
                )}
              </div>
              <p className="text-sm text-muted-foreground">Status</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{metrics.length}</div>
              <p className="text-sm text-muted-foreground">Data Points</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{alerts.length}</div>
              <p className="text-sm text-muted-foreground">Alerts</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {latestMetric ? `${latestMetric.processingTime}ms` : '-'}
              </div>
              <p className="text-sm text-muted-foreground">Latency</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  title: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable' | null;
  threshold?: number;
  thresholdType?: 'min' | 'max';
  format: 'percentage' | 'number';
}> = ({ title, value, unit, trend, threshold, thresholdType = 'min', format }) => {
  const isAboveThreshold = threshold ? 
    (thresholdType === 'min' ? value >= threshold : value <= threshold) : true;
  
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : null;
  
  return (
    <Card className={!isAboveThreshold ? 'border-red-500' : ''}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-muted-foreground">{title}</span>
          {TrendIcon && (
            <TrendIcon className={`w-4 h-4 ${
              trend === 'up' ? 'text-green-500' : 'text-red-500'
            }`} />
          )}
        </div>
        <div className="text-2xl font-bold">
          {format === 'percentage' ? value.toFixed(1) : value.toLocaleString()}
          {unit}
        </div>
        {threshold && (
          <div className="mt-2">
            <Progress 
              value={format === 'percentage' ? value : (value / threshold) * 100} 
              className="h-1"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Threshold: {threshold}{unit}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Quality Trend Chart Component (simplified)
const QualityTrendChart: React.FC<{ metrics: any[] }> = ({ metrics }) => {
  const maxValue = 100;
  const chartHeight = 192; // h-48 = 12rem = 192px
  const chartWidth = 100;
  const pointWidth = chartWidth / Math.max(metrics.length - 1, 1);
  
  const getY = (value: number) => chartHeight - (value / maxValue) * chartHeight;
  
  const completenessPath = metrics
    .map((m, i) => `${i * pointWidth},${getY(m.completeness)}`)
    .join(' L');
    
  const validityPath = metrics
    .map((m, i) => `${i * pointWidth},${getY(m.validity)}`)
    .join(' L');
  
  return (
    <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-full">
      {/* Grid lines */}
      {[0, 25, 50, 75, 100].map(val => (
        <line
          key={val}
          x1="0"
          y1={getY(val)}
          x2={chartWidth}
          y2={getY(val)}
          stroke="currentColor"
          strokeOpacity="0.1"
          strokeDasharray="2 2"
        />
      ))}
      
      {/* Completeness line */}
      <polyline
        points={`M${completenessPath}`}
        fill="none"
        stroke="rgb(34, 197, 94)"
        strokeWidth="2"
      />
      
      {/* Validity line */}
      <polyline
        points={`M${validityPath}`}
        fill="none"
        stroke="rgb(59, 130, 246)"
        strokeWidth="2"
      />
      
      {/* Legend */}
      <g transform={`translate(${chartWidth - 60}, 10)`}>
        <rect x="0" y="0" width="12" height="2" fill="rgb(34, 197, 94)" />
        <text x="16" y="4" fontSize="10" fill="currentColor">Completeness</text>
        
        <rect x="0" y="12" width="12" height="2" fill="rgb(59, 130, 246)" />
        <text x="16" y="16" fontSize="10" fill="currentColor">Validity</text>
      </g>
    </svg>
  );
};