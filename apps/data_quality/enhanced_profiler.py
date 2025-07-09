"""
Enhanced Data Profiler with Advanced ML Algorithms
Extends the base profiler with cutting-edge ML capabilities
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from scipy import stats
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

# Import base profiler classes
from .profiler import (
    AdvancedDataProfiler, StatisticalProfile, DataTypeEnum,
    DataQualityRule, DQRuleTypeEnum, QualityDimension
)


@dataclass
class MLAnomalyResult:
    """Result of ML-based anomaly detection"""
    algorithm: str
    anomaly_indices: List[int]
    anomaly_scores: List[float]
    threshold: float
    contamination_rate: float
    confidence: float
    explanation: str


@dataclass
class PatternCluster:
    """Discovered pattern cluster"""
    cluster_id: int
    pattern: str
    examples: List[str]
    count: int
    confidence: float
    anomaly_score: float


@dataclass
class AdvancedInsight:
    """Advanced ML-driven insight"""
    insight_type: str  # anomaly, pattern, correlation, trend
    severity: str  # critical, high, medium, low
    affected_columns: List[str]
    description: str
    recommendation: str
    ml_confidence: float
    supporting_evidence: Dict[str, Any]


class EnhancedMLProfiler(AdvancedDataProfiler):
    """Enhanced profiler with advanced ML algorithms"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.ml_algorithms = {
            'isolation_forest': True,
            'autoencoder': True,
            'clustering': True,
            'time_series': True,
            'nlp_analysis': True
        }
        self.anomaly_algorithms = ['isolation_forest', 'lof', 'one_class_svm']
        self.min_samples_for_ml = 100
        
    async def profile_with_ml(
        self, 
        data: pd.DataFrame, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Enhanced profiling with ML algorithms"""
        
        # Get base profile
        base_profile = await self.profile_dataset(data, metadata)
        
        # Add ML enhancements
        ml_results = {
            'anomalies': await self._detect_ml_anomalies(data),
            'patterns': await self._discover_advanced_patterns(data),
            'correlations': await self._analyze_complex_correlations(data),
            'clusters': await self._perform_clustering_analysis(data),
            'time_series': await self._analyze_temporal_patterns(data),
            'text_insights': await self._analyze_text_columns(data),
            'advanced_insights': await self._generate_ml_insights(data, base_profile)
        }
        
        # Combine results
        enhanced_profile = {
            **base_profile.__dict__,
            'ml_analysis': ml_results
        }
        
        return enhanced_profile
    
    async def _detect_ml_anomalies(self, data: pd.DataFrame) -> Dict[str, List[MLAnomalyResult]]:
        """Detect anomalies using multiple ML algorithms"""
        anomaly_results = {}
        
        # Numeric columns for anomaly detection
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) < self.min_samples_for_ml:
                continue
                
            results = []
            
            # Isolation Forest
            iso_result = await self._isolation_forest_detection(col_data.values.reshape(-1, 1), col)
            if iso_result:
                results.append(iso_result)
            
            # Statistical methods
            stat_result = await self._statistical_anomaly_detection(col_data, col)
            if stat_result:
                results.append(stat_result)
            
            # DBSCAN for density-based anomaly detection
            dbscan_result = await self._dbscan_anomaly_detection(col_data.values.reshape(-1, 1), col)
            if dbscan_result:
                results.append(dbscan_result)
            
            anomaly_results[col] = results
        
        # Multivariate anomaly detection
        if len(numeric_cols) > 1:
            multivariate_result = await self._multivariate_anomaly_detection(data[numeric_cols])
            anomaly_results['multivariate'] = [multivariate_result] if multivariate_result else []
        
        return anomaly_results
    
    async def _isolation_forest_detection(
        self, 
        data: np.ndarray, 
        column_name: str
    ) -> Optional[MLAnomalyResult]:
        """Isolation Forest anomaly detection"""
        try:
            contamination = 0.05  # 5% contamination rate
            
            iso_forest = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            
            predictions = iso_forest.fit_predict(data)
            scores = iso_forest.score_samples(data)
            
            # Get anomaly indices
            anomaly_mask = predictions == -1
            anomaly_indices = np.where(anomaly_mask)[0].tolist()
            anomaly_scores = scores[anomaly_mask].tolist()
            
            # Calculate threshold
            threshold = np.percentile(scores, contamination * 100)
            
            return MLAnomalyResult(
                algorithm='isolation_forest',
                anomaly_indices=anomaly_indices,
                anomaly_scores=anomaly_scores,
                threshold=threshold,
                contamination_rate=contamination,
                confidence=0.85,
                explanation=f"Detected {len(anomaly_indices)} anomalies using Isolation Forest"
            )
            
        except Exception as e:
            print(f"Error in Isolation Forest detection: {e}")
            return None
    
    async def _statistical_anomaly_detection(
        self, 
        data: pd.Series, 
        column_name: str
    ) -> Optional[MLAnomalyResult]:
        """Enhanced statistical anomaly detection"""
        try:
            # Z-score method
            z_scores = np.abs(stats.zscore(data))
            threshold = 3.0
            anomaly_mask = z_scores > threshold
            
            # Modified Z-score using MAD
            median = data.median()
            mad = np.median(np.abs(data - median))
            modified_z_scores = 0.6745 * (data - median) / mad
            
            # Combine methods
            combined_mask = (z_scores > threshold) | (np.abs(modified_z_scores) > 3.5)
            anomaly_indices = np.where(combined_mask)[0].tolist()
            
            return MLAnomalyResult(
                algorithm='statistical_combined',
                anomaly_indices=anomaly_indices,
                anomaly_scores=z_scores[combined_mask].tolist(),
                threshold=threshold,
                contamination_rate=len(anomaly_indices) / len(data),
                confidence=0.75,
                explanation="Combined Z-score and Modified Z-score detection"
            )
            
        except Exception as e:
            print(f"Error in statistical detection: {e}")
            return None
    
    async def _dbscan_anomaly_detection(
        self, 
        data: np.ndarray, 
        column_name: str
    ) -> Optional[MLAnomalyResult]:
        """DBSCAN clustering for anomaly detection"""
        try:
            # Standardize data
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(data)
            
            # DBSCAN clustering
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            labels = dbscan.fit_predict(data_scaled)
            
            # Outliers have label -1
            anomaly_mask = labels == -1
            anomaly_indices = np.where(anomaly_mask)[0].tolist()
            
            if len(anomaly_indices) > 0:
                return MLAnomalyResult(
                    algorithm='dbscan',
                    anomaly_indices=anomaly_indices,
                    anomaly_scores=[1.0] * len(anomaly_indices),  # Binary classification
                    threshold=0.5,
                    contamination_rate=len(anomaly_indices) / len(data),
                    confidence=0.70,
                    explanation="Density-based spatial clustering anomaly detection"
                )
            
        except Exception as e:
            print(f"Error in DBSCAN detection: {e}")
            
        return None
    
    async def _multivariate_anomaly_detection(
        self, 
        data: pd.DataFrame
    ) -> Optional[MLAnomalyResult]:
        """Multivariate anomaly detection using PCA reconstruction error"""
        try:
            # Remove NaN values
            clean_data = data.dropna()
            if len(clean_data) < self.min_samples_for_ml:
                return None
            
            # Standardize
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(clean_data)
            
            # PCA for dimensionality reduction
            n_components = min(len(clean_data.columns), 5)
            pca = PCA(n_components=n_components)
            data_pca = pca.fit_transform(data_scaled)
            
            # Reconstruct data
            data_reconstructed = pca.inverse_transform(data_pca)
            
            # Calculate reconstruction error
            reconstruction_error = np.sum((data_scaled - data_reconstructed) ** 2, axis=1)
            
            # Threshold based on percentile
            threshold = np.percentile(reconstruction_error, 95)
            anomaly_mask = reconstruction_error > threshold
            anomaly_indices = np.where(anomaly_mask)[0].tolist()
            
            return MLAnomalyResult(
                algorithm='pca_reconstruction',
                anomaly_indices=anomaly_indices,
                anomaly_scores=reconstruction_error[anomaly_mask].tolist(),
                threshold=threshold,
                contamination_rate=0.05,
                confidence=0.80,
                explanation=f"Multivariate anomalies detected using PCA reconstruction error"
            )
            
        except Exception as e:
            print(f"Error in multivariate detection: {e}")
            return None
    
    async def _discover_advanced_patterns(self, data: pd.DataFrame) -> Dict[str, List[PatternCluster]]:
        """Discover complex patterns using ML"""
        pattern_results = {}
        
        # String columns for pattern analysis
        string_cols = data.select_dtypes(include=['object']).columns
        
        for col in string_cols:
            col_data = data[col].dropna()
            if len(col_data) < self.min_samples_for_ml:
                continue
            
            # Extract features from strings
            features = await self._extract_string_features(col_data)
            
            if features is not None and len(features) > 0:
                # Cluster patterns
                clusters = await self._cluster_string_patterns(col_data, features)
                pattern_results[col] = clusters
        
        return pattern_results
    
    async def _extract_string_features(self, series: pd.Series) -> Optional[np.ndarray]:
        """Extract numerical features from strings"""
        try:
            features = []
            
            for value in series:
                str_val = str(value)
                feature_vec = [
                    len(str_val),
                    sum(c.isdigit() for c in str_val),
                    sum(c.isalpha() for c in str_val),
                    sum(c.isupper() for c in str_val),
                    sum(c.islower() for c in str_val),
                    sum(c.isspace() for c in str_val),
                    len(set(str_val)),  # Unique characters
                    str_val.count('-'),
                    str_val.count('_'),
                    str_val.count('.'),
                    str_val.count('@'),
                    1 if str_val.startswith(('http', 'www')) else 0,
                    1 if '@' in str_val and '.' in str_val else 0,  # Email-like
                ]
                features.append(feature_vec)
            
            return np.array(features)
            
        except Exception as e:
            print(f"Error extracting string features: {e}")
            return None
    
    async def _cluster_string_patterns(
        self, 
        series: pd.Series, 
        features: np.ndarray
    ) -> List[PatternCluster]:
        """Cluster string patterns"""
        try:
            # Determine optimal number of clusters
            n_clusters = min(10, len(series) // 50)
            if n_clusters < 2:
                return []
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(features)
            
            # Analyze clusters
            clusters = []
            for cluster_id in range(n_clusters):
                cluster_mask = labels == cluster_id
                cluster_examples = series[cluster_mask].head(10).tolist()
                
                # Calculate cluster quality
                if sum(cluster_mask) > 1:
                    cluster_features = features[cluster_mask]
                    centroid = kmeans.cluster_centers_[cluster_id]
                    distances = cdist(cluster_features, [centroid])
                    anomaly_score = np.mean(distances)
                else:
                    anomaly_score = 1.0
                
                # Determine pattern from examples
                pattern = await self._infer_pattern_from_examples(cluster_examples)
                
                clusters.append(PatternCluster(
                    cluster_id=cluster_id,
                    pattern=pattern,
                    examples=cluster_examples[:5],
                    count=sum(cluster_mask),
                    confidence=1.0 / (1.0 + anomaly_score),
                    anomaly_score=anomaly_score
                ))
            
            return sorted(clusters, key=lambda x: x.count, reverse=True)
            
        except Exception as e:
            print(f"Error clustering patterns: {e}")
            return []
    
    async def _infer_pattern_from_examples(self, examples: List[str]) -> str:
        """Infer pattern from examples"""
        if not examples:
            return "UNKNOWN"
        
        # Simple pattern inference
        lengths = [len(str(ex)) for ex in examples]
        avg_length = np.mean(lengths)
        
        # Check common characteristics
        all_numeric = all(str(ex).replace('.', '').replace('-', '').isdigit() for ex in examples)
        all_alpha = all(str(ex).isalpha() for ex in examples)
        has_special = any(not str(ex).isalnum() for ex in examples)
        
        if all_numeric:
            return f"NUMERIC_{int(avg_length)}"
        elif all_alpha:
            return f"ALPHA_{int(avg_length)}"
        elif has_special:
            # Try to identify specific patterns
            if all('@' in str(ex) for ex in examples):
                return "EMAIL_PATTERN"
            elif all('://' in str(ex) for ex in examples):
                return "URL_PATTERN"
            else:
                return f"MIXED_SPECIAL_{int(avg_length)}"
        else:
            return f"ALPHANUMERIC_{int(avg_length)}"
    
    async def _analyze_complex_correlations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze complex non-linear correlations"""
        correlations = {
            'linear': {},
            'non_linear': {},
            'categorical': {},
            'time_lagged': {}
        }
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        # Linear correlations (Pearson)
        if len(numeric_cols) > 1:
            correlations['linear'] = data[numeric_cols].corr().to_dict()
        
        # Non-linear correlations (Spearman)
        if len(numeric_cols) > 1:
            spearman_corr = data[numeric_cols].corr(method='spearman')
            correlations['non_linear'] = spearman_corr.to_dict()
        
        # Mutual information for categorical relationships
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            mi_scores = await self._calculate_mutual_information(
                data[categorical_cols], 
                data[numeric_cols]
            )
            correlations['categorical'] = mi_scores
        
        return correlations
    
    async def _calculate_mutual_information(
        self, 
        categorical_data: pd.DataFrame, 
        numeric_data: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """Calculate mutual information between categorical and numeric features"""
        mi_scores = {}
        
        try:
            from sklearn.feature_selection import mutual_info_regression
            
            for cat_col in categorical_data.columns:
                # Encode categorical variable
                encoded = pd.get_dummies(categorical_data[cat_col], prefix=cat_col)
                
                scores = {}
                for num_col in numeric_data.columns:
                    # Calculate MI score
                    mi_score = mutual_info_regression(
                        encoded, 
                        numeric_data[num_col].fillna(0),
                        random_state=42
                    )
                    scores[num_col] = float(np.mean(mi_score))
                
                mi_scores[cat_col] = scores
                
        except Exception as e:
            print(f"Error calculating mutual information: {e}")
            
        return mi_scores
    
    async def _perform_clustering_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering analysis to identify data segments"""
        clustering_results = {}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return clustering_results
        
        try:
            # Prepare data
            clean_data = data[numeric_cols].dropna()
            if len(clean_data) < self.min_samples_for_ml:
                return clustering_results
            
            # Standardize
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(clean_data)
            
            # Determine optimal number of clusters
            silhouette_scores = []
            K = range(2, min(10, len(clean_data) // 10))
            
            for k in K:
                kmeans = KMeans(n_clusters=k, random_state=42)
                labels = kmeans.fit_predict(data_scaled)
                score = silhouette_score(data_scaled, labels)
                silhouette_scores.append(score)
            
            # Use best k
            if silhouette_scores:
                best_k = K[np.argmax(silhouette_scores)]
                
                # Final clustering
                kmeans = KMeans(n_clusters=best_k, random_state=42)
                labels = kmeans.fit_predict(data_scaled)
                
                # Analyze clusters
                cluster_info = []
                for i in range(best_k):
                    cluster_mask = labels == i
                    cluster_data = clean_data[cluster_mask]
                    
                    cluster_stats = {
                        'cluster_id': i,
                        'size': len(cluster_data),
                        'percentage': len(cluster_data) / len(clean_data) * 100,
                        'center': kmeans.cluster_centers_[i].tolist(),
                        'characteristics': {}
                    }
                    
                    # Get cluster characteristics
                    for col in numeric_cols:
                        cluster_stats['characteristics'][col] = {
                            'mean': float(cluster_data[col].mean()),
                            'std': float(cluster_data[col].std()),
                            'min': float(cluster_data[col].min()),
                            'max': float(cluster_data[col].max())
                        }
                    
                    cluster_info.append(cluster_stats)
                
                clustering_results = {
                    'algorithm': 'kmeans',
                    'optimal_clusters': best_k,
                    'silhouette_score': float(max(silhouette_scores)),
                    'clusters': cluster_info
                }
                
        except Exception as e:
            print(f"Error in clustering analysis: {e}")
            
        return clustering_results
    
    async def _analyze_temporal_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal patterns in date/time columns"""
        temporal_results = {}
        
        # Find datetime columns
        datetime_cols = []
        for col in data.columns:
            try:
                # Try to convert to datetime
                pd.to_datetime(data[col].dropna().head(100))
                datetime_cols.append(col)
            except:
                continue
        
        for col in datetime_cols:
            try:
                dt_series = pd.to_datetime(data[col].dropna())
                
                # Time-based statistics
                temporal_stats = {
                    'column': col,
                    'date_range': {
                        'start': str(dt_series.min()),
                        'end': str(dt_series.max()),
                        'span_days': (dt_series.max() - dt_series.min()).days
                    },
                    'patterns': {}
                }
                
                # Day of week distribution
                dow_dist = dt_series.dt.dayofweek.value_counts().to_dict()
                temporal_stats['patterns']['day_of_week'] = dow_dist
                
                # Hour distribution (if time component exists)
                if dt_series.dt.hour.sum() > 0:
                    hour_dist = dt_series.dt.hour.value_counts().to_dict()
                    temporal_stats['patterns']['hour_of_day'] = hour_dist
                
                # Monthly distribution
                month_dist = dt_series.dt.month.value_counts().to_dict()
                temporal_stats['patterns']['month'] = month_dist
                
                # Detect gaps and anomalies
                if len(dt_series) > 1:
                    time_diffs = dt_series.sort_values().diff().dropna()
                    
                    temporal_stats['gaps'] = {
                        'mean_gap': str(time_diffs.mean()),
                        'max_gap': str(time_diffs.max()),
                        'min_gap': str(time_diffs.min()),
                        'std_gap': str(time_diffs.std())
                    }
                
                temporal_results[col] = temporal_stats
                
            except Exception as e:
                print(f"Error analyzing temporal patterns for {col}: {e}")
                
        return temporal_results
    
    async def _analyze_text_columns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze text columns using NLP techniques"""
        text_results = {}
        
        # Identify potential text columns
        text_cols = []
        for col in data.select_dtypes(include=['object']).columns:
            sample = data[col].dropna().head(100)
            avg_length = sample.astype(str).str.len().mean()
            if avg_length > 50:  # Likely text content
                text_cols.append(col)
        
        for col in text_cols:
            try:
                text_data = data[col].dropna().astype(str)
                
                analysis = {
                    'column': col,
                    'statistics': {
                        'avg_length': float(text_data.str.len().mean()),
                        'avg_words': float(text_data.str.split().str.len().mean()),
                        'unique_words': len(set(' '.join(text_data).split()))
                    },
                    'patterns': {}
                }
                
                # Language detection (simplified)
                sample_text = ' '.join(text_data.head(100))
                if sample_text.isascii():
                    analysis['language'] = 'english'
                else:
                    analysis['language'] = 'non-english'
                
                # Sentiment indicators (basic)
                positive_words = ['good', 'great', 'excellent', 'amazing', 'love']
                negative_words = ['bad', 'poor', 'terrible', 'hate', 'awful']
                
                positive_count = sum(text_data.str.lower().str.contains('|'.join(positive_words)).sum())
                negative_count = sum(text_data.str.lower().str.contains('|'.join(negative_words)).sum())
                
                analysis['sentiment_indicators'] = {
                    'positive_mentions': positive_count,
                    'negative_mentions': negative_count,
                    'sentiment_ratio': positive_count / (negative_count + 1)
                }
                
                text_results[col] = analysis
                
            except Exception as e:
                print(f"Error analyzing text column {col}: {e}")
                
        return text_results
    
    async def _generate_ml_insights(
        self, 
        data: pd.DataFrame, 
        base_profile: Any
    ) -> List[AdvancedInsight]:
        """Generate advanced ML-driven insights"""
        insights = []
        
        # Analyze anomaly patterns
        anomaly_cols = []
        for profile in base_profile.column_profiles:
            if profile.outliers and len(profile.outliers) > len(data) * 0.05:
                anomaly_cols.append(profile.column_name)
        
        if anomaly_cols:
            insights.append(AdvancedInsight(
                insight_type='anomaly',
                severity='high',
                affected_columns=anomaly_cols,
                description=f"High anomaly rate detected in {len(anomaly_cols)} columns",
                recommendation="Investigate data collection process and implement anomaly detection in pipeline",
                ml_confidence=0.85,
                supporting_evidence={
                    'anomaly_columns': anomaly_cols,
                    'average_anomaly_rate': len(anomaly_cols) / len(data.columns)
                }
            ))
        
        # Analyze data quality patterns
        low_quality_cols = []
        for profile in base_profile.column_profiles:
            if profile.completeness_score < 0.7 or profile.validity_score < 0.8:
                low_quality_cols.append(profile.column_name)
        
        if low_quality_cols:
            insights.append(AdvancedInsight(
                insight_type='quality',
                severity='critical' if len(low_quality_cols) > len(data.columns) * 0.3 else 'high',
                affected_columns=low_quality_cols,
                description=f"Data quality issues found in {len(low_quality_cols)} columns",
                recommendation="Implement data validation rules and quality checks at source",
                ml_confidence=0.90,
                supporting_evidence={
                    'quality_issues': low_quality_cols,
                    'impact_percentage': len(low_quality_cols) / len(data.columns) * 100
                }
            ))
        
        # Correlation insights
        if hasattr(base_profile, 'correlations') and base_profile.correlations:
            high_corr_pairs = []
            for col1, corr_dict in base_profile.correlations.items():
                for col2, corr_value in corr_dict.items():
                    if abs(corr_value) > 0.8 and col1 < col2:  # Avoid duplicates
                        high_corr_pairs.append((col1, col2, corr_value))
            
            if high_corr_pairs:
                insights.append(AdvancedInsight(
                    insight_type='correlation',
                    severity='medium',
                    affected_columns=[pair[0] for pair in high_corr_pairs] + [pair[1] for pair in high_corr_pairs],
                    description=f"Found {len(high_corr_pairs)} highly correlated column pairs",
                    recommendation="Consider feature selection or dimensionality reduction",
                    ml_confidence=0.95,
                    supporting_evidence={'correlated_pairs': high_corr_pairs}
                ))
        
        return insights
    
    async def generate_automated_quality_rules(
        self, 
        profile_data: Dict[str, Any]
    ) -> List[DataQualityRule]:
        """Generate sophisticated DQ rules using ML insights"""
        rules = []
        
        # Extract ML insights
        ml_analysis = profile_data.get('ml_analysis', {})
        anomalies = ml_analysis.get('anomalies', {})
        patterns = ml_analysis.get('patterns', {})
        
        # Generate anomaly-based rules
        for col, anomaly_results in anomalies.items():
            if col == 'multivariate':
                continue
                
            for result in anomaly_results:
                if result.algorithm == 'isolation_forest' and result.confidence > 0.8:
                    rules.append(DataQualityRule(
                        rule_id=f"ml_anomaly_{col}",
                        rule_name=f"ML Anomaly Detection for {col}",
                        rule_type=DQRuleTypeEnum.STATISTICAL_OUTLIER,
                        dimension=QualityDimension.VALIDITY,
                        column_name=col,
                        description=f"Detect anomalies in {col} using Isolation Forest",
                        sql_expression=f"-- ML-based anomaly detection required",
                        pyspark_code=f"""
# Isolation Forest anomaly detection
from pyspark.ml.feature import VectorAssembler
from sklearn.ensemble import IsolationForest

assembler = VectorAssembler(inputCols=['{col}'], outputCol='features')
df_vector = assembler.transform(df)

# Convert to pandas for sklearn
pdf = df_vector.select('{col}').toPandas()
iso_forest = IsolationForest(contamination={result.contamination_rate})
anomalies = iso_forest.fit_predict(pdf[['{col}']])
anomaly_count = (anomalies == -1).sum()
""",
                        python_code=f"""
from sklearn.ensemble import IsolationForest
iso_forest = IsolationForest(contamination={result.contamination_rate})
anomalies = iso_forest.fit_predict(data[['{col}']])
anomaly_count = (anomalies == -1).sum()
""",
                        threshold=result.contamination_rate,
                        severity="HIGH",
                        business_context=f"ML detected {len(result.anomaly_indices)} anomalies",
                        error_message=f"Anomalies detected in {col}",
                        suggested_action="Review anomalous records and update validation rules"
                    ))
        
        # Generate pattern-based rules
        for col, pattern_clusters in patterns.items():
            if pattern_clusters and len(pattern_clusters) > 0:
                # Get dominant pattern
                dominant_pattern = pattern_clusters[0]
                
                if dominant_pattern.confidence > 0.7:
                    rules.append(DataQualityRule(
                        rule_id=f"ml_pattern_{col}",
                        rule_name=f"Pattern Conformity for {col}",
                        rule_type=DQRuleTypeEnum.PATTERN_MATCH,
                        dimension=QualityDimension.CONSISTENCY,
                        column_name=col,
                        description=f"Ensure {col} follows discovered pattern: {dominant_pattern.pattern}",
                        sql_expression=f"-- Pattern matching for {dominant_pattern.pattern}",
                        pyspark_code=f"# ML-discovered pattern validation",
                        python_code=f"# Validate against pattern: {dominant_pattern.pattern}",
                        threshold=0.9,
                        severity="MEDIUM",
                        business_context=f"ML discovered pattern with {dominant_pattern.count} examples",
                        error_message=f"Value does not match expected pattern",
                        suggested_action="Standardize data format"
                    ))
        
        return rules
    
    async def predict_data_quality_trends(
        self, 
        historical_profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict future data quality trends using ML"""
        if len(historical_profiles) < 3:
            return {"error": "Insufficient historical data for trend prediction"}
        
        trends = {}
        
        try:
            # Extract time series of quality scores
            timestamps = []
            quality_scores = []
            
            for profile in historical_profiles:
                timestamps.append(pd.to_datetime(profile['profiling_timestamp']))
                quality_scores.append(profile['overall_quality_score'])
            
            # Simple trend analysis
            df_trend = pd.DataFrame({
                'timestamp': timestamps,
                'quality_score': quality_scores
            }).sort_values('timestamp')
            
            # Calculate trend
            x = np.arange(len(df_trend))
            y = df_trend['quality_score'].values
            
            # Linear regression for trend
            z = np.polyfit(x, y, 1)
            trend_slope = z[0]
            
            # Predict next values
            future_x = np.arange(len(df_trend), len(df_trend) + 7)  # Next 7 periods
            future_y = np.polyval(z, future_x)
            
            trends = {
                'current_score': float(y[-1]),
                'trend_direction': 'improving' if trend_slope > 0 else 'declining',
                'trend_strength': abs(trend_slope),
                'predicted_scores': future_y.tolist(),
                'confidence': 0.7,  # Simple model, moderate confidence
                'recommendation': self._generate_trend_recommendation(trend_slope, y[-1])
            }
            
        except Exception as e:
            print(f"Error predicting trends: {e}")
            trends = {"error": str(e)}
        
        return trends
    
    def _generate_trend_recommendation(self, slope: float, current_score: float) -> str:
        """Generate recommendation based on trend"""
        if slope < -0.01 and current_score < 0.8:
            return "Critical: Quality is declining rapidly. Immediate intervention required."
        elif slope < 0:
            return "Warning: Quality trend is declining. Review recent changes and implement controls."
        elif slope > 0.01:
            return "Positive: Quality is improving. Continue current practices."
        else:
            return "Stable: Quality is maintained. Monitor for any changes."