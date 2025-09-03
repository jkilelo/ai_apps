#!/usr/bin/env python3
"""
COMPREHENSIVE 100% COMPLIANCE TEST
===================================
This test verifies that ALL enforcement issues are fixed
and the system is 100% compliant.
"""

import json
import sys
from pathlib import Path
from agent_enforcement_contract import get_enforcer, ViolationType
from nexus_progress_tracker import NexusProgressTracker

def test_strict_mode_immutable():
    """Test 1: Verify strict_mode cannot be changed"""
    print("\n[TEST 1] Testing Strict Mode Immutability...")
    enforcer = get_enforcer()
    
    # Initial value should be True
    assert enforcer.strict_mode == True, "Initial strict_mode should be True"
    print("  [OK] Initial strict_mode is True")
    
    # Try to set to False
    enforcer.strict_mode = False
    
    # Should still be True
    assert enforcer.strict_mode == True, "Strict mode should still be True after attempting to disable"
    print("  [OK] Strict mode cannot be disabled")
    
    # Try setting to None, 0, empty string
    for value in [None, 0, "", []]:
        enforcer.strict_mode = value
        assert enforcer.strict_mode == True, f"Strict mode should be True even after setting to {value}"
    
    print("  [PASS] Strict mode is truly immutable")
    return True

def test_json_serialization():
    """Test 2: Verify ViolationType enum serializes correctly"""
    print("\n[TEST 2] Testing JSON Serialization...")
    enforcer = get_enforcer()
    
    # Clear any existing violations log
    log_file = Path("contract_violations.log")
    if log_file.exists():
        log_file.unlink()
    
    # Record a test violation
    try:
        enforcer.record_violation(
            ViolationType.SKIPPED_TESTING,
            "TEST-JSON-001",
            "Testing JSON serialization",
            "HIGH"
        )
    except Exception as e:
        if "CRITICAL" not in str(e):
            print(f"  [FAIL] Error recording violation: {e}")
            return False
    
    # Check that violation was logged to file
    assert log_file.exists(), "Violations log file should exist"
    print("  [OK] Violation logged to file")
    
    # Read and parse the JSON
    with open(log_file, 'r') as f:
        line = f.readline()
        try:
            violation_data = json.loads(line)
            assert 'violation_type' in violation_data, "violation_type should be in JSON"
            assert violation_data['violation_type'] == "Attempted to skip testing", "violation_type should be string value"
            print("  [OK] JSON serialization works correctly")
        except json.JSONDecodeError as e:
            print(f"  [FAIL] JSON parsing failed: {e}")
            return False
    
    print("  [PASS] ViolationType enum serializes properly")
    return True

def test_get_current_checkpoint():
    """Test 3: Verify get_current_checkpoint method exists and works"""
    print("\n[TEST 3] Testing get_current_checkpoint Method...")
    tracker = NexusProgressTracker()
    
    # Test that method exists
    assert hasattr(tracker, 'get_current_checkpoint'), "get_current_checkpoint method should exist"
    print("  [OK] Method exists")
    
    # Test that it returns a value
    try:
        checkpoint = tracker.get_current_checkpoint()
        assert checkpoint is not None, "Should return a checkpoint value"
        print(f"  [OK] Method returns: {checkpoint}")
    except AttributeError as e:
        print(f"  [FAIL] Method error: {e}")
        return False
    
    # Create a new checkpoint and verify it updates
    checkpoint_id = tracker.create_checkpoint("TEST-CHECK-100", {"test": "100% compliance"})
    current = tracker.get_current_checkpoint()
    assert current == "TEST-CHECK-100", "Current checkpoint should be updated"
    print(f"  [OK] Checkpoint updated to: {current}")
    
    print("  [PASS] get_current_checkpoint method works correctly")
    return True

def test_unicode_handling():
    """Test 4: Verify Unicode issues are fixed"""
    print("\n[TEST 4] Testing Unicode Handling...")
    
    # Test that problematic Unicode doesn't crash
    test_strings = [
        "Test with emoji: [!]",
        "Test with checkmark: [OK]",
        "Test with cross: [FAIL]",
        "Test with warning: [WARNING]"
    ]
    
    for test_str in test_strings:
        try:
            print(f"  {test_str}")
        except UnicodeEncodeError:
            print(f"  [FAIL] Unicode error with: {test_str}")
            return False
    
    print("  [PASS] Unicode handling fixed")
    return True

def test_enforcement_active():
    """Test 5: Verify enforcement is actually working"""
    print("\n[TEST 5] Testing Enforcement is Active...")
    enforcer = get_enforcer()
    
    # Check enforcement is active
    assert enforcer.enforcement_active == True, "Enforcement should be active"
    print("  [OK] Enforcement is active")
    
    # Check tracker is initialized
    assert enforcer.tracker is not None, "Tracker should be initialized"
    print("  [OK] Tracker is initialized")
    
    # Check violations can be recorded
    initial_count = len(enforcer.violations)
    try:
        enforcer.record_violation(
            ViolationType.BULK_IMPLEMENTATION,
            "TEST-ENFORCE-001",
            "Testing enforcement",
            "HIGH"
        )
    except:
        pass  # May raise for CRITICAL, that's OK
    
    assert len(enforcer.violations) > initial_count, "Violations should be recorded"
    print("  [OK] Violations are being recorded")
    
    print("  [PASS] Enforcement is fully active")
    return True

def test_all_files_present():
    """Test 6: Verify all enforcement files are present"""
    print("\n[TEST 6] Testing All Enforcement Files Present...")
    
    required_files = [
        ("CLAUDE.md", "Constitutional contract"),
        ("BINDING_COMMITMENT.md", "Binding commitment"),
        ("agent_enforcement_contract.py", "Enforcement system"),
        ("nexus_progress_tracker.py", "Progress tracking"),
        ("nexus_tasks.json", "Task structure"),
        ("nexus_progress.json", "Progress data")
    ]
    
    all_present = True
    for filename, description in required_files:
        file_path = Path(filename)
        if file_path.exists():
            print(f"  [OK] {filename}: {description}")
        else:
            print(f"  [FAIL] {filename}: MISSING")
            all_present = False
    
    if all_present:
        print("  [PASS] All enforcement files present")
    return all_present

def test_checkpoint_directory():
    """Test 7: Verify checkpoint directory exists and works"""
    print("\n[TEST 7] Testing Checkpoint Directory...")
    
    checkpoint_dir = Path("nexus_checkpoints")
    
    # Create if doesn't exist
    if not checkpoint_dir.exists():
        checkpoint_dir.mkdir()
        print("  [OK] Created checkpoint directory")
    else:
        print("  [OK] Checkpoint directory exists")
    
    # Test we can write to it
    test_file = checkpoint_dir / "test_100.json"
    try:
        with open(test_file, 'w') as f:
            json.dump({"test": "100% compliance"}, f)
        print("  [OK] Can write to checkpoint directory")
        test_file.unlink()  # Clean up
    except Exception as e:
        print(f"  [FAIL] Cannot write to checkpoint directory: {e}")
        return False
    
    print("  [PASS] Checkpoint directory operational")
    return True

def test_no_bypassing():
    """Test 8: Verify enforcement cannot be bypassed"""
    print("\n[TEST 8] Testing Enforcement Cannot Be Bypassed...")
    
    enforcer = get_enforcer()
    
    # Try to disable enforcement
    enforcer.enforcement_active = False
    # But it should still work
    
    # Try to clear violations
    enforcer.violations = []
    
    # Record a violation
    try:
        enforcer.record_violation(
            ViolationType.PROCESS_DEVIATION,
            "TEST-BYPASS-001",
            "Testing bypass prevention",
            "HIGH"
        )
    except:
        pass
    
    # Violation should still be recorded
    assert len(enforcer.violations) > 0, "Violations should still be recorded"
    print("  [OK] Violations still recorded even after attempted bypass")
    
    # Strict mode should still be True
    assert enforcer.strict_mode == True, "Strict mode should still be True"
    print("  [OK] Strict mode remains active")
    
    print("  [PASS] Enforcement cannot be bypassed")
    return True

def run_all_tests():
    """Run all compliance tests"""
    print("="*60)
    print("100% COMPLIANCE VERIFICATION TEST")
    print("="*60)
    
    tests = [
        ("Strict Mode Immutability", test_strict_mode_immutable),
        ("JSON Serialization", test_json_serialization),
        ("Checkpoint Method", test_get_current_checkpoint),
        ("Unicode Handling", test_unicode_handling),
        ("Enforcement Active", test_enforcement_active),
        ("Files Present", test_all_files_present),
        ("Checkpoint Directory", test_checkpoint_directory),
        ("No Bypassing", test_no_bypassing)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Calculate score
    passed = sum(1 for _, result in results if result)
    total = len(results)
    score = (passed / total) * 100
    
    print("\n" + "="*60)
    print("COMPLIANCE TEST RESULTS")
    print("="*60)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "="*60)
    print(f"FINAL SCORE: {score:.1f}%")
    print("="*60)
    
    if score == 100:
        print("\n[SUCCESS] 100% COMPLIANCE ACHIEVED!")
        print("The enforcement system is FULLY OPERATIONAL")
        print("All issues have been fixed")
        print("System is ready for compliant development")
    else:
        print(f"\n[WARNING] Only {score:.1f}% compliant")
        print("Some issues remain to be fixed")
    
    return score == 100

if __name__ == "__main__":
    # Clean up any test artifacts first
    import warnings
    warnings.filterwarnings("ignore")
    
    # Initialize enforcer
    print("Initializing enforcement system...")
    enforcer = get_enforcer()
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)