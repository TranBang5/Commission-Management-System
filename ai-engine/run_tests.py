#!/usr/bin/env python3
"""
Script to run all tests for AI Engine
"""

import sys
import os
import subprocess
import asyncio

def run_test_file(test_file):
    """Run a specific test file"""
    print(f"\n{'='*50}")
    print(f"Running {test_file}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Test passed!")
            print(result.stdout)
        else:
            print("❌ Test failed!")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {str(e)}")
        return False

def run_pytest_tests():
    """Run pytest tests"""
    print(f"\n{'='*50}")
    print("Running pytest tests")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Pytest tests passed!")
            print(result.stdout)
        else:
            print("❌ Pytest tests failed!")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {str(e)}")
        return False

def main():
    """Main function to run all tests"""
    print("🧪 Running AI Engine Tests")
    print("="*50)
    
    # List of test files to run
    test_files = [
        "test_reward_simple.py",
        "tests/test_multilingual_nlp.py"
    ]
    
    passed_tests = 0
    total_tests = len(test_files) + 1  # +1 for pytest tests
    
    # Run individual test files
    for test_file in test_files:
        if os.path.exists(test_file):
            if run_test_file(test_file):
                passed_tests += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    # Run pytest tests
    if run_pytest_tests():
        passed_tests += 1
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
