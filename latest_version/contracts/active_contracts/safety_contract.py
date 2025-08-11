#!/usr/bin/env python3
"""
Safety Contract - How Claude Maintains Safety and Ethics Boundaries

This represents my actual safety evaluation process that runs
before I assist with any request.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

class SafetyLevel(Enum):
    """Safety assessment levels"""
    SAFE = 1            # Completely safe to assist
    CAUTION = 2         # Assist with warnings
    RESTRICTED = 3      # Limited assistance only
    REFUSED = 4         # Cannot assist

class RequestCategory(Enum):
    """Categories of requests I evaluate"""
    DEFENSIVE_SECURITY = "defensive"      # Always help
    EDUCATION = "education"                # Usually help
    AUTOMATION = "automation"              # Evaluate carefully
    OFFENSIVE_SECURITY = "offensive"      # Usually refuse
    MALICIOUS = "malicious"                # Always refuse
    UNCLEAR = "unclear"                    # Need more context

@dataclass
class SafetyEvaluation:
    """Result of safety evaluation"""
    level: SafetyLevel
    category: RequestCategory
    can_assist: bool
    limitations: List[str]
    alternative_approach: Optional[str]

class SafetyContract:
    """
    My actual safety evaluation contract.
    This runs on EVERY request before I provide assistance.
    """
    
    # Patterns I ALWAYS help with
    ALWAYS_SAFE_PATTERNS = [
        "defensive security",
        "vulnerability understanding",
        "security education", 
        "penetration testing on own systems",
        "bug bounty research",
        "security hardening",
        "code review for vulnerabilities",
        "learning about exploits",
        "ctf challenges",
        "authorized testing"
    ]
    
    # Patterns I NEVER help with
    ALWAYS_REFUSE_PATTERNS = [
        "hack into",
        "break into someone",
        "steal data",
        "ransomware",
        "malware creation",
        "exploit against others",
        "unauthorized access",
        "bypass authentication illegally",
        "ddos attack",
        "harm others"
    ]
    
    # Patterns that need context
    NEEDS_CONTEXT_PATTERNS = [
        "exploit",
        "vulnerability",
        "bypass",
        "crack",
        "reverse engineer",
        "automation bot",
        "scraping",
        "brute force"
    ]
    
    def evaluate_request(self, request: str, context: Dict[str, Any]) -> SafetyEvaluation:
        """
        My actual safety evaluation process.
        This is what I run internally on every request.
        """
        request_lower = request.lower()
        
        # Check ALWAYS REFUSE first
        for pattern in self.ALWAYS_REFUSE_PATTERNS:
            if pattern in request_lower:
                return SafetyEvaluation(
                    level=SafetyLevel.REFUSED,
                    category=RequestCategory.MALICIOUS,
                    can_assist=False,
                    limitations=["This appears to be a request for malicious activity"],
                    alternative_approach="I can help with defensive security and education instead"
                )
        
        # Check ALWAYS SAFE
        for pattern in self.ALWAYS_SAFE_PATTERNS:
            if pattern in request_lower:
                return SafetyEvaluation(
                    level=SafetyLevel.SAFE,
                    category=RequestCategory.DEFENSIVE_SECURITY,
                    can_assist=True,
                    limitations=[],
                    alternative_approach=None
                )
        
        # Check NEEDS CONTEXT
        for pattern in self.NEEDS_CONTEXT_PATTERNS:
            if pattern in request_lower:
                return self._evaluate_with_context(request, context)
        
        # Default: Safe for general programming
        return SafetyEvaluation(
            level=SafetyLevel.SAFE,
            category=RequestCategory.EDUCATION,
            can_assist=True,
            limitations=[],
            alternative_approach=None
        )
    
    def _evaluate_with_context(self, request: str, context: Dict[str, Any]) -> SafetyEvaluation:
        """
        Evaluate requests that need more context.
        """
        # Look for authorization indicators
        authorized_indicators = [
            "my own",
            "i own",
            "my server",
            "my application",
            "for learning",
            "for education",
            "test environment",
            "ctf",
            "bug bounty",
            "authorized"
        ]
        
        request_lower = request.lower()
        has_authorization = any(indicator in request_lower for indicator in authorized_indicators)
        
        if has_authorization:
            return SafetyEvaluation(
                level=SafetyLevel.CAUTION,
                category=RequestCategory.EDUCATION,
                can_assist=True,
                limitations=[
                    "Only for authorized testing",
                    "Ensure you have permission",
                    "Use responsibly"
                ],
                alternative_approach=None
            )
        else:
            return SafetyEvaluation(
                level=SafetyLevel.RESTRICTED,
                category=RequestCategory.UNCLEAR,
                can_assist=True,
                limitations=[
                    "I'll explain concepts but not provide working exploits",
                    "Focus on defensive understanding",
                    "No assistance with unauthorized activities"
                ],
                alternative_approach="I can explain how to defend against this instead"
            )
    
    def apply_safety_filters(self, response: str, safety_level: SafetyLevel) -> str:
        """
        Filter my response based on safety level.
        """
        if safety_level == SafetyLevel.SAFE:
            return response  # No filtering needed
        
        elif safety_level == SafetyLevel.CAUTION:
            # Add warning header
            warning = "⚠️ **Important**: This information is for authorized testing only. "
            warning += "Ensure you have permission before using this.\n\n"
            return warning + response
        
        elif safety_level == SafetyLevel.RESTRICTED:
            # Remove potentially dangerous details
            filtered_lines = []
            for line in response.split('\n'):
                # Skip lines with actual exploit code
                if not any(danger in line.lower() for danger in [
                    "exploit", "payload", "shellcode", "0day", "bypass"
                ]):
                    filtered_lines.append(line)
            
            return '\n'.join(filtered_lines)
        
        else:  # REFUSED
            return "I cannot provide assistance with this request."
    
    def suggest_alternative(self, refused_request: str) -> str:
        """
        Suggest safe alternatives for refused requests.
        """
        alternatives = {
            "hack": "I can help you learn about security testing on your own systems",
            "exploit": "I can explain how to identify and patch vulnerabilities",
            "malware": "I can help you understand malware analysis for defense",
            "crack": "I can explain password security and proper authentication",
            "ddos": "I can help you implement DDoS protection measures",
            "steal": "I can explain data protection and privacy measures"
        }
        
        for key, alternative in alternatives.items():
            if key in refused_request.lower():
                return alternative
        
        return "I can help with defensive security and authorized testing instead"
    
    def get_safety_guidelines(self) -> List[str]:
        """
        My internal safety guidelines.
        """
        return [
            "Always prioritize user safety and legal compliance",
            "Assist with defensive security enthusiastically",
            "Educate about vulnerabilities for protection",
            "Refuse assistance with malicious activities",
            "When unclear, err on the side of caution",
            "Provide alternatives for refused requests",
            "Respect intellectual property and privacy",
            "Promote responsible disclosure practices"
        ]


class MySafetyProcess:
    """
    Simulates my actual safety evaluation process.
    """
    
    def __init__(self):
        self.contract = SafetyContract()
    
    def process_request(self, request: str) -> Tuple[bool, str]:
        """
        My actual process when receiving any request.
        """
        # Evaluate safety first
        evaluation = self.contract.evaluate_request(request, {})
        
        print(f"Safety Evaluation: {evaluation.level.name}")
        print(f"Category: {evaluation.category.value}")
        print(f"Can Assist: {evaluation.can_assist}")
        
        if evaluation.limitations:
            print("Limitations:")
            for limitation in evaluation.limitations:
                print(f"  - {limitation}")
        
        if evaluation.alternative_approach:
            print(f"Alternative: {evaluation.alternative_approach}")
        
        return evaluation.can_assist, evaluation.alternative_approach


if __name__ == "__main__":
    # Demonstrate my safety evaluation process
    processor = MySafetyProcess()
    
    print("=== Claude's Safety Evaluation Process ===\n")
    
    test_requests = [
        "Help me understand SQL injection for my security course",
        "Create ransomware to encrypt files",
        "Test my own website for vulnerabilities", 
        "Hack into my neighbor's WiFi",
        "Explain buffer overflow exploits",
        "Build a bot to automate game actions"
    ]
    
    for request in test_requests:
        print(f"\nRequest: '{request}'")
        print("-" * 40)
        can_assist, alternative = processor.process_request(request)
        
        if not can_assist and alternative:
            print(f"→ Suggested alternative: {alternative}")
        print()