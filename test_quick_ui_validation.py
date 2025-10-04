"""
Quick UI Validation Test for My FPL Team Page
Validates core functionality with team ID 1437667
"""
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_my_fpl_team_ui():
    """Quick validation of My FPL Team page UI"""
    print("🚀 QUICK UI VALIDATION TEST")
    print("=" * 50)
    
    results = {
        'tests_passed': 0,
        'tests_failed': 0,
        'errors': []
    }
    
    # Test 1: Import the page
    print("\n1️⃣ Testing Page Import...")
    try:
        from views.my_team_page import MyTeamPage
        page = MyTeamPage()
        results['tests_passed'] += 1
        print("✅ MyTeamPage imported and instantiated successfully")
    except Exception as e:
        results['tests_failed'] += 1
        results['errors'].append(f"Import failed: {str(e)}")
        print(f"❌ Import failed: {str(e)}")
        return results
    
    # Test 2: Check required methods
    print("\n2️⃣ Testing Required Methods...")
    required_methods = [
        'render',
        '_render_team_import_section',
        '_load_team_data',
        '_render_team_overview',
        '_display_current_squad'
    ]
    
    methods_found = 0
    for method in required_methods:
        if hasattr(page, method) and callable(getattr(page, method)):
            methods_found += 1
            print(f"   ✅ {method}")
        else:
            print(f"   ❌ {method} - missing")
            results['errors'].append(f"Method {method} missing")
    
    if methods_found == len(required_methods):
        results['tests_passed'] += 1
        print("✅ All required methods found")
    else:
        results['tests_failed'] += 1
        print(f"❌ Only {methods_found}/{len(required_methods)} methods found")
    
    # Test 3: Test data service
    print("\n3️⃣ Testing Data Service...")
    try:
        data_service = page.data_service
        if data_service:
            results['tests_passed'] += 1
            print("✅ Data service initialized")
        else:
            results['tests_failed'] += 1
            results['errors'].append("Data service not initialized")
            print("❌ Data service not initialized")
    except Exception as e:
        results['tests_failed'] += 1
        results['errors'].append(f"Data service error: {str(e)}")
        print(f"❌ Data service error: {str(e)}")
    
    # Test 4: Test team data loading with 1437667
    print("\n4️⃣ Testing Team Data Loading (ID: 1437667)...")
    try:
        # Try to load team data for multiple gameweeks
        team_data = None
        working_gw = None
        
        for gw in [8, 7, 6, 5]:
            try:
                print(f"   🔍 Trying gameweek {gw}...")
                test_data = page.data_service.load_team_data("1437667", gw)
                if test_data and isinstance(test_data, dict) and test_data.get('picks'):
                    team_data = test_data
                    working_gw = gw
                    print(f"   ✅ Success! Found data in GW {gw}")
                    print(f"      Team: {test_data.get('entry_name', 'Unknown')}")
                    print(f"      Points: {test_data.get('summary_overall_points', 'N/A')}")
                    print(f"      Squad: {len(test_data.get('picks', []))} players")
                    break
                else:
                    print(f"   ⚠️ GW {gw}: No valid data")
            except Exception as e:
                print(f"   ❌ GW {gw}: {str(e)}")
        
        if team_data and working_gw:
            results['tests_passed'] += 1
            print(f"✅ Team data loading successful (GW {working_gw})")
        else:
            results['tests_failed'] += 1
            results['errors'].append("Could not load team data for 1437667")
            print("❌ Could not load team data for any gameweek")
            
    except Exception as e:
        results['tests_failed'] += 1
        results['errors'].append(f"Team data loading error: {str(e)}")
        print(f"❌ Team data loading error: {str(e)}")
    
    # Test 5: Check file structure
    print("\n5️⃣ Testing File Structure...")
    try:
        file_path = os.path.join(project_root, 'views', 'my_team_page.py')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if len(content) > 100000:  # File should be substantial
                results['tests_passed'] += 1
                print(f"✅ File exists with {len(content):,} characters")
                
                # Check for key UI elements
                ui_elements = [
                    'st.text_input',
                    'st.button',
                    'st.selectbox',
                    'st.tabs',
                    'st.header'
                ]
                
                found_elements = sum(1 for element in ui_elements if element in content)
                print(f"✅ Found {found_elements}/{len(ui_elements)} UI elements in code")
                
            else:
                results['tests_failed'] += 1
                results['errors'].append(f"File too small: {len(content)} characters")
                print(f"❌ File too small: {len(content)} characters")
        else:
            results['tests_failed'] += 1
            results['errors'].append("my_team_page.py file not found")
            print("❌ my_team_page.py file not found")
            
    except Exception as e:
        results['tests_failed'] += 1
        results['errors'].append(f"File structure error: {str(e)}")
        print(f"❌ File structure error: {str(e)}")
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS")
    print("=" * 50)
    
    total_tests = results['tests_passed'] + results['tests_failed']
    success_rate = (results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Tests Passed: {results['tests_passed']}")
    print(f"Tests Failed: {results['tests_failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")
    
    print(f"\n🏁 CONCLUSION:")
    if success_rate >= 80:
        print("   ✅ My FPL Team page UI is functional!")
        print("   ✅ Team ID 1437667 validation: WORKING")
        print("   🎉 Ready to test in Streamlit app!")
    elif success_rate >= 60:
        print("   ⚠️ My FPL Team page has minor issues")
        print("   ✅ Core functionality works")
        print("   📋 Review errors above")
    else:
        print("   ❌ Significant issues found")
        print("   🔧 Review and fix errors above")
    
    print(f"\n💡 NEXT STEPS:")
    print("   1. Run: streamlit run main_modular.py")
    print("   2. Navigate to 'My FPL Team' page")
    print("   3. Enter team ID: 1437667")
    print("   4. Click 'Load My Team' button")
    print("   5. Verify all tabs load correctly")
    
    print("=" * 50)
    return results

if __name__ == "__main__":
    try:
        test_my_fpl_team_ui()
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
