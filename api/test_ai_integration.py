#!/usr/bin/env python3
"""
Simple test to verify AI-API integration components
Tests the integration without requiring Django to be running
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai', 'module3-ai'))

def test_ai_modules_available():
    """Test if AI modules can be imported"""
    print("Testing AI Module Imports...")
    try:
        from train_demand_model import EnergyDemandForecaster
        from optimize_sources import SourceOptimizer, EnergySource
        print("  ✓ AI modules import successfully")
        return True
    except ImportError as e:
        print(f"  ✗ AI modules import failed: {e}")
        return False

def test_ai_models_exist():
    """Test if trained models exist"""
    print("\nTesting AI Model Files...")
    model_path = os.path.join(os.path.dirname(__file__), '..', 'ai', 'models')
    
    required_files = [
        'demand_forecaster.h5',
        'demand_forecaster_config.json',
        'demand_forecaster_scalers.pkl',
        'optimizer_config.json'
    ]
    
    all_exist = True
    for file in required_files:
        filepath = os.path.join(model_path, file)
        if os.path.exists(filepath):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_integration_service():
    """Test the AI inference service logic (without Django)"""
    print("\nTesting AI Inference Service Logic...")
    
    # Test that we can read the service file
    service_path = os.path.join(os.path.dirname(__file__), 
                                'data_pipeline', 'services', 'ai_inference.py')
    
    if os.path.exists(service_path):
        print(f"  ✓ ai_inference.py exists")
        
        # Read and check for key components
        with open(service_path, 'r') as f:
            content = f.read()
            
        checks = {
            'AIInferenceService class': 'class AIInferenceService',
            'forecast_demand method': 'def forecast_demand',
            'recommend_source method': 'def recommend_source',
            'make_decision method': 'def make_decision',
            'is_available method': 'def is_available'
        }
        
        for name, pattern in checks.items():
            if pattern in content:
                print(f"  ✓ {name} implemented")
            else:
                print(f"  ✗ {name} missing")
                return False
        
        return True
    else:
        print(f"  ✗ ai_inference.py not found")
        return False

def test_api_endpoints():
    """Test that API view components exist"""
    print("\nTesting API Endpoint Configuration...")
    
    views_path = os.path.join(os.path.dirname(__file__), 'data_pipeline', 'views.py')
    urls_path = os.path.join(os.path.dirname(__file__), 'data_pipeline', 'urls.py')
    
    # Check views
    if os.path.exists(views_path):
        with open(views_path, 'r') as f:
            views_content = f.read()
        
        if 'class AIPredictionViewSet' in views_content:
            print("  ✓ AIPredictionViewSet class exists")
            
            endpoints = [
                ('status endpoint', 'def status'),
                ('forecast endpoint', 'def forecast'),
                ('recommend_source endpoint', 'def recommend_source'),
                ('decide endpoint', 'def decide')
            ]
            
            for name, pattern in endpoints:
                if pattern in views_content:
                    print(f"  ✓ {name} implemented")
                else:
                    print(f"  ✗ {name} missing")
        else:
            print("  ✗ AIPredictionViewSet not found")
            return False
    else:
        print("  ✗ views.py not found")
        return False
    
    # Check URLs
    if os.path.exists(urls_path):
        with open(urls_path, 'r') as f:
            urls_content = f.read()
        
        if 'ai' in urls_content and 'AIPredictionViewSet' in urls_content:
            print("  ✓ AI endpoints registered in URLs")
        else:
            print("  ✗ AI endpoints not registered")
            return False
    else:
        print("  ✗ urls.py not found")
        return False
    
    return True

def test_documentation():
    """Test that integration documentation exists"""
    print("\nTesting Documentation...")
    
    doc_path = os.path.join(os.path.dirname(__file__), '..', 'AI_API_INTEGRATION.md')
    
    if os.path.exists(doc_path):
        with open(doc_path, 'r') as f:
            doc_content = f.read()
        
        required_sections = [
            '## Architecture',
            '## API Endpoints',
            '/api/ai/status/',
            '/api/ai/forecast/',
            '/api/ai/recommend_source/',
            '/api/ai/decide/',
            '## Integration with Other Modules',
            '## Testing'
        ]
        
        all_present = True
        for section in required_sections:
            if section in doc_content:
                print(f"  ✓ {section}")
            else:
                print(f"  ✗ {section} missing")
                all_present = False
        
        return all_present
    else:
        print("  ✗ AI_API_INTEGRATION.md not found")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("AI-API INTEGRATION VERIFICATION")
    print("=" * 70)
    
    tests = [
        ("AI Modules", test_ai_modules_available),
        ("AI Model Files", test_ai_models_exist),
        ("Integration Service", test_integration_service),
        ("API Endpoints", test_api_endpoints),
        ("Documentation", test_documentation)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ AI-API INTEGRATION IS READY!")
        print("\nNext Steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run Django migrations: cd api && python manage.py migrate")
        print("  3. Start the server: python manage.py runserver")
        print("  4. Test endpoints: curl http://localhost:8000/api/ai/status/")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed - integration incomplete")
        return 1

if __name__ == "__main__":
    sys.exit(main())
