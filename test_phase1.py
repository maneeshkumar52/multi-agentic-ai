#!/usr/bin/env python3
"""
Phase 1 Testing Script
Tests all core utilities and dependencies
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing Config and Logger"""
    print("1. Testing imports...")
    try:
        from utils import Config, Logger
        print("✓ Config and Logger imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_env_variables():
    """Test environment variables loaded"""
    print("\n2. Testing environment variables...")
    from utils import Config

    vars_to_check = [
        ('SMTP_HOST', Config.SMTP_HOST),
        ('SMTP_PORT', Config.SMTP_PORT),
        ('SMTP_USER', Config.SMTP_USER),
        ('SMTP_PASSWORD', Config.SMTP_PASSWORD),
        ('AZURE_OPENAI_API_KEY', Config.AZURE_OPENAI_API_KEY),
        ('AZURE_OPENAI_ENDPOINT', Config.AZURE_OPENAI_ENDPOINT),
        ('AZURE_OPENAI_API_VERSION', Config.AZURE_OPENAI_API_VERSION),
        ('AZURE_OPENAI_DEPLOYMENT', Config.AZURE_OPENAI_DEPLOYMENT),
        ('FROM_EMAIL', Config.FROM_EMAIL),
        ('DEFAULT_TO_EMAIL', Config.DEFAULT_TO_EMAIL),
        ('OUTPUT_DIR', Config.OUTPUT_DIR),
    ]

    all_loaded = True
    for var_name, value in vars_to_check:
        if value is not None:
            print(f"✓ {var_name}: {value}")
        else:
            print(f"✗ {var_name}: Not loaded")
            all_loaded = False

    return all_loaded

def test_output_dir():
    """Test OUTPUT_DIR exists and is writable"""
    print("\n3. Testing OUTPUT_DIR...")
    from utils import Config

    if not Config.OUTPUT_DIR:
        print("✗ OUTPUT_DIR is None")
        return False

    try:
        Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # Test writability
        test_file = Config.OUTPUT_DIR / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()  # Remove test file
        print(f"✓ OUTPUT_DIR exists and is writable: {Config.OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"✗ OUTPUT_DIR error: {e}")
        return False

def test_logger_singleton():
    """Test Logger singleton behavior"""
    print("\n4. Testing Logger singleton...")
    from utils import Logger

    logger1 = Logger()
    logger2 = Logger()

    if logger1 is logger2:
        print("✓ Logger singleton works correctly")
        return True
    else:
        print("✗ Logger singleton failed")
        return False

def test_config_validate():
    """Test Config.validate() returns empty list"""
    print("\n5. Testing Config.validate()...")
    from utils import Config

    errors = Config.validate()
    if not errors:
        print("✓ Config.validate() returns empty list")
        return True
    else:
        print(f"✗ Config validation errors: {errors}")
        return False

def test_logger_methods():
    """Test Logger methods"""
    print("\n6. Testing Logger methods...")
    from utils import Logger

    logger = Logger()

    try:
        logger.log_agent_activity("TestAgent", "test_action", "test_details")
        logger.log_error("Test error message")
        print("✓ Logger methods work correctly")
        return True
    except Exception as e:
        print(f"✗ Logger methods failed: {e}")
        return False

def test_virtual_env():
    """Test virtual environment Python path"""
    print("\n7. Testing virtual environment...")
    venv_indicators = ['venv', '.venv', 'virtualenv', 'conda']
    python_path = sys.executable.lower()

    is_venv = any(indicator in python_path for indicator in venv_indicators)

    if is_venv:
        print(f"✓ Using virtual environment: {sys.executable}")
        return True
    else:
        print(f"⚠ Not using virtual environment: {sys.executable}")
        # Don't fail, just warn
        return True

def test_pymupdf_import():
    """Test PyMuPDF import with both methods"""
    print("\n8. Testing PyMuPDF import...")

    # Test method 1: import fitz
    try:
        import fitz
        print(f"✓ import fitz works: {fitz.__version__}")
        method1_success = True
    except ImportError:
        print("⚠ import fitz failed (expected for PyMuPDF >= 1.24)")
        method1_success = False

    # Test method 2: import pymupdf as fitz
    try:
        import pymupdf as fitz
        print(f"✓ import pymupdf as fitz works: {fitz.__version__}")
        method2_success = True
    except ImportError:
        print("✗ import pymupdf as fitz failed")
        method2_success = False

    if method1_success or method2_success:
        return True
    else:
        return False

def main():
    """Run all tests"""
    print("=== PHASE 1 TESTING ===\n")

    tests = [
        test_imports,
        test_env_variables,
        test_output_dir,
        test_logger_singleton,
        test_config_validate,
        test_logger_methods,
        test_virtual_env,
        test_pymupdf_import,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n=== RESULTS: {passed}/{total} tests passed ===")

    if passed == total:
        print("✓ PHASE 1 COMPLETE - Core utilities operational")
        return True
    else:
        print("✗ Some tests failed. Please fix issues and re-run.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)