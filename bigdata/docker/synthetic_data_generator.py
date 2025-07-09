#!/usr/bin/env python3
"""
Comprehensive Synthetic Data Generator for Big Data Projects
Generates realistic data for multiple business domains with relationships
"""

import random
import datetime
from typing import List, Dict, Any, Tuple
from faker import Faker
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """Generate synthetic data for various business domains"""
    
    def __init__(self, spark: SparkSession, seed: int = 42):
        self.spark = spark
        self.faker = Faker()
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        
        # Cache for maintaining relationships
        self.customer_ids = []
        self.product_ids = []
        self.store_ids = []
        self.employee_ids = []
        self.supplier_ids = []
        
    def generate_customers(self, num_records: int = 10000) -> pd.DataFrame:
        """Generate customer data"""
        logger.info(f"Generating {num_records} customer records...")
        
        customers = []
        for i in range(num_records):
            customer_id = f"CUST{i+1:08d}"
            self.customer_ids.append(customer_id)
            
            # Generate age-appropriate data
            age = random.randint(18, 85)
            registration_date = self.faker.date_between(start_date='-5y', end_date='today')
            
            customer = {
                'customer_id': customer_id,
                'first_name': self.faker.first_name(),
                'last_name': self.faker.last_name(),
                'email': self.faker.email(),
                'phone': self.faker.phone_number(),
                'date_of_birth': self.faker.date_of_birth(minimum_age=age, maximum_age=age),
                'gender': random.choice(['M', 'F', 'Other']),
                'address_line1': self.faker.street_address(),
                'address_line2': self.faker.secondary_address() if random.random() > 0.7 else None,
                'city': self.faker.city(),
                'state': self.faker.state_abbr(),
                'zip_code': self.faker.zipcode(),
                'country': 'USA',
                'registration_date': registration_date,
                'customer_segment': random.choice(['Premium', 'Regular', 'Basic', 'VIP']),
                'credit_score': random.randint(300, 850),
                'annual_income': random.randint(20000, 250000),
                'preferred_contact': random.choice(['email', 'phone', 'sms', 'mail']),
                'marketing_opt_in': random.choice([True, False]),
                'last_updated': self.faker.date_time_between(start_date=registration_date, end_date='now')
            }
            customers.append(customer)
            
        return pd.DataFrame(customers)
    
    def generate_products(self, num_records: int = 5000) -> pd.DataFrame:
        """Generate product catalog data"""
        logger.info(f"Generating {num_records} product records...")
        
        categories = {
            'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Camera', 'Headphones', 'Smart Watch'],
            'Clothing': ['Shirt', 'Pants', 'Dress', 'Jacket', 'Shoes', 'Accessories'],
            'Home & Garden': ['Furniture', 'Kitchen Appliances', 'Decor', 'Tools', 'Outdoor'],
            'Books': ['Fiction', 'Non-fiction', 'Educational', 'Children', 'Comics'],
            'Sports': ['Equipment', 'Apparel', 'Footwear', 'Accessories', 'Nutrition'],
            'Beauty': ['Skincare', 'Makeup', 'Haircare', 'Fragrance', 'Tools']
        }
        
        products = []
        for i in range(num_records):
            product_id = f"PROD{i+1:08d}"
            self.product_ids.append(product_id)
            
            category = random.choice(list(categories.keys()))
            subcategory = random.choice(categories[category])
            
            # Price based on category
            base_price = {
                'Electronics': (50, 2000),
                'Clothing': (20, 300),
                'Home & Garden': (15, 1500),
                'Books': (5, 50),
                'Sports': (10, 500),
                'Beauty': (5, 200)
            }
            
            price_range = base_price[category]
            cost = round(random.uniform(price_range[0] * 0.3, price_range[1] * 0.6), 2)
            price = round(cost * random.uniform(1.2, 2.5), 2)
            
            product = {
                'product_id': product_id,
                'product_name': f"{self.faker.company()} {subcategory} {self.faker.word().title()}",
                'sku': self.faker.bothify(text='???-#####-??'),
                'category': category,
                'subcategory': subcategory,
                'brand': self.faker.company(),
                'description': self.faker.text(max_nb_chars=200),
                'unit_cost': cost,
                'unit_price': price,
                'weight_kg': round(random.uniform(0.1, 20), 2),
                'dimensions_cm': f"{random.randint(5,100)}x{random.randint(5,100)}x{random.randint(5,50)}",
                'color': self.faker.safe_color_name(),
                'size': random.choice(['XS', 'S', 'M', 'L', 'XL', 'XXL', 'One Size', None]),
                'material': random.choice(['Cotton', 'Polyester', 'Leather', 'Metal', 'Plastic', 'Wood', None]),
                'supplier_id': None,  # Will be updated after suppliers are generated
                'reorder_point': random.randint(10, 100),
                'reorder_quantity': random.randint(50, 500),
                'discontinued': random.choice([True, False]) if random.random() > 0.95 else False,
                'launch_date': self.faker.date_between(start_date='-3y', end_date='today'),
                'last_updated': self.faker.date_time_between(start_date='-1y', end_date='now')
            }
            products.append(product)
            
        return pd.DataFrame(products)
    
    def generate_stores(self, num_records: int = 500) -> pd.DataFrame:
        """Generate store/location data"""
        logger.info(f"Generating {num_records} store records...")
        
        store_types = ['Retail', 'Warehouse', 'Outlet', 'Online', 'Pop-up']
        
        stores = []
        for i in range(num_records):
            store_id = f"STORE{i+1:05d}"
            self.store_ids.append(store_id)
            
            store_type = random.choice(store_types)
            
            store = {
                'store_id': store_id,
                'store_name': f"{self.faker.city()} {store_type} Store",
                'store_type': store_type,
                'address': self.faker.street_address(),
                'city': self.faker.city(),
                'state': self.faker.state_abbr(),
                'zip_code': self.faker.zipcode(),
                'country': 'USA',
                'phone': self.faker.phone_number(),
                'email': self.faker.company_email(),
                'manager_name': self.faker.name(),
                'opening_date': self.faker.date_between(start_date='-10y', end_date='-1d'),
                'store_size_sqft': random.randint(1000, 50000),
                'parking_spaces': random.randint(20, 500),
                'employees_count': random.randint(5, 200),
                'operating_hours': '9:00 AM - 9:00 PM' if store_type != 'Online' else '24/7',
                'latitude': float(self.faker.latitude()),
                'longitude': float(self.faker.longitude()),
                'is_active': random.choice([True, False]) if random.random() > 0.95 else True,
                'last_renovation': self.faker.date_between(start_date='-5y', end_date='today'),
                'annual_revenue_target': random.randint(500000, 10000000)
            }
            stores.append(store)
            
        return pd.DataFrame(stores)
    
    def generate_employees(self, num_records: int = 2000) -> pd.DataFrame:
        """Generate employee data"""
        logger.info(f"Generating {num_records} employee records...")
        
        departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations', 'Customer Service', 'Logistics']
        positions = {
            'Sales': ['Sales Associate', 'Sales Manager', 'Account Executive', 'Sales Director'],
            'Marketing': ['Marketing Coordinator', 'Marketing Manager', 'Brand Manager', 'CMO'],
            'IT': ['Developer', 'System Admin', 'Data Analyst', 'IT Manager', 'CTO'],
            'HR': ['HR Coordinator', 'HR Manager', 'Recruiter', 'HR Director'],
            'Finance': ['Accountant', 'Financial Analyst', 'Controller', 'CFO'],
            'Operations': ['Operations Coordinator', 'Operations Manager', 'Supply Chain Manager', 'COO'],
            'Customer Service': ['CS Representative', 'CS Supervisor', 'CS Manager'],
            'Logistics': ['Warehouse Worker', 'Driver', 'Logistics Coordinator', 'Logistics Manager']
        }
        
        employees = []
        for i in range(num_records):
            employee_id = f"EMP{i+1:06d}"
            self.employee_ids.append(employee_id)
            
            department = random.choice(departments)
            position = random.choice(positions[department])
            hire_date = self.faker.date_between(start_date='-15y', end_date='today')
            
            # Salary based on position
            base_salaries = {
                'Associate': (30000, 50000),
                'Coordinator': (40000, 60000),
                'Representative': (30000, 45000),
                'Worker': (25000, 40000),
                'Driver': (30000, 50000),
                'Analyst': (60000, 90000),
                'Manager': (70000, 120000),
                'Supervisor': (50000, 70000),
                'Director': (100000, 150000),
                'Executive': (80000, 130000),
                'Admin': (50000, 80000),
                'Developer': (70000, 130000),
                'Controller': (90000, 130000),
                'CTO': (150000, 250000),
                'CFO': (150000, 250000),
                'CMO': (150000, 250000),
                'COO': (150000, 250000)
            }
            
            # Find salary range based on position keywords
            salary_range = (40000, 60000)  # default
            for key, range_val in base_salaries.items():
                if key in position:
                    salary_range = range_val
                    break
            
            employee = {
                'employee_id': employee_id,
                'first_name': self.faker.first_name(),
                'last_name': self.faker.last_name(),
                'email': self.faker.company_email(),
                'phone': self.faker.phone_number(),
                'ssn': self.faker.ssn(),
                'date_of_birth': self.faker.date_of_birth(minimum_age=22, maximum_age=65),
                'gender': random.choice(['M', 'F', 'Other']),
                'department': department,
                'position': position,
                'hire_date': hire_date,
                'salary': random.randint(salary_range[0], salary_range[1]),
                'bonus_percentage': random.randint(0, 25),
                'store_id': random.choice(self.store_ids) if self.store_ids else None,
                'manager_id': random.choice(self.employee_ids[:i]) if i > 10 else None,
                'employment_type': random.choice(['Full-time', 'Part-time', 'Contract']),
                'performance_rating': round(random.uniform(1, 5), 1),
                'address': self.faker.street_address(),
                'city': self.faker.city(),
                'state': self.faker.state_abbr(),
                'zip_code': self.faker.zipcode(),
                'emergency_contact': self.faker.name(),
                'emergency_phone': self.faker.phone_number(),
                'is_active': random.choice([True, False]) if random.random() > 0.9 else True,
                'termination_date': self.faker.date_between(start_date=hire_date, end_date='today') 
                                   if random.random() > 0.9 else None
            }
            employees.append(employee)
            
        return pd.DataFrame(employees)
    
    def generate_suppliers(self, num_records: int = 1000) -> pd.DataFrame:
        """Generate supplier data"""
        logger.info(f"Generating {num_records} supplier records...")
        
        supplier_types = ['Manufacturer', 'Distributor', 'Wholesaler', 'Importer', 'Direct']
        
        suppliers = []
        for i in range(num_records):
            supplier_id = f"SUPP{i+1:06d}"
            self.supplier_ids.append(supplier_id)
            
            supplier = {
                'supplier_id': supplier_id,
                'supplier_name': self.faker.company(),
                'supplier_type': random.choice(supplier_types),
                'contact_name': self.faker.name(),
                'contact_email': self.faker.company_email(),
                'contact_phone': self.faker.phone_number(),
                'address': self.faker.street_address(),
                'city': self.faker.city(),
                'state': self.faker.state_abbr(),
                'zip_code': self.faker.zipcode(),
                'country': random.choice(['USA', 'China', 'India', 'Mexico', 'Canada', 'Germany']),
                'website': self.faker.url(),
                'tax_id': self.faker.bothify(text='##-#######'),
                'payment_terms': random.choice(['Net 30', 'Net 60', 'Net 90', 'COD', '2/10 Net 30']),
                'credit_limit': random.randint(10000, 1000000),
                'rating': round(random.uniform(1, 5), 1),
                'contract_start': self.faker.date_between(start_date='-5y', end_date='-1y'),
                'contract_end': self.faker.date_between(start_date='today', end_date='+3y'),
                'is_preferred': random.choice([True, False]),
                'lead_time_days': random.randint(1, 60),
                'minimum_order_value': random.randint(100, 10000),
                'last_order_date': self.faker.date_between(start_date='-6m', end_date='today'),
                'total_orders': random.randint(0, 1000),
                'quality_score': round(random.uniform(70, 100), 1)
            }
            suppliers.append(supplier)
            
        return pd.DataFrame(suppliers)
    
    def generate_transactions(self, num_records: int = 50000) -> pd.DataFrame:
        """Generate sales transaction data"""
        logger.info(f"Generating {num_records} transaction records...")
        
        if not self.customer_ids or not self.product_ids or not self.store_ids:
            raise ValueError("Generate customers, products, and stores first!")
        
        transactions = []
        transaction_id = 1
        
        for _ in range(num_records):
            trans_date = self.faker.date_time_between(start_date='-2y', end_date='now')
            num_items = random.randint(1, 10)
            
            # Create line items for this transaction
            for _ in range(num_items):
                transaction = {
                    'transaction_id': f"TRX{transaction_id:010d}",
                    'line_item': _ + 1,
                    'transaction_date': trans_date,
                    'customer_id': random.choice(self.customer_ids),
                    'product_id': random.choice(self.product_ids),
                    'store_id': random.choice(self.store_ids),
                    'quantity': random.randint(1, 5),
                    'unit_price': round(random.uniform(10, 500), 2),
                    'discount_percentage': random.choice([0, 5, 10, 15, 20, 25]) if random.random() > 0.7 else 0,
                    'tax_rate': round(random.uniform(0, 0.10), 3),
                    'payment_method': random.choice(['Credit Card', 'Debit Card', 'Cash', 'PayPal', 'Gift Card']),
                    'transaction_status': random.choice(['Completed', 'Pending', 'Cancelled']) 
                                        if random.random() > 0.95 else 'Completed',
                    'channel': random.choice(['In-Store', 'Online', 'Mobile App', 'Phone']),
                    'promotion_id': f"PROMO{random.randint(1, 100):03d}" if random.random() > 0.8 else None,
                    'cashier_id': random.choice(self.employee_ids) if self.employee_ids else None
                }
                
                # Calculate totals
                subtotal = transaction['quantity'] * transaction['unit_price']
                discount = subtotal * (transaction['discount_percentage'] / 100)
                tax = (subtotal - discount) * transaction['tax_rate']
                
                transaction['subtotal'] = round(subtotal, 2)
                transaction['discount_amount'] = round(discount, 2)
                transaction['tax_amount'] = round(tax, 2)
                transaction['total_amount'] = round(subtotal - discount + tax, 2)
                
                transactions.append(transaction)
            
            transaction_id += 1
            
        return pd.DataFrame(transactions)
    
    def generate_inventory(self, num_records: int = 20000) -> pd.DataFrame:
        """Generate inventory tracking data"""
        logger.info(f"Generating {num_records} inventory records...")
        
        if not self.product_ids or not self.store_ids:
            raise ValueError("Generate products and stores first!")
        
        inventory = []
        
        # Ensure each product-store combination
        for _ in range(num_records):
            last_updated = self.faker.date_time_between(start_date='-30d', end_date='now')
            
            inv_record = {
                'inventory_id': f"INV{_+1:08d}",
                'product_id': random.choice(self.product_ids),
                'store_id': random.choice(self.store_ids),
                'quantity_on_hand': random.randint(0, 500),
                'quantity_reserved': random.randint(0, 50),
                'quantity_on_order': random.randint(0, 200),
                'reorder_point': random.randint(10, 100),
                'reorder_quantity': random.randint(50, 500),
                'bin_location': f"{random.choice(['A','B','C','D','E'])}{random.randint(1,99):02d}",
                'last_count_date': self.faker.date_between(start_date='-90d', end_date='today'),
                'last_received_date': self.faker.date_between(start_date='-60d', end_date='today'),
                'average_daily_usage': round(random.uniform(0.5, 20), 2),
                'days_of_supply': random.randint(0, 120),
                'stockout_flag': random.choice([True, False]) if random.random() > 0.9 else False,
                'last_updated': last_updated
            }
            
            # Calculate available quantity
            inv_record['quantity_available'] = inv_record['quantity_on_hand'] - inv_record['quantity_reserved']
            
            inventory.append(inv_record)
            
        return pd.DataFrame(inventory)
    
    def generate_customer_behavior(self, num_records: int = 30000) -> pd.DataFrame:
        """Generate customer behavior/clickstream data"""
        logger.info(f"Generating {num_records} customer behavior records...")
        
        if not self.customer_ids or not self.product_ids:
            raise ValueError("Generate customers and products first!")
        
        behaviors = []
        session_id = 1
        
        for _ in range(num_records):
            session_start = self.faker.date_time_between(start_date='-1y', end_date='now')
            customer_id = random.choice(self.customer_ids)
            
            # Generate session events
            events = ['page_view', 'product_view', 'add_to_cart', 'remove_from_cart', 
                     'checkout_start', 'purchase', 'search', 'filter_apply']
            
            num_events = random.randint(1, 20)
            current_time = session_start
            
            for event_num in range(num_events):
                behavior = {
                    'session_id': f"SESSION{session_id:010d}",
                    'customer_id': customer_id,
                    'event_timestamp': current_time,
                    'event_type': random.choice(events),
                    'product_id': random.choice(self.product_ids) if random.random() > 0.3 else None,
                    'page_url': self.faker.url(),
                    'referrer_url': self.faker.url() if random.random() > 0.5 else None,
                    'device_type': random.choice(['Desktop', 'Mobile', 'Tablet']),
                    'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge', 'Mobile Safari']),
                    'os': random.choice(['Windows', 'MacOS', 'iOS', 'Android', 'Linux']),
                    'ip_address': self.faker.ipv4(),
                    'country': 'USA',
                    'city': self.faker.city(),
                    'search_query': self.faker.word() if random.random() > 0.8 else None,
                    'click_count': random.randint(0, 10),
                    'time_on_page_seconds': random.randint(1, 600),
                    'bounce': random.choice([True, False]) if event_num == 0 and random.random() > 0.7 else False
                }
                
                behaviors.append(behavior)
                
                # Increment time for next event
                current_time += datetime.timedelta(seconds=random.randint(10, 300))
            
            session_id += 1
            
        return pd.DataFrame(behaviors)
    
    def generate_reviews(self, num_records: int = 15000) -> pd.DataFrame:
        """Generate product review data"""
        logger.info(f"Generating {num_records} review records...")
        
        if not self.customer_ids or not self.product_ids:
            raise ValueError("Generate customers and products first!")
        
        review_titles = [
            "Great product!", "Disappointed", "Exactly what I needed", "Not worth the money",
            "Exceeded expectations", "Average quality", "Highly recommend", "Would not buy again",
            "Perfect!", "Terrible experience", "Good value", "Overpriced"
        ]
        
        reviews = []
        for i in range(num_records):
            rating = random.randint(1, 5)
            
            review = {
                'review_id': f"REV{i+1:08d}",
                'product_id': random.choice(self.product_ids),
                'customer_id': random.choice(self.customer_ids),
                'rating': rating,
                'review_title': random.choice(review_titles),
                'review_text': self.faker.text(max_nb_chars=500),
                'review_date': self.faker.date_between(start_date='-2y', end_date='today'),
                'verified_purchase': random.choice([True, False]) if random.random() > 0.2 else True,
                'helpful_count': random.randint(0, 100),
                'total_votes': random.randint(0, 150),
                'has_images': random.choice([True, False]) if random.random() > 0.8 else False,
                'response_from_seller': self.faker.text(max_nb_chars=200) if random.random() > 0.9 else None,
                'sentiment_score': round(rating / 5.0 + random.uniform(-0.2, 0.2), 2)
            }
            
            reviews.append(review)
            
        return pd.DataFrame(reviews)
    
    def generate_marketing_campaigns(self, num_records: int = 500) -> pd.DataFrame:
        """Generate marketing campaign data"""
        logger.info(f"Generating {num_records} marketing campaign records...")
        
        campaign_types = ['Email', 'Social Media', 'Display Ads', 'Search Ads', 'Direct Mail', 'SMS']
        campaign_goals = ['Brand Awareness', 'Lead Generation', 'Sales', 'Customer Retention', 'Product Launch']
        
        campaigns = []
        for i in range(num_records):
            start_date = self.faker.date_between(start_date='-2y', end_date='+6m')
            duration_days = random.randint(7, 90)
            end_date = start_date + datetime.timedelta(days=duration_days)
            budget = random.randint(1000, 100000)
            
            campaign = {
                'campaign_id': f"CAMP{i+1:06d}",
                'campaign_name': f"{self.faker.catch_phrase()} Campaign",
                'campaign_type': random.choice(campaign_types),
                'campaign_goal': random.choice(campaign_goals),
                'start_date': start_date,
                'end_date': end_date,
                'budget': budget,
                'actual_spend': round(budget * random.uniform(0.7, 1.1), 2),
                'target_audience': random.choice(['All Customers', '18-25', '26-35', '36-50', '50+', 'Premium Segment']),
                'channel': random.choice(['Online', 'Offline', 'Omnichannel']),
                'impressions': random.randint(10000, 10000000),
                'clicks': random.randint(100, 100000),
                'conversions': random.randint(10, 10000),
                'revenue_generated': round(random.uniform(0, budget * 5), 2),
                'created_by': random.choice(self.employee_ids) if self.employee_ids else None,
                'status': random.choice(['Planning', 'Active', 'Paused', 'Completed', 'Cancelled']),
                'a_b_test': random.choice([True, False]),
                'notes': self.faker.text(max_nb_chars=200) if random.random() > 0.7 else None
            }
            
            # Calculate metrics
            campaign['ctr'] = round((campaign['clicks'] / campaign['impressions']) * 100, 2) if campaign['impressions'] > 0 else 0
            campaign['conversion_rate'] = round((campaign['conversions'] / campaign['clicks']) * 100, 2) if campaign['clicks'] > 0 else 0
            campaign['roi'] = round(((campaign['revenue_generated'] - campaign['actual_spend']) / campaign['actual_spend']) * 100, 2) if campaign['actual_spend'] > 0 else 0
            
            campaigns.append(campaign)
            
        return pd.DataFrame(campaigns)
    
    def save_to_hive(self, df: pd.DataFrame, database: str, table_name: str):
        """Save DataFrame to Hive table"""
        logger.info(f"Saving {len(df)} records to {database}.{table_name}")
        
        # Convert pandas DataFrame to Spark DataFrame
        spark_df = self.spark.createDataFrame(df)
        
        # Create database if not exists
        self.spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")
        
        # Write to Hive table
        spark_df.write \
            .mode("overwrite") \
            .saveAsTable(f"{database}.{table_name}")
        
        logger.info(f"Successfully saved to {database}.{table_name}")
        
    def generate_all_data(self, records_multiplier: float = 1.0):
        """Generate all datasets with relationships"""
        logger.info("Starting comprehensive data generation...")
        
        # Generate base data
        customers_df = self.generate_customers(int(10000 * records_multiplier))
        stores_df = self.generate_stores(int(500 * records_multiplier))
        suppliers_df = self.generate_suppliers(int(1000 * records_multiplier))
        products_df = self.generate_products(int(5000 * records_multiplier))
        
        # Update products with supplier relationships
        products_df['supplier_id'] = products_df.apply(
            lambda x: random.choice(self.supplier_ids), axis=1
        )
        
        employees_df = self.generate_employees(int(2000 * records_multiplier))
        
        # Generate transactional data
        transactions_df = self.generate_transactions(int(50000 * records_multiplier))
        inventory_df = self.generate_inventory(int(20000 * records_multiplier))
        behavior_df = self.generate_customer_behavior(int(30000 * records_multiplier))
        reviews_df = self.generate_reviews(int(15000 * records_multiplier))
        campaigns_df = self.generate_marketing_campaigns(int(500 * records_multiplier))
        
        # Save all to Hive
        self.save_to_hive(customers_df, "retail_analytics", "customers")
        self.save_to_hive(products_df, "retail_analytics", "products")
        self.save_to_hive(stores_df, "retail_analytics", "stores")
        self.save_to_hive(employees_df, "retail_analytics", "employees")
        self.save_to_hive(suppliers_df, "retail_analytics", "suppliers")
        self.save_to_hive(transactions_df, "retail_analytics", "transactions")
        self.save_to_hive(inventory_df, "retail_analytics", "inventory")
        self.save_to_hive(behavior_df, "retail_analytics", "customer_behavior")
        self.save_to_hive(reviews_df, "retail_analytics", "product_reviews")
        self.save_to_hive(campaigns_df, "retail_analytics", "marketing_campaigns")
        
        logger.info("Data generation completed successfully!")
        
        # Print summary
        print("\nData Generation Summary:")
        print(f"Customers: {len(customers_df):,}")
        print(f"Products: {len(products_df):,}")
        print(f"Stores: {len(stores_df):,}")
        print(f"Employees: {len(employees_df):,}")
        print(f"Suppliers: {len(suppliers_df):,}")
        print(f"Transactions: {len(transactions_df):,}")
        print(f"Inventory Records: {len(inventory_df):,}")
        print(f"Customer Behaviors: {len(behavior_df):,}")
        print(f"Product Reviews: {len(reviews_df):,}")
        print(f"Marketing Campaigns: {len(campaigns_df):,}")


def main():
    """Main execution function"""
    # Initialize Spark session with Hive support
    spark = SparkSession.builder \
        .appName("Synthetic Data Generator") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .enableHiveSupport() \
        .getOrCreate()
    
    # Set log level
    spark.sparkContext.setLogLevel("WARN")
    
    # Create generator instance
    generator = SyntheticDataGenerator(spark)
    
    # Generate all data
    generator.generate_all_data(records_multiplier=1.0)
    
    # Show sample queries
    print("\nSample Queries to Verify Data:")
    print("1. Total customers by segment:")
    spark.sql("""
        SELECT customer_segment, COUNT(*) as count 
        FROM retail_analytics.customers 
        GROUP BY customer_segment
    """).show()
    
    print("2. Top 5 products by transaction count:")
    spark.sql("""
        SELECT p.product_name, COUNT(*) as transaction_count
        FROM retail_analytics.transactions t
        JOIN retail_analytics.products p ON t.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY transaction_count DESC
        LIMIT 5
    """).show()
    
    print("3. Revenue by store:")
    spark.sql("""
        SELECT s.store_name, SUM(t.total_amount) as total_revenue
        FROM retail_analytics.transactions t
        JOIN retail_analytics.stores s ON t.store_id = s.store_id
        WHERE t.transaction_status = 'Completed'
        GROUP BY s.store_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """).show()
    
    # Stop Spark session
    spark.stop()


if __name__ == "__main__":
    main()