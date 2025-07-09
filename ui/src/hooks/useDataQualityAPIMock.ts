import { useState, useCallback } from 'react';

// Mock implementation for demonstration
export const useDataQualityAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Mock profile data
  const mockProfileData = {
    overall_quality_score: 92.5,
    total_rows: 10000,
    total_columns: 7,
    data_size_bytes: 2457600,
    quality_dimensions: {
      completeness: 95.2,
      validity: 93.8,
      uniqueness: 98.1,
      consistency: 91.5,
      timeliness: 85.3
    },
    critical_issues: [
      "5 columns have missing values above 5% threshold",
      "Date format inconsistencies detected in 'registration_date' column",
      "Potential duplicates found in customer_id column"
    ],
    column_profiles: [
      {
        column_name: "customer_id",
        data_type: "string",
        null_count: 0,
        null_percentage: 0,
        unique_count: 10000,
        duplicate_count: 0,
        completeness_score: 1.0,
        validity_score: 1.0,
        consistency_score: 1.0,
        top_values: [
          { value: "CUST001", count: 1, percentage: 0.01 },
          { value: "CUST002", count: 1, percentage: 0.01 }
        ],
        quality_issues: []
      },
      {
        column_name: "email",
        data_type: "string",
        null_count: 250,
        null_percentage: 2.5,
        unique_count: 9750,
        duplicate_count: 0,
        completeness_score: 0.975,
        validity_score: 0.95,
        consistency_score: 0.98,
        common_patterns: [
          { pattern: "[a-z]+[0-9]*@[a-z]+\\.[a-z]+", count: 9500, percentage: 95.0, confidence: 0.95 }
        ],
        quality_issues: ["2.5% missing values"]
      },
      {
        column_name: "age",
        data_type: "integer",
        null_count: 50,
        null_percentage: 0.5,
        unique_count: 62,
        min_value: 18,
        max_value: 80,
        mean: 42.5,
        median: 41,
        std_dev: 15.3,
        completeness_score: 0.995,
        validity_score: 0.98,
        consistency_score: 1.0,
        quality_issues: []
      }
    ],
    ml_analysis: {
      anomalies: {
        age: [{
          algorithm: "Isolation Forest",
          anomaly_indices: [156, 892, 3421],
          confidence: 0.85,
          contamination_rate: 0.003,
          explanation: "3 records with age values significantly different from the distribution"
        }],
        total_spent: [{
          algorithm: "DBSCAN",
          anomaly_indices: [45, 231, 567, 891],
          confidence: 0.78,
          contamination_rate: 0.004,
          explanation: "4 customers with unusually high spending patterns"
        }]
      },
      patterns: {
        email: [
          { pattern: "^[a-z]+[0-9]+@gmail\\.com$", count: 3200, confidence: 0.95, examples: ["john123@gmail.com"] },
          { pattern: "^[a-z]+\\.[a-z]+@company\\.com$", count: 2100, confidence: 0.93, examples: ["jane.doe@company.com"] }
        ]
      },
      correlations: {
        linear: {
          age: { total_spent: 0.42, registration_date: -0.15 },
          total_spent: { age: 0.42, is_active: 0.68 }
        }
      },
      clusters: {
        algorithm: "KMeans",
        optimal_clusters: 4,
        silhouette_score: 0.72,
        clusters: [
          {
            cluster_id: 0,
            size: 3500,
            percentage: 35,
            characteristics: { age: { mean: 35, std: 8 }, total_spent: { mean: 250, std: 100 } }
          },
          {
            cluster_id: 1,
            size: 2800,
            percentage: 28,
            characteristics: { age: { mean: 45, std: 10 }, total_spent: { mean: 500, std: 200 } }
          }
        ]
      },
      advanced_insights: [
        {
          insight_type: "anomaly",
          severity: "high",
          affected_columns: ["total_spent", "age"],
          description: "Correlation between age and spending shows unusual pattern for younger customers",
          recommendation: "Investigate young high-spenders for potential fraud or data quality issues",
          ml_confidence: 0.82,
          supporting_evidence: {}
        }
      ]
    }
  };
  
  const profileDataSource = useCallback(async (dataSource: any, options: any) => {
    setLoading(true);
    setError(null);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setLoading(false);
    return mockProfileData;
  }, []);
  
  const generateQualityRules = useCallback(async (profileData: any, options: any) => {
    setLoading(true);
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockRules = [
      {
        rule_id: "rule_email_completeness",
        rule_name: "Email Completeness Check",
        rule_type: "completeness",
        dimension: "completeness",
        column_name: "email",
        description: "Ensure email field has minimal null values",
        sql_expression: "SELECT COUNT(*) FROM customers WHERE email IS NULL",
        pyspark_code: "df.filter(df['email'].isNull()).count()",
        python_code: "df['email'].isnull().sum()",
        threshold: 95.0,
        severity: "HIGH",
        enabled: true,
        business_context: "Email is required for customer communication"
      },
      {
        rule_id: "rule_age_validity",
        rule_name: "Age Range Validation",
        rule_type: "range_check",
        dimension: "validity",
        column_name: "age",
        description: "Validate age is within acceptable range",
        sql_expression: "SELECT COUNT(*) FROM customers WHERE age < 18 OR age > 100",
        pyspark_code: "df.filter((df['age'] < 18) | (df['age'] > 100)).count()",
        python_code: "df[(df['age'] < 18) | (df['age'] > 100)].shape[0]",
        threshold: 0,
        severity: "CRITICAL",
        enabled: true,
        business_context: "Age must be between 18 and 100"
      }
    ];
    
    setLoading(false);
    return mockRules;
  }, []);
  
  const executeQualityRules = useCallback(async (rules: any[], dataSource: any) => {
    setLoading(true);
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const results = {
      execution_time: new Date().toISOString(),
      total_rules: rules.length,
      passed_count: Math.floor(rules.length * 0.8),
      failed_count: Math.ceil(rules.length * 0.2),
      passed: Math.random() > 0.3,
      details: rules.map(rule => ({
        rule_id: rule.rule_id,
        rule_name: rule.rule_name,
        passed: Math.random() > 0.2,
        actual_value: Math.random() * 100,
        threshold: rule.threshold,
        message: `Rule ${rule.rule_name} ${Math.random() > 0.2 ? 'passed' : 'failed'}`
      }))
    };
    
    setLoading(false);
    return results;
  }, []);
  
  const getMLInsights = useCallback(async (dataSource: any) => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setLoading(false);
    return mockProfileData.ml_analysis;
  }, []);
  
  const startMonitoring = useCallback(async () => {
    return `session_${Date.now()}`;
  }, []);
  
  const stopMonitoring = useCallback(async () => {
    return true;
  }, []);
  
  const getCatalogData = useCallback(async () => {
    return {
      entries: [
        {
          id: "customers",
          name: "customers",
          type: "table",
          quality_score: 92,
          owner: "data-team",
          tags: ["pii", "master-data"]
        }
      ]
    };
  }, []);
  
  const connectWebSocket = useCallback((sessionId: string, onMessage: (data: any) => void) => {
    // Mock WebSocket
    const mockWs = {
      send: () => {},
      close: () => {},
      addEventListener: () => {},
      removeEventListener: () => {}
    };
    
    // Simulate periodic updates
    const interval = setInterval(() => {
      onMessage({
        type: 'metric',
        metric: {
          timestamp: new Date().toISOString(),
          completeness: 95 + Math.random() * 5,
          validity: 92 + Math.random() * 8,
          rowCount: Math.floor(10000 + Math.random() * 1000)
        }
      });
    }, 5000);
    
    return mockWs as any;
  }, []);
  
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
    updateCatalogEntry: async () => ({}),
    exportProfile: async () => true,
    connectWebSocket,
    generateSparkCode: async () => "# Generated Spark code",
    getDataLineage: async () => ({})
  };
};