#!/usr/bin/env python3
"""
PySpark example script demonstrating basic functionality
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, max as spark_max
import os

def create_spark_session():
    """Create and configure Spark session"""
    return SparkSession.builder \
        .appName("PySpark Demo") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def demo_basic_operations():
    """Demonstrate basic PySpark operations"""
    print("🚀 Starting PySpark Demo")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        print(f"✅ Spark version: {spark.version}")
        print(f"✅ Spark UI available at: http://localhost:4040")
        
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
        
        # Create DataFrame
        df = spark.createDataFrame(data, columns)
        
        print("\n📊 Sample DataFrame:")
        df.show()
        
        # Basic operations
        print("\n🔍 Department Statistics:")
        df.groupBy("department") \
          .agg(count("*").alias("count"),
               avg("salary").alias("avg_salary"),
               spark_max("salary").alias("max_salary")) \
          .show()
        
        # Filter operations
        print("\n💰 High earners (>70k):")
        df.filter(col("salary") > 70000).show()
        
        # SQL operations
        df.createOrReplaceTempView("employees")
        result = spark.sql("""
            SELECT department, 
                   COUNT(*) as employee_count,
                   ROUND(AVG(salary), 2) as avg_salary
            FROM employees 
            GROUP BY department 
            ORDER BY avg_salary DESC
        """)
        
        print("\n📈 SQL Query Results:")
        result.show()
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        
    finally:
        # Stop Spark session
        spark.stop()
        print("🛑 Spark session stopped")

if __name__ == "__main__":
    demo_basic_operations()
