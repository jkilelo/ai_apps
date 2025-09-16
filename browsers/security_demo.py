#!/usr/bin/env python3
"""
Security demonstration script for AI-First Smart Browser

This script demonstrates security features including:
- API key encryption and management
- Rate limiting and quota management
- Security auditing
- Safe secret handling
"""
import asyncio
import os
from pathlib import Path
import json

# Add src to path for local imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from security.encryption import SecureKeyManager, APIKeyValidator, SecretSanitizer, get_api_key
from security.rate_limiter import get_rate_limiter, get_quota_manager, rate_limit
from security.audit import run_security_audit
from common.logger import logger


class SecurityDemo:
    """Demonstration of security features"""
    
    def __init__(self):
        self.secure_key_manager = SecureKeyManager()
        self.rate_limiter = get_rate_limiter()
        self.quota_manager = get_quota_manager()
        self.secret_sanitizer = SecretSanitizer()
    
    def demo_1_key_encryption(self):
        """Demo 1: API key encryption and secure storage"""
        print("\n[LOCKED] Demo 1: API Key Encryption")
        print("-" * 40)
        
        # Example API keys (fake for demo)
        test_keys = {
            "openai": "sk-example1234567890abcdef1234567890abcdef123456",
            "anthropic": "sk-ant-example1234567890abcdef1234567890abcdef123456", 
            "google": "AIzaExample1234567890abcdef1234567890abcdef123456"
        }
        
        # Validate key formats
        for provider, key in test_keys.items():
            is_valid = APIKeyValidator.validate_key(provider, key)
            print(f"  {provider} key format: {'[SUCCESS] Valid' if is_valid else '[ERROR] Invalid'}")
        
        # Encrypt and store keys
        print("\n  Encrypting API keys...")
        for provider, key in test_keys.items():
            success = self.secure_key_manager.encrypt_api_key(
                provider, 
                key,
                metadata={"demo": True, "created_by": "security_demo"}
            )
            print(f"    {provider}: {'[SUCCESS] Encrypted' if success else '[ERROR] Failed'}")
        
        # List stored keys (without revealing actual keys)
        stored_keys = self.secure_key_manager.list_stored_keys()
        print(f"\n  Stored keys: {len(stored_keys)}")
        for name, info in stored_keys.items():
            print(f"    {name}: hash={info['key_hash']}, created={info['created_at']}")
        
        # Demonstrate retrieval
        print("\n  Testing key retrieval...")
        retrieved_key = self.secure_key_manager.decrypt_api_key("openai")
        if retrieved_key and retrieved_key == test_keys["openai"]:
            print("    [SUCCESS] Key retrieval successful")
        else:
            print("    [ERROR] Key retrieval failed")
        
        # Clean up demo keys
        for provider in test_keys.keys():
            self.secure_key_manager.remove_api_key(provider)
        
        print("    [CLEANUP] Demo keys cleaned up")
    
    async def demo_2_rate_limiting(self):
        """Demo 2: Rate limiting and quota management"""
        print("\n[TIMER] Demo 2: Rate Limiting")
        print("-" * 40)
        
        # Test different rate limit scenarios
        test_scenarios = [
            ("openai_gpt4", 1, "Normal request"),
            ("openai_gpt4", 5, "Burst request"),
            ("browser_actions", 10, "Multiple actions"),
        ]
        
        for rule_name, tokens, description in test_scenarios:
            print(f"\n  Testing: {description}")
            
            # Check rate limit status
            status = self.rate_limiter.get_rate_limit_status(rule_name)
            print(f"    Current usage: {status['current_requests']}/{status['max_requests']}")
            
            # Test rate limit check
            allowed, reason = await self.rate_limiter.check_rate_limit(rule_name, tokens)
            print(f"    Request allowed: {'[SUCCESS] Yes' if allowed else f'[ERROR] No - {reason}'}")
            
            if allowed:
                print(f"    [SUCCESS] Consumed {tokens} tokens for {rule_name}")
        
        # Demonstrate rate limit status
        print("\n  Rate limit summary:")
        all_status = self.rate_limiter.get_all_status()
        for rule_name, status in all_status.items():
            usage_pct = (status['current_requests'] / status['max_requests']) * 100
            print(f"    {rule_name}: {usage_pct:.1f}% used")
    
    async def demo_3_quota_management(self):
        """Demo 3: API quota management"""
        print("\n[STATS] Demo 3: Quota Management")
        print("-" * 40)
        
        providers = ["openai", "anthropic", "google"]
        
        for provider in providers:
            # Check current quota status
            status = self.quota_manager.get_quota_status(provider)
            if status:
                print(f"\n  {provider.title()} quota:")
                print(f"    Daily: {status['daily_usage']['used']}/{status['daily_usage']['limit']} tokens")
                print(f"    Cost: ${status['cost_usage']['used']:.2f}/${status['cost_usage']['limit']:.2f}")
                
                # Simulate quota consumption
                test_tokens = 1000
                test_cost = 0.02
                
                allowed, reason = self.quota_manager.check_quota(provider, test_tokens, test_cost)
                if allowed:
                    success = self.quota_manager.consume_quota(provider, test_tokens, test_cost)
                    print(f"    [SUCCESS] Consumed {test_tokens} tokens, ${test_cost:.2f}")
                else:
                    print(f"    [ERROR] Quota check failed: {reason}")
        
        print("\n  [CHART] Quota usage summary complete")
    
    def demo_4_secret_sanitization(self):
        """Demo 4: Secret sanitization for logging"""
        print("\n[CLEANUP] Demo 4: Secret Sanitization")
        print("-" * 40)
        
        # Example data with secrets
        test_data = {
            "user_input": "Use API key sk-1234567890abcdef to call OpenAI",
            "config": {
                "api_key": "sk-ant-abcdef1234567890",
                "database_url": "postgresql://user:password@localhost/db"
            },
            "logs": [
                "Request sent with key AIzaAbcDef1234567890",
                "Authentication successful for user@example.com"
            ]
        }
        
        print("  Original data (UNSAFE for logging):")
        print(f"    {json.dumps(test_data, indent=4)}")
        
        print("\n  Sanitized data (SAFE for logging):")
        sanitized = self.secret_sanitizer.sanitize_dict(test_data)
        print(f"    {json.dumps(sanitized, indent=4)}")
        
        # Test string sanitization
        unsafe_string = "Error with API key sk-1234567890abcdef1234567890abcdef"
        safe_string = self.secret_sanitizer.sanitize_string(unsafe_string)
        
        print(f"\n  String sanitization:")
        print(f"    Unsafe: {unsafe_string}")
        print(f"    Safe:   {safe_string}")
    
    async def demo_5_security_audit(self):
        """Demo 5: Security auditing"""
        print("\n[SEARCH] Demo 5: Security Audit")
        print("-" * 40)
        
        # Run comprehensive security audit
        print("  Running security audit (this may take a moment)...")
        
        try:
            audit_result = run_security_audit(Path("."))
            
            # Display audit summary
            summary = audit_result["summary"]
            print(f"\n  Audit Results:")
            print(f"    Security Score: {summary['security_score']}/100")
            print(f"    Total Findings: {summary['total_findings']}")
            
            # Show severity breakdown
            severity = summary["severity_breakdown"]
            print(f"    Critical: {severity['critical']}")
            print(f"    High:     {severity['high']}")
            print(f"    Medium:   {severity['medium']}")
            print(f"    Low:      {severity['low']}")
            
            # Show category breakdown
            categories = summary["category_breakdown"]
            print(f"\n  Issues by category:")
            for category, count in categories.items():
                print(f"    {category}: {count}")
            
            # Show compliance summary
            compliance = audit_result["compliance"]["summary"]
            print(f"\n  Compliance summary:")
            for standard, results in compliance.items():
                total_checks = sum(results.values())
                passed = results.get("pass", 0)
                print(f"    {standard}: {passed}/{total_checks} checks passed")
            
            # Save detailed audit report
            report_path = Path("examples/outputs/security_audit.json")
            with open(report_path, 'w') as f:
                json.dump(audit_result, f, indent=2)
            
            print(f"\n    [REPORT] Detailed report saved: {report_path}")
            
            # Show top recommendations
            recommendations = audit_result.get("recommendations", [])
            if recommendations:
                print(f"\n  Top recommendations:")
                for rec in recommendations[:3]:
                    print(f"    {rec['priority'].upper()}: {rec['action']}")
        
        except Exception as e:
            print(f"    [ERROR] Audit failed: {e}")
    
    async def demo_6_secure_api_usage(self):
        """Demo 6: Secure API key usage in practice"""
        print("\n[KEY] Demo 6: Secure API Usage")
        print("-" * 40)
        
        # Demonstrate secure API key retrieval
        providers = ["openai", "anthropic", "google"]
        
        for provider in providers:
            print(f"\n  Testing {provider} API key access:")
            
            # Try to get API key securely
            api_key = get_api_key(provider)
            
            if api_key:
                # Sanitize for logging
                safe_key = self.secret_sanitizer.sanitize_string(api_key)
                print(f"    [SUCCESS] Key retrieved: {safe_key}")
                
                # Check rate limits before API call
                allowed, reason = await self.rate_limiter.check_rate_limit(f"{provider}_api", 1)
                if allowed:
                    print(f"    [SUCCESS] Rate limit check passed")
                    
                    # Check quotas
                    quota_ok, quota_reason = self.quota_manager.check_quota(provider, 1000, 0.01)
                    if quota_ok:
                        print(f"    [SUCCESS] Quota check passed")
                        # Here you would make the actual API call
                        print(f"    [SIGNAL] (API call would be made here)")
                    else:
                        print(f"    [ERROR] Quota exceeded: {quota_reason}")
                else:
                    print(f"    [ERROR] Rate limited: {reason}")
            else:
                print(f"    [WARNING] No API key configured for {provider}")
    
    async def run_all_demos(self):
        """Run all security demonstrations"""
        print("[SECURITY] AI-First Smart Browser - Security Demonstration")
        print("=" * 60)
        
        try:
            # Create output directory
            Path("examples/outputs").mkdir(exist_ok=True, parents=True)
            
            # Run all demos
            self.demo_1_key_encryption()
            await self.demo_2_rate_limiting()
            await self.demo_3_quota_management()
            self.demo_4_secret_sanitization()
            await self.demo_5_security_audit()
            await self.demo_6_secure_api_usage()
            
            print("\n" + "=" * 60)
            print("[SUCCESS] All security demonstrations completed!")
            print("\n[SECURE] Key takeaways:")
            print("  • API keys are encrypted at rest")
            print("  • Rate limiting prevents API abuse")
            print("  • Quotas control costs and usage")
            print("  • Secrets are sanitized in logs")
            print("  • Regular security audits identify issues")
            print("  • Secure patterns are easy to implement")
            
        except Exception as e:
            logger.error(f"Security demo failed: {e}")
            raise


async def main():
    """Main execution function"""
    # Check if running in secure environment
    if os.path.exists(".env"):
        print("[WARNING]  Warning: .env file detected in project root")
        print("   This file may contain unencrypted secrets")
        print("   Consider using encrypted storage instead\n")
    
    # Run security demonstrations
    demo = SecurityDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[WARNING] Security demo interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Security demo failed: {e}")
        sys.exit(1)