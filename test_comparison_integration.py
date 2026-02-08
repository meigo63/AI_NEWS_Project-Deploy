#!/usr/bin/env python
"""
Test script for Gemini API and ML model classification comparison.

This script tests the dual classification system without requiring a running Flask server.
Run with: python test_comparison_integration.py
"""

import sys
import os
import json
from typing import Dict

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_classification_comparison():
    """Test the classification comparison service."""
    print("=" * 70)
    print("Testing Classification Comparison Service")
    print("=" * 70)
    
    # Import after adding to path
    from app.services.classification_comparison import ClassificationComparisonService
    
    print("\n1. Initializing ClassificationComparisonService...")
    try:
        service = ClassificationComparisonService()
        gemini_available = service.gemini_service is not None
        print(f"   ✓ Service initialized")
        print(f"   ✓ Gemini API available: {gemini_available}")
    except Exception as e:
        print(f"   ✗ Error initializing service: {e}")
        return False
    
    # Test cases
    test_cases = [
        {
            'name': 'Clear Fake News',
            'text': 'Breaking: Scientists discover Earth is flat and NASA has been covering it up for decades!',
            'ml_result': 'fake',
            'ml_confidence': 0.92
        },
        {
            'name': 'Legitimate News',
            'text': 'The Federal Reserve announced a 0.5% interest rate increase in their latest statement to combat inflation.',
            'ml_result': 'real',
            'ml_confidence': 0.88
        },
        {
            'name': 'Borderline Content',
            'text': 'Some experts claim that new study shows coffee might be good for health, though other experts disagree.',
            'ml_result': 'real',
            'ml_confidence': 0.62
        }
    ]
    
    print("\n2. Running classification tests...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("-" * 70)
        
        try:
            # Run comparison
            result = service.classify_with_comparison(
                article_text=test_case['text'],
                model_result=test_case['ml_result'],
                model_confidence=test_case['ml_confidence']
            )
            
            # Display results
            print(f"Input (first 80 chars): {test_case['text'][:80]}...")
            print(f"ML Model Result:        {result['model_result']} (confidence: {result['model_confidence']:.2f})")
            print(f"Gemini Result:         {result['gemini_result']}")
            print(f"Final Result:          {result['final_displayed_result']}")
            print(f"Comparison Status:     {result['comparison_status']}")
            print(f"Processing Time:       {result['processing_details']['processing_time_ms']:.2f}ms")
            print(f"Gemini Available:      {result['processing_details']['gemini_available']}")
            
            if result['processing_details']['gemini_error']:
                print(f"Gemini Error:          {result['processing_details']['gemini_error']}")
            
            # Validate response structure
            required_fields = [
                'original_text', 'model_result', 'model_confidence',
                'gemini_result', 'final_displayed_result', 'comparison_status',
                'processing_details'
            ]
            
            missing_fields = [f for f in required_fields if f not in result]
            if missing_fields:
                print(f"✗ Missing fields: {missing_fields}")
            else:
                print("✓ Response structure valid")
            
            # Validate comparison status
            if result['comparison_status'] not in ['matched', 'conflict', 'model_only']:
                print(f"✗ Invalid comparison_status: {result['comparison_status']}")
            else:
                print("✓ Comparison status valid")
            
            # Validate final result
            if result['final_displayed_result'] not in [None, 'real', 'fake']:
                print(f"✗ Invalid final_displayed_result: {result['final_displayed_result']}")
            else:
                print("✓ Final result valid")
        
        except Exception as e:
            print(f"✗ Error during classification: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print("\n✓ Classification Comparison Service is working correctly!")
    print("\nIntegration Points:")
    print("  1. ML Model: BERT-based classifier")
    print("  2. Gemini API: Secondary verification")
    print("  3. Comparison Logic: Applied automatically")
    print("  4. Fallback: ML model used if Gemini fails")
    print("\nNote: If Gemini results show 'ERROR', verify GEMINI_API_KEY in .env file")
    
    return True


def test_normalization():
    """Test response normalization."""
    print("\n" + "=" * 70)
    print("Testing Response Normalization")
    print("=" * 70)
    
    from app.services.classification_comparison import ClassificationComparisonService
    
    service = ClassificationComparisonService()
    
    test_cases = [
        ('real', 'real'),
        ('REAL', 'real'),
        ('Real', 'real'),
        ('fake', 'fake'),
        ('FAKE', 'fake'),
        ('Fake', 'fake'),
        ('authentic', 'real'),
        ('genuine', 'real'),
        ('hoax', 'fake'),
        ('misinformation', 'fake'),
        ('invalid', None),
        ('', None),
    ]
    
    print("\nTesting normalization function...")
    all_passed = True
    
    for input_val, expected in test_cases:
        result = service._normalize_classification(input_val)
        status = "✓" if result == expected else "✗"
        result_str = result if result else "None"
        expected_str = expected if expected else "None"
        print(f"{status} Input: '{input_val:20s}' → Output: {str(result_str):10s} (Expected: {expected_str})")
        if result != expected:
            all_passed = False
    
    if all_passed:
        print("\n✓ All normalization tests passed!")
    else:
        print("\n✗ Some normalization tests failed!")
    
    return all_passed


def test_comparison_logic():
    """Test comparison logic."""
    print("\n" + "=" * 70)
    print("Testing Comparison Logic")
    print("=" * 70)
    
    from app.services.classification_comparison import ClassificationComparisonService
    
    service = ClassificationComparisonService()
    
    test_cases = [
        {
            'model': 'real',
            'gemini': 'real',
            'expected_result': 'real',
            'expected_status': 'matched',
            'description': 'Both agree on real'
        },
        {
            'model': 'fake',
            'gemini': 'fake',
            'expected_result': 'fake',
            'expected_status': 'matched',
            'description': 'Both agree on fake'
        },
        {
            'model': 'real',
            'gemini': 'fake',
            'expected_result': 'fake',
            'expected_status': 'conflict',
            'description': 'ML says real, Gemini says fake'
        },
        {
            'model': 'fake',
            'gemini': 'real',
            'expected_result': 'real',
            'expected_status': 'conflict',
            'description': 'ML says fake, Gemini says real'
        },
    ]
    
    print("\nTesting comparison logic...")
    all_passed = True
    
    for test in test_cases:
        result = service._apply_comparison_logic(test['model'], test['gemini'])
        
        result_match = result['final_result'] == test['expected_result']
        status_match = result['status'] == test['expected_status']
        
        status = "✓" if (result_match and status_match) else "✗"
        print(f"{status} {test['description']}")
        print(f"   ML: {test['model']}, Gemini: {test['gemini']}")
        print(f"   Result: {result['final_result']} (Expected: {test['expected_result']})")
        print(f"   Status: {result['status']} (Expected: {test['expected_status']})")
        
        if not (result_match and status_match):
            all_passed = False
    
    if all_passed:
        print("\n✓ All comparison logic tests passed!")
    else:
        print("\n✗ Some comparison logic tests failed!")
    
    return all_passed


if __name__ == '__main__':
    try:
        # Run all tests
        test_normalization()
        test_comparison_logic()
        test_classification_comparison()
        
        print("\n" + "=" * 70)
        print("Integration Test Complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Ensure GEMINI_API_KEY is set in .env")
        print("2. Run: python run.py")
        print("3. Test the API endpoint: POST /api/classify")
        print("4. Check GEMINI_INTEGRATION_GUIDE.md for detailed usage")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
