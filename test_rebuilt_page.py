"""
Test Script for Rebuilt My FPL Team Page
=======================================

This script tests the rebuilt My FPL Team page with modern UI components.
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rebuilt_page():
    """Test the rebuilt My FPL Team page"""
    print("=" * 70)
    print("🎨 TESTING REBUILT MY FPL TEAM PAGE")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    try:
        # Test 1: Import rebuilt page
        print("🔍 Test 1: Import Rebuilt Page...")
        from views.my_team_page_rebuilt import RebuildMyTeamPage
        test_results.append(("✅", "Rebuilt page import", "SUCCESS"))
        print("✅ Rebuilt page imported successfully")
        
        # Test 2: Initialize page
        print("\n🔍 Test 2: Initialize Page...")
        page = RebuildMyTeamPage()
        test_results.append(("✅", "Page initialization", "SUCCESS"))
        print("✅ Page initialized successfully")
        
        # Test 3: Check version and title
        print("\n🔍 Test 3: Check Version and Title...")
        if hasattr(page, 'version') and "2.0 - Rebuilt" in page.version:
            test_results.append(("✅", "Version identification", "SUCCESS"))
            print(f"✅ Version: {page.version}")
        else:
            test_results.append(("❌", "Version identification", "MISSING"))
            print("❌ Version not found")
        
        if hasattr(page, 'page_title') and page.page_title:
            test_results.append(("✅", "Page title", "SUCCESS"))
            print(f"✅ Title: {page.page_title}")
        else:
            test_results.append(("❌", "Page title", "MISSING"))
            print("❌ Page title not found")
        
        # Test 4: Check core methods
        print("\n🔍 Test 4: Check Core Methods...")
        required_methods = [
            'render', '__call__', '_setup_page_config', '_render_header',
            '_initialize_session_state', '_render_team_import_section',
            '_render_team_dashboard', '_validate_team_id', '_load_team'
        ]
        
        for method in required_methods:
            if hasattr(page, method) and callable(getattr(page, method)):
                test_results.append(("✅", f"Method {method}", "AVAILABLE"))
                print(f"✅ Method {method} is available")
            else:
                test_results.append(("❌", f"Method {method}", "MISSING"))
                print(f"❌ Method {method} is missing")
        
        # Test 5: Check data service integration
        print("\n🔍 Test 5: Data Service Integration...")
        if hasattr(page, 'data_service'):
            test_results.append(("✅", "Data service integration", "SUCCESS"))
            print("✅ Data service integrated")
            
            if hasattr(page.data_service, 'load_fpl_data'):
                test_results.append(("✅", "Data service methods", "SUCCESS"))
                print("✅ Data service methods available")
            else:
                test_results.append(("❌", "Data service methods", "MISSING"))
                print("❌ Data service methods missing")
        else:
            test_results.append(("❌", "Data service integration", "MISSING"))
            print("❌ Data service not integrated")
        
        # Test 6: Test team ID validation
        print("\n🔍 Test 6: Team ID Validation...")
        test_ids = ["1437667", "123456", "abc", "", "0"]
        valid_results = [True, True, False, False, False]
        
        for test_id, expected in zip(test_ids, valid_results):
            result = page._validate_team_id(test_id)
            if result == expected:
                test_results.append(("✅", f"Team ID validation '{test_id}'", "CORRECT"))
                print(f"✅ Team ID '{test_id}' validation: {result} (expected {expected})")
            else:
                test_results.append(("❌", f"Team ID validation '{test_id}'", "INCORRECT"))
                print(f"❌ Team ID '{test_id}' validation: {result} (expected {expected})")
        
        # Test 7: Test mock data generation
        print("\n🔍 Test 7: Mock Data Generation...")
        try:
            mock_data = page._get_mock_team_data("1437667")
            if isinstance(mock_data, dict) and 'entry_name' in mock_data:
                test_results.append(("✅", "Mock data generation", "SUCCESS"))
                print("✅ Mock data generated successfully")
                print(f"   Entry name: {mock_data.get('entry_name')}")
                print(f"   Points: {mock_data.get('summary_overall_points')}")
            else:
                test_results.append(("❌", "Mock data generation", "INVALID_FORMAT"))
                print("❌ Mock data format invalid")
        except Exception as e:
            test_results.append(("❌", "Mock data generation", f"ERROR: {e}"))
            print(f"❌ Mock data generation failed: {e}")
        
        # Test 8: Test recommendations system
        print("\n🔍 Test 8: Recommendations System...")
        try:
            mock_team_data = {
                'summary_overall_rank': 600000,
                'summary_event_points': 35
            }
            recommendations = page._generate_recommendations(mock_team_data)
            
            if isinstance(recommendations, list) and len(recommendations) > 0:
                test_results.append(("✅", "Recommendations generation", "SUCCESS"))
                print(f"✅ Generated {len(recommendations)} recommendations")
                for i, rec in enumerate(recommendations[:2], 1):
                    print(f"   {i}. {rec.get('title', 'No title')}")
            else:
                test_results.append(("❌", "Recommendations generation", "EMPTY"))
                print("❌ No recommendations generated")
        except Exception as e:
            test_results.append(("❌", "Recommendations generation", f"ERROR: {e}"))
            print(f"❌ Recommendations failed: {e}")
        
        # Test 9: Test performance
        print("\n🔍 Test 9: Performance Test...")
        start_time = time.time()
        
        # Test multiple initializations
        for _ in range(5):
            test_page = RebuildMyTeamPage()
        
        total_time = time.time() - start_time
        avg_time = total_time / 5
        
        if avg_time < 0.1:
            test_results.append(("✅", f"Performance {avg_time:.4f}s avg", "EXCELLENT"))
            print(f"✅ Performance excellent: {avg_time:.4f}s average")
        elif avg_time < 0.5:
            test_results.append(("✅", f"Performance {avg_time:.4f}s avg", "GOOD"))
            print(f"✅ Performance good: {avg_time:.4f}s average")
        else:
            test_results.append(("⚠️", f"Performance {avg_time:.4f}s avg", "SLOW"))
            print(f"⚠️ Performance slow: {avg_time:.4f}s average")
        
        # Test 10: Test modern UI components import
        print("\n🔍 Test 10: Modern UI Components...")
        try:
            from utils.modern_ui_components import (
                create_metric_card, create_player_card, create_progress_bar
            )
            test_results.append(("✅", "Modern UI components import", "SUCCESS"))
            print("✅ Modern UI components imported successfully")
        except ImportError as e:
            test_results.append(("⚠️", "Modern UI components import", f"PARTIAL: {e}"))
            print(f"⚠️ Some modern UI components missing: {e}")
        except Exception as e:
            test_results.append(("❌", "Modern UI components import", f"ERROR: {e}"))
            print(f"❌ Modern UI components import failed: {e}")
        
    except Exception as e:
        test_results.append(("❌", "Rebuilt page test", f"CRITICAL_ERROR: {e}"))
        print(f"❌ Critical error in rebuilt page test: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 REBUILT PAGE TEST SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for status, _, _ in test_results if status == "✅")
    warning_count = sum(1 for status, _, _ in test_results if status == "⚠️")
    failure_count = sum(1 for status, _, _ in test_results if status == "❌")
    total_count = len(test_results)
    
    print(f"✅ Passed: {success_count}")
    print(f"⚠️ Warnings: {warning_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📊 Total: {total_count}")
    
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    # Overall assessment
    if failure_count == 0 and warning_count == 0:
        print("\n🎉 REBUILT PAGE PERFECT!")
        print("✅ All tests passed - ready for production!")
    elif failure_count == 0:
        print("\n✅ REBUILT PAGE EXCELLENT!")
        print("✅ Core functionality working with minor considerations")
    elif success_rate >= 80:
        print("\n⭐ REBUILT PAGE GOOD!")
        print("✅ Most functionality working - minor fixes needed")
    elif success_rate >= 60:
        print("\n⚠️ REBUILT PAGE NEEDS WORK!")
        print("⚠️ Some issues need attention before production")
    else:
        print("\n❌ REBUILT PAGE NEEDS MAJOR FIXES!")
        print("❌ Multiple critical issues require resolution")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return test_results

if __name__ == "__main__":
    try:
        results = test_rebuilt_page()
        
        # Return appropriate exit code
        failure_count = sum(1 for status, _, _ in results if status == "❌")
        sys.exit(0 if failure_count == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
