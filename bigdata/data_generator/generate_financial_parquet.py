#!/usr/bin/env python3
"""
Generate financial data and save as Parquet files
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
        .appName("Financial Data Generator - Parquet") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def generate_financial_data():
    """Generate all financial data and save as Parquet"""
    logger.info("Starting financial data generation...")
    
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Create output directory
    output_dir = "/workspace/generated_data/financial"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Import the generator
        sys.path.append('/workspace')
        from financial_data_generator import FinancialDataGenerator
        
        # Create generator instance
        generator = FinancialDataGenerator(spark)
        
        # Generate and save data
        logger.info("Generating bank customers...")
        customers_df = generator.generate_bank_customers(10000)
        customers_spark = spark.createDataFrame(customers_df.to_dict('records'))
        customers_spark.write.mode("overwrite").parquet(f"{output_dir}/customers")
        logger.info(f"✓ Saved {customers_spark.count()} bank customers")
        
        logger.info("Generating accounts...")
        accounts_df = generator.generate_accounts(20000)
        accounts_spark = spark.createDataFrame(accounts_df.to_dict('records'))
        accounts_spark.write.mode("overwrite").parquet(f"{output_dir}/accounts")
        logger.info(f"✓ Saved {accounts_spark.count()} accounts")
        
        logger.info("Generating transactions...")
        transactions_df = generator.generate_transactions(100000)
        transactions_spark = spark.createDataFrame(transactions_df.to_dict('records'))
        transactions_spark.write.mode("overwrite").parquet(f"{output_dir}/transactions")
        logger.info(f"✓ Saved {transactions_spark.count()} transactions")
        
        logger.info("Generating credit cards...")
        cards_df = generator.generate_credit_cards(5000)
        cards_spark = spark.createDataFrame(cards_df.to_dict('records'))
        cards_spark.write.mode("overwrite").parquet(f"{output_dir}/credit_cards")
        logger.info(f"✓ Saved {cards_spark.count()} credit cards")
        
        logger.info("Generating loans...")
        loans_df = generator.generate_loans(3000)
        loans_spark = spark.createDataFrame(loans_df.to_dict('records'))
        loans_spark.write.mode("overwrite").parquet(f"{output_dir}/loans")
        logger.info(f"✓ Saved {loans_spark.count()} loans")
        
        logger.info("Generating fraud cases...")
        fraud_df = generator.generate_fraud_cases(1000)
        fraud_spark = spark.createDataFrame(fraud_df.to_dict('records'))
        fraud_spark.write.mode("overwrite").parquet(f"{output_dir}/fraud_cases")
        logger.info(f"✓ Saved {fraud_spark.count()} fraud cases")
        
        # Create views for analysis
        logger.info("\nCreating temporary views for analysis...")
        spark.read.parquet(f"{output_dir}/customers").createOrReplaceTempView("bank_customers")
        spark.read.parquet(f"{output_dir}/accounts").createOrReplaceTempView("accounts")
        spark.read.parquet(f"{output_dir}/transactions").createOrReplaceTempView("bank_transactions")
        spark.read.parquet(f"{output_dir}/credit_cards").createOrReplaceTempView("credit_cards")
        spark.read.parquet(f"{output_dir}/loans").createOrReplaceTempView("loans")
        spark.read.parquet(f"{output_dir}/fraud_cases").createOrReplaceTempView("fraud_cases")
        
        # Run sample analytics
        logger.info("\n=== Financial Analytics Summary ===")
        
        logger.info("\n1. Customer segments:")
        spark.sql("""
            SELECT customer_segment, COUNT(*) as count,
                   AVG(annual_income) as avg_income,
                   AVG(credit_score) as avg_credit_score
            FROM bank_customers
            GROUP BY customer_segment
            ORDER BY count DESC
        """).show()
        
        logger.info("\n2. Account type distribution:")
        spark.sql("""
            SELECT account_type, 
                   COUNT(*) as count,
                   SUM(current_balance) as total_balance,
                   AVG(current_balance) as avg_balance
            FROM accounts
            WHERE account_status = 'Active'
            GROUP BY account_type
            ORDER BY total_balance DESC
        """).show()
        
        logger.info("\n3. Loan portfolio:")
        spark.sql("""
            SELECT loan_type,
                   COUNT(*) as loan_count,
                   SUM(loan_amount) as total_amount,
                   AVG(interest_rate) as avg_rate,
                   SUM(CASE WHEN loan_status = 'Current' THEN 1 ELSE 0 END) as current_loans
            FROM loans
            GROUP BY loan_type
            ORDER BY total_amount DESC
        """).show()
        
        logger.info("\n4. Fraud detection summary:")
        spark.sql("""
            SELECT fraud_type,
                   COUNT(*) as cases,
                   SUM(amount_involved) as total_amount,
                   AVG(amount_involved) as avg_amount,
                   SUM(amount_recovered) as recovered
            FROM fraud_cases
            GROUP BY fraud_type
            ORDER BY cases DESC
        """).show()
        
        logger.info(f"\n✅ Financial data generation completed!")
        logger.info(f"📁 Data saved to: {output_dir}")
        
    except Exception as e:
        logger.error(f"Error during data generation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    generate_financial_data()