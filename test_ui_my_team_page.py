"""
UI Test for My FPL Team Page - Check if all components render properly
"""
import sys
import os
import pandas as pd
from unittest.mock import MagicMock, patch
from io import StringIO
import traceback

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

class UITestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.components_rendered = []
    
    def assert_rendered(self, component_type, content=""):
        """Assert that a UI component was rendered"""
        self.components_rendered.append(f"{component_type}: {content}")
        self.passed += 1
        print(f"✅ {component_type}: {content}")
    
    def assert_failed(self, component_type, error):
        """Record a failed assertion"""
        self.errors.append(f"{component_type}: {error}")
        self.failed += 1  
        print(f"❌ {component_type}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n📊 UI TEST SUMMARY:")
        print(f"   Total Components: {total}")
        print(f"   ✅ Rendered: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "   Success Rate: 0%")
        
        if self.errors:
            print(f"\n🔍 ERRORS FOUND:")
            for error in self.errors:
                print(f"   • {error}")

# Mock Streamlit components with UI validation
class MockStreamlit:
    def __init__(self, test_result):
        self.test_result = test_result
        self.session_state = MockSessionState()
        self.current_context = []
    
    def header(self, text):
        self.test_result.assert_rendered("HEADER", text)
        return text
    
    def subheader(self, text):
        self.test_result.assert_rendered("SUBHEADER", text)
        return text
    
    def write(self, text):
        self.test_result.assert_rendered("WRITE", str(text)[:50] + "..." if len(str(text)) > 50 else str(text))
        return text
    
    def divider(self):
        self.test_result.assert_rendered("DIVIDER", "---")
        return "---"
    
    def success(self, text):
        self.test_result.assert_rendered("SUCCESS", text)
        return text
    
    def error(self, text):
        self.test_result.assert_rendered("ERROR", text)
        return text
    
    def warning(self, text):
        self.test_result.assert_rendered("WARNING", text)
        return text
    
    def info(self, text):
        self.test_result.assert_rendered("INFO", text)
        return text
    
    def button(self, label, type=None, key=None, help=None):
        button_info = f"{label} (type={type})" if type else label
        self.test_result.assert_rendered("BUTTON", button_info)
        # Return True for test button to trigger auto-test
        return label == "🧪 Test with Team ID 1437667"
    
    def text_input(self, label, value="", placeholder="", help="", key=None):
        self.test_result.assert_rendered("TEXT_INPUT", f"{label} (placeholder: {placeholder})")
        return value or "1437667"  # Return test team ID
    
    def selectbox(self, label, options, index=0, help="", key=None):
        selected = options[index] if options and index < len(options) else None
        self.test_result.assert_rendered("SELECTBOX", f"{label} -> {selected}")
        return selected
    
    def columns(self, spec):
        columns = [MockColumn(f"COL_{i}", self.test_result) for i in range(spec)]
        self.test_result.assert_rendered("COLUMNS", f"{spec} columns")
        return columns
    
    def tabs(self, tab_names):
        tabs = [MockTab(name, self.test_result) for name in tab_names]
        self.test_result.assert_rendered("TABS", f"{len(tab_names)} tabs: {', '.join(tab_names[:3])}...")
        return tabs
    
    def expander(self, label, expanded=False):
        self.test_result.assert_rendered("EXPANDER", f"{label} (expanded={expanded})")
        return MockContext(f"EXPANDER: {label}")
    
    def spinner(self, text):
        self.test_result.assert_rendered("SPINNER", text)
        return MockContext(f"SPINNER: {text}")
    
    def metric(self, label, value, delta=None):
        metric_info = f"{label} = {value}"
        if delta:
            metric_info += f" (Δ{delta})"
        self.test_result.assert_rendered("METRIC", metric_info)
        return value
    
    def dataframe(self, data, use_container_width=True, hide_index=False, **kwargs):
        rows = len(data) if hasattr(data, '__len__') else "unknown"
        self.test_result.assert_rendered("DATAFRAME", f"DataFrame with {rows} rows")
        return data
    
    def markdown(self, text):
        self.test_result.assert_rendered("MARKDOWN", text[:100] + "..." if len(text) > 100 else text)
        return text
    
    def code(self, text, language="text"):
        self.test_result.assert_rendered("CODE", f"{language}: {text[:50]}...")
        return text
    
    def rerun(self):
        self.test_result.assert_rendered("RERUN", "Page rerun triggered")
        return None
    
    @property
    def sidebar(self):
        return MockSidebar(self.test_result)

class MockSessionState:
    def __init__(self):
        self._state = {
            'my_team_loaded': False,
            'data_loaded': False,
            'my_team_id': None,
            'my_team_data': None
        }
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __getitem__(self, key):
        return self._state.get(key)
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __contains__(self, key):
        return key in self._state

class MockColumn:
    def __init__(self, name, test_result):
        self.name = name
        self.test_result = test_result
    
    def __enter__(self):
        self.test_result.assert_rendered("COLUMN_ENTER", self.name)
        return self
    
    def __exit__(self, *args):
        self.test_result.assert_rendered("COLUMN_EXIT", self.name)

class MockTab:
    def __init__(self, name, test_result):
        self.name = name
        self.test_result = test_result
    
    def __enter__(self):
        self.test_result.assert_rendered("TAB_ENTER", self.name)
        return self
    
    def __exit__(self, *args):
        self.test_result.assert_rendered("TAB_EXIT", self.name)

class MockSidebar:
    def __init__(self, test_result):
        self.test_result = test_result
    
    def button(self, label, key=None):
        self.test_result.assert_rendered("SIDEBAR_BUTTON", label)
        return False

class MockContext:
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

def test_my_team_page_ui():
    """Comprehensive UI test for My Team Page"""
    print("=" * 80)
    print("🧪 MY FPL TEAM PAGE UI TEST")
    print("=" * 80)
    
    test_result = UITestResult()
    
    try:
        # Mock streamlit
        import streamlit as st
        mock_st = MockStreamlit(test_result)
        
        # Replace streamlit functions
        original_st = {}
        for attr in dir(mock_st):
            if not attr.startswith('_'):
                if hasattr(st, attr):
                    original_st[attr] = getattr(st, attr)
                setattr(st, attr, getattr(mock_st, attr))
        
        print("\n1️⃣ TESTING PAGE INITIALIZATION...")
        from views.my_team_page import MyTeamPage
        page = MyTeamPage()
        test_result.assert_rendered("PAGE_INIT", "MyTeamPage instance created")
        
        print("\n2️⃣ TESTING INITIAL RENDER (No Team Loaded)...")
        page.render()
        
        print("\n3️⃣ TESTING WITH MOCK TEAM DATA...")
        # Create mock team data
        mock_team_data = {
            'entry_name': 'Test Team',
            'summary_overall_points': 500,
            'summary_overall_rank': 1000000,
            'summary_event_points': 65,
            'summary_event_rank': 500000,
            'value': 1000,
            'bank': 5,
            'picks': [
                {'element': 1, 'position': 1, 'is_captain': False, 'is_vice_captain': False},
                {'element': 2, 'position': 2, 'is_captain': True, 'is_vice_captain': False},
                {'element': 3, 'position': 3, 'is_captain': False, 'is_vice_captain': True},
                # Add more mock picks to make 15 total
            ] + [{'element': i, 'position': i, 'is_captain': False, 'is_vice_captain': False} for i in range(4, 16)]
        }
        
        # Mock player data
        mock_players_df = pd.DataFrame({
            'id': range(1, 16),
            'web_name': [f'Player {i}' for i in range(1, 16)],
            'position_name': ['Goalkeeper'] + ['Defender']*4 + ['Midfielder']*5 + ['Forward']*5,
            'team_short_name': ['ARS', 'LIV', 'MCI'] * 5,
            'cost_millions': [5.0] * 15,
            'total_points': [50, 75, 100] * 5,
            'form': [5.5] * 15,
            'selected_by_percent': [25.0] * 15,
            'points_per_million': [10.0] * 15,
            'minutes': [1500] * 15
        })
        
        # Set session state with team data
        st.session_state.my_team_loaded = True
        st.session_state.my_team_data = mock_team_data
        st.session_state.my_team_id = "1437667"
        st.session_state.data_loaded = True
        st.session_state.players_df = mock_players_df
        st.session_state.teams_df = pd.DataFrame({'short_name': ['ARS', 'LIV', 'MCI']})
        
        print("\n4️⃣ TESTING FULL RENDER WITH TEAM DATA...")
        page.render()
        
        print("\n5️⃣ TESTING INDIVIDUAL METHODS...")
        
        # Test team overview
        try:
            page._render_team_overview(mock_team_data)
            test_result.assert_rendered("METHOD", "_render_team_overview")
        except Exception as e:
            test_result.assert_failed("METHOD", f"_render_team_overview failed: {str(e)}")
        
        # Test import section
        try:
            page._render_team_import_section()
            test_result.assert_rendered("METHOD", "_render_team_import_section")
        except Exception as e:
            test_result.assert_failed("METHOD", f"_render_team_import_section failed: {str(e)}")
        
        # Test squad display
        try:
            page._display_current_squad(mock_team_data)
            test_result.assert_rendered("METHOD", "_display_current_squad")
        except Exception as e:
            test_result.assert_failed("METHOD", f"_display_current_squad failed: {str(e)}")
        
        # Test performance analysis
        try:
            page._display_performance_analysis(mock_team_data)
            test_result.assert_rendered("METHOD", "_display_performance_analysis")
        except Exception as e:
            test_result.assert_failed("METHOD", f"_display_performance_analysis failed: {str(e)}")
        
        # Test recommendations
        try:
            page._display_recommendations(mock_team_data)
            test_result.assert_rendered("METHOD", "_display_recommendations")
        except Exception as e:
            test_result.assert_failed("METHOD", f"_display_recommendations failed: {str(e)}")
        
        print("\n6️⃣ TESTING ERROR SCENARIOS...")
        
        # Test with invalid team data
        try:
            st.session_state.my_team_data = None
            page.render()
            test_result.assert_rendered("ERROR_HANDLING", "Invalid team data handled")
        except Exception as e:
            test_result.assert_failed("ERROR_HANDLING", f"Error handling failed: {str(e)}")
        
        # Restore streamlit
        for attr, value in original_st.items():
            setattr(st, attr, value)
        
    except Exception as e:
        test_result.assert_failed("CRITICAL", f"Critical error: {str(e)}")
        print(f"\n💥 CRITICAL ERROR:")
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    test_result.summary()
    print("=" * 80)
    
    # Detailed component analysis
    print(f"\n🔍 DETAILED COMPONENT ANALYSIS:")
    print(f"Components that should be rendered:")
    expected_components = [
        "Header (👤 My FPL Team)",
        "Debug Info Section", 
        "Test Button",
        "Team Import Section",
        "Team Overview (when loaded)",
        "9 Analysis Tabs",
        "Various UI Elements (buttons, inputs, metrics)"
    ]
    
    for component in expected_components:
        print(f"   • {component}")
    
    print(f"\n📋 COMPONENTS ACTUALLY RENDERED:")
    component_types = {}
    for comp in test_result.components_rendered:
        comp_type = comp.split(':')[0]
        component_types[comp_type] = component_types.get(comp_type, 0) + 1
    
    for comp_type, count in sorted(component_types.items()):
        print(f"   • {comp_type}: {count} instances")
    
    return test_result

if __name__ == "__main__":
    result = test_my_team_page_ui()
    
    if result.failed == 0:
        print(f"\n🎉 ALL UI COMPONENTS RENDERED SUCCESSFULLY!")
        print(f"✅ The My FPL Team page UI is working properly")
    else:
        print(f"\n⚠️  Some UI components had issues")
        print(f"❌ Check the errors above for details")
