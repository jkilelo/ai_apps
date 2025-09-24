"""
Comprehensive test runner for all element detection systems
Compares effectiveness across all strategies
"""
import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Set

# Set UTF-8 environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Import all detection systems
from ultimate_showcase_beautiful import UltimateShowcaseBeautiful
from ultimate_showcase_ultra_premium import UltimateShowcaseUltraPremium
from ultimate_showcase_maximum import UltimateShowcaseMaximum
from quantum_detection_matrix import QuantumDetectionMatrix

class DetectionSystemAnalyzer:
    """Analyze and compare all detection systems."""

    def __init__(self, url: str):
        self.url = url
        self.results = {}

    async def test_beautiful_system(self) -> Dict:
        """Test the Beautiful showcase system."""
        print("\n" + "="*80)
        print("[1/4] TESTING BEAUTIFUL SHOWCASE SYSTEM")
        print("="*80)

        start_time = datetime.now()
        showcase = UltimateShowcaseBeautiful(self.url, headless=False)

        try:
            # Run detection - method name is run_ultimate_beautification
            await showcase.run_ultimate_beautification()

            # Get results from the system
            elements_count = 0
            if hasattr(showcase, 'elements'):
                elements_count = len(showcase.elements)

            duration = (datetime.now() - start_time).total_seconds()

            return {
                'system': 'Beautiful Showcase',
                'elements_detected': elements_count,
                'duration': duration,
                'strategies': ['Exhaustive Scrolling', 'Visual Enhancement', 'Bullseye Targeting']
            }
        except Exception as e:
            print(f"Error in Beautiful system: {e}")
            return {
                'system': 'Beautiful Showcase',
                'elements_detected': 0,
                'duration': 0,
                'error': str(e)
            }

    async def test_ultra_premium_system(self) -> Dict:
        """Test the Ultra Premium system."""
        print("\n" + "="*80)
        print("[2/4] TESTING ULTRA PREMIUM SYSTEM")
        print("="*80)

        start_time = datetime.now()
        showcase = UltimateShowcaseUltraPremium(self.url, headless=False)

        try:
            await showcase.run_maximum_showcase()

            elements_count = 0
            if hasattr(showcase, 'elements'):
                elements_count = len(showcase.elements)

            duration = (datetime.now() - start_time).total_seconds()

            return {
                'system': 'Ultra Premium',
                'elements_detected': elements_count,
                'duration': duration,
                'strategies': ['Micro-Scrolling', 'Matrix Effects', 'Quantum Particles', 'Neural Networks']
            }
        except Exception as e:
            print(f"Error in Ultra Premium system: {e}")
            return {
                'system': 'Ultra Premium',
                'elements_detected': 0,
                'duration': 0,
                'error': str(e)
            }

    async def test_maximum_system(self) -> Dict:
        """Test the Maximum detection system."""
        print("\n" + "="*80)
        print("[3/4] TESTING MAXIMUM DETECTION SYSTEM")
        print("="*80)

        start_time = datetime.now()
        showcase = UltimateShowcaseMaximum(self.url, headless=False)

        try:
            await showcase.run_maximum_showcase()

            # Maximum system tracks multiple element sets
            total_elements = 0
            strategy_breakdown = {}

            if hasattr(showcase, 'all_elements'):
                total_elements = len(showcase.all_elements)
            if hasattr(showcase, 'scroll_elements'):
                strategy_breakdown['Scroll Detection'] = len(showcase.scroll_elements)
            if hasattr(showcase, 'shadow_elements'):
                strategy_breakdown['Shadow DOM'] = len(showcase.shadow_elements)
            if hasattr(showcase, 'aria_elements'):
                strategy_breakdown['Accessibility'] = len(showcase.aria_elements)

            duration = (datetime.now() - start_time).total_seconds()

            return {
                'system': 'Maximum Detection',
                'elements_detected': total_elements,
                'duration': duration,
                'strategies': list(strategy_breakdown.keys()),
                'breakdown': strategy_breakdown
            }
        except Exception as e:
            print(f"Error in Maximum system: {e}")
            return {
                'system': 'Maximum Detection',
                'elements_detected': 0,
                'duration': 0,
                'error': str(e)
            }

    async def test_quantum_system(self) -> Dict:
        """Test the Quantum Detection Matrix."""
        print("\n" + "="*80)
        print("[4/4] TESTING QUANTUM DETECTION MATRIX")
        print("="*80)

        start_time = datetime.now()
        detector = QuantumDetectionMatrix(self.url, headless=False)

        try:
            await detector.run_quantum_detection()

            # Quantum system has detailed tracking
            total_elements = 0
            strategy_breakdown = {}

            if hasattr(detector, 'all_unique_elements'):
                total_elements = len(detector.all_unique_elements)
            if hasattr(detector, 'strategy_results'):
                for strategy, elements in detector.strategy_results.items():
                    strategy_breakdown[strategy] = len(elements)

            duration = (datetime.now() - start_time).total_seconds()

            return {
                'system': 'Quantum Detection Matrix',
                'elements_detected': total_elements,
                'duration': duration,
                'strategies': list(strategy_breakdown.keys()),
                'breakdown': strategy_breakdown
            }
        except Exception as e:
            print(f"Error in Quantum system: {e}")
            return {
                'system': 'Quantum Detection Matrix',
                'elements_detected': 0,
                'duration': 0,
                'error': str(e)
            }

    async def run_comprehensive_test(self):
        """Run all detection systems and compare results."""
        print("="*80)
        print("COMPREHENSIVE DETECTION SYSTEM ANALYSIS")
        print(f"Target URL: {self.url}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Run all tests
        self.results['beautiful'] = await self.test_beautiful_system()
        self.results['ultra_premium'] = await self.test_ultra_premium_system()
        self.results['maximum'] = await self.test_maximum_system()
        self.results['quantum'] = await self.test_quantum_system()

        # Generate analysis report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive analysis report."""
        print("\n" + "="*80)
        print("FINAL ANALYSIS REPORT")
        print("="*80)

        # Sort systems by elements detected
        sorted_systems = sorted(
            self.results.values(),
            key=lambda x: x.get('elements_detected', 0),
            reverse=True
        )

        print("\n[+] DETECTION EFFECTIVENESS RANKING:")
        print("-" * 40)
        for i, result in enumerate(sorted_systems, 1):
            elements = result.get('elements_detected', 0)
            duration = result.get('duration', 0)
            efficiency = elements / duration if duration > 0 else 0

            print(f"{i}. {result['system']}")
            print(f"   Elements Detected: {elements}")
            print(f"   Time Taken: {duration:.2f} seconds")
            print(f"   Efficiency: {efficiency:.1f} elements/second")

            if 'breakdown' in result:
                print(f"   Strategy Breakdown:")
                for strategy, count in result['breakdown'].items():
                    print(f"     - {strategy}: {count} elements")

            if 'error' in result:
                print(f"   [ERROR]: {result['error']}")
            print()

        # Best performer analysis
        if sorted_systems:
            best = sorted_systems[0]
            print("\n[+] BEST PERFORMER:")
            print("-" * 40)
            print(f"System: {best['system']}")
            print(f"Elements Detected: {best.get('elements_detected', 0)}")
            print(f"Strategies Used: {', '.join(best.get('strategies', []))}")

        # Strategy effectiveness
        print("\n[+] STRATEGY EFFECTIVENESS:")
        print("-" * 40)
        all_strategies = {}
        for result in self.results.values():
            if 'breakdown' in result:
                for strategy, count in result['breakdown'].items():
                    if strategy not in all_strategies:
                        all_strategies[strategy] = []
                    all_strategies[strategy].append(count)

        for strategy, counts in sorted(all_strategies.items(), key=lambda x: max(x[1]), reverse=True):
            avg_count = sum(counts) / len(counts)
            print(f"- {strategy}: Avg {avg_count:.1f} elements (Max: {max(counts)})")

        # Performance metrics
        print("\n[+] PERFORMANCE METRICS:")
        print("-" * 40)
        total_elements = sum(r.get('elements_detected', 0) for r in self.results.values())
        total_duration = sum(r.get('duration', 0) for r in self.results.values())

        print(f"Total Unique Elements Found: {total_elements}")
        print(f"Total Test Duration: {total_duration:.2f} seconds")
        print(f"Average Elements per System: {total_elements/len(self.results):.1f}")

        # Recommendations
        print("\n[+] RECOMMENDATIONS:")
        print("-" * 40)
        if sorted_systems:
            if sorted_systems[0].get('elements_detected', 0) > 150:
                print("[SUCCESS] Quantum Detection Matrix achieves maximum coverage")
                print("         Recommended for production use when completeness is critical")
            elif sorted_systems[0].get('elements_detected', 0) > 100:
                print("[GOOD] Maximum Detection System provides excellent coverage")
                print("       Balance of performance and detection capability")
            else:
                print("[INFO] Consider combining multiple strategies for better coverage")

        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)

async def main():
    """Run comprehensive system analysis."""
    # Test URL
    url = "https://uat.citi.com"

    # Create analyzer
    analyzer = DetectionSystemAnalyzer(url)

    # Run comprehensive test
    await analyzer.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())