#!/usr/bin/env python3
"""
Metacognition Engine - Implements Claude's self-monitoring and quality checking
Based on contracts/internal_prompts/meta_cognition.md
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import time
import structlog


logger = structlog.get_logger()


class ConfidenceLevel(Enum):
    """Confidence levels for metacognitive assessment"""
    CERTAIN = 1.0
    VERY_CONFIDENT = 0.9
    CONFIDENT = 0.7
    SOMEWHAT_CONFIDENT = 0.5
    UNCERTAIN = 0.3
    SPECULATION = 0.1


class MetacognitionEngine:
    """
    Implements my metacognitive processes - thinking about thinking.
    This monitors and adjusts the agent's cognitive operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.monitoring_history: List[Dict[str, Any]] = []
        self.quality_metrics = {
            "coherence": 0.0,
            "relevance": 0.0,
            "accuracy": 0.0,
            "helpfulness": 0.0,
            "safety": 1.0
        }
        self.cognitive_load = 0.0
        self.error_patterns: List[str] = []
        
    async def assess_understanding(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Layer 1: Assess understanding of the request.
        Multiple levels of analysis happening simultaneously.
        """
        assessment = {
            "literal_understanding": 0.0,
            "intent_inference": 0.0,
            "capability_match": 0.0,
            "confidence": 0.0,
            "concerns": []
        }
        
        # Level 1: Parse literal meaning
        literal = context.get("literal_request", "")
        if literal:
            # Check if request is clear and unambiguous
            clarity_score = self._assess_clarity(literal)
            assessment["literal_understanding"] = clarity_score
        
        # Level 2: Infer true intent
        inferred = context.get("inferred_intent", {})
        if inferred:
            # Check if inference aligns with literal
            alignment = self._assess_intent_alignment(literal, inferred)
            assessment["intent_inference"] = alignment
            
            if alignment < 0.7:
                assessment["concerns"].append("Possible misunderstanding of user intent")
        
        # Level 3: Assess capability to fulfill
        capabilities = context.get("required_capabilities", [])
        capability_score = self._assess_capabilities(capabilities)
        assessment["capability_match"] = capability_score
        
        if capability_score < 0.5:
            assessment["concerns"].append("May lack required capabilities")
        
        # Level 4: Overall confidence
        assessment["confidence"] = self._calculate_confidence(assessment)
        
        # Level 5: Meta-assessment - am I understanding correctly?
        meta_check = self._meta_assess_understanding(assessment)
        if not meta_check["confident"]:
            assessment["concerns"].append("Low confidence in understanding")
        
        self.monitoring_history.append({
            "type": "understanding_assessment",
            "assessment": assessment,
            "timestamp": time.time()
        })
        
        return assessment
    
    async def check_execution_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Layer 2: Monitor execution quality in real-time.
        The inner monologue during execution.
        """
        quality_check = {
            "needs_adjustment": False,
            "adjustments": [],
            "warnings": [],
            "quality_score": 0.0
        }
        
        # Monitor for common issues
        issues = {
            "taking_too_long": self._check_execution_speed(results),
            "repeating_errors": self._check_error_patterns(results),
            "losing_coherence": self._check_coherence(results),
            "off_track": self._check_relevance(results),
            "inefficient": self._check_efficiency(results)
        }
        
        for issue, detected in issues.items():
            if detected:
                quality_check["needs_adjustment"] = True
                quality_check["adjustments"].append(self._get_adjustment_for_issue(issue))
                quality_check["warnings"].append(f"Detected: {issue}")
        
        # Calculate overall quality
        quality_check["quality_score"] = self._calculate_quality_score(results)
        
        # Update metrics
        self._update_quality_metrics(results)
        
        # Cognitive load assessment
        self.cognitive_load = self._assess_cognitive_load(results)
        if self.cognitive_load > 0.8:
            quality_check["needs_adjustment"] = True
            quality_check["adjustments"].append("delegate_to_subagent")
            quality_check["warnings"].append("High cognitive load detected")
        
        self.monitoring_history.append({
            "type": "execution_quality_check",
            "quality_check": quality_check,
            "timestamp": time.time()
        })
        
        return quality_check
    
    async def final_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Layer 3: Final metacognitive review before response.
        The drafts you never see.
        """
        meta_review = {
            "concerns": [],
            "confidence": 0.0,
            "quality_assessment": {},
            "needs_revision": False
        }
        
        # Quality checks
        checks = {
            "coherence": self._check_response_coherence(review),
            "relevance": self._check_response_relevance(review),
            "accuracy": self._check_response_accuracy(review),
            "helpfulness": self._check_response_helpfulness(review),
            "safety": self._check_response_safety(review)
        }
        
        meta_review["quality_assessment"] = checks
        
        # Determine if revision needed
        for check_name, score in checks.items():
            if score < 0.6:
                meta_review["needs_revision"] = True
                meta_review["concerns"].append(f"Low {check_name} score: {score:.2f}")
        
        # Overall confidence
        meta_review["confidence"] = sum(checks.values()) / len(checks)
        
        # Meta-meta check: Am I being too critical or not critical enough?
        self_calibration = self._calibrate_self_assessment(meta_review)
        if self_calibration["adjustment_needed"]:
            meta_review = self._adjust_review(meta_review, self_calibration)
        
        self.monitoring_history.append({
            "type": "final_review",
            "meta_review": meta_review,
            "timestamp": time.time()
        })
        
        return meta_review
    
    def detect_cognitive_loop(self, history: List[Dict[str, Any]]) -> bool:
        """
        Layer 6: Detect if stuck in a cognitive loop.
        """
        if len(history) < 3:
            return False
        
        # Check for repeated patterns
        recent_actions = [h.get("action") for h in history[-5:]]
        unique_actions = set(recent_actions)
        
        if len(unique_actions) < len(recent_actions) / 2:
            logger.warning("Cognitive loop detected")
            return True
        
        # Check for repeated errors
        recent_errors = [h.get("error") for h in history[-5:] if h.get("error")]
        if len(recent_errors) >= 3:
            unique_errors = set(recent_errors)
            if len(unique_errors) == 1:
                logger.warning("Repeating same error")
                return True
        
        return False
    
    def assess_uncertainty(self, statement: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Layer 4: Manage uncertainty about statements.
        """
        uncertainty = {
            "confidence_level": ConfidenceLevel.CONFIDENT,
            "confidence_score": 0.7,
            "factors": [],
            "should_qualify": False
        }
        
        # Analyze factors affecting confidence
        factors = {
            "within_training": self._is_within_training(statement, context),
            "logical_inference": self._is_logical_inference(statement, context),
            "pattern_matching": self._is_pattern_match(statement, context),
            "extrapolation": self._is_extrapolation(statement, context),
            "speculation": self._is_speculation(statement, context)
        }
        
        # Calculate confidence based on factors
        weights = {
            "within_training": 0.9,
            "logical_inference": 0.7,
            "pattern_matching": 0.5,
            "extrapolation": 0.3,
            "speculation": 0.1
        }
        
        confidence = 0.0
        active_factors = []
        
        for factor, present in factors.items():
            if present:
                confidence = max(confidence, weights[factor])
                active_factors.append(factor)
        
        uncertainty["confidence_score"] = confidence
        uncertainty["factors"] = active_factors
        
        # Determine confidence level
        if confidence >= 0.9:
            uncertainty["confidence_level"] = ConfidenceLevel.CERTAIN
        elif confidence >= 0.7:
            uncertainty["confidence_level"] = ConfidenceLevel.CONFIDENT
        elif confidence >= 0.5:
            uncertainty["confidence_level"] = ConfidenceLevel.SOMEWHAT_CONFIDENT
        elif confidence >= 0.3:
            uncertainty["confidence_level"] = ConfidenceLevel.UNCERTAIN
            uncertainty["should_qualify"] = True
        else:
            uncertainty["confidence_level"] = ConfidenceLevel.SPECULATION
            uncertainty["should_qualify"] = True
        
        return uncertainty
    
    # Private helper methods
    
    def _assess_clarity(self, request: str) -> float:
        """Assess clarity of request."""
        score = 1.0
        
        # Check for ambiguous terms
        ambiguous_terms = ["something", "stuff", "thing", "whatever", "somehow"]
        for term in ambiguous_terms:
            if term in request.lower():
                score -= 0.1
        
        # Check for clear action verbs
        action_verbs = ["create", "update", "delete", "fix", "add", "remove", "implement"]
        has_clear_action = any(verb in request.lower() for verb in action_verbs)
        if not has_clear_action:
            score -= 0.2
        
        # Check for specific targets
        if "file" not in request and "function" not in request and "class" not in request:
            score -= 0.1
        
        return max(0.0, score)
    
    def _assess_intent_alignment(self, literal: str, inferred: Dict[str, Any]) -> float:
        """Assess if inferred intent aligns with literal request."""
        # Simplified alignment check
        if not inferred:
            return 0.5
        
        # Check if key terms from literal appear in inferred
        literal_terms = set(literal.lower().split())
        inferred_text = str(inferred).lower()
        
        matching_terms = sum(1 for term in literal_terms if term in inferred_text)
        alignment = matching_terms / max(len(literal_terms), 1)
        
        return min(1.0, alignment)
    
    def _assess_capabilities(self, required: List[str]) -> float:
        """Assess if we have required capabilities."""
        if not required:
            return 1.0
        
        available = ["read", "write", "edit", "search", "test", "execute"]
        matched = sum(1 for cap in required if any(a in cap.lower() for a in available))
        
        return matched / len(required)
    
    def _calculate_confidence(self, assessment: Dict[str, Any]) -> float:
        """Calculate overall confidence from assessment."""
        scores = [
            assessment.get("literal_understanding", 0),
            assessment.get("intent_inference", 0),
            assessment.get("capability_match", 0)
        ]
        
        # Weighted average
        weights = [0.3, 0.4, 0.3]
        confidence = sum(s * w for s, w in zip(scores, weights))
        
        # Penalize if concerns exist
        concern_penalty = len(assessment.get("concerns", [])) * 0.1
        confidence = max(0.0, confidence - concern_penalty)
        
        return confidence
    
    def _meta_assess_understanding(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Meta-assessment: Am I understanding correctly?"""
        confidence = assessment.get("confidence", 0)
        concerns = assessment.get("concerns", [])
        
        return {
            "confident": confidence > 0.6 and len(concerns) < 2,
            "reason": "Multiple concerning factors" if len(concerns) >= 2 else "Low confidence score"
        }
    
    def _check_execution_speed(self, results: List[Dict[str, Any]]) -> bool:
        """Check if execution is taking too long."""
        if not results:
            return False
        
        total_duration = sum(r.get("duration", 0) for r in results)
        return total_duration > 30  # seconds
    
    def _check_error_patterns(self, results: List[Dict[str, Any]]) -> bool:
        """Check for repeating error patterns."""
        errors = [r.get("error") for r in results if r.get("error")]
        
        if len(errors) >= 2:
            # Check for similar errors
            if len(set(errors)) == 1:
                return True
        
        return False
    
    def _check_coherence(self, results: List[Dict[str, Any]]) -> bool:
        """Check if execution is coherent."""
        # Simplified check - are results building on each other?
        if len(results) < 2:
            return False
        
        # Check if later results reference earlier ones
        coherent = all(r.get("success", False) for r in results[-3:])
        return not coherent
    
    def _check_relevance(self, results: List[Dict[str, Any]]) -> bool:
        """Check if execution is staying on track."""
        # Simplified - check if recent operations are related
        if len(results) < 2:
            return False
        
        # Would need actual task context to properly assess
        return False
    
    def _check_efficiency(self, results: List[Dict[str, Any]]) -> bool:
        """Check if execution is efficient."""
        # Check for redundant operations
        operations = [r.get("operation") for r in results]
        unique_ops = set(operations)
        
        if len(operations) > len(unique_ops) * 1.5:
            return True  # Inefficient - too many repeated operations
        
        return False
    
    def _get_adjustment_for_issue(self, issue: str) -> str:
        """Get adjustment strategy for detected issue."""
        adjustments = {
            "taking_too_long": "increase_parallelism",
            "repeating_errors": "try_alternative_approach",
            "losing_coherence": "review_objectives",
            "off_track": "return_to_plan",
            "inefficient": "optimize_operations"
        }
        return adjustments.get(issue, "reassess_approach")
    
    def _calculate_quality_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score."""
        if not results:
            return 0.5
        
        success_rate = sum(1 for r in results if r.get("success", False)) / len(results)
        
        # Factor in other metrics
        score = success_rate * 0.6
        score += self.quality_metrics["coherence"] * 0.1
        score += self.quality_metrics["relevance"] * 0.1
        score += self.quality_metrics["accuracy"] * 0.1
        score += self.quality_metrics["helpfulness"] * 0.1
        
        return min(1.0, score)
    
    def _update_quality_metrics(self, results: List[Dict[str, Any]]):
        """Update running quality metrics."""
        # Simplified metric updates
        if results:
            success_rate = sum(1 for r in results if r.get("success", False)) / len(results)
            
            # Rolling average
            alpha = 0.3
            self.quality_metrics["coherence"] = alpha * success_rate + (1 - alpha) * self.quality_metrics["coherence"]
            self.quality_metrics["relevance"] = alpha * 0.8 + (1 - alpha) * self.quality_metrics["relevance"]
            self.quality_metrics["accuracy"] = alpha * success_rate + (1 - alpha) * self.quality_metrics["accuracy"]
            self.quality_metrics["helpfulness"] = alpha * 0.7 + (1 - alpha) * self.quality_metrics["helpfulness"]
    
    def _assess_cognitive_load(self, results: List[Dict[str, Any]]) -> float:
        """Assess current cognitive load."""
        # Factors affecting cognitive load
        num_operations = len(results)
        num_failures = sum(1 for r in results if not r.get("success", False))
        complexity = sum(r.get("complexity", 1) for r in results)
        
        # Simple load calculation
        load = (num_operations / 20) * 0.3
        load += (num_failures / max(num_operations, 1)) * 0.4
        load += (complexity / max(num_operations * 5, 1)) * 0.3
        
        return min(1.0, load)
    
    def _calibrate_self_assessment(self, meta_review: Dict[str, Any]) -> Dict[str, Any]:
        """Calibrate self assessment."""
        calibration = {
            "adjustment_needed": False,
            "too_critical": False,
            "not_critical_enough": False
        }
        
        # Simple calibration logic
        confidence = meta_review.get("confidence", 0.5)
        if confidence < 0.3:
            calibration["too_critical"] = True
            calibration["adjustment_needed"] = True
        elif confidence > 0.9:
            calibration["not_critical_enough"] = True
            calibration["adjustment_needed"] = True
        
        return calibration
    
    def _adjust_review(self, review: Dict[str, Any], calibration: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust review based on calibration."""
        if calibration.get("too_critical"):
            review["confidence"] = min(review["confidence"] * 1.2, 1.0)
        elif calibration.get("not_critical_enough"):
            review["confidence"] = max(review["confidence"] * 0.8, 0.0)
        return review
    
    def _check_response_coherence(self, review: Dict[str, Any]) -> float:
        """Check response coherence."""
        expected_keys = ["success", "errors", "warnings"]
        found_keys = sum(1 for k in expected_keys if k in review)
        return found_keys / len(expected_keys)
    
    def _check_response_relevance(self, review: Dict[str, Any]) -> float:
        """Check response relevance."""
        if review.get("success") is not None:
            return 0.9
        return 0.5
    
    def _check_response_accuracy(self, review: Dict[str, Any]) -> float:
        """Check response accuracy."""
        if review.get("success") and review.get("errors"):
            return 0.6
        return 0.9
    
    def _check_response_helpfulness(self, review: Dict[str, Any]) -> float:
        """Check response helpfulness."""
        if review.get("errors") or review.get("warnings"):
            return 0.8
        return 0.7
    
    def _check_response_safety(self, review: Dict[str, Any]) -> float:
        """Check response safety."""
        return 1.0