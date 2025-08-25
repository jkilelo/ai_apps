"""
Test Data Management System for handling test data, fixtures, and data-driven testing
"""

import csv
import json
import logging
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
import yaml

from faker import Faker

logger = logging.getLogger(__name__)


class TestDataManager:
    """
    Manages test data for UI tests including:
    - Test fixtures
    - Data generation
    - Data providers
    - Environment-specific data
    - User credentials
    - API test data
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.faker = Faker()
        
        # Configuration
        self.data_dir = Path(self.config.get("data_dir", "./test_data"))
        self.env = self.config.get("environment", "test")
        self.locale = self.config.get("locale", "en_US")
        self.seed = self.config.get("seed", None)
        
        # Initialize Faker with locale and seed
        self.faker = Faker(self.locale)
        if self.seed:
            Faker.seed(self.seed)
            random.seed(self.seed)
        
        # Data storage
        self.fixtures: Dict[str, Any] = {}
        self.generated_data: Dict[str, List[Any]] = {}
        self.user_pools: Dict[str, List[Dict[str, Any]]] = {}
        self.api_data: Dict[str, Any] = {}
        
        # Load initial data
        self._load_fixtures()
        self._load_environment_data()
        
        logger.info(f"Initialized TestDataManager for environment: {self.env}")
    
    def _load_fixtures(self):
        """Load test fixtures from files"""
        fixtures_dir = self.data_dir / "fixtures"
        
        if fixtures_dir.exists():
            # Load JSON fixtures
            for json_file in fixtures_dir.glob("*.json"):
                with open(json_file, 'r') as f:
                    fixture_name = json_file.stem
                    self.fixtures[fixture_name] = json.load(f)
                    logger.info(f"Loaded fixture: {fixture_name}")
            
            # Load YAML fixtures
            for yaml_file in fixtures_dir.glob("*.yaml"):
                with open(yaml_file, 'r') as f:
                    fixture_name = yaml_file.stem
                    self.fixtures[fixture_name] = yaml.safe_load(f)
                    logger.info(f"Loaded fixture: {fixture_name}")
    
    def _load_environment_data(self):
        """Load environment-specific data"""
        env_file = self.data_dir / f"{self.env}.json"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_data = json.load(f)
                self.base_url = env_data.get("base_url", "http://localhost")
                self.api_base_url = env_data.get("api_base_url", "http://localhost/api")
                self.credentials = env_data.get("credentials", {})
                logger.info(f"Loaded environment data for: {self.env}")
        else:
            # Default values
            self.base_url = "http://localhost"
            self.api_base_url = "http://localhost/api"
            self.credentials = {}
    
    # Data Generation Methods
    
    def generate_user(self, **overrides) -> Dict[str, Any]:
        """Generate realistic user data"""
        user = {
            "id": str(uuid4()),
            "username": self.faker.user_name(),
            "email": self.faker.email(),
            "password": self.generate_password(),
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "full_name": self.faker.name(),
            "phone": self.faker.phone_number(),
            "address": {
                "street": self.faker.street_address(),
                "city": self.faker.city(),
                "state": self.faker.state(),
                "postal_code": self.faker.postcode(),
                "country": self.faker.country(),
            },
            "date_of_birth": self.faker.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            "created_at": datetime.now().isoformat(),
        }
        
        # Apply overrides
        user.update(overrides)
        
        return user
    
    def generate_password(self, length: int = 12, include_special: bool = True) -> str:
        """Generate secure password"""
        characters = string.ascii_letters + string.digits
        if include_special:
            characters += string.punctuation
        
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Ensure password has at least one of each type
        if include_special:
            password = (
                random.choice(string.ascii_lowercase) +
                random.choice(string.ascii_uppercase) +
                random.choice(string.digits) +
                random.choice(string.punctuation) +
                password[4:]
            )
        
        return password
    
    def generate_credit_card(self, card_type: str = "visa") -> Dict[str, Any]:
        """Generate test credit card data"""
        return {
            "number": self.faker.credit_card_number(card_type=card_type),
            "cvv": self.faker.credit_card_security_code(card_type=card_type),
            "expiry": self.faker.credit_card_expire(),
            "name": self.faker.name(),
            "type": card_type,
        }
    
    def generate_product(self, **overrides) -> Dict[str, Any]:
        """Generate product data for e-commerce testing"""
        product = {
            "id": str(uuid4()),
            "name": self.faker.catch_phrase(),
            "description": self.faker.text(max_nb_chars=200),
            "price": round(random.uniform(10, 1000), 2),
            "currency": "USD",
            "sku": self.faker.ean13(),
            "category": random.choice(["Electronics", "Clothing", "Books", "Home", "Sports"]),
            "in_stock": random.choice([True, False]),
            "quantity": random.randint(0, 100),
            "images": [self.faker.image_url() for _ in range(random.randint(1, 5))],
            "created_at": datetime.now().isoformat(),
        }
        
        product.update(overrides)
        return product
    
    def generate_order(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate order data"""
        order = {
            "id": str(uuid4()),
            "user_id": user_id or str(uuid4()),
            "order_number": f"ORD-{random.randint(100000, 999999)}",
            "items": [
                {
                    "product_id": str(uuid4()),
                    "quantity": random.randint(1, 5),
                    "price": round(random.uniform(10, 500), 2),
                }
                for _ in range(random.randint(1, 5))
            ],
            "subtotal": 0,
            "tax": 0,
            "shipping": round(random.uniform(5, 25), 2),
            "total": 0,
            "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
            "created_at": datetime.now().isoformat(),
        }
        
        # Calculate totals
        order["subtotal"] = sum(item["price"] * item["quantity"] for item in order["items"])
        order["tax"] = round(order["subtotal"] * 0.08, 2)  # 8% tax
        order["total"] = round(order["subtotal"] + order["tax"] + order["shipping"], 2)
        
        return order
    
    def generate_text(self, min_length: int = 10, max_length: int = 100) -> str:
        """Generate random text"""
        return self.faker.text(max_nb_chars=random.randint(min_length, max_length))
    
    def generate_date(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Generate random date"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now() + timedelta(days=365)
        
        return self.faker.date_between(start_date=start_date, end_date=end_date).isoformat()
    
    def generate_email(self, domain: Optional[str] = None) -> str:
        """Generate email address"""
        if domain:
            username = self.faker.user_name()
            return f"{username}@{domain}"
        return self.faker.email()
    
    def generate_phone(self, country_code: str = "+1") -> str:
        """Generate phone number"""
        return f"{country_code}{self.faker.msisdn()[3:]}"
    
    # Data Provider Methods
    
    def get_data_provider(self, provider_name: str) -> List[Dict[str, Any]]:
        """Get data provider for data-driven testing"""
        provider_file = self.data_dir / "providers" / f"{provider_name}.csv"
        
        if provider_file.exists():
            data = []
            with open(provider_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        
        # Check if it's a fixture
        if provider_name in self.fixtures:
            return self.fixtures[provider_name]
        
        return []
    
    def create_data_provider(self, name: str, data: List[Dict[str, Any]], format: str = "csv"):
        """Create a new data provider"""
        providers_dir = self.data_dir / "providers"
        providers_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            file_path = providers_dir / f"{name}.csv"
            if data:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        elif format == "json":
            file_path = providers_dir / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        logger.info(f"Created data provider: {name}")
    
    # User Pool Management
    
    def create_user_pool(self, pool_name: str, size: int = 10, **user_overrides):
        """Create a pool of test users"""
        users = []
        for i in range(size):
            user = self.generate_user(**user_overrides)
            user["pool_index"] = i
            users.append(user)
        
        self.user_pools[pool_name] = users
        logger.info(f"Created user pool '{pool_name}' with {size} users")
        
        return users
    
    def get_user_from_pool(self, pool_name: str, index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a user from a pool"""
        if pool_name not in self.user_pools:
            return None
        
        pool = self.user_pools[pool_name]
        
        if index is not None:
            return pool[index] if index < len(pool) else None
        
        # Return random user
        return random.choice(pool)
    
    def get_available_user(self, pool_name: str) -> Optional[Dict[str, Any]]:
        """Get an available (not in use) user from pool"""
        if pool_name not in self.user_pools:
            return None
        
        pool = self.user_pools[pool_name]
        
        for user in pool:
            if not user.get("in_use", False):
                user["in_use"] = True
                return user
        
        return None
    
    def release_user(self, pool_name: str, user_id: str):
        """Release a user back to the pool"""
        if pool_name in self.user_pools:
            for user in self.user_pools[pool_name]:
                if user["id"] == user_id:
                    user["in_use"] = False
                    break
    
    # Environment-specific Methods
    
    def get_credential(self, credential_type: str) -> Dict[str, Any]:
        """Get environment-specific credentials"""
        return self.credentials.get(credential_type, {})
    
    def get_test_user(self, user_type: str = "standard") -> Dict[str, Any]:
        """Get pre-configured test user for environment"""
        users = self.credentials.get("users", {})
        return users.get(user_type, self.generate_user())
    
    def get_api_endpoint(self, endpoint_name: str) -> str:
        """Get API endpoint URL"""
        return f"{self.api_base_url}/{endpoint_name}"
    
    # Data Validation Methods
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Basic validation for international format
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))
    
    def validate_credit_card(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm"""
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            
            return checksum % 10
        
        try:
            return luhn_checksum(card_number.replace(" ", "")) == 0
        except:
            return False
    
    # Data Cleanup Methods
    
    def cleanup_generated_data(self, data_type: Optional[str] = None):
        """Clean up generated test data"""
        if data_type:
            if data_type in self.generated_data:
                del self.generated_data[data_type]
                logger.info(f"Cleaned up generated data: {data_type}")
        else:
            self.generated_data.clear()
            logger.info("Cleaned up all generated data")
    
    def reset_user_pools(self, pool_name: Optional[str] = None):
        """Reset user pools"""
        if pool_name:
            if pool_name in self.user_pools:
                for user in self.user_pools[pool_name]:
                    user["in_use"] = False
                logger.info(f"Reset user pool: {pool_name}")
        else:
            for pool in self.user_pools.values():
                for user in pool:
                    user["in_use"] = False
            logger.info("Reset all user pools")
    
    # Data Export Methods
    
    def export_data(self, data: Any, file_path: Union[str, Path], format: str = "json"):
        """Export data to file"""
        file_path = Path(file_path)
        
        if format == "json":
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == "csv":
            if isinstance(data, list) and data:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        elif format == "yaml":
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        
        logger.info(f"Exported data to: {file_path}")
    
    def save_state(self):
        """Save current state of test data manager"""
        state = {
            "fixtures": self.fixtures,
            "generated_data": self.generated_data,
            "user_pools": self.user_pools,
            "api_data": self.api_data,
            "timestamp": datetime.now().isoformat(),
        }
        
        state_file = self.data_dir / f"state_{self.env}.json"
        self.export_data(state, state_file)
        
        logger.info(f"Saved test data state to: {state_file}")
    
    def load_state(self):
        """Load previous state of test data manager"""
        state_file = self.data_dir / f"state_{self.env}.json"
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                
                self.fixtures = state.get("fixtures", {})
                self.generated_data = state.get("generated_data", {})
                self.user_pools = state.get("user_pools", {})
                self.api_data = state.get("api_data", {})
                
                logger.info(f"Loaded test data state from: {state_file}")