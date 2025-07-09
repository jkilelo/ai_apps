#!/usr/bin/env python3
"""
Big Data Development Examples
Demonstrates integration between Spark, Hive, and Kafka
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, max as spark_max, window, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

class BigDataDemo:
    def __init__(self):
        self.spark = None
        self.setup_spark()
    
    def setup_spark(self):
        """Initialize Spark session with Hive and Kafka support"""
        self.spark = SparkSession.builder \
            .appName("BigData Demo") \
            .config("spark.sql.warehouse.dir", "hdfs://namenode:8020/user/hive/warehouse") \
            .config("spark.sql.catalogImplementation", "hive") \
            .config("spark.hadoop.hive.metastore.uris", "thrift://hive-metastore:9083") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3") \
            .enableHiveSupport() \
            .getOrCreate()
        
        print(f"✅ Spark session created: {self.spark.version}")
        print(f"✅ Hive support: {self.spark.conf.get('spark.sql.catalogImplementation')}")
    
    def demo_hdfs_operations(self):
        """Demonstrate HDFS operations with Spark"""
        print("\n🗂️  HDFS Operations Demo")
        
        # Create sample data
        data = [
            ("Alice", 25, "Engineering", 75000),
            ("Bob", 30, "Sales", 65000),
            ("Charlie", 35, "Engineering", 85000),
            ("Diana", 28, "Marketing", 60000),
            ("Eve", 32, "Engineering", 90000),
            ("Frank", 29, "Sales", 70000)
        ]
        
        columns = ["name", "age", "department", "salary"]
        df = self.spark.createDataFrame(data, columns)
        
        # Write to HDFS
        hdfs_path = "hdfs://namenode:8020/user/data/employees"
        df.write.mode("overwrite").parquet(hdfs_path)
        print(f"✅ Data written to HDFS: {hdfs_path}")
        
        # Read from HDFS
        df_read = self.spark.read.parquet(hdfs_path)
        print("📊 Data read from HDFS:")
        df_read.show()
        
        return df_read
    
    def demo_hive_operations(self):
        """Demonstrate Hive table operations"""
        print("\n🏢 Hive Operations Demo")
        
        # Create database
        self.spark.sql("CREATE DATABASE IF NOT EXISTS demo_db")
        self.spark.sql("USE demo_db")
        
        # Create sample data
        data = [
            (1, "Alice", "Engineering", 75000),
            (2, "Bob", "Sales", 65000),
            (3, "Charlie", "Engineering", 85000),
            (4, "Diana", "Marketing", 60000),
            (5, "Eve", "Engineering", 90000),
            (6, "Frank", "Sales", 70000)
        ]
        
        columns = ["id", "name", "department", "salary"]
        df = self.spark.createDataFrame(data, columns)
        
        # Write to Hive table
        df.write.mode("overwrite").saveAsTable("employees")
        print("✅ Data written to Hive table: demo_db.employees")
        
        # Query Hive table
        print("📊 Querying Hive table:")
        self.spark.sql("SELECT * FROM employees").show()
        
        # Complex query
        print("📈 Department statistics from Hive:")
        self.spark.sql("""
            SELECT department, 
                   COUNT(*) as employee_count,
                   ROUND(AVG(salary), 2) as avg_salary,
                   MAX(salary) as max_salary
            FROM employees 
            GROUP BY department 
            ORDER BY avg_salary DESC
        """).show()
        
        return df
    
    def demo_kafka_streaming(self):
        """Demonstrate Kafka streaming with Spark"""
        print("\n🌊 Kafka Streaming Demo")
        
        try:
            # Define schema for streaming data
            schema = StructType([
                StructField("id", IntegerType(), True),
                StructField("name", StringType(), True),
                StructField("department", StringType(), True),
                StructField("salary", DoubleType(), True),
                StructField("timestamp", TimestampType(), True)
            ])
            
            # Read from Kafka
            df_stream = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "kafka:9092") \
                .option("subscribe", "employees") \
                .load()
            
            # Parse JSON data
            df_parsed = df_stream.select(
                from_json(col("value").cast("string"), schema).alias("data")
            ).select("data.*")
            
            # Windowed aggregation
            df_windowed = df_parsed \
                .withWatermark("timestamp", "10 minutes") \
                .groupBy(
                    window(col("timestamp"), "5 minutes"),
                    col("department")
                ) \
                .agg(
                    count("*").alias("employee_count"),
                    avg("salary").alias("avg_salary")
                )
            
            print("✅ Kafka streaming query configured")
            print("📊 Schema for streaming data:")
            schema.printTreeString()
            
            # Note: In production, you would start the streaming query
            # query = df_windowed.writeStream.outputMode("append").format("console").start()
            # query.awaitTermination()
            
        except Exception as e:
            print(f"⚠️  Kafka streaming demo requires Kafka to be running: {e}")
    
    def demo_data_pipeline(self):
        """Demonstrate a complete data pipeline"""
        print("\n🔄 Complete Data Pipeline Demo")
        
        # 1. Load data from HDFS
        try:
            df_hdfs = self.spark.read.parquet("hdfs://namenode:8020/user/data/employees")
            print("✅ Step 1: Data loaded from HDFS")
        except:
            print("⚠️  HDFS data not found, creating sample data...")
            df_hdfs = self.demo_hdfs_operations()
        
        # 2. Transform data
        df_transformed = df_hdfs \
            .withColumn("salary_grade", 
                       col("salary").cast("int") // 10000) \
            .withColumn("experience_level",
                       col("age") - 22)
        
        print("✅ Step 2: Data transformed")
        df_transformed.show()
        
        # 3. Save to Hive
        self.spark.sql("CREATE DATABASE IF NOT EXISTS pipeline_db")
        df_transformed.write.mode("overwrite").saveAsTable("pipeline_db.processed_employees")
        print("✅ Step 3: Data saved to Hive table: pipeline_db.processed_employees")
        
        # 4. Create analytics view
        self.spark.sql("""
            CREATE OR REPLACE VIEW pipeline_db.department_analytics AS
            SELECT 
                department,
                COUNT(*) as total_employees,
                AVG(salary) as avg_salary,
                AVG(experience_level) as avg_experience,
                MAX(salary) as max_salary,
                MIN(salary) as min_salary
            FROM pipeline_db.processed_employees
            GROUP BY department
        """)
        
        print("✅ Step 4: Analytics view created")
        
        # 5. Query analytics
        print("📊 Final Analytics Results:")
        self.spark.sql("SELECT * FROM pipeline_db.department_analytics").show()
        
        print("✅ Pipeline completed successfully!")
    
    def demo_advanced_analytics(self):
        """Demonstrate advanced analytics capabilities"""
        print("\n🧠 Advanced Analytics Demo")
        
        # Machine Learning preparation
        from pyspark.ml.feature import VectorAssembler, StringIndexer
        from pyspark.ml.regression import LinearRegression
        from pyspark.ml.evaluation import RegressionEvaluator
        
        # Create larger dataset
        import random
        departments = ["Engineering", "Sales", "Marketing", "HR", "Finance"]
        data = []
        
        for i in range(1000):
            dept = random.choice(departments)
            age = random.randint(22, 65)
            experience = age - 22
            base_salary = {
                "Engineering": 80000,
                "Sales": 65000,
                "Marketing": 60000,
                "HR": 55000,
                "Finance": 70000
            }[dept]
            
            salary = base_salary + (experience * 2000) + random.randint(-10000, 20000)
            data.append((i, f"Employee_{i}", dept, age, experience, salary))
        
        columns = ["id", "name", "department", "age", "experience", "salary"]
        df = self.spark.createDataFrame(data, columns)
        
        print("✅ Large dataset created for ML")
        print("📊 Dataset statistics:")
        df.describe().show()
        
        # Prepare features for ML
        indexer = StringIndexer(inputCol="department", outputCol="department_index")
        df_indexed = indexer.fit(df).transform(df)
        
        assembler = VectorAssembler(
            inputCols=["age", "experience", "department_index"],
            outputCol="features"
        )
        df_ml = assembler.transform(df_indexed)
        
        # Split data
        train_df, test_df = df_ml.randomSplit([0.8, 0.2], seed=42)
        
        # Train model
        lr = LinearRegression(featuresCol="features", labelCol="salary")
        model = lr.fit(train_df)
        
        # Make predictions
        predictions = model.transform(test_df)
        
        # Evaluate
        evaluator = RegressionEvaluator(labelCol="salary", predictionCol="prediction", metricName="rmse")
        rmse = evaluator.evaluate(predictions)
        
        print(f"✅ ML Model trained - RMSE: {rmse:.2f}")
        
        # Show some predictions
        print("📊 Sample predictions:")
        predictions.select("name", "department", "age", "salary", "prediction").show(10)
        
        # Save model results to Hive
        predictions.select("id", "name", "department", "age", "salary", "prediction") \
            .write.mode("overwrite").saveAsTable("pipeline_db.salary_predictions")
        
        print("✅ ML results saved to Hive table: pipeline_db.salary_predictions")
    
    def cleanup(self):
        """Clean up resources"""
        if self.spark:
            self.spark.stop()
            print("🛑 Spark session stopped")

def main():
    print("🚀 Starting Big Data Demo")
    
    demo = BigDataDemo()
    
    try:
        # Run demos
        demo.demo_hdfs_operations()
        demo.demo_hive_operations()
        demo.demo_kafka_streaming()
        demo.demo_data_pipeline()
        demo.demo_advanced_analytics()
        
        print("\n🎉 All demos completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
