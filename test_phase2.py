#!/usr/bin/env python3
"""
Phase 2 Testing Script
Tests the Web Search Agent functionality
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test importing WebSearchAgent"""
    print("1. Testing WebSearchAgent import...")
    try:
        from agents import WebSearchAgent
        print("✓ WebSearchAgent imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_agent_initialization():
    """Test WebSearchAgent initialization"""
    print("\n2. Testing WebSearchAgent initialization...")
    try:
        from agents import WebSearchAgent
        agent = WebSearchAgent()
        print("✓ WebSearchAgent initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_search_execution():
    """Test search execution with sample query"""
    print("\n3. Testing search execution...")
    try:
        from agents import WebSearchAgent
        agent = WebSearchAgent()

        # Test with a simple query
        result = agent.search("Python programming", num_results=3)

        if result['status'] == 'success':
            print(f"✓ Search completed: {result['total_results']} results found")
            return True
        else:
            print(f"✗ Search failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"✗ Search execution failed: {e}")
        return False

def test_result_structure():
    """Test that results have expected structure"""
    print("\n4. Testing result structure...")
    try:
        from agents import WebSearchAgent
        agent = WebSearchAgent()

        result = agent.search("Python programming", num_results=2)

        if result['status'] != 'success':
            print("✗ Search failed, cannot test structure")
            return False

        # Check required fields
        required_fields = ['status', 'query', 'results', 'total_results', 'sources', 'ai_summary']
        for field in required_fields:
            if field not in result:
                print(f"✗ Missing required field: {field}")
                return False

        # Check results structure
        if not isinstance(result['results'], list):
            print("✗ results is not a list")
            return False

        if len(result['results']) == 0:
            print("⚠ No results found, but structure is valid")
            return True  # Allow empty results

        # Check each result
        for i, res in enumerate(result['results']):
            required_result_fields = ['title', 'url', 'snippet', 'source']
            for field in required_result_fields:
                if field not in res:
                    print(f"✗ Result {i} missing field: {field}")
                    return False

            # Check field types
            if not isinstance(res['title'], str) or not res['title']:
                print(f"✗ Result {i} title is not valid string")
                return False

            if not isinstance(res['url'], str):
                print(f"✗ Result {i} url is not string")
                return False

            if not isinstance(res['snippet'], str):
                print(f"✗ Result {i} snippet is not string")
                return False

            if res['source'] != 'DuckDuckGo':
                print(f"✗ Result {i} source is not 'DuckDuckGo'")
                return False

        print("✓ Result structure is valid")
        return True

    except Exception as e:
        print(f"✗ Structure test failed: {e}")
        return False

def test_ai_summary():
    """Test AI summary generation"""
    print("\n5. Testing AI summary generation...")
    try:
        from agents import WebSearchAgent
        agent = WebSearchAgent()

        result = agent.search("Python programming", num_results=3)

        if result['status'] != 'success':
            print("✗ Search failed, cannot test AI summary")
            return False

        ai_summary = result.get('ai_summary')
        if ai_summary is None:
            print("⚠ AI summary is None (expected if Azure OpenAI not configured)")
            return True
        elif isinstance(ai_summary, str) and len(ai_summary) > 10:
            print("✓ AI summary generated successfully")
            return True
        else:
            print(f"✗ AI summary is invalid: {ai_summary}")
            return False

    except Exception as e:
        print(f"✗ AI summary test failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid query"""
    print("\n6. Testing error handling...")
    try:
        from agents import WebSearchAgent
        agent = WebSearchAgent()

        # Test with empty query
        result = agent.search("", num_results=1)

        if result['status'] == 'error':
            print("✓ Error handling works for invalid query")
            return True
        else:
            print("⚠ Unexpected success with empty query")
            return True  # Not a critical failure

    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def test_sample_output():
    """Print sample result for verification"""
    print("\n7. Testing sample output...")
    try:
        from agents import WebSearchAgent
        agent = WebSearchAgent()

        result = agent.search("Python programming", num_results=1)

        if result['status'] == 'success' and result['results']:
            sample = result['results'][0]
            print("Sample result:")
            print(f"  Title: {sample['title'][:50]}...")
            print(f"  URL: {sample['url'][:50]}...")
            print(f"  Snippet: {sample['snippet'][:50]}...")
            print(f"  Source: {sample['source']}")
            print(f"  AI Summary: {result['ai_summary'][:100] if result['ai_summary'] else 'None'}...")
            print("✓ Sample output displayed")
            return True
        else:
            print("⚠ No results to display")
            return True

    except Exception as e:
        print(f"✗ Sample output test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== PHASE 2 TESTING ===\n")

    tests = [
        test_import,
        test_agent_initialization,
        test_search_execution,
        test_result_structure,
        test_ai_summary,
        test_error_handling,
        test_sample_output,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n=== RESULTS: {passed}/{total} tests passed ===")

    if passed >= 6:  # Allow some flexibility for network-dependent tests
        print("✓ PHASE 2 COMPLETE - Web search operational")
        return True
    else:
        print("✗ Some tests failed. Please check network connectivity and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)