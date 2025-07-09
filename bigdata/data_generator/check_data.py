#!/usr/bin/env python3
"""Check generated data counts"""

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Check Data").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

print("\n=== Generated Data Summary ===\n")

tables = [
    "customers", "stores", "suppliers", "products", 
    "employees", "transactions", "inventory"
]

for table in tables:
    try:
        df = spark.read.parquet(f"/workspace/generated_data/{table}")
        count = df.count()
        print(f"{table:20} {count:>10,} records")
    except:
        print(f"{table:20} Not yet generated")

# Show sample data
print("\n=== Sample Customer Data ===")
customers = spark.read.parquet("/workspace/generated_data/customers")
customers.show(5, truncate=False)

print("\n=== Sample Transaction Data ===")
transactions = spark.read.parquet("/workspace/generated_data/transactions")
transactions.select("transaction_id", "customer_id", "product_id", "total_amount", "transaction_status").show(5)

spark.stop()