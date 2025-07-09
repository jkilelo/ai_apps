#!/usr/bin/env python3
"""
Generate synthetic data and save as Parquet files
This version avoids Hive metastore complexity
"""

import os
import sys
from pyspark.sql import SparkSession
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create a new Spark session"""
    return SparkSession.builder \
        .appName("Synthetic Data Generator - Parquet") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def generate_data():
    """Generate all data and save as Parquet"""
    logger.info("Starting data generation...")
    
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Create output directory
    output_dir = "/workspace/generated_data"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Import the generator
        sys.path.append('/workspace')
        from synthetic_data_generator_fixed import SyntheticDataGenerator
        
        # Create generator instance
        generator = SyntheticDataGenerator(spark)
        
        # Generate and save data
        logger.info("Generating customers...")
        customers_df = generator.generate_customers(10000)
        customers_spark = spark.createDataFrame(customers_df.to_dict('records'))
        customers_spark.write.mode("overwrite").parquet(f"{output_dir}/customers")
        logger.info(f"✓ Saved {customers_spark.count()} customers")
        
        logger.info("Generating stores...")
        stores_df = generator.generate_stores(500)
        stores_spark = spark.createDataFrame(stores_df.to_dict('records'))
        stores_spark.write.mode("overwrite").parquet(f"{output_dir}/stores")
        logger.info(f"✓ Saved {stores_spark.count()} stores")
        
        logger.info("Generating suppliers...")
        suppliers_df = generator.generate_suppliers(1000)
        suppliers_spark = spark.createDataFrame(suppliers_df.to_dict('records'))
        suppliers_spark.write.mode("overwrite").parquet(f"{output_dir}/suppliers")
        logger.info(f"✓ Saved {suppliers_spark.count()} suppliers")
        
        logger.info("Generating products...")
        products_df = generator.generate_products(5000)
        # Update products with supplier relationships
        import random
        products_df['supplier_id'] = products_df.apply(
            lambda x: random.choice(generator.supplier_ids), axis=1
        )
        products_spark = spark.createDataFrame(products_df.to_dict('records'))
        products_spark.write.mode("overwrite").parquet(f"{output_dir}/products")
        logger.info(f"✓ Saved {products_spark.count()} products")
        
        logger.info("Generating employees...")
        employees_df = generator.generate_employees(2000)
        employees_spark = spark.createDataFrame(employees_df.to_dict('records'))
        employees_spark.write.mode("overwrite").parquet(f"{output_dir}/employees")
        logger.info(f"✓ Saved {employees_spark.count()} employees")
        
        logger.info("Generating transactions...")
        transactions_df = generator.generate_transactions(50000)
        transactions_spark = spark.createDataFrame(transactions_df.to_dict('records'))
        transactions_spark.write.mode("overwrite").parquet(f"{output_dir}/transactions")
        logger.info(f"✓ Saved {transactions_spark.count()} transactions")
        
        logger.info("Generating inventory...")
        inventory_df = generator.generate_inventory(20000)
        inventory_spark = spark.createDataFrame(inventory_df.to_dict('records'))
        inventory_spark.write.mode("overwrite").parquet(f"{output_dir}/inventory")
        logger.info(f"✓ Saved {inventory_spark.count()} inventory records")
        
        logger.info("Generating customer behavior (this may take a while)...")
        # Split into smaller batches
        all_behaviors = []
        for i in range(3):
            logger.info(f"  Batch {i+1}/3...")
            behavior_df = generator.generate_customer_behavior(10000)
            all_behaviors.append(behavior_df)
        
        import pandas as pd
        combined_behaviors = pd.concat(all_behaviors, ignore_index=True)
        behaviors_spark = spark.createDataFrame(combined_behaviors.to_dict('records'))
        behaviors_spark.write.mode("overwrite").parquet(f"{output_dir}/customer_behavior")
        logger.info(f"✓ Saved {behaviors_spark.count()} customer behavior records")
        
        logger.info("Generating product reviews...")
        reviews_df = generator.generate_reviews(15000)
        reviews_spark = spark.createDataFrame(reviews_df.to_dict('records'))
        reviews_spark.write.mode("overwrite").parquet(f"{output_dir}/product_reviews")
        logger.info(f"✓ Saved {reviews_spark.count()} product reviews")
        
        logger.info("Generating marketing campaigns...")
        campaigns_df = generator.generate_marketing_campaigns(500)
        campaigns_spark = spark.createDataFrame(campaigns_df.to_dict('records'))
        campaigns_spark.write.mode("overwrite").parquet(f"{output_dir}/marketing_campaigns")
        logger.info(f"✓ Saved {campaigns_spark.count()} marketing campaigns")
        
        # Create views for easy querying
        logger.info("\nCreating temporary views for analysis...")
        spark.read.parquet(f"{output_dir}/customers").createOrReplaceTempView("customers")
        spark.read.parquet(f"{output_dir}/products").createOrReplaceTempView("products")
        spark.read.parquet(f"{output_dir}/stores").createOrReplaceTempView("stores")
        spark.read.parquet(f"{output_dir}/transactions").createOrReplaceTempView("transactions")
        
        # Run sample queries
        logger.info("\n=== Sample Analysis ===")
        
        logger.info("\n1. Customer segments:")
        spark.sql("""
            SELECT customer_segment, COUNT(*) as count 
            FROM customers 
            GROUP BY customer_segment
            ORDER BY count DESC
        """).show()
        
        logger.info("\n2. Top product categories:")
        spark.sql("""
            SELECT category, COUNT(*) as product_count
            FROM products
            GROUP BY category
            ORDER BY product_count DESC
        """).show()
        
        logger.info("\n3. Transaction summary:")
        spark.sql("""
            SELECT 
                COUNT(DISTINCT transaction_id) as total_transactions,
                COUNT(*) as total_line_items,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_transaction_value
            FROM transactions
            WHERE transaction_status = 'Completed'
        """).show()
        
        logger.info(f"\n✅ All data generated successfully!")
        logger.info(f"📁 Data saved to: {output_dir}")
        logger.info("\nTo query the data later:")
        logger.info("1. Start PySpark: podman exec -it pyspark-app pyspark")
        logger.info("2. Load data: df = spark.read.parquet('/workspace/generated_data/customers')")
        logger.info("3. Create view: df.createOrReplaceTempView('customers')")
        logger.info("4. Query: spark.sql('SELECT * FROM customers LIMIT 10').show()")
        
    except Exception as e:
        logger.error(f"Error during data generation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    generate_data()