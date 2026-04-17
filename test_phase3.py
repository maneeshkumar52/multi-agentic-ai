#!/usr/bin/env python3
"""
Phase 3 Testing Script
Tests all agents and orchestrator for the multi-agent pipeline
"""

import sys
import os
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all required imports"""
    print("Testing imports...")

    try:
        from utils import Logger, Config
        from agents import WebSearchAgent, ComplianceGuardAgent, DocumentFormatterAgent, EmailerAgent
        from orchestrator import PipelineOrchestrator
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_config_validation():
    """Test configuration validation"""
    print("\nTesting configuration validation...")

    try:
        from utils import Config

        errors = Config.validate()
        if errors:
            print(f"✗ Config validation failed: {errors}")
            return False

        print("✓ Config validation passed")
        return True
    except Exception as e:
        print(f"✗ Config validation error: {e}")
        traceback.print_exc()
        return False

def test_compliance_guard_agent():
    """Test ComplianceGuardAgent"""
    print("\nTesting ComplianceGuardAgent...")

    try:
        from agents import ComplianceGuardAgent

        agent = ComplianceGuardAgent()

        # Test with good data (proper web search result format)
        good_data = {
            'status': 'success',
            'results': [
                {
                    'title': 'Test Article',
                    'url': 'https://example.com/article',
                    'snippet': 'This is a test snippet with proper content.',
                    'content': 'Full content here with citations.'
                }
            ],
            'ai_summary': 'This is a test summary.'
        }

        result = agent.validate(good_data)
        if result['status'] != 'success' or not result['approved']:
            print(f"✗ Compliance guard failed on good data: {result}")
            return False

        # Test with bad data (no citations)
        bad_data = {
            'status': 'success',
            'results': [
                {
                    'title': 'Bad Article',
                    'url': 'https://bad.com',
                    'snippet': 'No citations here.',
                    'content': 'Content without any sources.'
                }
            ],
            'ai_summary': 'Bad summary.'
        }

        result = agent.validate(bad_data)
        if result['status'] != 'success':
            print(f"✗ Compliance guard failed to process bad data: {result}")
            return False

        print("✓ ComplianceGuardAgent tests passed")
        return True
    except Exception as e:
        print(f"✗ ComplianceGuardAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_document_formatter_agent():
    """Test DocumentFormatterAgent"""
    print("\nTesting DocumentFormatterAgent...")

    try:
        from agents import DocumentFormatterAgent

        agent = DocumentFormatterAgent()

        # Test data (proper compliance result format)
        test_data = {
            'approved': True,
            'cleaned_results': [
                {
                    'title': 'Test Document',
                    'url': 'https://example.com',
                    'snippet': 'Test snippet',
                    'content': 'Test content'
                }
            ],
            'validated_summary': 'Test summary',
            'quality_score': 0.85,
            'original_count': 1,
            'cleaned_count': 1
        }

        result = agent.format_documents(test_data, "test query", "test_report")

        if result['status'] != 'success':
            print(f"✗ Document formatter failed: {result}")
            return False

        # Check if files were created
        files_created = result.get('files_created', [])
        if not files_created:
            print("✗ No files were created")
            return False

        # Verify files exist
        from utils import Config
        for file_path in files_created:
            full_path = Config.OUTPUT_DIR / file_path
            if not full_path.exists():
                print(f"✗ File not found: {full_path}")
                return False

        print(f"✓ DocumentFormatterAgent tests passed - created {len(files_created)} files")
        return True
    except Exception as e:
        print(f"✗ DocumentFormatterAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_emailer_agent():
    """Test EmailerAgent (without actually sending)"""
    print("\nTesting EmailerAgent...")

    try:
        from agents import EmailerAgent

        agent = EmailerAgent()

        # Test data
        test_data = {
            'results': [
                {
                    'title': 'Test Email',
                    'url': 'https://example.com',
                    'snippet': 'Test snippet',
                    'content': 'Test content'
                }
            ]
        }

        # Test with invalid email (should fail gracefully)
        result = agent.send_search_results_email(test_data, "invalid-email", [])

        # Should return error status for invalid email
        if result['status'] == 'error':
            print("✓ EmailerAgent handled invalid email gracefully")
            return True
        else:
            print(f"✗ EmailerAgent should have failed with invalid email: {result}")
            return False

    except Exception as e:
        print(f"✗ EmailerAgent test failed: {e}")
        traceback.print_exc()
        return False

def test_orchestrator():
    """Test PipelineOrchestrator"""
    print("\nTesting PipelineOrchestrator...")

    try:
        from orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()

        # Test configuration validation
        config_errors = orchestrator.validate_configuration()
        if config_errors:
            print(f"✗ Orchestrator config validation failed: {config_errors}")
            return False

        # Test pipeline with a simple query
        result = orchestrator.run_pipeline("test query", num_results=2, send_email=False)

        if result['status'] not in ['success', 'partial_success']:
            print(f"✗ Pipeline failed: {result}")
            return False

        # Check if compliance passed
        if not result.get('compliance_passed', False):
            print(f"✗ Pipeline rejected by compliance: {result.get('issues', [])}")
            return False

        print("✓ PipelineOrchestrator tests passed")
        return True
    except Exception as e:
        print(f"✗ PipelineOrchestrator test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all Phase 3 tests"""
    print("=== PHASE 3 TESTING ===\n")

    tests = [
        ("Imports", test_imports),
        ("Config Validation", test_config_validation),
        ("ComplianceGuardAgent", test_compliance_guard_agent),
        ("DocumentFormatterAgent", test_document_formatter_agent),
        ("EmailerAgent", test_emailer_agent),
        ("PipelineOrchestrator", test_orchestrator)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"FAILED: {test_name}")
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            traceback.print_exc()

    print(f"\n=== RESULTS ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL PHASE 3 TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())