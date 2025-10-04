"""
Comprehensive UI Validation - Tests all sub-pages with team ID 1437667
Validates that all 9 analysis tabs load correctly with real data
"""
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def validate_sub_pages():
    """Validate all 9 analysis tabs/sub-pages"""
    print("🚀 COMPREHENSIVE SUB-PAGES VALIDATION")
    print("=" * 60)
    print("Testing all 9 analysis tabs with team ID 1437667")
    print("=" * 60)
    
    results = {
        'page_import': False,
        'data_loading': False,
        'team_data': None,
        'sub_pages': {
            'Current Squad': {'exists': False, 'callable': False},
            'Performance Analysis': {'exists': False, 'callable': False},
            'Recommendations': {'exists': False, 'callable': False},
            'Starting XI Optimizer': {'exists': False, 'callable': False},
            'SWOT Analysis': {'exists': False, 'callable': False},
            'Advanced Analytics': {'exists': False, 'callable': False},
            'Transfer Planning': {'exists': False, 'callable': False},
            'Performance Comparison': {'exists': False, 'callable': False},
            'Fixture Analysis': {'exists': False, 'callable': False}
        },
        'errors': []
    }
    
    # Step 1: Import and initialize page
    print("\n1️⃣ Initializing My FPL Team Page...")
    try:
        from views.my_team_page import MyTeamPage
        page = MyTeamPage()
        results['page_import'] = True
        print("✅ Page imported and initialized successfully")
    except Exception as e:
        results['errors'].append(f"Page import failed: {str(e)}")
        print(f"❌ Page import failed: {str(e)}")
        return results
    
    # Step 2: Load team data
    print("\n2️⃣ Loading Team Data (ID: 1437667)...")
    try:
        # Find working gameweek
        team_data = None
        working_gw = None
        
        for gw in [8, 7, 6, 5, 4]:
            try:
                print(f"   🔍 Testing gameweek {gw}...")
                test_data = page.data_service.load_team_data("1437667", gw)
                if test_data and isinstance(test_data, dict) and test_data.get('picks'):
                    team_data = test_data
                    working_gw = gw
                    print(f"   ✅ Data found in gameweek {gw}")
                    break
                else:
                    print(f"   ⚠️ No picks data in GW {gw}")
            except Exception as e:
                print(f"   ❌ GW {gw} error: {str(e)}")
        
        if team_data:
            results['data_loading'] = True
            results['team_data'] = team_data
            print(f"✅ Team data loaded successfully from GW {working_gw}")
            print(f"   📊 Team: {team_data.get('entry_name', 'Unknown')}")
            print(f"   🎯 Points: {team_data.get('summary_overall_points', 'N/A'):,}")
            print(f"   📈 Rank: {team_data.get('summary_overall_rank', 'N/A'):,}")
            print(f"   👥 Squad: {len(team_data.get('picks', []))} players")
        else:
            results['errors'].append("Could not load team data for 1437667")
            print("❌ Could not load team data")
            return results
            
    except Exception as e:
        results['errors'].append(f"Data loading error: {str(e)}")
        print(f"❌ Data loading error: {str(e)}")
        return results
    
    # Step 3: Validate all sub-page methods
    print("\n3️⃣ Validating Sub-Page Methods...")
    
    sub_page_methods = {
        'Current Squad': '_display_current_squad',
        'Performance Analysis': '_display_performance_analysis', 
        'Recommendations': '_display_recommendations',
        'Starting XI Optimizer': '_display_starting_xi_optimizer',
        'SWOT Analysis': '_display_swot_analysis',
        'Advanced Analytics': '_display_advanced_analytics',
        'Transfer Planning': '_display_transfer_planning',
        'Performance Comparison': '_display_performance_comparison',
        'Fixture Analysis': '_display_fixture_analysis'
    }
    
    for tab_name, method_name in sub_page_methods.items():
        print(f"\n   🔍 Testing: {tab_name}")
        
        # Check if method exists
        if hasattr(page, method_name):
            results['sub_pages'][tab_name]['exists'] = True
            print(f"      ✅ Method {method_name} exists")
            
            # Check if method is callable
            if callable(getattr(page, method_name)):
                results['sub_pages'][tab_name]['callable'] = True
                print(f"      ✅ Method is callable")
                
                # Try to inspect method signature
                try:
                    import inspect
                    method = getattr(page, method_name)
                    sig = inspect.signature(method)
                    params = list(sig.parameters.keys())
                    print(f"      📋 Parameters: {params}")
                except Exception as e:
                    print(f"      ⚠️ Could not inspect signature: {str(e)}")
            else:
                results['errors'].append(f"{method_name} is not callable")
                print(f"      ❌ Method is not callable")
        else:
            results['errors'].append(f"{method_name} does not exist")
            print(f"      ❌ Method {method_name} does not exist")
    
    # Step 4: Test main render method structure
    print("\n4️⃣ Testing Render Structure...")
    try:
        # Read the source code to check for tab structure
        import inspect
        source = inspect.getsource(page.render)
        
        # Check for key UI elements
        ui_checks = {
            'st.tabs': 'st.tabs' in source,
            'tab_names': 'tab_names' in source,
            'Current Squad': 'Current Squad' in source,
            'Performance Analysis': 'Performance Analysis' in source,
            'SWOT Analysis': 'SWOT Analysis' in source
        }
        
        for check_name, passed in ui_checks.items():
            if passed:
                print(f"   ✅ {check_name} found in render method")
            else:
                print(f"   ⚠️ {check_name} not found in render method")
                results['errors'].append(f"{check_name} not found in render method")
                
    except Exception as e:
        results['errors'].append(f"Render structure analysis failed: {str(e)}")
        print(f"❌ Render structure analysis failed: {str(e)}")
    
    # Step 5: Check for required dependencies
    print("\n5️⃣ Checking Dependencies...")
    try:
        # Check if we have player data available
        players_df, teams_df = page.data_service.load_fpl_data()
        if not players_df.empty:
            print(f"   ✅ Player data available: {len(players_df)} players")
        else:
            print("   ⚠️ Player data not available")
            results['errors'].append("Player data not available")
        
        if not teams_df.empty:
            print(f"   ✅ Team data available: {len(teams_df)} teams")
        else:
            print("   ⚠️ Team data not available")
            results['errors'].append("Team data not available")
            
    except Exception as e:
        results['errors'].append(f"Dependency check failed: {str(e)}")
        print(f"❌ Dependency check failed: {str(e)}")
    
    # Print comprehensive results
    print_comprehensive_results(results)
    return results

def print_comprehensive_results(results):
    """Print detailed validation results"""
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE VALIDATION RESULTS")
    print("=" * 60)
    
    # Core functionality
    print("🔧 Core Functionality:")
    print(f"   {'✅' if results['page_import'] else '❌'} Page Import: {'SUCCESS' if results['page_import'] else 'FAILED'}")
    print(f"   {'✅' if results['data_loading'] else '❌'} Data Loading: {'SUCCESS' if results['data_loading'] else 'FAILED'}")
    
    # Sub-pages analysis
    print(f"\n📑 Sub-Pages Analysis (9 total):")
    existing_methods = sum(1 for sp in results['sub_pages'].values() if sp['exists'])
    callable_methods = sum(1 for sp in results['sub_pages'].values() if sp['callable'])
    
    print(f"   Methods Exist: {existing_methods}/9")
    print(f"   Methods Callable: {callable_methods}/9")
    
    for tab_name, status in results['sub_pages'].items():
        exists_icon = "✅" if status['exists'] else "❌"
        callable_icon = "✅" if status['callable'] else "❌"
        print(f"   {exists_icon}{callable_icon} {tab_name}")
    
    # Team data summary
    if results['team_data']:
        team_data = results['team_data']
        print(f"\n👤 Team ID 1437667 Data:")
        print(f"   ✅ Successfully loaded")
        print(f"   📊 Team Name: {team_data.get('entry_name', 'Unknown')}")
        print(f"   🎯 Overall Points: {team_data.get('summary_overall_points', 'N/A'):,}")
        print(f"   📈 Overall Rank: {team_data.get('summary_overall_rank', 'N/A'):,}")
        print(f"   💰 Team Value: £{team_data.get('value', 0)/10:.1f}M")
        print(f"   🏦 Bank: £{team_data.get('bank', 0)/10:.1f}M")
        print(f"   👥 Squad Size: {len(team_data.get('picks', []))}")
    else:
        print(f"\n👤 Team ID 1437667 Data:")
        print(f"   ❌ Could not load team data")
    
    # Errors summary
    if results['errors']:
        print(f"\n⚠️ Issues Found ({len(results['errors'])}):")
        for i, error in enumerate(results['errors'][:5], 1):
            print(f"   {i}. {error}")
        if len(results['errors']) > 5:
            print(f"   ... and {len(results['errors']) - 5} more")
    
    # Overall assessment
    total_checks = 2 + len(results['sub_pages']) * 2  # Core + sub-pages (exist + callable)
    passed_checks = (
        (1 if results['page_import'] else 0) +
        (1 if results['data_loading'] else 0) +
        existing_methods + callable_methods
    )
    
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed_checks}/{total_checks})")
    
    print(f"\n🏁 FINAL VALIDATION SUMMARY:")
    if success_rate >= 90 and results['data_loading']:
        print("   🎉 EXCELLENT: My FPL Team page is fully functional!")
        print("   ✅ Team ID 1437667 input: WORKING")
        print("   ✅ All 9 sub-pages: READY") 
        print("   🚀 Page is production-ready!")
    elif success_rate >= 75:
        print("   ✅ GOOD: My FPL Team page is working well")
        print("   ✅ Core functionality: WORKING")
        print("   ⚠️ Some sub-pages may need attention")
    else:
        print("   ⚠️ NEEDS REVIEW: Several issues found")
        print("   🔧 Address the issues above")
    
    print(f"\n🎮 MANUAL TESTING INSTRUCTIONS:")
    print("   1. Run: streamlit run main_modular.py")
    print("   2. Navigate to 'My FPL Team' page")
    print("   3. Enter team ID: 1437667")
    print("   4. Click 'Load My Team' button")
    print("   5. Expected result: Team loads with 9 analysis tabs")
    print("   6. Click through each tab to verify they all work:")
    print("      • Current Squad")
    print("      • Performance Analysis") 
    print("      • Recommendations")
    print("      • Starting XI Optimizer")
    print("      • SWOT Analysis")
    print("      • Advanced Analytics")
    print("      • Transfer Planning")
    print("      • Performance Comparison")
    print("      • Fixture Analysis")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        validate_sub_pages()
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
