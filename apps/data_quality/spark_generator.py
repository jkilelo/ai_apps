"""
Advanced Spark Code Generator for Distributed Data Profiling
Generates optimized PySpark code for large-scale data profiling and quality checks
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re


class SparkProfilerGenerator:
    """Generates optimized PySpark code for distributed data profiling"""
    
    def __init__(self):
        self.spark_functions = {
            'statistical': ['min', 'max', 'mean', 'stddev', 'variance', 'skewness', 'kurtosis'],
            'quantiles': ['approx_quantile', 'percentile_approx'],
            'counts': ['count', 'countDistinct', 'approx_count_distinct'],
            'string': ['length', 'lower', 'upper', 'trim', 'regexp_extract'],
            'date': ['year', 'month', 'dayofmonth', 'hour', 'minute', 'second'],
            'null': ['isNull', 'isNotNull', 'coalesce', 'when']
        }
        
    def generate_profiling_job(self, 
                             table_name: str,
                             schema: Dict[str, Any],
                             profiling_config: Optional[Dict] = None) -> str:
        """Generate complete PySpark job for data profiling"""
        
        config = profiling_config or self._default_profiling_config()
        
        code_parts = [
            self._generate_imports(),
            self._generate_spark_session(),
            self._generate_udf_definitions(),
            self._generate_data_loader(table_name, schema),
            self._generate_basic_statistics(schema, config),
            self._generate_pattern_detection(schema, config),
            self._generate_anomaly_detection(schema, config),
            self._generate_correlation_analysis(schema, config),
            self._generate_data_quality_metrics(schema, config),
            self._generate_output_writer(config)
        ]
        
        return "\n\n".join(code_parts)
    
    def _default_profiling_config(self) -> Dict:
        """Default configuration for profiling"""
        return {
            'sample_size': 1000000,
            'enable_patterns': True,
            'enable_anomalies': True,
            'enable_correlations': True,
            'anomaly_threshold': 3.0,
            'correlation_threshold': 0.7,
            'top_values_count': 100,
            'histogram_bins': 50,
            'output_format': 'parquet',
            'output_path': '/tmp/profiling_results'
        }
    
    def _generate_imports(self) -> str:
        """Generate import statements"""
        return """from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.types import *
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler, StandardScaler
import numpy as np
import pandas as pd
from datetime import datetime
import json
import re
from typing import Dict, List, Any, Tuple"""
    
    def _generate_spark_session(self) -> str:
        """Generate Spark session initialization"""
        return """# Initialize Spark session with optimized settings
spark = SparkSession.builder \\
    .appName("Advanced Data Profiling") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \\
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \\
    .config("spark.sql.statistics.histogram.enabled", "true") \\
    .config("spark.sql.cbo.enabled", "true") \\
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \\
    .config("spark.sql.shuffle.partitions", "200") \\
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")"""
    
    def _generate_udf_definitions(self) -> str:
        """Generate User Defined Functions"""
        return '''# Define UDFs for pattern detection
@F.udf(returnType=StringType())
def detect_pattern(value):
    """Detect common patterns in string values"""
    if not value:
        return "NULL"
    
    # Email pattern
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', value):
        return "EMAIL"
    
    # Phone pattern
    if re.match(r'^[\\+]?[(]?[0-9]{3}[)]?[-\\s\\.]?[(]?[0-9]{3}[)]?[-\\s\\.]?[0-9]{4,6}$', value):
        return "PHONE"
    
    # URL pattern
    if re.match(r'^https?://(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b', value):
        return "URL"
    
    # UUID pattern
    if re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', value):
        return "UUID"
    
    # Credit card pattern (basic)
    if re.match(r'^[0-9]{13,19}$', value):
        return "CREDIT_CARD"
    
    # IP address pattern
    if re.match(r'^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$', value):
        return "IP_ADDRESS"
    
    # Date patterns
    if re.match(r'^\\d{4}-\\d{2}-\\d{2}$', value):
        return "DATE_ISO"
    if re.match(r'^\\d{2}/\\d{2}/\\d{4}$', value):
        return "DATE_US"
    
    # Numeric patterns
    if re.match(r'^-?\\d+$', value):
        return "INTEGER"
    if re.match(r'^-?\\d+\\.\\d+$', value):
        return "DECIMAL"
    
    # Alphanumeric ID
    if re.match(r'^[A-Z0-9]{5,}$', value):
        return "ALPHANUMERIC_ID"
    
    return "OTHER"

@F.udf(returnType=BooleanType())
def is_outlier_iqr(value, q1, q3, factor=1.5):
    """Detect outliers using IQR method"""
    if value is None:
        return False
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    return value < lower_bound or value > upper_bound

@F.udf(returnType=StringType())
def detect_pii(column_name, value):
    """Detect potential PII data"""
    if not value:
        return "NO_PII"
    
    # Check column name hints
    pii_column_patterns = [
        'ssn', 'social_security', 'email', 'phone', 'address',
        'credit_card', 'account_number', 'passport', 'license'
    ]
    
    column_lower = column_name.lower()
    for pattern in pii_column_patterns:
        if pattern in column_lower:
            return f"PII_{pattern.upper()}"
    
    # Check value patterns
    if re.match(r'^\\d{3}-\\d{2}-\\d{4}$', str(value)):
        return "PII_SSN"
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', str(value)):
        return "PII_EMAIL"
    
    return "NO_PII"'''
    
    def _generate_data_loader(self, table_name: str, schema: Dict[str, Any]) -> str:
        """Generate data loading code"""
        return f"""# Load data
print(f"Loading data from {{table_name}}...")
df = spark.read.parquet("{table_name}")

# Cache for better performance
df.cache()
total_rows = df.count()
print(f"Total rows: {{total_rows:,}}")

# Get schema information
schema_info = {{}}
for field in df.schema.fields:
    schema_info[field.name] = {{
        'data_type': str(field.dataType),
        'nullable': field.nullable
    }}"""
    
    def _generate_basic_statistics(self, schema: Dict[str, Any], config: Dict) -> str:
        """Generate code for basic statistical profiling"""
        return """# Basic Statistics Profiling
print("\\nCalculating basic statistics...")

# Numeric columns statistics
numeric_cols = [field.name for field in df.schema.fields 
                if field.dataType in [IntegerType(), LongType(), FloatType(), DoubleType(), DecimalType()]]

numeric_stats = {}
for col in numeric_cols:
    stats = df.select(
        F.min(col).alias('min'),
        F.max(col).alias('max'),
        F.mean(col).alias('mean'),
        F.stddev(col).alias('stddev'),
        F.variance(col).alias('variance'),
        F.skewness(col).alias('skewness'),
        F.kurtosis(col).alias('kurtosis'),
        F.expr(f'percentile_approx({col}, 0.25)').alias('q1'),
        F.expr(f'percentile_approx({col}, 0.5)').alias('median'),
        F.expr(f'percentile_approx({col}, 0.75)').alias('q3'),
        F.count(F.when(F.col(col).isNull(), 1)).alias('null_count'),
        F.count(F.when(F.col(col) == 0, 1)).alias('zero_count')
    ).collect()[0]
    
    numeric_stats[col] = stats.asDict()

# String columns statistics
string_cols = [field.name for field in df.schema.fields 
               if field.dataType == StringType()]

string_stats = {}
for col in string_cols:
    stats = df.select(
        F.count(F.col(col)).alias('non_null_count'),
        F.countDistinct(col).alias('distinct_count'),
        F.min(F.length(col)).alias('min_length'),
        F.max(F.length(col)).alias('max_length'),
        F.avg(F.length(col)).alias('avg_length'),
        F.count(F.when(F.col(col).isNull(), 1)).alias('null_count'),
        F.count(F.when(F.trim(col) == '', 1)).alias('empty_count')
    ).collect()[0]
    
    # Get top values
    top_values = df.groupBy(col).count() \\
        .orderBy(F.desc('count')) \\
        .limit(config.get('top_values_count', 100)) \\
        .collect()
    
    string_stats[col] = {
        **stats.asDict(),
        'top_values': [(row[col], row['count']) for row in top_values]
    }"""
    
    def _generate_pattern_detection(self, schema: Dict[str, Any], config: Dict) -> str:
        """Generate pattern detection code"""
        return """# Pattern Detection
if config.get('enable_patterns', True):
    print("\\nDetecting patterns...")
    
    pattern_results = {}
    for col in string_cols:
        # Sample data for pattern detection
        sample_df = df.select(col).filter(F.col(col).isNotNull()).limit(10000)
        
        # Apply pattern detection
        patterns = sample_df.select(
            col,
            detect_pattern(F.col(col)).alias('pattern')
        ).groupBy('pattern').count() \\
         .orderBy(F.desc('count')) \\
         .collect()
        
        pattern_results[col] = {row['pattern']: row['count'] for row in patterns}
        
        # PII Detection
        pii_check = sample_df.select(
            detect_pii(F.lit(col), F.col(col)).alias('pii_type')
        ).groupBy('pii_type').count() \\
         .filter(F.col('pii_type') != 'NO_PII') \\
         .collect()
        
        if pii_check:
            pattern_results[col]['pii_detected'] = {row['pii_type']: row['count'] for row in pii_check}"""
    
    def _generate_anomaly_detection(self, schema: Dict[str, Any], config: Dict) -> str:
        """Generate anomaly detection code"""
        return """# Anomaly Detection
if config.get('enable_anomalies', True):
    print("\\nDetecting anomalies...")
    
    anomaly_results = {}
    threshold = config.get('anomaly_threshold', 3.0)
    
    # Numeric anomalies using IQR and Z-score
    for col in numeric_cols:
        # Calculate statistics for anomaly detection
        stats = df.select(
            F.expr(f'percentile_approx({col}, 0.25)').alias('q1'),
            F.expr(f'percentile_approx({col}, 0.75)').alias('q3'),
            F.mean(col).alias('mean'),
            F.stddev(col).alias('stddev')
        ).collect()[0]
        
        q1, q3 = stats['q1'], stats['q3']
        mean, stddev = stats['mean'], stats['stddev']
        
        # IQR method
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        iqr_outliers = df.filter(
            (F.col(col) < lower_bound) | (F.col(col) > upper_bound)
        ).count()
        
        # Z-score method
        if stddev and stddev > 0:
            z_outliers = df.filter(
                F.abs((F.col(col) - mean) / stddev) > threshold
            ).count()
        else:
            z_outliers = 0
        
        anomaly_results[col] = {
            'iqr_outliers': iqr_outliers,
            'iqr_percentage': (iqr_outliers / total_rows) * 100,
            'z_score_outliers': z_outliers,
            'z_score_percentage': (z_outliers / total_rows) * 100,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }
    
    # Detect sudden changes in time series data
    date_cols = [field.name for field in df.schema.fields 
                 if field.dataType in [DateType(), TimestampType()]]
    
    if date_cols and numeric_cols:
        # Use first date column for time series analysis
        date_col = date_cols[0]
        
        for metric_col in numeric_cols[:5]:  # Limit to first 5 numeric columns
            # Calculate rolling statistics
            window_spec = Window.partitionBy().orderBy(date_col).rowsBetween(-7, 0)
            
            time_series_df = df.select(
                date_col,
                metric_col,
                F.avg(metric_col).over(window_spec).alias('rolling_avg'),
                F.stddev(metric_col).over(window_spec).alias('rolling_std')
            ).filter(F.col('rolling_std') > 0)
            
            # Detect anomalies based on deviation from rolling average
            anomalies = time_series_df.filter(
                F.abs((F.col(metric_col) - F.col('rolling_avg')) / F.col('rolling_std')) > threshold
            ).count()
            
            anomaly_results[f'{metric_col}_time_series'] = {
                'anomalies': anomalies,
                'percentage': (anomalies / total_rows) * 100
            }"""
    
    def _generate_correlation_analysis(self, schema: Dict[str, Any], config: Dict) -> str:
        """Generate correlation analysis code"""
        return """# Correlation Analysis
if config.get('enable_correlations', True) and len(numeric_cols) > 1:
    print("\\nAnalyzing correlations...")
    
    # Prepare data for correlation
    assembler = VectorAssembler(inputCols=numeric_cols, outputCol="features")
    vector_df = assembler.transform(df.select(numeric_cols).na.drop())
    
    # Calculate correlation matrix
    correlation_matrix = Correlation.corr(vector_df, "features", method="pearson").collect()[0][0]
    corr_array = correlation_matrix.toArray()
    
    # Find significant correlations
    significant_correlations = []
    threshold = config.get('correlation_threshold', 0.7)
    
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            corr_value = corr_array[i][j]
            if abs(corr_value) > threshold:
                significant_correlations.append({
                    'column1': numeric_cols[i],
                    'column2': numeric_cols[j],
                    'correlation': corr_value,
                    'strength': 'strong' if abs(corr_value) > 0.9 else 'moderate'
                })
    
    # Detect functional dependencies
    functional_deps = []
    for col1 in df.columns:
        for col2 in df.columns:
            if col1 != col2:
                # Check if col1 determines col2
                dep_check = df.groupBy(col1, col2).count() \\
                    .groupBy(col1).agg(F.countDistinct(col2).alias('distinct_values')) \\
                    .filter(F.col('distinct_values') == 1) \\
                    .count()
                
                total_distinct = df.select(col1).distinct().count()
                
                if dep_check == total_distinct and total_distinct > 1:
                    functional_deps.append(f"{col1} -> {col2}")"""
    
    def _generate_data_quality_metrics(self, schema: Dict[str, Any], config: Dict) -> str:
        """Generate data quality metrics calculation"""
        return """# Data Quality Metrics
print("\\nCalculating data quality metrics...")

quality_metrics = {}

# Completeness metrics
completeness = {}
for col in df.columns:
    null_count = df.filter(F.col(col).isNull()).count()
    completeness[col] = {
        'completeness_score': ((total_rows - null_count) / total_rows) * 100,
        'null_count': null_count,
        'null_percentage': (null_count / total_rows) * 100
    }

quality_metrics['completeness'] = completeness

# Uniqueness metrics
uniqueness = {}
for col in df.columns:
    distinct_count = df.select(col).distinct().count()
    duplicate_count = total_rows - distinct_count
    
    uniqueness[col] = {
        'uniqueness_score': (distinct_count / total_rows) * 100,
        'distinct_count': distinct_count,
        'duplicate_count': duplicate_count,
        'cardinality': distinct_count / total_rows
    }

quality_metrics['uniqueness'] = uniqueness

# Validity metrics (based on patterns and data types)
validity = {}
for col in string_cols:
    if col in pattern_results:
        valid_patterns = sum(count for pattern, count in pattern_results[col].items() 
                           if pattern not in ['OTHER', 'NULL'])
        total_non_null = df.filter(F.col(col).isNotNull()).count()
        
        validity[col] = {
            'validity_score': (valid_patterns / total_non_null) * 100 if total_non_null > 0 else 0,
            'valid_count': valid_patterns,
            'invalid_count': total_non_null - valid_patterns
        }

quality_metrics['validity'] = validity

# Consistency metrics (based on patterns within columns)
consistency = {}
for col in string_cols[:10]:  # Limit to first 10 columns for performance
    # Check format consistency
    sample = df.select(col).filter(F.col(col).isNotNull()).limit(1000).collect()
    if sample:
        # Analyze string lengths
        lengths = [len(str(row[col])) for row in sample if row[col]]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            
            consistency[col] = {
                'length_consistency': 100 - min((length_variance / avg_length) * 100, 100) if avg_length > 0 else 100,
                'avg_length': avg_length,
                'length_variance': length_variance
            }

quality_metrics['consistency'] = consistency

# Overall data quality score
overall_completeness = sum(m['completeness_score'] for m in completeness.values()) / len(completeness)
overall_uniqueness = sum(m['uniqueness_score'] for m in uniqueness.values()) / len(uniqueness)
overall_validity = sum(m.get('validity_score', 100) for m in validity.values()) / len(validity) if validity else 100

quality_metrics['overall'] = {
    'completeness_score': overall_completeness,
    'uniqueness_score': overall_uniqueness,
    'validity_score': overall_validity,
    'overall_score': (overall_completeness + overall_uniqueness + overall_validity) / 3
}"""
    
    def _generate_output_writer(self, config: Dict) -> str:
        """Generate code to write profiling results"""
        return f"""# Compile all results
profiling_results = {{
    'metadata': {{
        'table_name': table_name,
        'total_rows': total_rows,
        'total_columns': len(df.columns),
        'profiling_timestamp': datetime.now().isoformat(),
        'spark_version': spark.version
    }},
    'schema': schema_info,
    'numeric_statistics': numeric_stats,
    'string_statistics': string_stats,
    'pattern_detection': pattern_results if 'pattern_results' in locals() else {{}},
    'anomaly_detection': anomaly_results if 'anomaly_results' in locals() else {{}},
    'correlations': {{
        'significant_correlations': significant_correlations if 'significant_correlations' in locals() else [],
        'functional_dependencies': functional_deps if 'functional_deps' in locals() else []
    }},
    'quality_metrics': quality_metrics
}}

# Save results
output_path = config.get('output_path', '/tmp/profiling_results')
output_format = config.get('output_format', 'parquet')

print(f"\\nSaving results to {{output_path}}...")

# Save as JSON for easy reading
with open(f"{{output_path}}_results.json", 'w') as f:
    json.dump(profiling_results, f, indent=2, default=str)

# Save detailed statistics as Parquet for further analysis
if numeric_stats:
    numeric_df = spark.createDataFrame([
        {{**{{'column': col}}, **stats}} 
        for col, stats in numeric_stats.items()
    ])
    numeric_df.write.mode('overwrite').parquet(f"{{output_path}}_numeric_stats")

if string_stats:
    string_df = spark.createDataFrame([
        {{**{{'column': col}}, **{{k: v for k, v in stats.items() if k != 'top_values'}}}} 
        for col, stats in string_stats.items()
    ])
    string_df.write.mode('overwrite').parquet(f"{{output_path}}_string_stats")

print("Profiling completed successfully!")
print(f"\\nOverall Data Quality Score: {{quality_metrics['overall']['overall_score']:.2f}}%")

# Return results for API response
return profiling_results"""
    
    def generate_streaming_profiler(self, 
                                  stream_config: Dict[str, Any]) -> str:
        """Generate PySpark code for streaming data profiling"""
        
        code_parts = [
            self._generate_imports(),
            self._generate_streaming_session(),
            self._generate_streaming_reader(stream_config),
            self._generate_streaming_profiler_logic(),
            self._generate_streaming_writer(stream_config)
        ]
        
        return "\n\n".join(code_parts)
    
    def _generate_streaming_session(self) -> str:
        """Generate Spark session for streaming"""
        return """# Initialize Spark session for streaming
spark = SparkSession.builder \\
    .appName("Streaming Data Profiler") \\
    .config("spark.sql.streaming.checkpointLocation", "/tmp/streaming_checkpoint") \\
    .config("spark.sql.streaming.stateStore.stateSchemaCheck", "false") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \\
    .getOrCreate()"""
    
    def _generate_streaming_reader(self, config: Dict) -> str:
        """Generate streaming data reader"""
        source_type = config.get('source_type', 'kafka')
        
        if source_type == 'kafka':
            return f"""# Read from Kafka stream
stream_df = spark.readStream \\
    .format("kafka") \\
    .option("kafka.bootstrap.servers", "{config.get('kafka_servers', 'localhost:9092')}") \\
    .option("subscribe", "{config.get('topic', 'data-stream')}") \\
    .option("startingOffsets", "latest") \\
    .load()

# Parse JSON data
parsed_df = stream_df.select(
    F.from_json(F.col("value").cast("string"), schema).alias("data")
).select("data.*")"""
        else:
            return f"""# Read from file stream
stream_df = spark.readStream \\
    .format("{config.get('format', 'parquet')}") \\
    .schema(schema) \\
    .load("{config.get('path', '/tmp/streaming_data')}")"""
    
    def _generate_streaming_profiler_logic(self) -> str:
        """Generate streaming profiler logic"""
        return """# Define stateful profiling function
def profile_batch(df, epoch_id):
    '''Profile each micro-batch'''
    
    # Basic statistics
    stats = {}
    
    # Numeric columns
    numeric_cols = [f.name for f in df.schema.fields 
                    if f.dataType in [IntegerType(), LongType(), FloatType(), DoubleType()]]
    
    for col in numeric_cols:
        col_stats = df.agg(
            F.min(col).alias('min'),
            F.max(col).alias('max'),
            F.avg(col).alias('mean'),
            F.stddev(col).alias('stddev'),
            F.count(col).alias('count'),
            F.sum(F.when(F.col(col).isNull(), 1).otherwise(0)).alias('nulls')
        ).collect()[0].asDict()
        
        stats[col] = col_stats
    
    # String columns
    string_cols = [f.name for f in df.schema.fields if f.dataType == StringType()]
    
    for col in string_cols:
        col_stats = df.agg(
            F.countDistinct(col).alias('distinct'),
            F.count(col).alias('count'),
            F.sum(F.when(F.col(col).isNull(), 1).otherwise(0)).alias('nulls')
        ).collect()[0].asDict()
        
        stats[col] = col_stats
    
    # Save batch statistics
    stats_df = spark.createDataFrame([{
        'batch_id': epoch_id,
        'timestamp': datetime.now().isoformat(),
        'row_count': df.count(),
        'statistics': json.dumps(stats)
    }])
    
    stats_df.write.mode('append').parquet('/tmp/streaming_stats')
    
    # Detect anomalies in real-time
    for col in numeric_cols:
        # Simple anomaly detection using recent statistics
        recent_stats = spark.read.parquet('/tmp/streaming_stats') \\
            .orderBy(F.desc('timestamp')) \\
            .limit(10) \\
            .select(F.get_json_object('statistics', f'$.{col}.mean').alias('mean'),
                    F.get_json_object('statistics', f'$.{col}.stddev').alias('stddev'))
        
        if recent_stats.count() > 5:
            avg_mean = recent_stats.agg(F.avg('mean')).collect()[0][0]
            avg_std = recent_stats.agg(F.avg('stddev')).collect()[0][0]
            
            current_mean = stats[col]['mean']
            
            if avg_std and abs(current_mean - float(avg_mean)) > 3 * float(avg_std):
                print(f"ANOMALY DETECTED in {col}: Current mean {current_mean} deviates from historical average {avg_mean}")

# Apply profiling to stream
query = parsed_df.writeStream \\
    .foreachBatch(profile_batch) \\
    .outputMode("append") \\
    .trigger(processingTime='30 seconds') \\
    .start()"""
    
    def _generate_streaming_writer(self, config: Dict) -> str:
        """Generate streaming output writer"""
        return """# Also write raw data for analysis
raw_query = parsed_df.writeStream \\
    .format("parquet") \\
    .option("path", "/tmp/streaming_raw") \\
    .option("checkpointLocation", "/tmp/streaming_checkpoint_raw") \\
    .outputMode("append") \\
    .trigger(processingTime='1 minute') \\
    .start()

# Wait for termination
query.awaitTermination()"""
    
    def generate_quality_rules_executor(self, 
                                      rules: List[Dict[str, Any]],
                                      table_name: str) -> str:
        """Generate PySpark code to execute data quality rules"""
        
        code_parts = [
            self._generate_imports(),
            self._generate_spark_session(),
            f"# Load data\ndf = spark.read.parquet('{table_name}')\ntotal_rows = df.count()\n",
            self._generate_rule_execution(rules),
            self._generate_rule_results_aggregation()
        ]
        
        return "\n\n".join(code_parts)
    
    def _generate_rule_execution(self, rules: List[Dict[str, Any]]) -> str:
        """Generate code to execute each rule"""
        rule_code = ["# Execute Data Quality Rules", "rule_results = []"]
        
        for i, rule in enumerate(rules):
            rule_type = rule.get('rule_type', 'custom')
            column = rule.get('column', '')
            
            if rule_type == 'completeness':
                code = f"""
# Rule {i+1}: Completeness check for {column}
null_count = df.filter(F.col('{column}').isNull()).count()
completeness_score = ((total_rows - null_count) / total_rows) * 100
rule_results.append({{
    'rule_id': '{rule.get('id', i+1)}',
    'rule_name': '{rule.get('name', f'Completeness check for {column}')}',
    'rule_type': 'completeness',
    'column': '{column}',
    'passed': completeness_score >= {rule.get('threshold', 95)},
    'score': completeness_score,
    'threshold': {rule.get('threshold', 95)},
    'failed_records': null_count,
    'details': f'Completeness: {{completeness_score:.2f}}%'
}})"""
            
            elif rule_type == 'uniqueness':
                code = f"""
# Rule {i+1}: Uniqueness check for {column}
duplicate_count = df.groupBy('{column}').count().filter(F.col('count') > 1).agg(F.sum('count') - F.count('*')).collect()[0][0] or 0
uniqueness_score = ((total_rows - duplicate_count) / total_rows) * 100
rule_results.append({{
    'rule_id': '{rule.get('id', i+1)}',
    'rule_name': '{rule.get('name', f'Uniqueness check for {column}')}',
    'rule_type': 'uniqueness',
    'column': '{column}',
    'passed': uniqueness_score >= {rule.get('threshold', 99)},
    'score': uniqueness_score,
    'threshold': {rule.get('threshold', 99)},
    'failed_records': int(duplicate_count),
    'details': f'Uniqueness: {{uniqueness_score:.2f}}%'
}})"""
            
            elif rule_type == 'validity_regex':
                pattern = rule.get('pattern', '.*')
                code = f"""
# Rule {i+1}: Pattern validity check for {column}
invalid_count = df.filter(~F.col('{column}').rlike('{pattern}')).count()
validity_score = ((total_rows - invalid_count) / total_rows) * 100
rule_results.append({{
    'rule_id': '{rule.get('id', i+1)}',
    'rule_name': '{rule.get('name', f'Pattern check for {column}')}',
    'rule_type': 'validity_regex',
    'column': '{column}',
    'passed': validity_score >= {rule.get('threshold', 95)},
    'score': validity_score,
    'threshold': {rule.get('threshold', 95)},
    'failed_records': invalid_count,
    'details': f'Pattern validity: {{validity_score:.2f}}%',
    'pattern': '{pattern}'
}})"""
            
            elif rule_type == 'range':
                min_val = rule.get('min_value', float('-inf'))
                max_val = rule.get('max_value', float('inf'))
                code = f"""
# Rule {i+1}: Range check for {column}
out_of_range = df.filter((F.col('{column}') < {min_val}) | (F.col('{column}') > {max_val})).count()
range_score = ((total_rows - out_of_range) / total_rows) * 100
rule_results.append({{
    'rule_id': '{rule.get('id', i+1)}',
    'rule_name': '{rule.get('name', f'Range check for {column}')}',
    'rule_type': 'range',
    'column': '{column}',
    'passed': range_score >= {rule.get('threshold', 99)},
    'score': range_score,
    'threshold': {rule.get('threshold', 99)},
    'failed_records': out_of_range,
    'details': f'Range validity: {{range_score:.2f}}%',
    'range': '[{min_val}, {max_val}]'
}})"""
            
            elif rule_type == 'custom_sql':
                sql_expr = rule.get('sql_expression', 'true')
                code = f"""
# Rule {i+1}: Custom SQL rule
df.createOrReplaceTempView('temp_table')
failed_count = spark.sql(f"SELECT COUNT(*) FROM temp_table WHERE NOT ({sql_expr})").collect()[0][0]
custom_score = ((total_rows - failed_count) / total_rows) * 100
rule_results.append({{
    'rule_id': '{rule.get('id', i+1)}',
    'rule_name': '{rule.get('name', 'Custom SQL rule')}',
    'rule_type': 'custom_sql',
    'passed': custom_score >= {rule.get('threshold', 95)},
    'score': custom_score,
    'threshold': {rule.get('threshold', 95)},
    'failed_records': failed_count,
    'details': f'Custom rule score: {{custom_score:.2f}}%',
    'sql_expression': '''{sql_expr}'''
}})"""
            
            rule_code.append(code)
        
        return "\n".join(rule_code)
    
    def _generate_rule_results_aggregation(self) -> str:
        """Generate code to aggregate rule results"""
        return """# Aggregate results
passed_rules = sum(1 for r in rule_results if r['passed'])
total_rules = len(rule_results)
overall_score = sum(r['score'] for r in rule_results) / total_rules if total_rules > 0 else 0

summary = {
    'execution_timestamp': datetime.now().isoformat(),
    'total_records': total_rows,
    'total_rules': total_rules,
    'passed_rules': passed_rules,
    'failed_rules': total_rules - passed_rules,
    'overall_score': overall_score,
    'rule_results': rule_results
}

# Save results
results_df = spark.createDataFrame(rule_results)
results_df.write.mode('overwrite').parquet('/tmp/quality_rule_results')

# Print summary
print(f"\\nData Quality Check Summary:")
print(f"Total Rules: {total_rules}")
print(f"Passed: {passed_rules}")
print(f"Failed: {total_rules - passed_rules}")
print(f"Overall Score: {overall_score:.2f}%")

# Return results
return summary"""


class DataQualityMonitor:
    """Real-time data quality monitoring using Spark Streaming"""
    
    def __init__(self, spark_session):
        self.spark = spark_session
        self.metrics_path = "/tmp/dq_metrics"
        
    def generate_monitoring_job(self, 
                              source_config: Dict,
                              quality_rules: List[Dict],
                              alert_config: Dict) -> str:
        """Generate Spark Streaming job for continuous DQ monitoring"""
        
        return f"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
import json
from datetime import datetime
import requests

# Initialize monitoring session
spark = SparkSession.builder \\
    .appName("Data Quality Monitor") \\
    .config("spark.sql.streaming.checkpointLocation", "/tmp/dq_monitor_checkpoint") \\
    .getOrCreate()

# Define quality check functions
def check_quality_rules(df, batch_id):
    '''Check quality rules on each batch'''
    
    metrics = {{
        'batch_id': batch_id,
        'timestamp': datetime.now().isoformat(),
        'row_count': df.count(),
        'rules': []
    }}
    
    # Execute each rule
    {self._generate_streaming_rules(quality_rules)}
    
    # Check for alerts
    {self._generate_alert_logic(alert_config)}
    
    # Save metrics
    metrics_df = spark.createDataFrame([metrics])
    metrics_df.write.mode('append').json('{self.metrics_path}')
    
    return metrics

# Start monitoring
stream_df = {self._generate_stream_reader(source_config)}

query = stream_df \\
    .writeStream \\
    .foreachBatch(check_quality_rules) \\
    .outputMode("append") \\
    .trigger(processingTime='{source_config.get('interval', '5 minutes')}') \\
    .start()

query.awaitTermination()
"""
    
    def _generate_streaming_rules(self, rules: List[Dict]) -> str:
        """Generate streaming rule checks"""
        rule_checks = []
        
        for rule in rules:
            if rule['rule_type'] == 'completeness':
                check = f"""
    # Check {rule['name']}
    null_count = df.filter(F.col('{rule['column']}').isNull()).count()
    completeness = ((df.count() - null_count) / df.count()) * 100 if df.count() > 0 else 100
    metrics['rules'].append({{
        'rule': '{rule['name']}',
        'column': '{rule['column']}',
        'metric': completeness,
        'threshold': {rule.get('threshold', 95)},
        'passed': completeness >= {rule.get('threshold', 95)}
    }})"""
            
            elif rule['rule_type'] == 'freshness':
                check = f"""
    # Check data freshness
    latest_timestamp = df.agg(F.max('{rule['timestamp_column']}').alias('max_ts')).collect()[0]['max_ts']
    freshness_hours = (datetime.now() - latest_timestamp).total_seconds() / 3600
    metrics['rules'].append({{
        'rule': '{rule['name']}',
        'column': '{rule['timestamp_column']}',
        'metric': freshness_hours,
        'threshold': {rule.get('max_delay_hours', 1)},
        'passed': freshness_hours <= {rule.get('max_delay_hours', 1)}
    }})"""
            
            rule_checks.append(check)
        
        return "\n".join(rule_checks)
    
    def _generate_stream_reader(self, config: Dict) -> str:
        """Generate stream reader based on source type"""
        source_type = config.get('source_type', 'kafka')
        
        if source_type == 'kafka':
            return f"""spark.readStream \\
    .format("kafka") \\
    .option("kafka.bootstrap.servers", "{config.get('servers', 'localhost:9092')}") \\
    .option("subscribe", "{config.get('topic', 'data-stream')}") \\
    .load() \\
    .select(F.from_json(F.col("value").cast("string"), schema).alias("data")) \\
    .select("data.*")"""
        else:
            return f"""spark.readStream \\
    .format("{config.get('format', 'parquet')}") \\
    .schema(schema) \\
    .load("{config.get('path', '/tmp/stream_data')}")"""
    
    def _generate_alert_logic(self, alert_config: Dict) -> str:
        """Generate alerting logic"""
        return f"""
    # Check for alerts
    failed_rules = [r for r in metrics['rules'] if not r['passed']]
    
    if failed_rules and {alert_config.get('enabled', True)}:
        alert_payload = {{
            'alert_type': 'data_quality_failure',
            'timestamp': metrics['timestamp'],
            'failed_rules': failed_rules,
            'severity': 'high' if len(failed_rules) > {alert_config.get('critical_threshold', 3)} else 'medium'
        }}
        
        # Send alert (webhook example)
        if '{alert_config.get('webhook_url', '')}':
            try:
                requests.post('{alert_config.get('webhook_url', '')}', json=alert_payload)
            except Exception as e:
                print(f"Failed to send alert: {{e}}")
        
        # Log alert
        print(f"ALERT: {{len(failed_rules)}} quality rules failed!")
        for rule in failed_rules:
            print(f"  - {{rule['rule']}}: {{rule['metric']:.2f}} (threshold: {{rule['threshold']}})")"""