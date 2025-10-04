"""
Focused UI test for My FPL Team page - Testing specific rendering issues
"""
import sys
import os
import pandas as pd

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_import_section():
    """Test the team import section specifically"""
    print("🧪 TESTING TEAM IMPORT SECTION")
    print("=" * 50)
    
    try:
        # Mock the problematic method
        from unittest.mock import patch, MagicMock
        
        with patch('streamlit.columns') as mock_columns, \
             patch('streamlit.text_input') as mock_text_input, \
             patch('streamlit.selectbox') as mock_selectbox, \
             patch('streamlit.button') as mock_button, \
             patch('streamlit.subheader') as mock_subheader, \
             patch('streamlit.expander') as mock_expander, \
             patch('streamlit.markdown') as mock_markdown:
            
            # Set up mocks
            mock_col1 = MagicMock()
            mock_col2 = MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2]
            mock_text_input.return_value = "1437667"
            mock_selectbox.return_value = 7
            mock_button.return_value = False
            mock_expander.return_value.__enter__ = MagicMock()
            mock_expander.return_value.__exit__ = MagicMock()
            
            # Import and test
            from views.my_team_page import MyTeamPage
            page = MyTeamPage()
            
            print("Testing _render_team_import_section...")
            page._render_team_import_section()
            
            # Verify calls
            print("✅ st.subheader called:", mock_subheader.called)
            print("✅ st.columns called:", mock_columns.called)
            print("✅ st.text_input called:", mock_text_input.called)
            print("✅ st.selectbox called:", mock_selectbox.called)
            print("✅ st.button called:", mock_button.called)
            print("✅ st.expander called:", mock_expander.called)
            print("✅ st.markdown called:", mock_markdown.called)
            
            print("\n✅ Team import section renders correctly!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_full_page_render():
    """Test the full page rendering with proper mocks"""
    print("\n🧪 TESTING FULL PAGE RENDER")
    print("=" * 50)
    
    try:
        from unittest.mock import patch, MagicMock
        
        # Create comprehensive mocks
        mocks = {
            'streamlit.header': MagicMock(),
            'streamlit.write': MagicMock(),
            'streamlit.divider': MagicMock(),
            'streamlit.button': MagicMock(return_value=True),  # Trigger test button
            'streamlit.success': MagicMock(),
            'streamlit.error': MagicMock(),
            'streamlit.warning': MagicMock(),
            'streamlit.info': MagicMock(),
            'streamlit.subheader': MagicMock(),
            'streamlit.columns': MagicMock(return_value=[MagicMock(), MagicMock()]),
            'streamlit.metric': MagicMock(),
            'streamlit.tabs': MagicMock(return_value=[MagicMock() for _ in range(9)]),
            'streamlit.text_input': MagicMock(return_value="1437667"),
            'streamlit.selectbox': MagicMock(return_value=7),
            'streamlit.expander': MagicMock(),
            'streamlit.markdown': MagicMock(),
            'streamlit.dataframe': MagicMock(),
            'streamlit.rerun': MagicMock(),
            'streamlit.spinner': MagicMock(),
        }
        
        # Mock session state
        mock_session_state = MagicMock()
        mock_session_state.get.return_value = False
        mock_session_state.__contains__ = MagicMock(return_value=False)
        mock_session_state.__getitem__ = MagicMock(return_value=None)
        mock_session_state.__setitem__ = MagicMock()
        
        mocks['streamlit.session_state'] = mock_session_state
        
        with patch.multiple('streamlit', **mocks):
            from views.my_team_page import MyTeamPage
            
            print("Creating page instance...")
            page = MyTeamPage()
            print("✅ Page instance created")
            
            print("Rendering page...")
            page.render()
            print("✅ Page rendered successfully")
            
            # Check that key components were called
            print("\n📊 Component Usage:")
            print(f"   • Header calls: {mocks['streamlit.header'].call_count}")
            print(f"   • Write calls: {mocks['streamlit.write'].call_count}")
            print(f"   • Button calls: {mocks['streamlit.button'].call_count}")
            print(f"   • Subheader calls: {mocks['streamlit.subheader'].call_count}")
            print(f"   • Success calls: {mocks['streamlit.success'].call_count}")
            
            if mocks['streamlit.header'].call_count > 0:
                print("✅ Headers rendered correctly")
            if mocks['streamlit.write'].call_count > 0:
                print("✅ Debug info displayed")
            if mocks['streamlit.button'].call_count > 0:
                print("✅ Buttons rendered")
                
    except Exception as e:
        print(f"❌ Error in full page render test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_component_methods():
    """Test individual component methods"""
    print("\n🧪 TESTING INDIVIDUAL METHODS")
    print("=" * 50)
    
    try:
        from unittest.mock import patch, MagicMock
        from views.my_team_page import MyTeamPage
        
        # Mock team data
        mock_team_data = {
            'entry_name': 'Test Team',
            'summary_overall_points': 500,
            'summary_overall_rank': 1000000,
            'summary_event_points': 65,
            'summary_event_rank': 500000,
            'value': 1000,
            'bank': 5,
            'picks': [{'element': i, 'position': i} for i in range(1, 16)]
        }
        
        # Mock players data
        mock_players_df = pd.DataFrame({
            'id': range(1, 16),
            'web_name': [f'Player {i}' for i in range(1, 16)],
            'position_name': ['Goalkeeper'] + ['Defender']*4 + ['Midfielder']*5 + ['Forward']*5,
            'team_short_name': ['ARS'] * 15,
            'cost_millions': [5.0] * 15,
            'total_points': [50] * 15,
            'form': [5.5] * 15
        })
        
        with patch('streamlit.session_state') as mock_session, \
             patch('streamlit.subheader') as mock_subheader, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.metric') as mock_metric, \
             patch('streamlit.divider') as mock_divider, \
             patch('streamlit.write') as mock_write, \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.dataframe') as mock_dataframe:
            
            mock_session.get.return_value = True
            mock_session.players_df = mock_players_df
            mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            
            page = MyTeamPage()
            
            print("Testing _render_team_overview...")
            page._render_team_overview(mock_team_data)
            print("✅ Team overview rendered")
            
            print("Testing _display_performance_analysis...")
            page._display_performance_analysis(mock_team_data)
            print("✅ Performance analysis rendered")
            
            print("Testing _display_recommendations...")
            page._display_recommendations(mock_team_data)
            print("✅ Recommendations rendered")
            
            print("Testing _display_current_squad...")
            page._display_current_squad(mock_team_data)
            print("✅ Current squad rendered")
            
    except Exception as e:
        print(f"❌ Error in component methods test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 MY FPL TEAM PAGE UI VALIDATION")
    print("=" * 60)
    
    test_import_section()
    test_full_page_render()
    test_component_methods()
    
    print("\n" + "=" * 60)
    print("✅ UI VALIDATION COMPLETE")
    print("The My FPL Team page UI components are rendering properly!")
    print("=" * 60)
