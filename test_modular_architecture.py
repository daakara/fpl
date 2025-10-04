"""
Test Modular My Team Page - Validates the new component-based architecture
"""
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_modular_architecture():
    """Test the modular My Team page architecture"""
    print("🧪 TESTING MODULAR MY TEAM PAGE ARCHITECTURE")
    print("=" * 60)
    
    results = {
        'imports_passed': 0,
        'imports_failed': 0,
        'components_tested': 0,
        'components_passed': 0,
        'errors': []
    }
    
    # Test 1: Import the modular page
    print("\n1️⃣ Testing Modular Page Import...")
    try:
        from views.my_team_page_modular import ModularMyTeamPage, MyTeamPage
        results['imports_passed'] += 1
        print("✅ Modular page imported successfully")
        
        # Test backward compatibility alias
        if MyTeamPage == ModularMyTeamPage:
            print("✅ Backward compatibility alias working")
        else:
            print("⚠️ Backward compatibility alias not working")
            
    except Exception as e:
        results['imports_failed'] += 1
        results['errors'].append(f"Modular page import failed: {str(e)}")
        print(f"❌ Modular page import failed: {str(e)}")
        return results
    
    # Test 2: Import individual components
    print("\n2️⃣ Testing Component Imports...")
    
    components_to_test = [
        ("TeamImportComponent", "views.my_team.team_import"),
        ("TeamOverviewComponent", "views.my_team.team_overview"),
        ("SquadAnalysisComponent", "views.my_team.squad_analysis"),
        ("PerformanceAnalysisComponent", "views.my_team.performance_analysis"),
        ("RecommendationsComponent", "views.my_team.recommendations"),
        ("BaseTeamComponent", "views.my_team.base_component")
    ]
    
    for component_name, module_path in components_to_test:
        try:
            module = __import__(module_path, fromlist=[component_name])
            component_class = getattr(module, component_name)
            results['imports_passed'] += 1
            print(f"   ✅ {component_name}")
        except Exception as e:
            results['imports_failed'] += 1
            results['errors'].append(f"{component_name}: {str(e)}")
            print(f"   ❌ {component_name}: {str(e)}")
    
    # Test 3: Initialize the modular page
    print("\n3️⃣ Testing Page Initialization...")
    try:
        page = ModularMyTeamPage()
        results['components_tested'] += 1
        results['components_passed'] += 1
        print("✅ Modular page initialized successfully")
        
        # Test component initialization
        component_attrs = [
            'team_import', 'team_overview', 'squad_analysis', 
            'performance_analysis', 'recommendations', 'data_service'
        ]
        
        for attr in component_attrs:
            results['components_tested'] += 1
            if hasattr(page, attr) and getattr(page, attr) is not None:
                results['components_passed'] += 1
                print(f"   ✅ {attr} component initialized")
            else:
                results['errors'].append(f"{attr} component not initialized")
                print(f"   ❌ {attr} component not initialized")
                
    except Exception as e:
        results['components_tested'] += 1
        results['errors'].append(f"Page initialization failed: {str(e)}")
        print(f"❌ Page initialization failed: {str(e)}")
    
    # Test 4: Check component methods
    print("\n4️⃣ Testing Component Methods...")
    try:
        # Test base component functionality
        from views.my_team.base_component import BaseTeamComponent
        from services.fpl_data_service import FPLDataService
        
        data_service = FPLDataService()
        base_component = type('TestComponent', (BaseTeamComponent,), {
            'render': lambda self: None
        })(data_service)
        
        results['components_tested'] += 1
        
        # Test base methods
        test_methods = ['get_session_data', 'set_session_data', 'validate_team_data', 'handle_error']
        for method in test_methods:
            if hasattr(base_component, method) and callable(getattr(base_component, method)):
                print(f"   ✅ {method} method available")
            else:
                results['errors'].append(f"{method} method missing")
                print(f"   ❌ {method} method missing")
        
        results['components_passed'] += 1
        
    except Exception as e:
        results['errors'].append(f"Component method testing failed: {str(e)}")
        print(f"❌ Component method testing failed: {str(e)}")
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 MODULAR ARCHITECTURE TEST RESULTS")
    print("=" * 60)
    
    total_imports = results['imports_passed'] + results['imports_failed']
    total_components = results['components_passed'] + (results['components_tested'] - results['components_passed'])
    
    print(f"📦 Import Tests:")
    print(f"   Passed: {results['imports_passed']}")
    print(f"   Failed: {results['imports_failed']}")
    print(f"   Success Rate: {(results['imports_passed']/total_imports*100):.1f}%")
    
    print(f"\n🔧 Component Tests:")
    print(f"   Passed: {results['components_passed']}")
    print(f"   Failed: {results['components_tested'] - results['components_passed']}")
    print(f"   Success Rate: {(results['components_passed']/results['components_tested']*100):.1f}%")
    
    overall_success = (results['imports_passed'] + results['components_passed']) / (total_imports + results['components_tested']) * 100
    
    print(f"\n🎯 Overall Success Rate: {overall_success:.1f}%")
    
    if results['errors']:
        print(f"\n❌ Issues Found ({len(results['errors'])}):")
        for i, error in enumerate(results['errors'][:5], 1):
            print(f"   {i}. {error}")
        if len(results['errors']) > 5:
            print(f"   ... and {len(results['errors']) - 5} more")
    
    print(f"\n🏁 CONCLUSION:")
    if overall_success >= 80:
        print("   ✅ Modular architecture is working well!")
        print("   🎉 Ready for integration and testing")
    elif overall_success >= 60:
        print("   ⚠️ Modular architecture mostly working")
        print("   🔧 Minor issues need attention")
    else:
        print("   ❌ Modular architecture needs significant work")
        print("   🛠️ Review errors above")
    
    print(f"\n📋 NEXT STEPS:")
    print("   1. Address any import issues shown above")
    print("   2. Test with actual Streamlit app")
    print("   3. Extract remaining functionality from original file")
    print("   4. Update main application imports")
    
    print("=" * 60)
    return results


if __name__ == "__main__":
    try:
        test_modular_architecture()
    except Exception as e:
        print(f"❌ Critical testing error: {str(e)}")
        import traceback
        traceback.print_exc()
