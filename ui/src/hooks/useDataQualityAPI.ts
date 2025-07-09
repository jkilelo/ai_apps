import { useState, useCallback } from 'react';
import axios from 'axios';

// Temporary: Use mock implementation
export { useDataQualityAPI } from './useDataQualityAPIMock';

/* Original implementation commented out temporarily

interface ProfileOptions {
  includeML?: boolean;
  sampleSize?: number;
  columns?: string[];
  qualityDimensions?: string[];
}

interface QualityRule {
  rule_id: string;
  rule_name: string;
  rule_type: string;
  dimension: string;
  column_name: string;
  description: string;
  sql_expression: string;
  pyspark_code: string;
  python_code: string;
  threshold?: number;
  severity: string;
  enabled: boolean;
  business_context?: string;
  error_message?: string;
  suggested_action?: string;
}

interface DataSource {
  id: string;
  name: string;
  type: 'database' | 'file' | 'streaming' | 'api';
  connection: any;
}

export const useDataQualityAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';
  
  // Profile data source
  const profileDataSource = useCallback(async (
    dataSource: DataSource,
    options: ProfileOptions = {}
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/data-quality/profile`,
        {
          data_source: dataSource,
          options: {
            include_ml: options.includeML ?? true,
            sample_size: options.sampleSize,
            columns: options.columns,
            quality_dimensions: options.qualityDimensions || [
              'completeness',
              'validity',
              'uniqueness',
              'consistency',
              'timeliness'
            ]
          }
        }
      );
      
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to profile data';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Generate quality rules based on profile
  const generateQualityRules = useCallback(async (
    profileData: any,
    options: { autoDetect?: boolean; sensitivity?: string } = {}
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/data-quality/rules/generate`,
        {
          profile_data: profileData,
          options: {
            auto_detect: options.autoDetect ?? true,
            sensitivity: options.sensitivity || 'medium'
          }
        }
      );
      
      return response.data.rules;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to generate rules';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Execute quality rules
  const executeQualityRules = useCallback(async (
    rules: QualityRule[],
    dataSource: DataSource
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/data-quality/rules/execute`,
        {
          rules: rules.filter(r => r.enabled),
          data_source: dataSource
        }
      );
      
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to execute rules';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Get ML insights
  const getMLInsights = useCallback(async (
    dataSource: DataSource,
    algorithms: string[] = ['isolation_forest', 'dbscan', 'pca']
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/data-quality/ml-insights`,
        {
          data_source: dataSource,
          algorithms
        }
      );
      
      return response.data.insights;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to get ML insights';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Start real-time monitoring
  const startMonitoring = useCallback(async (
    dataSource: DataSource,
    rules: QualityRule[],
    interval: number = 30
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/data-quality/monitor/start`,
        {
          data_source: dataSource,
          rules: rules.filter(r => r.enabled),
          interval_seconds: interval
        }
      );
      
      return response.data.session_id;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to start monitoring';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Stop real-time monitoring
  const stopMonitoring = useCallback(async (sessionId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      await axios.post(
        `${API_BASE_URL}/api/data-quality/monitor/stop`,
        { session_id: sessionId }
      );
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to stop monitoring';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Get catalog data
  const getCatalogData = useCallback(async (
    filters?: { tags?: string[]; owner?: string; search?: string }
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/data-quality/catalog`,
        { params: filters }
      );
      
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to get catalog data';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Update catalog entry
  const updateCatalogEntry = useCallback(async (
    entryId: string,
    updates: { tags?: string[]; description?: string; owner?: string }
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.patch(
        `${API_BASE_URL}/api/data-quality/catalog/${entryId}`,
        updates
      );
      
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to update catalog';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Export profile results
  const exportProfile = useCallback(async (
    profileData: any,
    format: 'json' | 'csv' | 'pdf' | 'excel' = 'json'
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/data-quality/export`,
        {
          profile_data: profileData,
          format
        },
        {
          responseType: 'blob'
        }
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `data-profile-${Date.now()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to export profile';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback((
    sessionId: string,
    onMessage: (data: any) => void,
    onError?: (error: any) => void
  ) => {
    const wsUrl = API_BASE_URL.replace(/^http/, 'ws');
    const ws = new WebSocket(`${wsUrl}/ws/data-quality/${sessionId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected for data quality monitoring');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    return ws;
  }, [API_BASE_URL]);
  
  // Generate Spark code for profiling
  const generateSparkCode = useCallback(async (
    tableName: string,
    schema: any,
    profilingConfig?: any
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/data-quality/spark/generate`,
        {
          table_name: tableName,
          schema,
          profiling_config: profilingConfig
        }
      );
      
      return response.data.code;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to generate Spark code';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  // Get data lineage
  const getDataLineage = useCallback(async (
    datasetId: string,
    depth: number = 2
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/data-quality/lineage/${datasetId}`,
        { params: { depth } }
      );
      
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to get lineage';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);
  
  return {
    loading,
    error,
    profileDataSource,
    generateQualityRules,
    executeQualityRules,
    getMLInsights,
    startMonitoring,
    stopMonitoring,
    getCatalogData,
    updateCatalogEntry,
    exportProfile,
    connectWebSocket,
    generateSparkCode,
    getDataLineage
  };
};
*/