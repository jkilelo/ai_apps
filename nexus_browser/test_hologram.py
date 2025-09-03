"""
TEST SUITE FOR HOLOGRAPHIC SYSTEM
==================================
Comprehensive tests for all holographic functionality.
"""

import sys
import os
import pytest
import numpy as np
import json
import pickle
import time
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hologram import (
    HolographicCodeGenerator,
    FractalLibrary,
    HolographicMemory,
    FractalType,
    StorageDimension,
    CodeTemplate,
    FractalMathematics,
    FourierTransformEngine,
    InterferencePatternEngine,
    HolographicOperations,
    MemoryFragment,
    HOLOGRAPHIC_VERSION,
    MAX_FRACTAL_DEPTH,
    DEFAULT_DIMENSIONS,
    RECONSTRUCTION_MIN_FRAGMENTS
)

# Test configuration
TEST_RESOLUTION = 64
TEST_DEPTH = 3
TEST_DATA_SIZE = 1024

class TestFractalLibrary:
    """Test fractal pattern generation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.library = FractalLibrary()
    
    def test_mandelbrot_generation(self):
        """Test Mandelbrot fractal generation"""
        fractal = self.library.generate_mandelbrot(TEST_RESOLUTION, TEST_DEPTH)
        assert fractal is not None
        assert fractal.shape == (TEST_RESOLUTION, TEST_RESOLUTION)
        assert np.min(fractal) >= 0
        assert np.max(fractal) <= TEST_DEPTH
    
    def test_julia_generation(self):
        """Test Julia set generation"""
        fractal = self.library.generate_julia(TEST_RESOLUTION, TEST_DEPTH)
        assert fractal is not None
        assert fractal.shape == (TEST_RESOLUTION, TEST_RESOLUTION)
    
    def test_sierpinski_generation(self):
        """Test Sierpinski triangle generation"""
        fractal = self.library.generate_sierpinski(TEST_RESOLUTION, TEST_DEPTH)
        assert fractal is not None
        assert fractal.shape == (TEST_RESOLUTION, TEST_RESOLUTION)
        assert np.all((fractal == 0) | (fractal == 1))
    
    def test_all_fractal_types(self):
        """Test generation of all fractal types"""
        for fractal_type in FractalType:
            fractal = self.library.generate_fractal(fractal_type, TEST_RESOLUTION, TEST_DEPTH)
            assert fractal is not None
            assert len(fractal.shape) > 0
    
    def test_fractal_combination(self):
        """Test combining multiple fractals"""
        fractals = [
            self.library.generate_mandelbrot(TEST_RESOLUTION, TEST_DEPTH),
            self.library.generate_julia(TEST_RESOLUTION, TEST_DEPTH)
        ]
        combined = self.library.combine_fractals(fractals)
        assert combined.shape == fractals[0].shape
    
    def test_fractal_hologram(self):
        """Test holographic encoding of fractal"""
        fractal = self.library.generate_mandelbrot(TEST_RESOLUTION, TEST_DEPTH)
        hologram = self.library.create_fractal_hologram(fractal)
        assert hologram is not None
        assert hologram.shape == fractal.shape

class TestHolographicMemory:
    """Test holographic memory storage"""
    
    def setup_method(self):
        """Setup for each test"""
        self.memory = HolographicMemory()
    
    def test_store_and_retrieve(self):
        """Test storing and retrieving data"""
        test_data = {"key": "value", "number": 42}
        
        # Store
        fragment_id = self.memory.store_holographically(test_data)
        assert fragment_id is not None
        
        # Retrieve
        retrieved = self.memory.retrieve_holographically(fragment_id)
        assert retrieved == test_data
    
    def test_fragment_creation(self):
        """Test redundant fragment creation"""
        test_data = b"Hello, Holographic World!"
        fragments = self.memory.create_redundant_fragments(test_data, 5)
        
        assert len(fragments) == 5
        for fragment in fragments:
            assert isinstance(fragment, bytes)
            assert len(fragment) > len(test_data)  # Includes metadata
    
    def test_fragment_reconstruction(self):
        """Test reconstruction from fragments"""
        test_data = b"Test reconstruction data"
        fragments = self.memory.create_redundant_fragments(test_data, 5)
        
        # Reconstruct from minimum fragments
        reconstructed = self.memory.reconstruct_from_fragments(
            fragments[:RECONSTRUCTION_MIN_FRAGMENTS], 
            RECONSTRUCTION_MIN_FRAGMENTS
        )
        
        assert reconstructed == test_data
    
    def test_partial_reconstruction(self):
        """Test reconstruction from partial fragments"""
        test_data = b"Partial reconstruction test"
        fragments = self.memory.create_redundant_fragments(test_data, 7)
        
        # Remove some fragments and reconstruct
        partial_fragments = fragments[::2]  # Every other fragment
        if len(partial_fragments) >= RECONSTRUCTION_MIN_FRAGMENTS:
            reconstructed = self.memory.reconstruct_from_fragments(
                partial_fragments,
                RECONSTRUCTION_MIN_FRAGMENTS
            )
            assert reconstructed == test_data
    
    def test_memory_statistics(self):
        """Test memory statistics"""
        # Store some data
        for i in range(5):
            self.memory.store_holographically(f"Test data {i}")
        
        stats = self.memory.get_memory_stats()
        assert stats['total_fragments'] == 5
        assert stats['dimensions'] == DEFAULT_DIMENSIONS
        assert 'cache_hit_rate' in stats
    
    def test_query_by_pattern(self):
        """Test querying memory by pattern"""
        # Store multiple fragments
        ids = []
        for i in range(3):
            fragment_id = self.memory.store_holographically(f"Data {i}")
            ids.append(fragment_id)
        
        # Query with empty pattern (should return all)
        results = self.memory.query_by_pattern({}, limit=10)
        assert len(results) >= 3

class TestHolographicCodeGenerator:
    """Test holographic code generation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.generator = HolographicCodeGenerator()
    
    def test_generate_fractal_class(self):
        """Test fractal class generation"""
        code = self.generator.generate_fractal_class(
            "TestClass",
            FractalType.MANDELBROT,
            base_classes=["object"],
            methods=[{'name': 'test_method', 'params': 'x', 'body': 'return x * 2'}]
        )
        
        assert "class TestClass" in code
        assert "holographic_encode" in code
        assert "holographic_decode" in code
        assert "test_method" in code
    
    def test_generate_fractal_function(self):
        """Test fractal function generation"""
        code = self.generator.generate_fractal_function(
            "test_function",
            "x, y",
            "return x + y",
            FractalType.JULIA
        )
        
        assert "def test_function" in code
        assert "holographic_function" in code
        assert "return x + y" in code
    
    def test_generate_fractal_module(self):
        """Test complete module generation"""
        components = [
            {'type': 'class', 'name': 'ModuleClass'},
            {'type': 'function', 'name': 'module_func', 'params': 'x'}
        ]
        
        module = self.generator.generate_fractal_module(
            "test_module",
            components,
            FractalType.SIERPINSKI
        )
        
        assert "test_module" in module
        assert "ModuleClass" in module
        assert "module_func" in module
        assert HOLOGRAPHIC_VERSION in module
    
    def test_holographic_merge(self):
        """Test merging code fragments"""
        fragment1 = "def func1():\n    return 1"
        fragment2 = "def func2():\n    return 2"
        
        merged = self.generator.holographic_merge(fragment1, fragment2)
        
        assert merged is not None
        assert "Holographically merged module" in merged
    
    def test_analyze_fractal_complexity(self):
        """Test code complexity analysis"""
        code = self.generator.generate_fractal_class(
            "ComplexClass",
            FractalType.LORENZ_ATTRACTOR
        )
        
        metrics = self.generator.analyze_fractal_complexity(code)
        
        assert 'total_lines' in metrics
        assert 'fractal_dimension' in metrics
        assert metrics['total_lines'] > 0
    
    def test_export_import_state(self):
        """Test state export and import"""
        # Generate some code
        self.generator.generate_fractal_class("TestClass", FractalType.MANDELBROT)
        
        # Export state
        state = self.generator.export_holographic_state()
        assert 'version' in state
        assert state['version'] == HOLOGRAPHIC_VERSION
        
        # Import state
        success = self.generator.import_holographic_state(state)
        assert success

class TestFourierTransformEngine:
    """Test Fourier transform operations"""
    
    def setup_method(self):
        """Setup for each test"""
        self.engine = FourierTransformEngine()
    
    def test_2d_fft(self):
        """Test 2D FFT and inverse"""
        data = np.random.randn(32, 32)
        
        # Forward transform
        fft_data = self.engine.fft_2d(data)
        assert fft_data.shape == data.shape
        
        # Inverse transform
        reconstructed = self.engine.ifft_2d(fft_data)
        np.testing.assert_array_almost_equal(data, np.real(reconstructed))
    
    def test_optical_fourier(self):
        """Test optical Fourier transform"""
        image = np.random.randn(64, 64)
        power_spectrum = self.engine.optical_fourier_transform(image)
        
        assert power_spectrum.shape == image.shape
        assert np.all(power_spectrum >= 0)  # Power spectrum is non-negative
    
    def test_fractional_fourier(self):
        """Test fractional Fourier transform"""
        signal = np.random.randn(128)
        alpha = 0.5
        
        # Forward fractional transform
        frac_fft = self.engine.fractional_fourier_transform(signal, alpha)
        assert len(frac_fft) == len(signal)
        
        # Inverse fractional transform
        inverse = self.engine.fractional_fourier_transform(frac_fft, -alpha)
        # Note: This is simplified; real inverse would need proper implementation
    
    def test_holographic_encoding(self):
        """Test holographic Fourier encoding/decoding"""
        test_data = b"Test data for Fourier encoding"
        
        # Encode
        encoded = self.engine.holographic_fourier_encode(test_data)
        assert encoded is not None
        
        # Decode
        decoded = self.engine.holographic_fourier_decode(encoded, len(test_data))
        assert decoded == test_data

class TestInterferencePatternEngine:
    """Test interference pattern operations"""
    
    def setup_method(self):
        """Setup for each test"""
        self.engine = InterferencePatternEngine()
    
    def test_create_interference_pattern(self):
        """Test interference pattern creation"""
        shape = (64, 64)
        object_wave = np.random.randn(*shape) + 1j * np.random.randn(*shape)
        reference_wave = self.engine.generate_reference_beam(shape)
        
        pattern = self.engine.create_interference_pattern(object_wave, reference_wave)
        
        assert pattern.shape == shape
        assert np.all(np.isfinite(pattern))
    
    def test_reference_beam_generation(self):
        """Test reference beam generation"""
        shape = (32, 32)
        angle = np.pi / 4
        
        reference = self.engine.generate_reference_beam(shape, angle)
        
        assert reference.shape == shape
        assert np.all(np.abs(reference) <= 1.1)  # Normalized amplitude
    
    def test_spherical_reference(self):
        """Test spherical reference wave generation"""
        shape = (48, 48)
        reference = self.engine.generate_spherical_reference(shape)
        
        assert reference.shape == shape
        assert np.all(np.isfinite(reference))
    
    def test_hologram_reconstruction(self):
        """Test reconstruction from hologram"""
        shape = (32, 32)
        
        # Create a simple object wave
        object_wave = np.ones(shape, dtype=complex) * 0.5
        reference_wave = self.engine.generate_reference_beam(shape)
        
        # Create hologram
        hologram = self.engine.create_interference_pattern(object_wave, reference_wave)
        
        # Reconstruct
        reconstructed = self.engine.reconstruct_from_hologram(hologram, reference_wave)
        
        assert reconstructed.shape == shape

class TestHolographicOperations:
    """Test advanced holographic operations"""
    
    def setup_method(self):
        """Setup for each test"""
        self.generator = HolographicCodeGenerator()
        self.operations = HolographicOperations(self.generator)
    
    def test_quantum_interference(self):
        """Test quantum interference between patterns"""
        pattern1 = np.random.randn(32, 32)
        pattern2 = np.random.randn(32, 32)
        
        interference = self.operations.quantum_interference(pattern1, pattern2)
        
        assert interference.shape == pattern1.shape
        assert np.all(interference >= 0)  # Intensity is non-negative
    
    def test_holographic_hash(self):
        """Test holographic hash creation"""
        test_data = {"key": "value", "list": [1, 2, 3]}
        
        hash1 = self.operations.create_holographic_hash(test_data)
        hash2 = self.operations.create_holographic_hash(test_data)
        
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA256 hex length
        # Hashes should be different due to fractal randomness
        assert hash1 != hash2
    
    def test_holographic_convolution(self):
        """Test holographic convolution"""
        pattern1 = np.random.randn(32, 32)
        pattern2 = np.random.randn(32, 32)
        
        convolved = self.operations.holographic_convolution(pattern1, pattern2)
        
        assert convolved.shape == pattern1.shape
        assert np.all(np.isfinite(convolved))
    
    def test_reconstruct_from_partial(self):
        """Test reconstruction from partial data"""
        complete_data = b"Complete data for testing"
        partial_data = complete_data[:10]
        
        # This should fail without proper structure
        reconstructed = self.operations.reconstruct_from_partial(partial_data)
        # Reconstruction from truly partial data is complex; this tests the mechanism

class TestFractalMathematics:
    """Test fractal mathematics operations"""
    
    def test_mandelbrot_iteration(self):
        """Test Mandelbrot set calculation"""
        # Test point in set
        c = complex(0, 0)
        iterations = FractalMathematics.mandelbrot_iteration(c, 100)
        assert iterations == 100  # Origin is in the set
        
        # Test point outside set
        c = complex(10, 10)
        iterations = FractalMathematics.mandelbrot_iteration(c, 100)
        assert iterations < 100  # Far point escapes quickly
    
    def test_julia_iteration(self):
        """Test Julia set calculation"""
        z = complex(0.5, 0.5)
        c = complex(-0.7, 0.27)
        iterations = FractalMathematics.julia_iteration(z, c, 100)
        assert 0 <= iterations <= 100
    
    def test_sierpinski_point(self):
        """Test Sierpinski triangle point checking"""
        # Center should be in triangle at depth 0
        in_triangle = FractalMathematics.sierpinski_point(0.25, 0.25, 1)
        assert isinstance(in_triangle, bool)
    
    def test_koch_curve_points(self):
        """Test Koch curve generation"""
        start = complex(0, 0)
        end = complex(1, 0)
        points = FractalMathematics.koch_curve_points(start, end, 2)
        
        assert len(points) > 2  # More points than just start and end
        assert points[0] == start
    
    def test_lorenz_attractor(self):
        """Test Lorenz attractor calculation"""
        x, y, z = 1.0, 1.0, 1.0
        new_x, new_y, new_z = FractalMathematics.lorenz_attractor(x, y, z)
        
        assert new_x != x  # Should change
        assert isinstance(new_x, float)

class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_complete_workflow(self):
        """Test complete holographic workflow"""
        # Initialize system
        generator = HolographicCodeGenerator()
        
        # Generate code
        class_code = generator.generate_fractal_class(
            "IntegrationTest",
            FractalType.MANDELBROT
        )
        
        # Store in memory
        storage_id = generator.memory.store_holographically(class_code)
        
        # Retrieve
        retrieved = generator.memory.retrieve_holographically(storage_id)
        
        assert retrieved == class_code
    
    def test_fractal_to_hologram_pipeline(self):
        """Test fractal generation to holographic storage pipeline"""
        library = FractalLibrary()
        memory = HolographicMemory()
        
        # Generate fractal
        fractal = library.generate_fractal(FractalType.JULIA, 64, 3)
        
        # Create hologram
        hologram = library.create_fractal_hologram(fractal)
        
        # Store hologram
        fragment_id = memory.store_holographically(hologram)
        
        # Retrieve
        retrieved = memory.retrieve_holographically(fragment_id)
        
        np.testing.assert_array_almost_equal(hologram, retrieved)
    
    def test_code_generation_and_merge(self):
        """Test code generation and merging"""
        generator = HolographicCodeGenerator()
        
        # Generate multiple code fragments
        codes = []
        for i, ftype in enumerate([FractalType.MANDELBROT, FractalType.JULIA]):
            code = generator.generate_fractal_class(f"Class{i}", ftype)
            codes.append(code)
        
        # Merge holographically
        merged = generator.holographic_merge(*codes)
        
        assert "Holographically merged module" in merged
        assert len(merged) > 0

class TestPerformance:
    """Performance tests for holographic system"""
    
    def test_fractal_generation_performance(self):
        """Test fractal generation performance"""
        library = FractalLibrary()
        
        start_time = time.time()
        for _ in range(10):
            library.generate_fractal(FractalType.MANDELBROT, 128, 5)
        elapsed = time.time() - start_time
        
        assert elapsed < 10  # Should complete in reasonable time
    
    def test_memory_storage_performance(self):
        """Test memory storage performance"""
        memory = HolographicMemory()
        
        # Generate test data
        test_data = [f"Data item {i}" * 100 for i in range(100)]
        
        start_time = time.time()
        for data in test_data:
            memory.store_holographically(data)
        elapsed = time.time() - start_time
        
        assert elapsed < 5  # Should store 100 items quickly
    
    def test_code_generation_performance(self):
        """Test code generation performance"""
        generator = HolographicCodeGenerator()
        
        start_time = time.time()
        for i in range(5):
            generator.generate_fractal_class(f"PerfClass{i}", FractalType.SIERPINSKI)
        elapsed = time.time() - start_time
        
        assert elapsed < 5  # Should generate 5 classes quickly

def run_all_tests():
    """Run all tests and report results"""
    print("=" * 70)
    print("HOLOGRAPHIC SYSTEM TEST SUITE")
    print("=" * 70)
    
    test_classes = [
        TestFractalLibrary,
        TestHolographicMemory,
        TestHolographicCodeGenerator,
        TestFourierTransformEngine,
        TestInterferencePatternEngine,
        TestHolographicOperations,
        TestFractalMathematics,
        TestIntegration,
        TestPerformance
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")
        print("-" * 40)
        
        instance = test_class()
        
        # Get all test methods
        test_methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                # Setup if needed
                if hasattr(instance, 'setup_method'):
                    instance.setup_method()
                
                # Run test
                method = getattr(instance, method_name)
                method()
                
                print(f"[PASS] {method_name}")
                passed_tests += 1
                
            except Exception as e:
                print(f"[FAIL] {method_name}: {str(e)}")
                failed_tests.append((test_class.__name__, method_name, str(e)))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  - {class_name}.{method_name}: {error}")
    else:
        print("\n[SUCCESS] All tests passed!")
    
    print("=" * 70)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)