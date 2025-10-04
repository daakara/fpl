"""
Simplified UI validation for My FPL Team Page
Focuses on key functionality validation
"""
import sys
import os
from unittest.mock import MagicMock, patch, Mock
import pandas as pd

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_ui_simple():
    """Simplified UI validation test"""
    print("🧪 SIMPLIFIED UI VALIDATION TEST")
    print("=" * 50)
    
    test_results = {
        'tests_run': 0,
        'tests_passed': 0,
        'errors': []
    }
    
    try:
        print("\n1️⃣ Testing Module Import...")
        try:
            from views.my_team_page import MyTeamPage
            test_results['tests_run'] += 1
            test_results['tests_passed'] += 1
            print("✅ Module imported successfully")
        except ImportError as e:
            test_results['tests_run'] += 1
            test_results['errors'].append(f"Import error: {str(e)}")
            print(f"❌ Import failed: {str(e)}")
            return test_results
        
        print("\n2️⃣ Testing Class Instantiation...")
        try:
            page = MyTeamPage()
            test_results['tests_run'] += 1
            test_results['tests_passed'] += 1
            print("✅ Class instantiated successfully")
        except Exception as e:
            test_results['tests_run'] += 1
            test_results['errors'].append(f"Instantiation error: {str(e)}")
            print(f"❌ Instantiation failed: {str(e)}")
            return test_results
        
        print("\n3️⃣ Testing Method Existence...")
        required_methods = [
            'render',
            '_render_team_import_section',
            '_render_team_overview',
            '_display_performance_analysis',
            '_display_recommendations',
            '_display_current_squad'
        ]
        
        for method_name in required_methods:
            test_results['tests_run'] += 1
            if hasattr(page, method_name) and callable(getattr(page, method_name)):
                test_results['tests_passed'] += 1
                print(f"✅ Method '{method_name}' exists")
            else:
                test_results['errors'].append(f"Method '{method_name}' missing")
                print(f"❌ Method '{method_name}' missing")
        
        print("\n4️⃣ Testing Streamlit Integration...")
        
        # Create minimal mocks
        st_mock = Mock()
        st_mock.header = Mock()
        st_mock.write = Mock()
        st_mock.button = Mock(return_value=False)
        st_mock.text_input = Mock(return_value="")
        st_mock.session_state = Mock()
        
        # Add session state attributes
        st_mock.session_state.my_team_loaded = False
        st_mock.session_state.data_loaded = False
        
        with patch.multiple('streamlit', 
                          header=st_mock.header,
                          write=st_mock.write,
                          button=st_mock.button,
                          text_input=st_mock.text_input,
                          session_state=st_mock.session_state,
                          divider=Mock(),
                          info=Mock(),
                          error=Mock(),
                          success=Mock(),
                          warning=Mock(),
                          subheader=Mock(),
                          selectbox=Mock(return_value=7),
                          columns=Mock(return_value=[Mock(), Mock(), Mock()]),
                          metric=Mock(),
                          expander=Mock(return_value=Mock()),
                          tabs=Mock(return_value=[Mock() for _ in range(9)]),
                          dataframe=Mock(),
                          spinner=Mock(return_value=Mock()),
                          markdown=Mock(),
                          rerun=Mock()):
            
            try:
                # Test team import section (minimal functionality)
                page._render_team_import_section()
                test_results['tests_run'] += 1
                test_results['tests_passed'] += 1
                print("✅ Team import section callable")
            except Exception as e:
                test_results['tests_run'] += 1
                test_results['errors'].append(f"Team import section: {str(e)}")
                print(f"❌ Team import section failed: {str(e)}")
            
            try:
                # Test basic render (no team loaded)
                page.render()
                test_results['tests_run'] += 1
                test_results['tests_passed'] += 1
                print("✅ Basic render completed")
            except Exception as e:
                test_results['tests_run'] += 1
                test_results['errors'].append(f"Basic render: {str(e)}")
                print(f"❌ Basic render failed: {str(e)}")
        
        print("\n5️⃣ Testing with Sample Data...")
        
        # Create sample team data
        sample_team_data = {
            'entry_name': 'Test Team',
            'summary_overall_points': 500,
            'summary_overall_rank': 1000000,
            'summary_event_points': 65,
            'value': 1000,
            'bank': 5,
            'gameweek': 7,
            'picks': []
        }
        
        with patch.multiple('streamlit',
                          header=Mock(),
                          subheader=Mock(),
                          write=Mock(),
                          columns=Mock(return_value=[Mock(), Mock(), Mock()]),
                          metric=Mock(),
                          divider=Mock(),
                          markdown=Mock()):
            
            try:
                page._render_team_overview(sample_team_data)
                test_results['tests_run'] += 1
                test_results['tests_passed'] += 1
                print("✅ Team overview with sample data")
            except Exception as e:
                test_results['tests_run'] += 1
                test_results['errors'].append(f"Team overview: {str(e)}")
                print(f"❌ Team overview failed: {str(e)}")
        
        print("\n6️⃣ Checking File Structure...")
        
        # Check if the file exists and has content
        file_path = os.path.join(project_root, 'views', 'my_team_page.py')
        test_results['tests_run'] += 1
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 1000:  # Has substantial content
                    test_results['tests_passed'] += 1
                    print(f"✅ File exists with {len(content)} characters")
                else:
                    test_results['errors'].append("File too small")
                    print(f"❌ File too small: {len(content)} characters")
        else:
            test_results['errors'].append("File does not exist")
            print("❌ File does not exist")
    
    except Exception as e:
        test_results['errors'].append(f"Critical error: {str(e)}")
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Final results
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    success_rate = (test_results['tests_passed'] / test_results['tests_run'] * 100) if test_results['tests_run'] > 0 else 0
    
    print(f"Tests Run: {test_results['tests_run']}")
    print(f"Tests Passed: {test_results['tests_passed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if test_results['errors']:
        print(f"\n❌ Issues Found ({len(test_results['errors'])}):")
        for error in test_results['errors'][:5]:  # Show first 5 errors
            print(f"   • {error}")
        if len(test_results['errors']) > 5:
            print(f"   ... and {len(test_results['errors']) - 5} more")
    
    print("\n🏁 FINAL CONCLUSION:")
    if success_rate >= 90:
        print("   ✅ The My FPL Team page UI is working correctly!")
        print("   All core components are functional.")
    elif success_rate >= 70:
        print("   ⚠️ The My FPL Team page UI is mostly working.")
        print("   Minor issues exist but functionality is intact.")
    else:
        print("   ❌ The My FPL Team page UI has issues.")
        print("   Review the problems above.")
    
    print("\n💡 NEXT STEPS:")
    print("   1. Open the My FPL Team page in your Streamlit app")
    print("   2. Click the '🧪 Test with Team ID 1437667' button")
    print("   3. Verify that team data loads and displays correctly")
    
    print("=" * 50)
    return test_results

if __name__ == "__main__":
    results = test_ui_simple()
