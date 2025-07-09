# Big Data Test Data Generation Summary

## Overview
Successfully generated comprehensive test data for big data analytics projects using Faker library. All data is stored as Parquet files in the PySpark container for efficient querying and analysis.

## Generated Datasets

### 1. Retail Analytics Data (`/workspace/generated_data/`)

| Dataset | Records | Description |
|---------|---------|-------------|
| **Customers** | 10,000 | Customer profiles with demographics, segments, preferences |
| **Stores** | 500 | Store locations, types, revenue targets |
| **Suppliers** | 1,000 | Supplier details, ratings, contract terms |
| **Products** | 5,000 | Product catalog across 6 categories |
| **Employees** | 2,000 | Employee data with departments, roles, salaries |
| **Transactions** | 274,855 | Sales transactions with line items |
| **Inventory** | 20,000 | Stock levels, reorder points by store/product |
| **Customer Behavior** | 30,000 | Clickstream and browsing behavior |
| **Product Reviews** | 15,000 | Customer reviews with ratings |
| **Marketing Campaigns** | 500 | Campaign performance metrics |

**Total Retail Records: 362,855+**

### 2. Financial Analytics Data (`/workspace/generated_data/financial/`)

| Dataset | Records | Description |
|---------|---------|-------------|
| **Bank Customers** | 10,000 | KYC verified customers with risk profiles |
| **Accounts** | 20,000 | Various account types (checking, savings, loans) |
| **Transactions** | 100,000 | Financial transactions across channels |
| **Credit Cards** | 5,000 | Card details with limits and balances |
| **Loans** | 3,000 | Different loan types (mortgage, auto, personal) |
| **Fraud Cases** | 1,000 | Fraud investigations and recoveries |

**Total Financial Records: 139,000**

## Key Features of Generated Data

### Data Quality
- **Realistic relationships** between entities (customers → accounts → transactions)
- **Proper date/time sequences** (account open dates before transaction dates)
- **Business logic applied** (credit scores affect loan rates, age affects income)
- **Geographic consistency** (valid US addresses, zip codes)

### Business Scenarios Covered
1. **Customer Segmentation** - Premium, Regular, Basic, VIP segments
2. **Product Categories** - Electronics, Clothing, Home & Garden, Books, Sports, Beauty
3. **Financial Products** - Checking, Savings, Credit Cards, Loans (5 types)
4. **Fraud Detection** - 7 fraud types with investigation status
5. **Marketing Analytics** - Campaign ROI, conversion rates
6. **Inventory Management** - Stock levels, reorder points
7. **Customer Behavior** - Session tracking, clickstream data

## Data Access

### Using PySpark Shell
```bash
# Access container
podman exec -it pyspark-app pyspark

# Load retail data
customers = spark.read.parquet("/workspace/generated_data/customers")
transactions = spark.read.parquet("/workspace/generated_data/transactions")

# Load financial data  
accounts = spark.read.parquet("/workspace/generated_data/financial/accounts")
loans = spark.read.parquet("/workspace/generated_data/financial/loans")

# Create views for SQL queries
customers.createOrReplaceTempView("customers")
transactions.createOrReplaceTempView("transactions")
```

### Sample Queries

#### Retail Analytics
```sql
-- Customer lifetime value
SELECT c.customer_id, c.customer_segment,
       COUNT(DISTINCT t.transaction_id) as total_orders,
       SUM(t.total_amount) as lifetime_value
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
WHERE t.transaction_status = 'Completed'
GROUP BY c.customer_id, c.customer_segment
ORDER BY lifetime_value DESC
LIMIT 10
```

#### Financial Analytics
```sql
-- Risk analysis by customer segment
SELECT customer_segment, risk_category,
       COUNT(*) as customer_count,
       AVG(annual_income) as avg_income,
       AVG(credit_score) as avg_credit_score
FROM bank_customers
GROUP BY customer_segment, risk_category
ORDER BY customer_segment, risk_category
```

## Data Files Location

All data is stored in Parquet format for optimal performance:

```
/workspace/generated_data/
├── customers/
├── stores/
├── suppliers/
├── products/
├── employees/
├── transactions/
├── inventory/
├── customer_behavior/
├── product_reviews/
├── marketing_campaigns/
└── financial/
    ├── customers/
    ├── accounts/
    ├── transactions/
    ├── credit_cards/
    ├── loans/
    └── fraud_cases/
```

## Next Steps

1. **Create Hive External Tables** pointing to Parquet files
2. **Build Data Pipeline** for incremental updates
3. **Create BI Dashboards** using the generated data
4. **Train ML Models** on fraud detection and customer segmentation
5. **Performance Testing** with the large datasets

## Technical Details

- **Generator**: Custom Python classes using Faker library
- **Storage Format**: Apache Parquet (columnar, compressed)
- **Processing Engine**: Apache Spark 3.3.2
- **Python Version**: 3.9.20
- **Container**: PySpark environment with Jupyter support

## Verification

To verify the data generation:

```bash
# Check all tables
podman exec -it pyspark-app python /workspace/check_data.py

# Access Jupyter for interactive analysis
http://localhost:8888
```

Generated on: 2025-07-08