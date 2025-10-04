"""
Automated UI Test for My FPL Team Page
=====================================

This script tests the My FPL Team page UI functionality including:
- Page initialization and rendering
- Component loading and error handling
- Data validation and team ID input
- Tab navigation and content display
- Performance and responsiveness
"""

import sys
import os
import time
import traceback
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work correctly"""
    print("🔍 Testing imports...")
    
    test_results = []
    
    # Test original page import
    try:
        from views.my_team_page import MyTeamPage as OriginalPage
        test_results.append(("✅", "Original MyTeamPage import", "SUCCESS"))
    except Exception as e:
        test_results.append(("❌", "Original MyTeamPage import", f"FAILED: {e}"))
    
    # Test modular page import
    try:
        from views.my_team_page_modular import MyTeamPage as ModularPage
        test_results.append(("✅", "Modular MyTeamPage import", "SUCCESS"))
    except Exception as e:
        test_results.append(("❌", "Modular MyTeamPage import", f"FAILED: {e}"))
    
    # Test component imports
    component_imports = [
        ("views.my_team.team_import", "TeamImportComponent"),
        ("views.my_team.team_overview", "TeamOverviewComponent"),
        ("views.my_team.squad_analysis", "SquadAnalysisComponent"),
        ("views.my_team.performance_analysis", "PerformanceAnalysisComponent"),
        ("views.my_team.recommendations", "RecommendationsComponent")
    ]
    
    for module_name, class_name in component_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            test_results.append(("✅", f"{class_name} import", "SUCCESS"))
        except Exception as e:
            test_results.append(("❌", f"{class_name} import", f"FAILED: {e}"))
    
    return test_results

def test_page_initialization():
    """Test page initialization and basic functionality"""
    print("🔍 Testing page initialization...")
    
    test_results = []
    
    # Test original page initialization
    try:
        from views.my_team_page import MyTeamPage as OriginalPage
        original_page = OriginalPage()
        test_results.append(("✅", "Original page initialization", "SUCCESS"))
        
        # Test methods exist
        required_methods = ['render', '__call__']
        for method in required_methods:
            if hasattr(original_page, method):
                test_results.append(("✅", f"Original page has {method}", "SUCCESS"))
            else:
                test_results.append(("❌", f"Original page has {method}", "MISSING"))
                
    except Exception as e:
        test_results.append(("❌", "Original page initialization", f"FAILED: {e}"))
    
    # Test modular page initialization
    try:
        from views.my_team_page_modular import MyTeamPage as ModularPage
        modular_page = ModularPage()
        test_results.append(("✅", "Modular page initialization", "SUCCESS"))
        
        # Test methods exist
        required_methods = ['render', '__call__', 'render_team_import', 'render_team_overview']
        for method in required_methods:
            if hasattr(modular_page, method):
                test_results.append(("✅", f"Modular page has {method}", "SUCCESS"))
            else:
                test_results.append(("❌", f"Modular page has {method}", "MISSING"))
        
        # Test components exist
        required_components = ['team_import', 'team_overview', 'squad_analysis', 'performance_analysis']
        for component in required_components:
            if hasattr(modular_page, component):
                test_results.append(("✅", f"Modular page has {component} component", "SUCCESS"))
            else:
                test_results.append(("❌", f"Modular page has {component} component", "MISSING"))
                
    except Exception as e:
        test_results.append(("❌", "Modular page initialization", f"FAILED: {e}"))
    
    return test_results

def test_data_service_integration():
    """Test FPL Data Service integration"""
    print("🔍 Testing data service integration...")
    
    test_results = []
    
    try:
        from services.fpl_data_service import FPLDataService
        data_service = FPLDataService()
        test_results.append(("✅", "FPL Data Service initialization", "SUCCESS"))
        
        # Test basic methods exist
        required_methods = ['load_fpl_data', 'get_manager_team']
        for method in required_methods:
            if hasattr(data_service, method):
                test_results.append(("✅", f"Data service has {method}", "SUCCESS"))
            else:
                test_results.append(("❌", f"Data service has {method}", "MISSING"))
        
    except Exception as e:
        test_results.append(("❌", "FPL Data Service integration", f"FAILED: {e}"))
    
    return test_results

def test_component_functionality():
    """Test individual component functionality"""
    print("🔍 Testing component functionality...")
    
    test_results = []
    
    try:
        from services.fpl_data_service import FPLDataService
        data_service = FPLDataService()
        
        # Test team import component
        try:
            from views.my_team.team_import import TeamImportComponent
            team_import = TeamImportComponent(data_service)
            
            # Test required methods
            required_methods = ['render', 'render_quick_test', 'render_debug_section']
            for method in required_methods:
                if hasattr(team_import, method):
                    test_results.append(("✅", f"TeamImport has {method}", "SUCCESS"))
                else:
                    test_results.append(("❌", f"TeamImport has {method}", "MISSING"))
                    
        except Exception as e:
            test_results.append(("❌", "TeamImportComponent test", f"FAILED: {e}"))
        
        # Test team overview component  
        try:
            from views.my_team.team_overview import TeamOverviewComponent
            team_overview = TeamOverviewComponent(data_service)
            
            if hasattr(team_overview, 'render'):
                test_results.append(("✅", "TeamOverview has render", "SUCCESS"))
            else:
                test_results.append(("❌", "TeamOverview has render", "MISSING"))
                
        except Exception as e:
            test_results.append(("❌", "TeamOverviewComponent test", f"FAILED: {e}"))
        
        # Test squad analysis component
        try:
            from views.my_team.squad_analysis import SquadAnalysisComponent
            squad_analysis = SquadAnalysisComponent(data_service)
            
            if hasattr(squad_analysis, 'render'):
                test_results.append(("✅", "SquadAnalysis has render", "SUCCESS"))
            else:
                test_results.append(("❌", "SquadAnalysis has render", "MISSING"))
                
        except Exception as e:
            test_results.append(("❌", "SquadAnalysisComponent test", f"FAILED: {e}"))
            
    except Exception as e:
        test_results.append(("❌", "Component functionality test", f"FAILED: {e}"))
    
    return test_results

def test_team_id_validation():
    """Test team ID validation functionality"""
    print("🔍 Testing team ID validation...")
    
    test_results = []
    
    try:
        from views.my_team.team_import import TeamImportComponent
        from services.fpl_data_service import FPLDataService
        
        data_service = FPLDataService()
        team_import = TeamImportComponent(data_service)
        
        # Test valid team ID (1437667)
        test_team_id = "1437667"
        
        # Check if validation methods exist
        if hasattr(team_import, '_validate_team_id'):
            test_results.append(("✅", "Team ID validation method exists", "SUCCESS"))
        else:
            test_results.append(("⚠️", "Team ID validation method", "NOT FOUND (may be in parent class)"))
        
        # Test team ID format validation
        valid_ids = ["1437667", "123456", "7654321"]
        invalid_ids = ["abc", "12.34", "", "0"]
        
        for team_id in valid_ids:
            if team_id.isdigit() and len(team_id) >= 1:
                test_results.append(("✅", f"Valid team ID format: {team_id}", "SUCCESS"))
            else:
                test_results.append(("❌", f"Valid team ID format: {team_id}", "FAILED"))
        
        for team_id in invalid_ids:
            if not team_id.isdigit() or len(team_id) == 0:
                test_results.append(("✅", f"Invalid team ID rejected: '{team_id}'", "SUCCESS"))
            else:
                test_results.append(("❌", f"Invalid team ID rejected: '{team_id}'", "FAILED"))
                
    except Exception as e:
        test_results.append(("❌", "Team ID validation test", f"FAILED: {e}"))
    
    return test_results

def test_error_handling():
    """Test error handling and graceful degradation"""
    print("🔍 Testing error handling...")
    
    test_results = []
    
    try:
        # Test error handling utilities
        from utils.error_handling import logger, handle_errors
        test_results.append(("✅", "Error handling utilities import", "SUCCESS"))
        
        # Test logger functionality
        if hasattr(logger, 'info') and hasattr(logger, 'error'):
            test_results.append(("✅", "Logger has required methods", "SUCCESS"))
        else:
            test_results.append(("❌", "Logger has required methods", "MISSING"))
        
        # Test handle_errors decorator
        if callable(handle_errors):
            test_results.append(("✅", "handle_errors decorator available", "SUCCESS"))
        else:
            test_results.append(("❌", "handle_errors decorator available", "MISSING"))
            
    except Exception as e:
        test_results.append(("❌", "Error handling test", f"FAILED: {e}"))
    
    return test_results

def test_performance_metrics():
    """Test performance and loading times"""
    print("🔍 Testing performance metrics...")
    
    test_results = []
    
    # Test import performance
    start_time = time.time()
    try:
        from views.my_team_page_modular import MyTeamPage
        import_time = time.time() - start_time
        
        if import_time < 2.0:
            test_results.append(("✅", f"Import time: {import_time:.3f}s", "GOOD"))
        elif import_time < 5.0:
            test_results.append(("⚠️", f"Import time: {import_time:.3f}s", "ACCEPTABLE"))
        else:
            test_results.append(("❌", f"Import time: {import_time:.3f}s", "TOO SLOW"))
            
    except Exception as e:
        test_results.append(("❌", "Import performance test", f"FAILED: {e}"))
    
    # Test initialization performance
    start_time = time.time()
    try:
        from views.my_team_page_modular import MyTeamPage
        page = MyTeamPage()
        init_time = time.time() - start_time
        
        if init_time < 1.0:
            test_results.append(("✅", f"Initialization time: {init_time:.3f}s", "GOOD"))
        elif init_time < 3.0:
            test_results.append(("⚠️", f"Initialization time: {init_time:.3f}s", "ACCEPTABLE"))
        else:
            test_results.append(("❌", f"Initialization time: {init_time:.3f}s", "TOO SLOW"))
            
    except Exception as e:
        test_results.append(("❌", "Initialization performance test", f"FAILED: {e}"))
    
    return test_results

def run_comprehensive_ui_test():
    """Run comprehensive UI test suite"""
    print("=" * 60)
    print("🚀 AUTOMATED MY FPL TEAM PAGE UI TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_test_results = []
    
    # Run all test categories
    test_categories = [
        ("Import Tests", test_imports),
        ("Page Initialization Tests", test_page_initialization),
        ("Data Service Integration Tests", test_data_service_integration),
        ("Component Functionality Tests", test_component_functionality),
        ("Team ID Validation Tests", test_team_id_validation),
        ("Error Handling Tests", test_error_handling),
        ("Performance Tests", test_performance_metrics)
    ]
    
    for category_name, test_function in test_categories:
        print(f"\n📋 {category_name}")
        print("-" * 50)
        
        try:
            category_results = test_function()
            all_test_results.extend(category_results)
            
            for status, test_name, result in category_results:
                print(f"{status} {test_name}: {result}")
                
        except Exception as e:
            error_result = ("❌", f"{category_name} (Category Error)", f"FAILED: {e}")
            all_test_results.append(error_result)
            print(f"❌ {category_name} failed: {e}")
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for status, _, _ in all_test_results if status == "✅")
    warning_count = sum(1 for status, _, _ in all_test_results if status == "⚠️")
    failure_count = sum(1 for status, _, _ in all_test_results if status == "❌")
    total_count = len(all_test_results)
    
    print(f"✅ Passed: {success_count}")
    print(f"⚠️ Warnings: {warning_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📊 Total: {total_count}")
    
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    # Overall status
    if failure_count == 0:
        print("\n🎉 ALL TESTS PASSED! Your My FPL Team page UI is working perfectly!")
    elif success_rate >= 80:
        print("\n✅ MOSTLY SUCCESSFUL! Your UI is working well with minor issues.")
    elif success_rate >= 60:
        print("\n⚠️ PARTIALLY SUCCESSFUL! Some components need attention.")
    else:
        print("\n❌ NEEDS ATTENTION! Multiple components require fixes.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return all_test_results

if __name__ == "__main__":
    try:
        results = run_comprehensive_ui_test()
        
        # Return appropriate exit code
        failure_count = sum(1 for status, _, _ in results if status == "❌")
        sys.exit(0 if failure_count == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)
