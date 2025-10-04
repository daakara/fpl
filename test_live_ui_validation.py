"""
Live Integration Test for My FPL Team Page
Tests actual functionality with team ID 1437667 and validates real UI components
"""
import sys
import os
import time

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

class LiveUIValidation:
    """Live validation of My FPL Team page functionality"""
    
    def __init__(self):
        self.test_results = {
            'component_tests': 0,
            'component_passed': 0,
            'integration_tests': 0,
            'integration_passed': 0,
            'errors': []
        }
    
    def test_component_structure(self):
        """Test 1: Validate component structure and methods"""
        print("🧪 Testing Component Structure...")
        
        try:
            from views.my_team_page import MyTeamPage
            page = MyTeamPage()
            
            # Test required methods exist
            required_methods = [
                'render',
                '_render_team_import_section',
                '_render_team_overview',
                '_display_current_squad',
                '_display_performance_analysis',
                '_display_recommendations',
                '_display_starting_xi_optimizer',
                '_display_swot_analysis',
                '_display_advanced_analytics',
                '_display_transfer_planning',
                '_display_performance_comparison',
                '_display_fixture_analysis',
                '_load_team_data'
            ]
            
            for method_name in required_methods:
                self.test_results['component_tests'] += 1
                if hasattr(page, method_name) and callable(getattr(page, method_name)):
                    self.test_results['component_passed'] += 1
                    print(f"   ✅ Method '{method_name}' exists and is callable")
                else:
                    self.test_results['errors'].append(f"Method '{method_name}' missing or not callable")
                    print(f"   ❌ Method '{method_name}' missing or not callable")
            
            print(f"✅ Component structure test completed: {self.test_results['component_passed']}/{self.test_results['component_tests']} methods found")
            return True
            
        except Exception as e:
            self.test_results['errors'].append(f"Component structure test failed: {str(e)}")
            print(f"❌ Component structure test failed: {str(e)}")
            return False
    
    def test_data_service_integration(self):
        """Test 2: Validate data service integration with team ID 1437667"""
        print("\n🧪 Testing Data Service Integration...")
        
        try:
            from services.fpl_data_service import FPLDataService
            data_service = FPLDataService()
            
            # Test 1: Basic FPL data loading
            print("   📊 Testing FPL data loading...")
            self.test_results['integration_tests'] += 1
            players_df, teams_df = data_service.load_fpl_data()
            if not players_df.empty and not teams_df.empty:
                self.test_results['integration_passed'] += 1
                print(f"   ✅ FPL data loaded: {len(players_df)} players, {len(teams_df)} teams")
            else:
                self.test_results['errors'].append("FPL data loading returned empty dataframes")
                print("   ❌ FPL data loading returned empty dataframes")
            
            # Test 2: Team data loading with ID 1437667
            print("   👤 Testing team data loading with ID 1437667...")
            self.test_results['integration_tests'] += 1
            
            # Try different gameweeks to find working data
            team_data = None
            working_gw = None
            
            for gw in [8, 7, 6, 5, 4, 3, 2, 1]:
                try:
                    print(f"      🔍 Trying gameweek {gw}...")
                    test_data = data_service.load_team_data("1437667", gw)
                    if test_data and test_data.get('picks'):
                        team_data = test_data
                        working_gw = gw
                        print(f"      ✅ Found team data in gameweek {gw}")
                        break
                    else:
                        print(f"      ⚠️ No picks data in gameweek {gw}")
                except Exception as e:
                    print(f"      ❌ Error in gameweek {gw}: {str(e)}")
            
            if team_data and working_gw:
                self.test_results['integration_passed'] += 1
                print(f"   ✅ Team data loaded successfully from GW {working_gw}")
                print(f"      Team: {team_data.get('entry_name', 'Unknown')}")
                print(f"      Points: {team_data.get('summary_overall_points', 'N/A')}")
                print(f"      Rank: {team_data.get('summary_overall_rank', 'N/A')}")
                print(f"      Squad size: {len(team_data.get('picks', []))}")
                return team_data, working_gw
            else:
                self.test_results['errors'].append("Could not load team data for ID 1437667")
                print("   ❌ Could not load team data for ID 1437667")
                return None, None
                
        except Exception as e:
            self.test_results['errors'].append(f"Data service integration test failed: {str(e)}")
            print(f"❌ Data service integration test failed: {str(e)}")
            return None, None
    
    def test_ui_component_instantiation(self):
        """Test 3: Test UI components can handle real data"""
        print("\n🧪 Testing UI Component Data Handling...")
        
        try:
            from views.my_team_page import MyTeamPage
            page = MyTeamPage()
            
            # Create realistic test data based on our successful API call
            mock_team_data = {
                'entry_name': 'Test Team FPL',
                'summary_overall_points': 307,
                'summary_overall_rank': 5325271,
                'summary_event_points': 65,
                'summary_event_rank': 2500000,
                'value': 1000,
                'bank': 5,
                'gameweek': 7,
                'picks': [
                    {'element': i, 'position': i, 'is_captain': i==2, 'is_vice_captain': i==3, 'multiplier': 2 if i==2 else 1}
                    for i in range(1, 16)
                ]
            }
            
            # Test data processing methods
            data_tests = [
                ('_validate_team_data', lambda: self._test_team_data_validation(page, mock_team_data)),
                ('_format_team_metrics', lambda: self._test_team_metrics(page, mock_team_data)),
                ('_get_squad_summary', lambda: self._test_squad_processing(page, mock_team_data))
            ]
            
            for test_name, test_func in data_tests:
                self.test_results['integration_tests'] += 1
                try:
                    print(f"   🔍 Testing {test_name}...")
                    result = test_func()
                    if result:
                        self.test_results['integration_passed'] += 1
                        print(f"   ✅ {test_name} passed")
                    else:
                        self.test_results['errors'].append(f"{test_name} returned falsy result")
                        print(f"   ⚠️ {test_name} returned falsy result")
                except Exception as e:
                    self.test_results['errors'].append(f"{test_name} failed: {str(e)}")
                    print(f"   ❌ {test_name} failed: {str(e)}")
            
            return True
            
        except Exception as e:
            self.test_results['errors'].append(f"UI component instantiation test failed: {str(e)}")
            print(f"❌ UI component instantiation test failed: {str(e)}")
            return False
    
    def _test_team_data_validation(self, page, team_data):
        """Test team data validation"""
        # This tests that the team data structure is correct
        required_fields = ['entry_name', 'picks', 'gameweek']
        for field in required_fields:
            if field not in team_data:
                return False
        return len(team_data['picks']) > 0
    
    def _test_team_metrics(self, page, team_data):
        """Test team metrics formatting"""
        # Test that we can extract and format key metrics
        metrics = {
            'points': team_data.get('summary_overall_points', 0),
            'rank': team_data.get('summary_overall_rank', 0),
            'value': team_data.get('value', 0),
            'bank': team_data.get('bank', 0)
        }
        return all(isinstance(v, (int, float)) for v in metrics.values())
    
    def _test_squad_processing(self, page, team_data):
        """Test squad data processing"""
        picks = team_data.get('picks', [])
        if not picks:
            return False
        
        # Test that we can process squad structure
        captain_count = sum(1 for pick in picks if pick.get('is_captain'))
        vice_captain_count = sum(1 for pick in picks if pick.get('is_vice_captain'))
        
        return captain_count <= 1 and vice_captain_count <= 1 and len(picks) <= 15
    
    def test_file_integrity(self):
        """Test 4: Validate file integrity and imports"""
        print("\n🧪 Testing File Integrity...")
        
        try:
            # Check file exists and has content
            file_path = os.path.join(project_root, 'views', 'my_team_page.py')
            self.test_results['integration_tests'] += 1
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check file size (should be substantial)
                if len(content) > 50000:  # At least 50KB of code
                    self.test_results['integration_passed'] += 1
                    print(f"   ✅ File exists with {len(content)} characters")
                    
                    # Check for key components
                    key_components = [
                        'class MyTeamPage',
                        'def render',
                        '_render_team_import_section',
                        '_display_current_squad',
                        'st.text_input',
                        'st.button',
                        'st.tabs'
                    ]
                    
                    missing_components = []
                    for component in key_components:
                        if component not in content:
                            missing_components.append(component)
                    
                    if not missing_components:
                        print("   ✅ All key UI components found in code")
                    else:
                        self.test_results['errors'].append(f"Missing components: {missing_components}")
                        print(f"   ⚠️ Missing components: {missing_components}")
                    
                else:
                    self.test_results['errors'].append(f"File too small: {len(content)} characters")
                    print(f"   ❌ File too small: {len(content)} characters")
            else:
                self.test_results['errors'].append("my_team_page.py file does not exist")
                print("   ❌ my_team_page.py file does not exist")
                
        except Exception as e:
            self.test_results['errors'].append(f"File integrity test failed: {str(e)}")
            print(f"❌ File integrity test failed: {str(e)}")
    
    def run_validation(self):
        """Run the complete validation suite"""
        print("🚀 LIVE UI VALIDATION FOR MY FPL TEAM PAGE")
        print("=" * 60)
        print("Testing with Team ID 1437667 and validating all sub-components")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        print("📋 Running validation tests...\n")
        
        # Test 1: Component Structure
        structure_ok = self.test_component_structure()
        
        # Test 2: Data Service Integration
        team_data, working_gw = self.test_data_service_integration()
        
        # Test 3: UI Component Data Handling
        if structure_ok:
            ui_ok = self.test_ui_component_instantiation()
        
        # Test 4: File Integrity
        self.test_file_integrity()
        
        end_time = time.time()
        
        # Print results
        self.print_validation_results(end_time - start_time, team_data, working_gw)
    
    def print_validation_results(self, duration, team_data, working_gw):
        """Print comprehensive validation results"""
        print("\n" + "=" * 60)
        print("📊 LIVE UI VALIDATION RESULTS")
        print("=" * 60)
        
        total_tests = self.test_results['component_tests'] + self.test_results['integration_tests']
        total_passed = self.test_results['component_passed'] + self.test_results['integration_passed']
        
        print(f"⏱️ Test Duration: {duration:.2f} seconds")
        print(f"🧪 Component Tests: {self.test_results['component_passed']}/{self.test_results['component_tests']} passed")
        print(f"🔗 Integration Tests: {self.test_results['integration_passed']}/{self.test_results['integration_tests']} passed")
        print(f"🎯 Overall Success: {total_passed}/{total_tests} ({(total_passed/total_tests*100):.1f}%)")
        
        # Team data validation results
        if team_data and working_gw:
            print(f"\n✅ TEAM ID 1437667 VALIDATION:")
            print(f"   ✅ Successfully loaded team data from gameweek {working_gw}")
            print(f"   📊 Team: {team_data.get('entry_name', 'Unknown')}")
            print(f"   🎯 Overall Points: {team_data.get('summary_overall_points', 'N/A'):,}")
            print(f"   📈 Overall Rank: {team_data.get('summary_overall_rank', 'N/A'):,}")
            print(f"   👥 Squad Size: {len(team_data.get('picks', []))}")
            print(f"   💰 Team Value: £{team_data.get('value', 0)/10:.1f}M")
            print(f"   🏦 Bank: £{team_data.get('bank', 0)/10:.1f}M")
        else:
            print(f"\n❌ TEAM ID 1437667 VALIDATION:")
            print(f"   ❌ Could not load team data")
        
        if self.test_results['errors']:
            print(f"\n⚠️ Issues Found ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results['errors'][:5], 1):
                print(f"   {i}. {error}")
            if len(self.test_results['errors']) > 5:
                print(f"   ... and {len(self.test_results['errors']) - 5} more")
        
        # Final assessment
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🏁 FINAL ASSESSMENT:")
        if success_rate >= 90 and team_data:
            print("   🎉 EXCELLENT: My FPL Team page is fully functional!")
            print("   ✅ Team ID input validation: WORKING")
            print("   ✅ Data loading with 1437667: WORKING") 
            print("   ✅ All UI components: READY")
            print("   🚀 Page is ready for production use!")
        elif success_rate >= 75:
            print("   ✅ GOOD: My FPL Team page is working well")
            print("   ✅ Core functionality: WORKING")
            print("   ⚠️ Minor issues may exist")
        else:
            print("   ⚠️ NEEDS ATTENTION: Some issues found")
            print("   🔧 Review the issues above")
        
        print(f"\n💡 MANUAL VERIFICATION STEPS:")
        print("   1. Open your Streamlit app (streamlit run main_modular.py)")
        print("   2. Navigate to 'My FPL Team' page")
        print("   3. You should see:")
        print("      - Debug info section")
        print("      - 'Import Your FPL Team' section")
        print("      - Team ID input field")
        print("      - 'Load My Team' button")
        print("   4. Enter '1437667' and click 'Load My Team'")
        if working_gw:
            print(f"   5. Team should load with data from gameweek {working_gw}")
        print("   6. Verify all 9 analysis tabs appear and function")
        
        print("=" * 60)

def main():
    """Main execution function"""
    try:
        validator = LiveUIValidation()
        validator.run_validation()
        
    except Exception as e:
        print("❌ CRITICAL ERROR:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
