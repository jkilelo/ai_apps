"""Security hardening: API key encryption and secure storage"""
import os
import base64
import json
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from loguru import logger


class SecureKeyManager:
    """Secure API key management with encryption"""
    
    def __init__(self, key_file: Path = Path(".claude/security/keys.enc")):
        self.key_file = key_file
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Master key location (should be separate from encrypted data)
        self.master_key_file = key_file.parent / "master.key"
        
        # Initialize encryption
        self._fernet = self._get_or_create_encryption_key()
        
        logger.info("Secure key manager initialized")
    
    def _get_or_create_encryption_key(self) -> Fernet:
        """Get or create master encryption key"""
        if self.master_key_file.exists():
            # Load existing key
            with open(self.master_key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            
            # Save key with restricted permissions
            with open(self.master_key_file, 'wb') as f:
                f.write(key)
            
            # Set file permissions (Unix-like systems)
            try:
                os.chmod(self.master_key_file, 0o600)
                logger.info("Created new master encryption key")
            except OSError:
                # Windows doesn't support chmod, but file is still created
                logger.warning("Could not set file permissions (Windows)")
        
        return Fernet(key)
    
    def encrypt_api_key(self, key_name: str, api_key: str, metadata: Optional[Dict] = None) -> bool:
        """Encrypt and store an API key"""
        try:
            # Load existing encrypted data
            encrypted_data = self._load_encrypted_data()
            
            # Prepare key data
            key_data = {
                "api_key": api_key,
                "encrypted_at": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Encrypt the key data
            encrypted_key_data = self._fernet.encrypt(json.dumps(key_data).encode())
            
            # Store in encrypted data structure
            encrypted_data[key_name] = {
                "data": base64.b64encode(encrypted_key_data).decode(),
                "created_at": datetime.now().isoformat(),
                "key_hash": hashlib.sha256(api_key.encode()).hexdigest()[:16]  # For verification
            }
            
            # Save encrypted data
            self._save_encrypted_data(encrypted_data)
            
            logger.info(f"API key encrypted and stored: {key_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to encrypt API key {key_name}: {e}")
            return False
    
    def decrypt_api_key(self, key_name: str) -> Optional[str]:
        """Decrypt and retrieve an API key"""
        try:
            encrypted_data = self._load_encrypted_data()
            
            if key_name not in encrypted_data:
                logger.warning(f"API key not found: {key_name}")
                return None
            
            # Decrypt the key data
            encrypted_key_data = base64.b64decode(encrypted_data[key_name]["data"])
            decrypted_data = self._fernet.decrypt(encrypted_key_data)
            key_data = json.loads(decrypted_data.decode())
            
            logger.debug(f"API key decrypted: {key_name}")
            return key_data["api_key"]
            
        except Exception as e:
            logger.error(f"Failed to decrypt API key {key_name}: {e}")
            return None
    
    def list_stored_keys(self) -> Dict[str, Dict[str, Any]]:
        """List all stored keys with metadata (no actual keys)"""
        try:
            encrypted_data = self._load_encrypted_data()
            
            result = {}
            for key_name, data in encrypted_data.items():
                result[key_name] = {
                    "created_at": data.get("created_at"),
                    "key_hash": data.get("key_hash"),
                    "has_metadata": "metadata" in data
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list stored keys: {e}")
            return {}
    
    def remove_api_key(self, key_name: str) -> bool:
        """Remove an encrypted API key"""
        try:
            encrypted_data = self._load_encrypted_data()
            
            if key_name in encrypted_data:
                del encrypted_data[key_name]
                self._save_encrypted_data(encrypted_data)
                logger.info(f"API key removed: {key_name}")
                return True
            else:
                logger.warning(f"API key not found for removal: {key_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove API key {key_name}: {e}")
            return False
    
    def rotate_master_key(self) -> bool:
        """Rotate the master encryption key and re-encrypt all data"""
        try:
            # Load all current data with old key
            old_data = self._load_encrypted_data()
            all_keys = {}
            
            for key_name in old_data.keys():
                api_key = self.decrypt_api_key(key_name)
                if api_key:
                    all_keys[key_name] = api_key
            
            # Generate new master key
            new_key = Fernet.generate_key()
            
            # Backup old key
            backup_file = self.master_key_file.with_suffix('.key.bak')
            if self.master_key_file.exists():
                self.master_key_file.rename(backup_file)
            
            # Save new master key
            with open(self.master_key_file, 'wb') as f:
                f.write(new_key)
            
            # Update fernet instance
            self._fernet = Fernet(new_key)
            
            # Re-encrypt all data with new key
            for key_name, api_key in all_keys.items():
                self.encrypt_api_key(key_name, api_key)
            
            logger.info("Master key rotated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate master key: {e}")
            return False
    
    def _load_encrypted_data(self) -> Dict[str, Any]:
        """Load encrypted data from file"""
        if not self.key_file.exists():
            return {}
        
        try:
            with open(self.key_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load encrypted data: {e}")
            return {}
    
    def _save_encrypted_data(self, data: Dict[str, Any]) -> None:
        """Save encrypted data to file"""
        with open(self.key_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Set restrictive permissions
        try:
            os.chmod(self.key_file, 0o600)
        except OSError:
            pass  # Windows compatibility


class APIKeyValidator:
    """Validate API key formats and permissions"""
    
    @staticmethod
    def validate_openai_key(api_key: str) -> bool:
        """Validate OpenAI API key format"""
        return (
            isinstance(api_key, str) and
            api_key.startswith('sk-') and
            len(api_key) >= 20
        )
    
    @staticmethod
    def validate_anthropic_key(api_key: str) -> bool:
        """Validate Anthropic API key format"""
        return (
            isinstance(api_key, str) and
            api_key.startswith('sk-ant-') and
            len(api_key) >= 20
        )
    
    @staticmethod
    def validate_google_key(api_key: str) -> bool:
        """Validate Google API key format"""
        return (
            isinstance(api_key, str) and
            len(api_key) >= 20 and
            not api_key.startswith('sk-')
        )
    
    @classmethod
    def validate_key(cls, provider: str, api_key: str) -> bool:
        """Validate API key for specific provider"""
        validators = {
            'openai': cls.validate_openai_key,
            'anthropic': cls.validate_anthropic_key,
            'google': cls.validate_google_key
        }
        
        validator = validators.get(provider.lower())
        if validator:
            return validator(api_key)
        
        # Generic validation for unknown providers
        return isinstance(api_key, str) and len(api_key) >= 10


class SecretSanitizer:
    """Sanitize logs and outputs to prevent key leakage"""
    
    def __init__(self):
        # Patterns to detect potential API keys
        self.key_patterns = [
            r'sk-[a-zA-Z0-9]{48,}',  # OpenAI pattern
            r'sk-ant-[a-zA-Z0-9]{48,}',  # Anthropic pattern
            r'AIza[a-zA-Z0-9]{35,}',  # Google pattern
            r'[a-zA-Z0-9]{32,}',  # Generic long strings
        ]
        
        self.replacement = "[REDACTED_API_KEY]"
    
    def sanitize_string(self, text: str) -> str:
        """Remove potential API keys from string"""
        import re
        
        for pattern in self.key_patterns:
            text = re.sub(pattern, self.replacement, text)
        
        return text
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove potential API keys from dictionary"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_string(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized


class SecurityAuditor:
    """Security audit and compliance checking"""
    
    def __init__(self, secure_key_manager: SecureKeyManager):
        self.key_manager = secure_key_manager
        self.audit_log = []
    
    def audit_key_storage(self) -> Dict[str, Any]:
        """Audit API key storage security"""
        findings = []
        
        # Check file permissions
        try:
            stat_info = os.stat(self.key_manager.key_file)
            file_mode = stat_info.st_mode & 0o777
            
            if file_mode != 0o600:
                findings.append({
                    "severity": "medium",
                    "issue": "Encrypted key file has overly permissive permissions",
                    "file": str(self.key_manager.key_file),
                    "current_permissions": oct(file_mode),
                    "recommended_permissions": "0o600"
                })
        except OSError:
            findings.append({
                "severity": "low", 
                "issue": "Could not check file permissions (Windows system)",
                "recommendation": "Ensure file is in secure location"
            })
        
        # Check master key file
        if not self.key_manager.master_key_file.exists():
            findings.append({
                "severity": "high",
                "issue": "Master key file not found",
                "file": str(self.key_manager.master_key_file)
            })
        
        # Check for .env files in repository
        env_files = [".env", ".env.local", ".env.production"]
        for env_file in env_files:
            if Path(env_file).exists():
                findings.append({
                    "severity": "high", 
                    "issue": f"Environment file {env_file} found - may contain unencrypted keys",
                    "recommendation": "Move keys to encrypted storage"
                })
        
        return {
            "audit_timestamp": datetime.now().isoformat(),
            "findings": findings,
            "total_issues": len(findings),
            "security_score": max(0, 100 - (len(findings) * 10))
        }
    
    def check_key_rotation_needed(self) -> Dict[str, bool]:
        """Check if keys need rotation based on age"""
        stored_keys = self.key_manager.list_stored_keys()
        rotation_needed = {}
        
        rotation_period = timedelta(days=90)  # 90 days
        
        for key_name, metadata in stored_keys.items():
            if metadata.get("created_at"):
                created_at = datetime.fromisoformat(metadata["created_at"])
                age = datetime.now() - created_at
                rotation_needed[key_name] = age > rotation_period
            else:
                rotation_needed[key_name] = True  # Unknown age, recommend rotation
        
        return rotation_needed
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security-related events"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        self.audit_log.append(event)
        
        # Log with appropriate severity
        if event_type in ["key_access_denied", "invalid_key_format", "encryption_failure"]:
            logger.warning(f"Security event: {event_type}", extra={"security": True, **details})
        else:
            logger.info(f"Security event: {event_type}", extra={"security": True, **details})


# Global instances
_secure_key_manager = None
_secret_sanitizer = SecretSanitizer()


def get_secure_key_manager() -> SecureKeyManager:
    """Get or create global secure key manager instance"""
    global _secure_key_manager
    if _secure_key_manager is None:
        _secure_key_manager = SecureKeyManager()
    return _secure_key_manager


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for provider from secure storage"""
    key_manager = get_secure_key_manager()
    
    # Try encrypted storage first
    api_key = key_manager.decrypt_api_key(provider)
    
    if not api_key:
        # Fallback to environment variables (with warning)
        env_var = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        
        if api_key:
            logger.warning(f"Using unencrypted API key from environment: {env_var}")
            
            # Optionally migrate to encrypted storage
            if APIKeyValidator.validate_key(provider, api_key):
                key_manager.encrypt_api_key(provider, api_key, {
                    "source": "environment_migration",
                    "migrated_at": datetime.now().isoformat()
                })
                logger.info(f"Migrated {provider} API key to encrypted storage")
    
    return api_key


def sanitize_for_logging(data: Any) -> Any:
    """Sanitize data before logging to remove secrets"""
    if isinstance(data, str):
        return _secret_sanitizer.sanitize_string(data)
    elif isinstance(data, dict):
        return _secret_sanitizer.sanitize_dict(data)
    else:
        return data