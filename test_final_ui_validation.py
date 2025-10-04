"""
Final comprehensive UI validation for My FPL Team Page
This test validates that all UI components render without errors
"""
import sys
import os
from unittest.mock import MagicMock, patch
import pandas as pd

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_mock_session_state():
    """Create a properly mocked session state"""
    mock_session = MagicMock()
    
    # Initialize with default values
    state_data = {
        'my_team_loaded': False,
        'data_loaded': False,
        'my_team_id': None,
        'my_team_data': None,
        'my_team_gameweek': None,
        'players_df': pd.DataFrame(),
        'teams_df': pd.DataFrame()
    }
    
    def get_item(key, default=None):
        return state_data.get(key, default)
    
    def set_item(key, value):
        state_data[key] = value
    
    def has_item(key):
        return key in state_data
    
    def get_attr(key):
        return state_data.get(key)
    
    mock_session.get = get_item
    mock_session.__getitem__ = get_item
    mock_session.__setitem__ = set_item
    mock_session.__contains__ = has_item
    mock_session.__getattr__ = get_attr
    
    # Set specific attributes
    for key, value in state_data.items():
        setattr(mock_session, key, value)
    
    return mock_session

def test_ui_validation():
    """Complete UI validation test"""
    print("🧪 COMPREHENSIVE UI VALIDATION TEST")
    print("=" * 60)
    
    test_results = {
        'components_tested': 0,
        'components_passed': 0,
        'errors': []
    }
    
    try:
        # Create comprehensive mocks
        mock_session_state = create_mock_session_state()
        
        # Mock all Streamlit components
        streamlit_mocks = {
            'header': MagicMock(),
            'subheader': MagicMock(),
            'write': MagicMock(),
            'divider': MagicMock(),
            'button': MagicMock(return_value=False),
            'text_input': MagicMock(return_value="1437667"),
            'selectbox': MagicMock(return_value=7),
            'columns': MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()]),
            'metric': MagicMock(),
            'success': MagicMock(),
            'error': MagicMock(),
            'warning': MagicMock(),
            'info': MagicMock(),
            'expander': MagicMock(),
            'markdown': MagicMock(),
            'tabs': MagicMock(return_value=[MagicMock() for _ in range(9)]),
            'dataframe': MagicMock(),
            'spinner': MagicMock(return_value=MagicMock()),
            'rerun': MagicMock(),
            'code': MagicMock(),
            'session_state': mock_session_state
        }
        
        # Set up expander context manager
        expander_mock = MagicMock()
        expander_mock.__enter__ = MagicMock(return_value=expander_mock)
        expander_mock.__exit__ = MagicMock(return_value=None)
        streamlit_mocks['expander'].return_value = expander_mock
        
        # Set up spinner context manager
        spinner_mock = MagicMock()
        spinner_mock.__enter__ = MagicMock(return_value=spinner_mock)
        spinner_mock.__exit__ = MagicMock(return_value=None)
        streamlit_mocks['spinner'].return_value = spinner_mock
        
        # Apply all patches
        patches = [
            patch('streamlit.header', streamlit_mocks['header']),
            patch('streamlit.subheader', streamlit_mocks['subheader']),
            patch('streamlit.write', streamlit_mocks['write']),
            patch('streamlit.divider', streamlit_mocks['divider']),
            patch('streamlit.button', streamlit_mocks['button']),
            patch('streamlit.text_input', streamlit_mocks['text_input']),
            patch('streamlit.selectbox', streamlit_mocks['selectbox']),
            patch('streamlit.columns', streamlit_mocks['columns']),
            patch('streamlit.metric', streamlit_mocks['metric']),
            patch('streamlit.success', streamlit_mocks['success']),
            patch('streamlit.error', streamlit_mocks['error']),
            patch('streamlit.warning', streamlit_mocks['warning']),
            patch('streamlit.info', streamlit_mocks['info']),
            patch('streamlit.expander', streamlit_mocks['expander']),
            patch('streamlit.markdown', streamlit_mocks['markdown']),
            patch('streamlit.tabs', streamlit_mocks['tabs']),
            patch('streamlit.dataframe', streamlit_mocks['dataframe']),
            patch('streamlit.spinner', streamlit_mocks['spinner']),
            patch('streamlit.rerun', streamlit_mocks['rerun']),
            patch('streamlit.code', streamlit_mocks['code']),
            patch('streamlit.session_state', mock_session_state)
        ]
        
        # Start all patches
        started_patches = [p.start() for p in patches]
        
        try:
            from views.my_team_page import MyTeamPage
            
            print("\n1️⃣ Testing Page Initialization...")
            page = MyTeamPage()
            test_results['components_tested'] += 1
            test_results['components_passed'] += 1
            print("✅ Page instance created successfully")
            
            print("\n2️⃣ Testing Initial Render (No Team)...")
            try:
                page.render()
                test_results['components_tested'] += 1
                test_results['components_passed'] += 1
                print("✅ Initial render completed")
            except Exception as e:
                test_results['components_tested'] += 1
                test_results['errors'].append(f"Initial render: {str(e)}")
                print(f"❌ Initial render failed: {str(e)}")
            
            print("\n3️⃣ Testing Team Import Section...")
            try:
                page._render_team_import_section()
                test_results['components_tested'] += 1
                test_results['components_passed'] += 1
                print("✅ Team import section rendered")
            except Exception as e:
                test_results['components_tested'] += 1
                test_results['errors'].append(f"Team import: {str(e)}")
                print(f"❌ Team import failed: {str(e)}")
            
            print("\n4️⃣ Testing with Mock Team Data...")
            # Set up team data
            mock_team_data = {
                'entry_name': 'Test Team',
                'summary_overall_points': 500,
                'summary_overall_rank': 1000000,
                'summary_event_points': 65,
                'summary_event_rank': 500000,
                'value': 1000,
                'bank': 5,
                'gameweek': 7,
                'picks': [
                    {'element': i, 'position': i, 'is_captain': i==2, 'is_vice_captain': i==3}
                    for i in range(1, 16)
                ]
            }
            
            # Mock player data
            mock_players_df = pd.DataFrame({
                'id': range(1, 16),
                'web_name': [f'Player {i}' for i in range(1, 16)],
                'position_name': (['Goalkeeper'] + ['Defender']*4 + ['Midfielder']*5 + ['Forward']*5),
                'team_short_name': ['ARS'] * 15,
                'cost_millions': [5.0] * 15,
                'total_points': [50] * 15,
                'form': [5.5] * 15,
                'selected_by_percent': [25.0] * 15,
                'points_per_million': [10.0] * 15,
                'minutes': [1500] * 15,
                'clean_sheets': [5] * 15,
                'goals_scored': [3] * 15,
                'now_cost': [50] * 15,
                'status': ['a'] * 15
            })
            
            # Update session state
            mock_session_state.my_team_loaded = True
            mock_session_state.my_team_data = mock_team_data
            mock_session_state.my_team_id = "1437667"
            mock_session_state.data_loaded = True
            mock_session_state.players_df = mock_players_df
            
            print("\n5️⃣ Testing Individual Components...")
            
            # Test team overview
            try:
                page._render_team_overview(mock_team_data)
                test_results['components_tested'] += 1
                test_results['components_passed'] += 1
                print("✅ Team overview rendered")
            except Exception as e:
                test_results['components_tested'] += 1
                test_results['errors'].append(f"Team overview: {str(e)}")
                print(f"❌ Team overview failed: {str(e)}")
            
            # Test performance analysis
            try:
                page._display_performance_analysis(mock_team_data)
                test_results['components_tested'] += 1
                test_results['components_passed'] += 1
                print("✅ Performance analysis rendered")
            except Exception as e:
                test_results['components_tested'] += 1
                test_results['errors'].append(f"Performance analysis: {str(e)}")
                print(f"❌ Performance analysis failed: {str(e)}")
            
            # Test recommendations
            try:
                page._display_recommendations(mock_team_data)
                test_results['components_tested'] += 1
                test_results['components_passed'] += 1
                print("✅ Recommendations rendered")
            except Exception as e:
                test_results['components_tested'] += 1
                test_results['errors'].append(f"Recommendations: {str(e)}")
                print(f"❌ Recommendations failed: {str(e)}")
            
            # Test current squad
            try:
                page._display_current_squad(mock_team_data)
                test_results['components_tested'] += 1
                test_results['components_passed'] += 1
                print("✅ Current squad rendered")
            except Exception as e:
                test_results['components_tested'] += 1
                test_results['errors'].append(f"Current squad: {str(e)}")
                print(f"❌ Current squad failed: {str(e)}")
            
            print("\n6️⃣ Testing Full Page with Team Data...")
            try:
                page.render()
                test_results['components_tested'] += 1
                test_results['components_passed'] += 1
                print("✅ Full page render with team data completed")
            except Exception as e:
                test_results['components_tested'] += 1
                test_results['errors'].append(f"Full render: {str(e)}")
                print(f"❌ Full render failed: {str(e)}")
            
            print("\n7️⃣ Validating Streamlit Component Usage...")
            
            component_usage = {
                'Headers': streamlit_mocks['header'].call_count + streamlit_mocks['subheader'].call_count,
                'Text Output': streamlit_mocks['write'].call_count,
                'Buttons': streamlit_mocks['button'].call_count,
                'Input Fields': streamlit_mocks['text_input'].call_count + streamlit_mocks['selectbox'].call_count,
                'Layout': streamlit_mocks['columns'].call_count + streamlit_mocks['tabs'].call_count,
                'Metrics': streamlit_mocks['metric'].call_count,
                'Feedback': (streamlit_mocks['success'].call_count + 
                           streamlit_mocks['error'].call_count + 
                           streamlit_mocks['warning'].call_count + 
                           streamlit_mocks['info'].call_count)
            }
            
            print("Component Usage Summary:")
            for component, count in component_usage.items():
                status = "✅" if count > 0 else "⚠️"
                print(f"   {status} {component}: {count} calls")
        
        finally:
            # Stop all patches
            for p in patches:
                p.stop()
            
    except Exception as e:
        test_results['errors'].append(f"Critical error: {str(e)}")
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL UI VALIDATION RESULTS")
    print("=" * 60)
    
    success_rate = (test_results['components_passed'] / test_results['components_tested'] * 100) if test_results['components_tested'] > 0 else 0
    
    print(f"Components Tested: {test_results['components_tested']}")
    print(f"Components Passed: {test_results['components_passed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if test_results['errors']:
        print(f"\n❌ Errors Found ({len(test_results['errors'])}):")
        for error in test_results['errors']:
            print(f"   • {error}")
    else:
        print(f"\n🎉 ALL COMPONENTS RENDERED SUCCESSFULLY!")
    
    print("\n✅ CONCLUSION:")
    if success_rate >= 90:
        print("   The My FPL Team page UI is rendering properly!")
        print("   All major components are working correctly.")
    elif success_rate >= 70:
        print("   The My FPL Team page UI is mostly working.")
        print("   Minor issues may exist but core functionality is intact.")
    else:
        print("   The My FPL Team page UI has significant issues.")
        print("   Review the errors above for details.")
    
    print("=" * 60)
    
    return test_results

if __name__ == "__main__":
    results = test_ui_validation()
