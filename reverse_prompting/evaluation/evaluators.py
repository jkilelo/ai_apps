"""
Comprehensive Code Evaluation System

This module provides sophisticated evaluation methods for comparing original code
with generated code, including semantic, structural, functional, and behavioral
similarity metrics.
"""

import ast
import difflib
import re
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import hashlib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..core.models import (
    CodeArtifact,
    EvaluationResult,
    ExecutionResult,
    SimilarityScore,
    SimilarityMetric,
    ExecutionStatus,
    CodeLanguage,
)


class BaseEvaluator(ABC):
    """Base class for code evaluators."""

    def __init__(self, metric: SimilarityMetric):
        self.metric = metric
        self.weights = {}

    @abstractmethod
    def evaluate(
        self, original: CodeArtifact, generated: CodeArtifact
    ) -> SimilarityScore:
        """Evaluate similarity between original and generated code."""
        pass

    def preprocess_code(self, code: str, language: CodeLanguage) -> str:
        """Preprocess code for evaluation."""
        # Remove comments and normalize whitespace
        if language == CodeLanguage.PYTHON:
            return self._preprocess_python(code)
        elif language in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT]:
            return self._preprocess_javascript(code)
        else:
            return self._preprocess_generic(code)

    def _preprocess_python(self, code: str) -> str:
        """Preprocess Python code."""
        lines = []
        for line in code.split("\n"):
            # Remove comments and docstrings
            line = re.sub(r"#.*$", "", line)
            line = line.strip()
            if line and not line.startswith('"""') and not line.startswith("'''"):
                lines.append(line)
        return "\n".join(lines)

    def _preprocess_javascript(self, code: str) -> str:
        """Preprocess JavaScript/TypeScript code."""
        # Remove single-line comments
        code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        # Normalize whitespace
        code = re.sub(r"\s+", " ", code)
        return code.strip()

    def _preprocess_generic(self, code: str) -> str:
        """Generic preprocessing for other languages."""
        # Basic whitespace normalization
        lines = [line.strip() for line in code.split("\n") if line.strip()]
        return "\n".join(lines)


class ExactMatchEvaluator(BaseEvaluator):
    """Evaluates exact string matching."""

    def __init__(self):
        super().__init__(SimilarityMetric.EXACT_MATCH)

    def evaluate(
        self, original: CodeArtifact, generated: CodeArtifact
    ) -> SimilarityScore:
        """Check if code is exactly the same."""
        original_processed = self.preprocess_code(original.content, original.language)
        generated_processed = self.preprocess_code(
            generated.content, generated.language
        )

        score = 1.0 if original_processed == generated_processed else 0.0

        return SimilarityScore(
            metric=self.metric,
            score=score,
            details={
                "original_length": len(original_processed),
                "generated_length": len(generated_processed),
                "exact_match": score == 1.0,
            },
        )


class SemanticEvaluator(BaseEvaluator):
    """Evaluates semantic similarity using TF-IDF and cosine similarity."""

    def __init__(self):
        super().__init__(SimilarityMetric.SEMANTIC)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3), stop_words=None, token_pattern=r"\b\w+\b|[^\w\s]"
        )

    def evaluate(
        self, original: CodeArtifact, generated: CodeArtifact
    ) -> SimilarityScore:
        """Calculate semantic similarity."""
        original_tokens = self._tokenize_code(original.content, original.language)
        generated_tokens = self._tokenize_code(generated.content, generated.language)

        if not original_tokens or not generated_tokens:
            return SimilarityScore(
                metric=self.metric,
                score=0.0,
                details={"error": "Empty token sequences"},
            )

        try:
            # Create TF-IDF vectors
            corpus = [original_tokens, generated_tokens]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return SimilarityScore(
                metric=self.metric,
                score=float(similarity),
                details={
                    "original_tokens": len(original_tokens.split()),
                    "generated_tokens": len(generated_tokens.split()),
                    "vocabulary_overlap": self._calculate_vocabulary_overlap(
                        original_tokens, generated_tokens
                    ),
                },
            )
        except Exception as e:
            return SimilarityScore(
                metric=self.metric, score=0.0, details={"error": str(e)}
            )

    def _tokenize_code(self, code: str, language: CodeLanguage) -> str:
        """Tokenize code into meaningful tokens."""
        # Extract identifiers, keywords, operators, and literals
        if language == CodeLanguage.PYTHON:
            return self._tokenize_python(code)
        elif language in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT]:
            return self._tokenize_javascript(code)
        else:
            return self._tokenize_generic(code)

    def _tokenize_python(self, code: str) -> str:
        """Tokenize Python code."""
        try:
            tree = ast.parse(code)
            tokens = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    tokens.append(node.id)
                elif isinstance(node, ast.FunctionDef):
                    tokens.append(f"def_{node.name}")
                elif isinstance(node, ast.ClassDef):
                    tokens.append(f"class_{node.name}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        tokens.append(f"import_{alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        tokens.append(f"from_{node.module}")

            return " ".join(tokens)
        except:
            # Fallback to regex tokenization
            return self._tokenize_generic(code)

    def _tokenize_javascript(self, code: str) -> str:
        """Tokenize JavaScript/TypeScript code."""
        # Extract function names, variable names, etc.
        patterns = [
            r"\bfunction\s+(\w+)",  # function declarations
            r"\b(\w+)\s*=\s*function",  # function expressions
            r"\bclass\s+(\w+)",  # class declarations
            r"\b(\w+)\s*:",  # object properties
            r"\bvar\s+(\w+)",  # var declarations
            r"\blet\s+(\w+)",  # let declarations
            r"\bconst\s+(\w+)",  # const declarations
        ]

        tokens = []
        for pattern in patterns:
            tokens.extend(re.findall(pattern, code))

        # Add generic identifiers
        identifiers = re.findall(r"\b[a-zA-Z_]\w*\b", code)
        tokens.extend(identifiers)

        return " ".join(tokens)

    def _tokenize_generic(self, code: str) -> str:
        """Generic tokenization for other languages."""
        # Extract identifiers and keywords
        identifiers = re.findall(r"\b[a-zA-Z_]\w*\b", code)
        return " ".join(identifiers)

    def _calculate_vocabulary_overlap(self, tokens1: str, tokens2: str) -> float:
        """Calculate vocabulary overlap between two token sequences."""
        vocab1 = set(tokens1.split())
        vocab2 = set(tokens2.split())

        if not vocab1 or not vocab2:
            return 0.0

        intersection = vocab1.intersection(vocab2)
        union = vocab1.union(vocab2)

        return len(intersection) / len(union) if union else 0.0


class StructuralEvaluator(BaseEvaluator):
    """Evaluates structural similarity using AST comparison."""

    def __init__(self):
        super().__init__(SimilarityMetric.STRUCTURAL)

    def evaluate(
        self, original: CodeArtifact, generated: CodeArtifact
    ) -> SimilarityScore:
        """Calculate structural similarity."""
        if original.language != generated.language:
            return SimilarityScore(
                metric=self.metric, score=0.0, details={"error": "Different languages"}
            )

        if original.language == CodeLanguage.PYTHON:
            return self._evaluate_python_structure(original.content, generated.content)
        else:
            # Fallback to line-based structural comparison
            return self._evaluate_line_structure(original.content, generated.content)

    def _evaluate_python_structure(
        self, original: str, generated: str
    ) -> SimilarityScore:
        """Evaluate Python AST structure."""
        try:
            original_tree = ast.parse(original)
            generated_tree = ast.parse(generated)

            original_structure = self._extract_ast_structure(original_tree)
            generated_structure = self._extract_ast_structure(generated_tree)

            similarity = self._compare_structures(
                original_structure, generated_structure
            )

            return SimilarityScore(
                metric=self.metric,
                score=similarity,
                details={
                    "original_nodes": len(original_structure),
                    "generated_nodes": len(generated_structure),
                    "structure_types": list(
                        set(original_structure) & set(generated_structure)
                    ),
                },
            )
        except Exception as e:
            return SimilarityScore(
                metric=self.metric,
                score=0.0,
                details={"error": f"AST parsing failed: {str(e)}"},
            )

    def _extract_ast_structure(self, tree: ast.AST) -> List[str]:
        """Extract AST node types and structure."""
        structure = []
        for node in ast.walk(tree):
            structure.append(type(node).__name__)
        return structure

    def _compare_structures(self, struct1: List[str], struct2: List[str]) -> float:
        """Compare two AST structures."""
        if not struct1 or not struct2:
            return 0.0

        # Use sequence matching
        matcher = difflib.SequenceMatcher(None, struct1, struct2)
        return matcher.ratio()

    def _evaluate_line_structure(
        self, original: str, generated: str
    ) -> SimilarityScore:
        """Evaluate structure based on line patterns."""
        original_lines = [line.strip() for line in original.split("\n") if line.strip()]
        generated_lines = [
            line.strip() for line in generated.split("\n") if line.strip()
        ]

        # Extract structural patterns (indentation, brackets, etc.)
        original_patterns = [
            self._extract_line_pattern(line) for line in original_lines
        ]
        generated_patterns = [
            self._extract_line_pattern(line) for line in generated_lines
        ]

        matcher = difflib.SequenceMatcher(None, original_patterns, generated_patterns)
        similarity = matcher.ratio()

        return SimilarityScore(
            metric=self.metric,
            score=similarity,
            details={
                "original_lines": len(original_lines),
                "generated_lines": len(generated_lines),
                "pattern_similarity": similarity,
            },
        )

    def _extract_line_pattern(self, line: str) -> str:
        """Extract structural pattern from a line of code."""
        pattern = ""

        # Indentation
        leading_spaces = len(line) - len(line.lstrip())
        pattern += f"indent_{leading_spaces}_"

        # Brackets and operators
        for char in line:
            if char in "(){}[]":
                pattern += char
            elif char in "=+-*/%<>!&|":
                pattern += "op"

        return pattern


class FunctionalEvaluator(BaseEvaluator):
    """Evaluates functional equivalence by executing code."""

    def __init__(self, timeout: int = 30):
        super().__init__(SimilarityMetric.FUNCTIONAL)
        self.timeout = timeout

    def evaluate(
        self, original: CodeArtifact, generated: CodeArtifact
    ) -> SimilarityScore:
        """Test functional equivalence."""
        if original.language != generated.language:
            return SimilarityScore(
                metric=self.metric, score=0.0, details={"error": "Different languages"}
            )

        # Generate test cases
        test_cases = self._generate_test_cases(original)

        if not test_cases:
            return SimilarityScore(
                metric=self.metric,
                score=0.0,
                details={"error": "No test cases generated"},
            )

        # Execute both versions
        original_results = self._execute_with_tests(original, test_cases)
        generated_results = self._execute_with_tests(generated, test_cases)

        # Compare results
        score = self._compare_execution_results(original_results, generated_results)

        return SimilarityScore(
            metric=self.metric,
            score=score,
            details={
                "test_cases": len(test_cases),
                "original_success": original_results.get("success", False),
                "generated_success": generated_results.get("success", False),
                "matching_outputs": original_results.get("outputs")
                == generated_results.get("outputs"),
            },
        )

    def _generate_test_cases(self, artifact: CodeArtifact) -> List[Dict[str, Any]]:
        """Generate test cases for the code."""
        # This is a simplified version - in practice, you'd want more sophisticated test generation
        test_cases = []

        if artifact.language == CodeLanguage.PYTHON:
            # Look for function definitions and create basic test cases
            functions = re.findall(r"def\s+(\w+)\s*\((.*?)\):", artifact.content)
            for func_name, params in functions:
                if params.strip():
                    # Generate simple test case
                    test_cases.append(
                        {
                            "function": func_name,
                            "inputs": self._generate_sample_inputs(params),
                            "expected": None,  # Would need actual execution to determine
                        }
                    )

        return test_cases

    def _generate_sample_inputs(self, params: str) -> List[Any]:
        """Generate sample inputs for function parameters."""
        # Very basic input generation
        param_list = [p.strip() for p in params.split(",") if p.strip()]
        inputs = []

        for param in param_list:
            # Remove default values and type hints
            param = param.split("=")[0].split(":")[0].strip()

            # Generate based on common parameter names
            if "num" in param or "count" in param or "size" in param:
                inputs.append(random.choice([1, 5, 10, 100]))
            elif "str" in param or "text" in param or "name" in param:
                inputs.append(random.choice(["test", "hello", "sample"]))
            elif "list" in param or "arr" in param:
                inputs.append([1, 2, 3])
            else:
                inputs.append(1)  # Default to integer

        return inputs

    def _execute_with_tests(
        self, artifact: CodeArtifact, test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute code with test cases."""
        if artifact.language == CodeLanguage.PYTHON:
            return self._execute_python_tests(artifact, test_cases)
        else:
            return {"success": False, "error": "Language not supported for execution"}

    def _execute_python_tests(
        self, artifact: CodeArtifact, test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute Python code with test cases."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(artifact.content)
                f.write("\n\n# Test execution\n")

                for i, test_case in enumerate(test_cases):
                    func_name = test_case["function"]
                    inputs = test_case["inputs"]
                    inputs_str = ", ".join(repr(inp) for inp in inputs)
                    f.write(f"print(f'test_{i}:{{repr({func_name}({inputs_str}))}}')\n")

                temp_path = f.name

            # Execute the code
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            outputs = []
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line.startswith("test_"):
                        outputs.append(line.split(":", 1)[1] if ":" in line else line)

            return {
                "success": result.returncode == 0,
                "outputs": outputs,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            # Cleanup
            try:
                Path(temp_path).unlink()
            except:
                pass

    def _compare_execution_results(
        self, original: Dict[str, Any], generated: Dict[str, Any]
    ) -> float:
        """Compare execution results."""
        if not original.get("success") or not generated.get("success"):
            return 0.0

        original_outputs = original.get("outputs", [])
        generated_outputs = generated.get("outputs", [])

        if not original_outputs and not generated_outputs:
            return 1.0

        if len(original_outputs) != len(generated_outputs):
            return 0.0

        matching = sum(1 for o, g in zip(original_outputs, generated_outputs) if o == g)
        return matching / len(original_outputs) if original_outputs else 0.0


class EditDistanceEvaluator(BaseEvaluator):
    """Evaluates similarity using edit distance."""

    def __init__(self):
        super().__init__(SimilarityMetric.EDIT_DISTANCE)

    def evaluate(
        self, original: CodeArtifact, generated: CodeArtifact
    ) -> SimilarityScore:
        """Calculate normalized edit distance."""
        original_processed = self.preprocess_code(original.content, original.language)
        generated_processed = self.preprocess_code(
            generated.content, generated.language
        )

        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(original_processed, generated_processed)
        max_length = max(len(original_processed), len(generated_processed))

        # Normalize to similarity score (0-1)
        similarity = 1.0 - (distance / max_length) if max_length > 0 else 1.0

        return SimilarityScore(
            metric=self.metric,
            score=max(0.0, similarity),
            details={
                "edit_distance": distance,
                "original_length": len(original_processed),
                "generated_length": len(generated_processed),
                "normalized_distance": distance / max_length if max_length > 0 else 0.0,
            },
        )

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


class ComprehensiveEvaluator:
    """Comprehensive evaluator that combines multiple evaluation metrics."""

    def __init__(self, weights: Optional[Dict[SimilarityMetric, float]] = None):
        self.evaluators = {
            SimilarityMetric.EXACT_MATCH: ExactMatchEvaluator(),
            SimilarityMetric.SEMANTIC: SemanticEvaluator(),
            SimilarityMetric.STRUCTURAL: StructuralEvaluator(),
            SimilarityMetric.FUNCTIONAL: FunctionalEvaluator(),
            SimilarityMetric.EDIT_DISTANCE: EditDistanceEvaluator(),
        }

        self.weights = weights or {
            SimilarityMetric.EXACT_MATCH: 0.1,
            SimilarityMetric.SEMANTIC: 0.3,
            SimilarityMetric.STRUCTURAL: 0.2,
            SimilarityMetric.FUNCTIONAL: 0.3,
            SimilarityMetric.EDIT_DISTANCE: 0.1,
        }

    def evaluate(
        self,
        original: CodeArtifact,
        generated: CodeArtifact,
        prompt_id: Optional[str] = None,
    ) -> EvaluationResult:
        """Comprehensive evaluation using all metrics."""
        evaluation = EvaluationResult(
            original_artifact_id=original.id,
            generated_artifact_id=generated.id,
            prompt_id=prompt_id or uuid4(),
        )

        # Run all evaluations
        for metric, evaluator in self.evaluators.items():
            try:
                score = evaluator.evaluate(original, generated)
                evaluation.add_similarity_score(metric, score.score, **score.details)
            except Exception as e:
                # Log error and continue with other metrics
                evaluation.add_similarity_score(metric, 0.0, error=str(e))

        # Calculate overall score
        evaluation.calculate_overall_score(self.weights)

        # Determine success based on threshold
        evaluation.functional_equivalence = any(
            score.metric == SimilarityMetric.FUNCTIONAL and score.score >= 0.9
            for score in evaluation.similarity_scores
        )

        evaluation.success = evaluation.overall_score >= 0.8

        return evaluation


# Export all evaluators
__all__ = [
    "BaseEvaluator",
    "ExactMatchEvaluator",
    "SemanticEvaluator",
    "StructuralEvaluator",
    "FunctionalEvaluator",
    "EditDistanceEvaluator",
    "ComprehensiveEvaluator",
]
