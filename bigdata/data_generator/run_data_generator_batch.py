#!/usr/bin/env python3
"""
Batch runner for synthetic data generator
Runs the data generation in smaller batches to avoid timeouts
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
        .appName("Synthetic Data Generator - Batch") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .config("spark.sql.catalogImplementation", "hive") \
        .config("spark.sql.hive.metastore.jars", "builtin") \
        .config("spark.sql.hive.metastore.version", "2.3.9") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .enableHiveSupport() \
        .getOrCreate()

def test_small_batch():
    """Test with a very small batch first"""
    logger.info("Starting small batch test...")
    
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        # Import the generator
        sys.path.append('/workspace')
        from synthetic_data_generator_fixed import SyntheticDataGenerator
        
        # Create generator instance
        generator = SyntheticDataGenerator(spark)
        
        # Generate only small amounts first
        logger.info("Generating 100 customers...")
        customers_df = generator.generate_customers(100)
        generator.save_to_hive(customers_df, "retail_analytics", "customers")
        
        logger.info("Generating 20 stores...")
        stores_df = generator.generate_stores(20)
        generator.save_to_hive(stores_df, "retail_analytics", "stores")
        
        logger.info("Generating 50 products...")
        products_df = generator.generate_products(50)
        generator.save_to_hive(products_df, "retail_analytics", "products")
        
        # Verify data
        logger.info("Verifying data...")
        count = spark.sql("SELECT COUNT(*) FROM retail_analytics.customers").collect()[0][0]
        logger.info(f"Customers count: {count}")
        
        count = spark.sql("SELECT COUNT(*) FROM retail_analytics.stores").collect()[0][0]
        logger.info(f"Stores count: {count}")
        
        count = spark.sql("SELECT COUNT(*) FROM retail_analytics.products").collect()[0][0]
        logger.info(f"Products count: {count}")
        
        logger.info("Small batch test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during small batch test: {str(e)}")
        raise
    finally:
        spark.stop()

def generate_full_data():
    """Generate full dataset"""
    logger.info("Starting full data generation...")
    
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        # Import the generator
        sys.path.append('/workspace')
        from synthetic_data_generator_fixed import SyntheticDataGenerator
        
        # Create generator instance  
        generator = SyntheticDataGenerator(spark)
        
        # Generate base data first
        logger.info("Phase 1: Generating base entities...")
        
        customers_df = generator.generate_customers(10000)
        generator.save_to_hive(customers_df, "retail_analytics", "customers")
        logger.info("✓ Customers saved")
        
        stores_df = generator.generate_stores(500)
        generator.save_to_hive(stores_df, "retail_analytics", "stores")
        logger.info("✓ Stores saved")
        
        suppliers_df = generator.generate_suppliers(1000)
        generator.save_to_hive(suppliers_df, "retail_analytics", "suppliers")
        logger.info("✓ Suppliers saved")
        
        products_df = generator.generate_products(5000)
        # Update products with supplier relationships
        import random
        products_df['supplier_id'] = products_df.apply(
            lambda x: random.choice(generator.supplier_ids), axis=1
        )
        generator.save_to_hive(products_df, "retail_analytics", "products")
        logger.info("✓ Products saved")
        
        employees_df = generator.generate_employees(2000)
        generator.save_to_hive(employees_df, "retail_analytics", "employees")
        logger.info("✓ Employees saved")
        
        # Generate transactional data
        logger.info("Phase 2: Generating transactional data...")
        
        transactions_df = generator.generate_transactions(50000)
        generator.save_to_hive(transactions_df, "retail_analytics", "transactions")
        logger.info("✓ Transactions saved")
        
        inventory_df = generator.generate_inventory(20000)
        generator.save_to_hive(inventory_df, "retail_analytics", "inventory")
        logger.info("✓ Inventory saved")
        
        # Generate behavioral data
        logger.info("Phase 3: Generating behavioral data...")
        
        # Split customer behavior into smaller chunks
        for i in range(3):
            logger.info(f"Generating customer behavior batch {i+1}/3...")
            behavior_df = generator.generate_customer_behavior(10000)
            if i == 0:
                generator.save_to_hive(behavior_df, "retail_analytics", "customer_behavior")
            else:
                # Append to existing table
                spark_df = spark.createDataFrame(behavior_df.to_dict('records'))
                spark_df.write.mode("append").saveAsTable("retail_analytics.customer_behavior")
            logger.info(f"✓ Customer behavior batch {i+1} saved")
        
        reviews_df = generator.generate_reviews(15000)
        generator.save_to_hive(reviews_df, "retail_analytics", "product_reviews")
        logger.info("✓ Product reviews saved")
        
        campaigns_df = generator.generate_marketing_campaigns(500)
        generator.save_to_hive(campaigns_df, "retail_analytics", "marketing_campaigns")
        logger.info("✓ Marketing campaigns saved")
        
        # Final summary
        logger.info("\n=== Data Generation Complete ===")
        logger.info("Verifying final counts...")
        
        tables = [
            "customers", "products", "stores", "employees", "suppliers",
            "transactions", "inventory", "customer_behavior", "product_reviews", 
            "marketing_campaigns"
        ]
        
        for table in tables:
            count = spark.sql(f"SELECT COUNT(*) FROM retail_analytics.{table}").collect()[0][0]
            logger.info(f"{table}: {count:,} records")
            
    except Exception as e:
        logger.error(f"Error during data generation: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run synthetic data generator')
    parser.add_argument('--test', action='store_true', help='Run small test batch only')
    args = parser.parse_args()
    
    if args.test:
        test_small_batch()
    else:
        generate_full_data()