# Synthetic Data Generation Guide

This guide explains how to generate comprehensive test data for big data projects using the provided data generators.

## Overview

The synthetic data generators create realistic, relationship-aware data for various business domains:

1. **Retail Analytics** - E-commerce and retail store data
2. **Financial Analytics** - Banking and financial services data

## Data Generators

### 1. Retail Analytics Data Generator

Located at: `bigdata/data_generator/synthetic_data_generator.py`

#### Generated Tables

| Table | Description | Record Count |
|-------|-------------|--------------|
| customers | Customer profiles with demographics | 10,000+ |
| products | Product catalog with categories | 5,000+ |
| stores | Physical and online store locations | 500+ |
| employees | Employee records with hierarchy | 2,000+ |
| suppliers | Supplier information | 1,000+ |
| transactions | Sales transactions with line items | 50,000+ |
| inventory | Stock levels by product and store | 20,000+ |
| customer_behavior | Web clickstream and behavior data | 30,000+ |
| product_reviews | Customer reviews and ratings | 15,000+ |
| marketing_campaigns | Campaign performance metrics | 500+ |

#### Key Features

- **Realistic Relationships**: Foreign keys maintain referential integrity
- **Time-based Data**: Historical data spanning 2-5 years
- **Business Logic**: Prices, discounts, and inventory follow realistic patterns
- **Geographic Distribution**: US-based addresses and locations
- **Customer Segmentation**: Premium, Regular, Basic, VIP segments

### 2. Financial Analytics Data Generator

Located at: `bigdata/data_generator/financial_data_generator.py`

#### Generated Tables

| Table | Description | Record Count |
|-------|-------------|--------------|
| customers | Bank customers with KYC info | 10,000+ |
| accounts | Various account types | 20,000+ |
| transactions | Financial transactions | 100,000+ |
| credit_cards | Credit card details | 5,000+ |
| loans | Various loan types | 3,000+ |
| fraud_cases | Fraud investigation records | 1,000+ |

#### Key Features

- **Account Types**: Checking, Savings, Credit Cards, Loans
- **Transaction Patterns**: Realistic spending patterns
- **Risk Metrics**: Credit scores, risk categories
- **Fraud Detection**: Simulated fraud cases with investigation data
- **Regulatory Compliance**: KYC verification dates

## Running the Data Generators

### Prerequisites

1. Docker or Podman installed
2. At least 8GB RAM available
3. 10GB+ free disk space

### Quick Start

```bash
# Navigate to the bigdata directory
cd bigdata/data_generator

# Run the retail data generation
./run_data_generation.sh
```

### Manual Execution

1. Start the PySpark container:
```bash
cd bigdata/docker
docker-compose -f docker-compose.pyspark.yml up -d
```

2. Copy generator files to container:
```bash
docker cp ../data_generator/synthetic_data_generator.py pyspark-app:/workspace/
```

3. Execute the generator:
```bash
docker exec -it pyspark-app spark-submit /workspace/synthetic_data_generator.py
```

### Customizing Data Volume

Modify the `records_multiplier` parameter in the generator:

```python
# Generate 2x the default data volume
generator.generate_all_data(records_multiplier=2.0)

# Generate smaller test dataset
generator.generate_all_data(records_multiplier=0.1)
```

## Accessing the Data

### 1. Jupyter Notebook

Access pre-built analysis notebooks:
- URL: http://localhost:8888
- No password required
- Navigate to `/workspace/notebooks/`

### 2. Spark SQL Shell

```bash
docker exec -it pyspark-app spark-sql

# Example queries
USE retail_analytics;
SHOW TABLES;
SELECT COUNT(*) FROM customers;
```

### 3. PySpark Shell

```bash
docker exec -it pyspark-app pyspark

# Load data
df = spark.sql("SELECT * FROM retail_analytics.customers LIMIT 10")
df.show()
```

### 4. Direct Container Access

```bash
docker exec -it pyspark-app /bin/bash
```

## Data Quality Characteristics

### Retail Data
- **Customer Distribution**: Normal distribution across states
- **Product Pricing**: Category-based pricing with realistic margins
- **Transaction Patterns**: 
  - Peak hours: 10am-2pm, 6pm-8pm
  - Seasonal variations
  - Weekend vs weekday patterns
- **Review Ratings**: Bell curve centered around 3.5-4.0 stars

### Financial Data
- **Account Balances**: Log-normal distribution
- **Transaction Amounts**: 
  - ATM: Fixed denominations ($20, $40, etc.)
  - Purchases: Long-tail distribution
  - Deposits: Bi-modal (paycheck amounts)
- **Fraud Rate**: ~0.1% of transactions
- **Loan Defaults**: ~5-10% based on risk category

## Common Use Cases

### 1. Data Quality Testing
```sql
-- Check for null values
SELECT 
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_customers,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as null_emails
FROM retail_analytics.customers;
```

### 2. Performance Testing
```sql
-- Large join operation
SELECT 
    c.customer_segment,
    COUNT(DISTINCT t.transaction_id) as transactions,
    SUM(t.total_amount) as revenue
FROM retail_analytics.customers c
JOIN retail_analytics.transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_segment;
```

### 3. Analytics Development
```sql
-- Customer lifetime value calculation
WITH customer_metrics AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT transaction_id) as purchase_count,
        SUM(total_amount) as total_spent,
        DATEDIFF(MAX(transaction_date), MIN(transaction_date)) as customer_lifetime_days
    FROM retail_analytics.transactions
    WHERE transaction_status = 'Completed'
    GROUP BY customer_id
)
SELECT 
    AVG(total_spent) as avg_clv,
    AVG(purchase_count) as avg_purchases,
    AVG(customer_lifetime_days) as avg_lifetime_days
FROM customer_metrics;
```

## Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker logs pyspark-app

# Ensure ports are available
netstat -tulpn | grep -E '(4040|8080|8888)'
```

### Out of Memory Errors
```bash
# Increase container memory
docker update pyspark-app --memory="8g" --memory-swap="8g"
```

### Data Generation Fails
```bash
# Check Spark logs
docker exec pyspark-app cat /opt/spark/logs/*.out

# Verify Hive metastore
docker exec pyspark-app spark-sql -e "SHOW DATABASES;"
```

## Advanced Configuration

### Custom Data Distributions

Modify the generator classes to create custom distributions:

```python
# Example: Skewed customer distribution
def generate_customers_skewed(self, num_records):
    # 80% from top 5 states
    top_states = ['CA', 'TX', 'NY', 'FL', 'IL']
    customers = []
    
    for i in range(int(num_records * 0.8)):
        customer = self._create_customer()
        customer['state'] = random.choice(top_states)
        customers.append(customer)
    
    # Remaining 20% from other states
    # ... continue implementation
```

### Adding New Tables

1. Create a new generation method in the appropriate generator class
2. Define the schema and relationships
3. Add to `generate_all_data()` method
4. Update save operations

### Integration with External Systems

The generated data can be exported to various formats:

```python
# Export to Parquet
df = spark.sql("SELECT * FROM retail_analytics.customers")
df.write.mode("overwrite").parquet("/data/exports/customers.parquet")

# Export to CSV
df.write.mode("overwrite").option("header", "true").csv("/data/exports/customers.csv")

# Export to JSON
df.write.mode("overwrite").json("/data/exports/customers.json")
```

## Best Practices

1. **Start Small**: Test with smaller datasets first (0.1x multiplier)
2. **Monitor Resources**: Watch memory and CPU usage during generation
3. **Validate Relationships**: Check foreign key integrity after generation
4. **Backup Data**: Export important test datasets for reuse
5. **Document Changes**: Keep track of any customizations made

## Next Steps

1. Explore the data using the provided Jupyter notebooks
2. Integrate with your data quality testing frameworks
3. Use for performance benchmarking and optimization
4. Extend generators for domain-specific requirements

For questions or issues, check the logs in `/var/log/spark/` within the container.