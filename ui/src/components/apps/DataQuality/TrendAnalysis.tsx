import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { TrendingUp, TrendingDown, AlertTriangle, Calendar } from 'lucide-react';

interface TrendAnalysisProps {
  dataSource: any;
}

export const TrendAnalysis: React.FC<TrendAnalysisProps> = ({ dataSource }) => {
  const [trends, setTrends] = useState<any>({
    overallTrend: 'improving',
    qualityHistory: [
      { date: '2024-01-01', score: 75, completeness: 80, validity: 70, consistency: 75 },
      { date: '2024-01-15', score: 78, completeness: 82, validity: 73, consistency: 77 },
      { date: '2024-02-01', score: 82, completeness: 85, validity: 78, consistency: 81 },
      { date: '2024-02-15', score: 85, completeness: 88, validity: 82, consistency: 84 },
      { date: '2024-03-01', score: 88, completeness: 90, validity: 85, consistency: 87 },
      { date: '2024-03-15', score: 92.5, completeness: 95.2, validity: 93.8, consistency: 91.3 }
    ],
    insights: [
      { type: 'improvement', metric: 'completeness', change: '+15.2%', period: '3 months' },
      { type: 'improvement', metric: 'validity', change: '+23.8%', period: '3 months' },
      { type: 'stable', metric: 'consistency', change: '+16.3%', period: '3 months' }
    ],
    predictions: {
      nextMonth: { score: 94.5, confidence: 85 },
      threeMonths: { score: 96.8, confidence: 72 }
    }
  });

  useEffect(() => {
    // Simulate loading trends for the selected data source
    if (dataSource) {
      // In real implementation, fetch trends from API
    }
  }, [dataSource]);

  const getTrendIcon = (trend: string) => {
    return trend === 'improving' ? TrendingUp : TrendingDown;
  };

  const getTrendColor = (type: string) => {
    switch (type) {
      case 'improvement': return 'text-green-600';
      case 'decline': return 'text-red-600';
      default: return 'text-blue-600';
    }
  };

  return (
    <div className="dq-grid dq-gap-lg">
      {/* Overall Trend Summary */}
      <Card className="dq-card">
        <CardHeader className="dq-card-header">
          <CardTitle className="dq-card-title dq-flex dq-items-center dq-gap-sm">
            <TrendingUp className="w-5 h-5 dq-text-primary" />
            Quality Trend Analysis
          </CardTitle>
          <p className="dq-text-sm dq-text-gray">Historical data quality trends and predictions</p>
        </CardHeader>
        <CardContent>
          <div className="dq-flex dq-items-center dq-justify-between dq-mb-lg">
            <div>
              <p className="dq-text-sm dq-text-gray dq-mb-sm">Overall Trend</p>
              <div className="dq-flex dq-items-center dq-gap-sm">
                <TrendingUp className="w-8 h-8 text-green-600" />
                <span className="dq-text-2xl dq-font-bold dq-text-success">Improving</span>
              </div>
            </div>
            <div className="dq-text-right">
              <p className="dq-text-sm dq-text-gray dq-mb-sm">Current Score</p>
              <span className="dq-text-3xl dq-font-bold">92.5%</span>
            </div>
          </div>

          {/* Quality Score Chart */}
          <div className="dq-chart-container dq-mt-lg">
            <div className="dq-chart-wrapper" style={{ height: '300px', background: '#f9fafb', borderRadius: 'var(--radius-lg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <p className="dq-text-gray">Quality Score Trend Chart</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      <Card className="dq-card">
        <CardHeader className="dq-card-header">
          <CardTitle className="dq-card-title">Key Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="dq-grid dq-gap-md">
            {trends.insights.map((insight: any, index: number) => (
              <div key={index} className="dq-alert dq-alert-info">
                <div className="dq-flex dq-items-center dq-justify-between dq-w-full">
                  <div>
                    <p className="dq-font-semibold capitalize">{insight.metric}</p>
                    <p className="dq-text-sm dq-text-gray">{insight.period}</p>
                  </div>
                  <Badge className={`dq-badge ${insight.type === 'improvement' ? 'dq-badge-success' : 'dq-badge-info'}`}>
                    {insight.change}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Predictions */}
      <Card className="dq-card">
        <CardHeader className="dq-card-header">
          <CardTitle className="dq-card-title dq-flex dq-items-center dq-gap-sm">
            <Calendar className="w-5 h-5 dq-text-primary" />
            Quality Predictions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="dq-grid dq-grid-cols-2 dq-gap-lg">
            <div className="dq-text-center dq-p-lg" style={{ background: '#f3f4f6', borderRadius: 'var(--radius-lg)' }}>
              <p className="dq-text-sm dq-text-gray dq-mb-sm">Next Month</p>
              <p className="dq-text-2xl dq-font-bold dq-mb-sm">{trends.predictions.nextMonth.score}%</p>
              <Badge className="dq-badge dq-badge-info">
                {trends.predictions.nextMonth.confidence}% confidence
              </Badge>
            </div>
            <div className="dq-text-center dq-p-lg" style={{ background: '#f3f4f6', borderRadius: 'var(--radius-lg)' }}>
              <p className="dq-text-sm dq-text-gray dq-mb-sm">3 Months</p>
              <p className="dq-text-2xl dq-font-bold dq-mb-sm">{trends.predictions.threeMonths.score}%</p>
              <Badge className="dq-badge dq-badge-info">
                {trends.predictions.threeMonths.confidence}% confidence
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Metrics Trend */}
      <Card className="dq-card">
        <CardHeader className="dq-card-header">
          <CardTitle className="dq-card-title">Metrics Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="dq-table-container">
            <table className="dq-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Overall Score</th>
                  <th>Completeness</th>
                  <th>Validity</th>
                  <th>Consistency</th>
                </tr>
              </thead>
              <tbody>
                {trends.qualityHistory.slice(-5).reverse().map((record: any, index: number) => (
                  <tr key={index}>
                    <td>{new Date(record.date).toLocaleDateString()}</td>
                    <td className="dq-font-semibold">{record.score}%</td>
                    <td>{record.completeness}%</td>
                    <td>{record.validity}%</td>
                    <td>{record.consistency}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};