#!/usr/bin/env python3
"""
Financial Data Generator for Banking and Financial Services Analytics
Generates realistic financial transaction data, account data, and risk metrics
"""

import random
import datetime
from typing import List, Dict
from faker import Faker
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataGenerator:
    """Generate synthetic financial data for banking analytics"""
    
    def __init__(self, spark: SparkSession, seed: int = 42):
        self.spark = spark
        self.faker = Faker()
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        
        # Cache for relationships
        self.account_ids = []
        self.customer_ids = []
        self.merchant_ids = []
        
    def generate_bank_customers(self, num_records: int = 10000) -> pd.DataFrame:
        """Generate bank customer data with KYC information"""
        logger.info(f"Generating {num_records} bank customer records...")
        
        customers = []
        for i in range(num_records):
            customer_id = f"CUST{i+1:08d}"
            self.customer_ids.append(customer_id)
            
            age = random.randint(18, 85)
            join_date = self.faker.date_between(start_date='-10y', end_date='today')
            
            # Income based on age
            if age < 25:
                income_range = (20000, 50000)
            elif age < 35:
                income_range = (30000, 80000)
            elif age < 50:
                income_range = (40000, 150000)
            else:
                income_range = (30000, 100000)
            
            customer = {
                'customer_id': customer_id,
                'first_name': self.faker.first_name(),
                'last_name': self.faker.last_name(),
                'date_of_birth': str(self.faker.date_of_birth(minimum_age=age, maximum_age=age)),
                'ssn': self.faker.ssn(),
                'email': self.faker.email(),
                'phone': self.faker.phone_number(),
                'address': self.faker.street_address(),
                'city': self.faker.city(),
                'state': self.faker.state_abbr(),
                'zip_code': self.faker.zipcode(),
                'occupation': self.faker.job(),
                'employer': self.faker.company(),
                'annual_income': random.randint(income_range[0], income_range[1]),
                'credit_score': random.randint(300, 850),
                'customer_segment': random.choice(['Retail', 'Premium', 'Private Banking', 'Mass Market']),
                'risk_category': random.choice(['Low', 'Medium', 'High']),
                'kyc_verified': True,
                'kyc_date': str(self.faker.date_between(start_date=join_date, end_date='today')),
                'join_date': str(join_date),
                'is_active': random.choice([True, False]) if random.random() > 0.95 else True
            }
            customers.append(customer)
            
        return pd.DataFrame(customers)
    
    def generate_accounts(self, num_records: int = 20000) -> pd.DataFrame:
        """Generate bank account data"""
        logger.info(f"Generating {num_records} account records...")
        
        if not self.customer_ids:
            raise ValueError("Generate customers first!")
        
        account_types = {
            'Checking': {'min_balance': 0, 'interest_rate': 0.01},
            'Savings': {'min_balance': 500, 'interest_rate': 0.5},
            'Money Market': {'min_balance': 2500, 'interest_rate': 1.5},
            'CD': {'min_balance': 1000, 'interest_rate': 2.5},
            'Credit Card': {'min_balance': -10000, 'interest_rate': 18.9},
            'Loan': {'min_balance': -100000, 'interest_rate': 5.5}
        }
        
        accounts = []
        for i in range(num_records):
            account_id = f"ACC{i+1:010d}"
            self.account_ids.append(account_id)
            
            account_type = random.choice(list(account_types.keys()))
            acc_config = account_types[account_type]
            
            open_date = self.faker.date_between(start_date='-8y', end_date='today')
            
            # Balance based on account type
            if account_type == 'Credit Card':
                balance = -random.randint(0, 10000)
                credit_limit = random.choice([1000, 2500, 5000, 10000, 25000])
            elif account_type == 'Loan':
                balance = -random.randint(5000, 100000)
                credit_limit = abs(balance)
            else:
                balance = random.randint(acc_config['min_balance'], 50000)
                credit_limit = None
            
            account = {
                'account_id': account_id,
                'customer_id': random.choice(self.customer_ids),
                'account_type': account_type,
                'account_status': random.choice(['Active', 'Inactive', 'Closed']) if random.random() > 0.9 else 'Active',
                'open_date': str(open_date),
                'close_date': str(self.faker.date_between(start_date=open_date, end_date='today')) if random.random() > 0.95 else None,
                'current_balance': balance,
                'available_balance': balance * 0.95 if account_type not in ['Credit Card', 'Loan'] else balance,
                'credit_limit': credit_limit,
                'interest_rate': acc_config['interest_rate'],
                'minimum_balance': acc_config['min_balance'],
                'overdraft_protection': random.choice([True, False]) if account_type == 'Checking' else False,
                'last_statement_date': str(self.faker.date_between(start_date='-30d', end_date='today')),
                'next_statement_date': str(self.faker.date_between(start_date='today', end_date='+30d'))
            }
            accounts.append(account)
            
        return pd.DataFrame(accounts)
    
    def generate_transactions(self, num_records: int = 100000) -> pd.DataFrame:
        """Generate financial transactions"""
        logger.info(f"Generating {num_records} transaction records...")
        
        if not self.account_ids:
            raise ValueError("Generate accounts first!")
        
        transaction_types = [
            'Deposit', 'Withdrawal', 'Transfer', 'Payment', 'Purchase',
            'ATM Withdrawal', 'Check Deposit', 'Wire Transfer', 'Interest',
            'Fee', 'Refund', 'Direct Deposit'
        ]
        
        merchant_categories = [
            'Grocery', 'Gas Station', 'Restaurant', 'Retail', 'Online Shopping',
            'Utilities', 'Healthcare', 'Entertainment', 'Travel', 'Education'
        ]
        
        transactions = []
        for i in range(num_records):
            trans_type = random.choice(transaction_types)
            trans_date = self.faker.date_time_between(start_date='-2y', end_date='now')
            
            # Amount based on transaction type
            if trans_type in ['Deposit', 'Direct Deposit']:
                amount = round(random.uniform(100, 5000), 2)
            elif trans_type == 'Wire Transfer':
                amount = round(random.uniform(500, 50000), 2)
            elif trans_type == 'Fee':
                amount = round(random.uniform(5, 50), 2)
            elif trans_type == 'ATM Withdrawal':
                amount = random.choice([20, 40, 60, 80, 100, 200, 300])
            else:
                amount = round(random.uniform(10, 1000), 2)
            
            transaction = {
                'transaction_id': f"TXN{i+1:012d}",
                'account_id': random.choice(self.account_ids),
                'transaction_date': str(trans_date),
                'transaction_type': trans_type,
                'amount': amount,
                'description': f"{trans_type} - {self.faker.company()}" if trans_type in ['Purchase', 'Payment'] else trans_type,
                'merchant_name': self.faker.company() if trans_type in ['Purchase', 'Payment'] else None,
                'merchant_category': random.choice(merchant_categories) if trans_type in ['Purchase', 'Payment'] else None,
                'channel': random.choice(['Online', 'Mobile', 'ATM', 'Branch', 'Phone']),
                'location': self.faker.city() + ', ' + self.faker.state_abbr(),
                'status': random.choice(['Completed', 'Pending', 'Failed']) if random.random() > 0.98 else 'Completed',
                'fraud_flag': random.choice([True, False]) if random.random() > 0.999 else False,
                'reference_number': self.faker.bothify(text='REF###########')
            }
            transactions.append(transaction)
            
        return pd.DataFrame(transactions)
    
    def generate_credit_cards(self, num_records: int = 5000) -> pd.DataFrame:
        """Generate credit card specific data"""
        logger.info(f"Generating {num_records} credit card records...")
        
        if not self.customer_ids:
            raise ValueError("Generate customers first!")
        
        card_types = ['Visa', 'Mastercard', 'American Express', 'Discover']
        card_tiers = ['Basic', 'Gold', 'Platinum', 'Black']
        
        cards = []
        for i in range(num_records):
            issue_date = self.faker.date_between(start_date='-5y', end_date='today')
            
            card = {
                'card_id': f"CARD{i+1:08d}",
                'customer_id': random.choice(self.customer_ids),
                'card_number': self.faker.credit_card_number(),
                'card_type': random.choice(card_types),
                'card_tier': random.choice(card_tiers),
                'issue_date': str(issue_date),
                'expiry_date': str(issue_date + datetime.timedelta(days=365*3)),
                'credit_limit': random.choice([1000, 2500, 5000, 10000, 25000, 50000]),
                'current_balance': round(random.uniform(0, 10000), 2),
                'available_credit': round(random.uniform(0, 40000), 2),
                'interest_rate': round(random.uniform(12.99, 24.99), 2),
                'annual_fee': random.choice([0, 95, 195, 495]),
                'reward_points': random.randint(0, 100000),
                'payment_due_date': str(self.faker.date_between(start_date='today', end_date='+30d')),
                'minimum_payment': round(random.uniform(25, 500), 2),
                'delinquent': random.choice([True, False]) if random.random() > 0.95 else False,
                'activation_status': 'Active'
            }
            cards.append(card)
            
        return pd.DataFrame(cards)
    
    def generate_loans(self, num_records: int = 3000) -> pd.DataFrame:
        """Generate loan data"""
        logger.info(f"Generating {num_records} loan records...")
        
        if not self.customer_ids:
            raise ValueError("Generate customers first!")
        
        loan_types = {
            'Personal': {'amount_range': (1000, 50000), 'term_range': (12, 60), 'rate_range': (5.99, 19.99)},
            'Auto': {'amount_range': (5000, 75000), 'term_range': (24, 84), 'rate_range': (2.99, 9.99)},
            'Mortgage': {'amount_range': (50000, 1000000), 'term_range': (120, 360), 'rate_range': (2.5, 6.5)},
            'Student': {'amount_range': (5000, 100000), 'term_range': (60, 240), 'rate_range': (3.5, 7.5)},
            'Business': {'amount_range': (10000, 500000), 'term_range': (12, 120), 'rate_range': (4.5, 12.5)}
        }
        
        loans = []
        for i in range(num_records):
            loan_type = random.choice(list(loan_types.keys()))
            loan_config = loan_types[loan_type]
            
            loan_amount = random.randint(loan_config['amount_range'][0], loan_config['amount_range'][1])
            term_months = random.randint(loan_config['term_range'][0], loan_config['term_range'][1])
            interest_rate = round(random.uniform(loan_config['rate_range'][0], loan_config['rate_range'][1]), 2)
            
            origination_date = self.faker.date_between(start_date='-5y', end_date='today')
            
            # Calculate monthly payment (simplified)
            monthly_rate = interest_rate / 100 / 12
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
            
            # Calculate current status
            months_paid = random.randint(0, min(term_months, 60))
            remaining_balance = loan_amount * (1 - months_paid / term_months)
            
            loan = {
                'loan_id': f"LOAN{i+1:08d}",
                'customer_id': random.choice(self.customer_ids),
                'loan_type': loan_type,
                'loan_amount': loan_amount,
                'interest_rate': interest_rate,
                'term_months': term_months,
                'monthly_payment': round(monthly_payment, 2),
                'origination_date': str(origination_date),
                'maturity_date': str(origination_date + datetime.timedelta(days=term_months*30)),
                'remaining_balance': round(remaining_balance, 2),
                'payments_made': months_paid,
                'payments_remaining': term_months - months_paid,
                'loan_status': random.choice(['Current', 'Late', 'Default', 'Paid Off']) if random.random() > 0.9 else 'Current',
                'collateral_type': 'Vehicle' if loan_type == 'Auto' else 'Property' if loan_type == 'Mortgage' else None,
                'collateral_value': loan_amount * 1.2 if loan_type in ['Auto', 'Mortgage'] else None,
                'cosigner': random.choice([True, False]) if random.random() > 0.8 else False
            }
            loans.append(loan)
            
        return pd.DataFrame(loans)
    
    def generate_fraud_cases(self, num_records: int = 1000) -> pd.DataFrame:
        """Generate fraud investigation data"""
        logger.info(f"Generating {num_records} fraud case records...")
        
        fraud_types = [
            'Card Not Present', 'ATM Skimming', 'Account Takeover',
            'Identity Theft', 'Check Fraud', 'Wire Fraud', 'Phishing'
        ]
        
        cases = []
        for i in range(num_records):
            case_date = self.faker.date_between(start_date='-1y', end_date='today')
            
            case = {
                'case_id': f"FRAUD{i+1:06d}",
                'account_id': random.choice(self.account_ids) if self.account_ids else None,
                'fraud_type': random.choice(fraud_types),
                'detection_date': str(case_date),
                'occurrence_date': str(self.faker.date_between(start_date=case_date - datetime.timedelta(days=30), end_date=case_date)),
                'amount_involved': round(random.uniform(100, 50000), 2),
                'detection_method': random.choice(['System Alert', 'Customer Report', 'Manual Review', 'ML Model']),
                'investigation_status': random.choice(['Open', 'Under Investigation', 'Closed', 'Escalated']),
                'resolution': random.choice(['Confirmed Fraud', 'False Positive', 'Pending']) if random.random() > 0.3 else 'Pending',
                'amount_recovered': round(random.uniform(0, 50000), 2) if random.random() > 0.5 else 0,
                'law_enforcement_involved': random.choice([True, False]),
                'customer_reimbursed': random.choice([True, False]),
                'investigator_id': f"INV{random.randint(1, 50):03d}",
                'notes': self.faker.text(max_nb_chars=200)
            }
            cases.append(case)
            
        return pd.DataFrame(cases)
    
    def save_to_hive(self, df: pd.DataFrame, database: str, table_name: str):
        """Save DataFrame to Hive table"""
        logger.info(f"Saving {len(df)} records to {database}.{table_name}")
        
        spark_df = self.spark.createDataFrame(df)
        self.spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")
        spark_df.write.mode("overwrite").saveAsTable(f"{database}.{table_name}")
        
        logger.info(f"Successfully saved to {database}.{table_name}")
    
    def generate_all_financial_data(self):
        """Generate all financial datasets"""
        logger.info("Starting financial data generation...")
        
        # Generate data
        customers_df = self.generate_bank_customers(10000)
        accounts_df = self.generate_accounts(20000)
        transactions_df = self.generate_transactions(100000)
        credit_cards_df = self.generate_credit_cards(5000)
        loans_df = self.generate_loans(3000)
        fraud_cases_df = self.generate_fraud_cases(1000)
        
        # Save to Hive
        self.save_to_hive(customers_df, "financial_analytics", "customers")
        self.save_to_hive(accounts_df, "financial_analytics", "accounts")
        self.save_to_hive(transactions_df, "financial_analytics", "transactions")
        self.save_to_hive(credit_cards_df, "financial_analytics", "credit_cards")
        self.save_to_hive(loans_df, "financial_analytics", "loans")
        self.save_to_hive(fraud_cases_df, "financial_analytics", "fraud_cases")
        
        logger.info("Financial data generation completed!")
        
        # Print summary
        print("\nFinancial Data Generation Summary:")
        print(f"Bank Customers: {len(customers_df):,}")
        print(f"Accounts: {len(accounts_df):,}")
        print(f"Transactions: {len(transactions_df):,}")
        print(f"Credit Cards: {len(credit_cards_df):,}")
        print(f"Loans: {len(loans_df):,}")
        print(f"Fraud Cases: {len(fraud_cases_df):,}")


def main():
    """Main execution function"""
    spark = SparkSession.builder \
        .appName("Financial Data Generator") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .enableHiveSupport() \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    generator = FinancialDataGenerator(spark)
    generator.generate_all_financial_data()
    
    # Sample queries
    print("\nSample Analytics Queries:")
    
    print("1. Account distribution by type:")
    spark.sql("""
        SELECT account_type, COUNT(*) as count, AVG(current_balance) as avg_balance
        FROM financial_analytics.accounts
        WHERE account_status = 'Active'
        GROUP BY account_type
        ORDER BY count DESC
    """).show()
    
    print("2. Fraud detection effectiveness:")
    spark.sql("""
        SELECT detection_method, COUNT(*) as cases, 
               SUM(CASE WHEN resolution = 'Confirmed Fraud' THEN 1 ELSE 0 END) as confirmed,
               AVG(amount_involved) as avg_amount
        FROM financial_analytics.fraud_cases
        GROUP BY detection_method
        ORDER BY cases DESC
    """).show()
    
    spark.stop()


if __name__ == "__main__":
    main()