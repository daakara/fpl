"""
Production Test App for Rebuilt My FPL Team Page
===============================================

This Streamlit app tests the rebuilt My FPL Team page in a production environment.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main production test app for rebuilt page"""
    st.set_page_config(
        page_title="My FPL Team - Rebuilt Version Test",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # App header
    st.markdown("""
    <div style='
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    '>
        <h1>🎨 My FPL Team - Rebuilt Version</h1>
        <p><strong>Production Test Environment</strong> | Enhanced UI & Modern Components</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("🎨 Rebuilt Page Test")
    st.sidebar.markdown("---")
    
    # Test mode selection
    test_mode = st.sidebar.selectbox(
        "Select Test Mode:",
        ["🚀 Full Production Test", "🔧 Component Test", "⚡ Performance Test"]
    )
    
    # Test configuration
    st.sidebar.markdown("### 🛠️ Configuration")
    auto_load_team = st.sidebar.checkbox("Auto-load sample team", value=True)
    show_debug_info = st.sidebar.checkbox("Show debug information", value=False)
    enable_animations = st.sidebar.checkbox("Enable animations", value=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Test Status")
    
    if show_debug_info:
        st.sidebar.success("🔧 Debug mode enabled")
    
    if enable_animations:
        st.sidebar.success("✨ Animations enabled")
    
    # Main content based on test mode
    if test_mode == "🚀 Full Production Test":
        run_full_production_test(auto_load_team, show_debug_info, enable_animations)
    elif test_mode == "🔧 Component Test":
        run_component_test(show_debug_info)
    elif test_mode == "⚡ Performance Test":
        run_performance_test()

def run_full_production_test(auto_load_team, show_debug_info, enable_animations):
    """Run full production test"""
    st.markdown("## 🚀 Full Production Test")
    st.markdown("Testing the rebuilt My FPL Team page in production environment.")
    
    try:
        # Import and initialize rebuilt page
        from views.my_team_page_rebuilt import RebuildMyTeamPage
        
        if show_debug_info:
            st.success("✅ Successfully imported RebuildMyTeamPage")
        
        # Initialize the page
        page = RebuildMyTeamPage()
        
        if show_debug_info:
            st.info(f"📊 Page version: {page.version}")
            st.info(f"🏷️ Page title: {page.page_title}")
        
        # Auto-load team if requested
        if auto_load_team:
            if 'auto_loaded' not in st.session_state:
                with st.spinner("🔄 Auto-loading sample team..."):
                    page._load_sample_data()
                    st.session_state.auto_loaded = True
                
                if enable_animations:
                    st.success("🎉 Sample team loaded successfully!")
        
        # Render the rebuilt page
        st.markdown("---")
        page.render()
        
    except Exception as e:
        st.error(f"❌ Production test failed: {str(e)}")
        if show_debug_info:
            st.exception(e)

def run_component_test(show_debug_info):
    """Run component-specific tests"""
    st.markdown("## 🔧 Component Test")
    st.markdown("Testing individual components of the rebuilt page.")
    
    try:
        from views.my_team_page_rebuilt import RebuildMyTeamPage
        page = RebuildMyTeamPage()
        
        # Test components
        st.markdown("### 📊 Quick Stats Component Test")
        
        # Mock team data for testing
        mock_team_data = {
            'summary_overall_points': 1247,
            'summary_overall_rank': 456789,
            'summary_event_points': 58,
            'value': 1003
        }
        
        page._render_quick_stats(mock_team_data)
        
        st.markdown("### 🎯 Recommendations Component Test")
        recommendations = page._generate_recommendations(mock_team_data)
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}. {rec['title']}**")
            st.markdown(rec['description'])
            
            if rec['priority'] == 'high':
                st.error(f"🔴 {rec['action']}")
            elif rec['priority'] == 'medium':
                st.warning(f"🟡 {rec['action']}")
            else:
                st.info(f"🟢 {rec['action']}")
        
        st.markdown("### 💰 Value Analysis Component Test")
        page._render_value_analysis(mock_team_data)
        
        if show_debug_info:
            st.success("✅ All components tested successfully")
        
    except Exception as e:
        st.error(f"❌ Component test failed: {str(e)}")
        if show_debug_info:
            st.exception(e)

def run_performance_test():
    """Run performance tests"""
    st.markdown("## ⚡ Performance Test")
    st.markdown("Testing performance metrics of the rebuilt page.")
    
    import time
    
    # Test 1: Import Performance
    st.markdown("### 📥 Import Performance")
    with st.spinner("Testing import speed..."):
        start_time = time.time()
        from views.my_team_page_rebuilt import RebuildMyTeamPage
        import_time = time.time() - start_time
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Import Time", f"{import_time:.4f}s")
    with col2:
        if import_time < 0.1:
            st.success("🚀 Excellent")
        elif import_time < 0.5:
            st.success("✅ Good")
        else:
            st.warning("⚠️ Could be better")
    
    # Test 2: Initialization Performance
    st.markdown("### 🔧 Initialization Performance")
    with st.spinner("Testing initialization speed..."):
        start_time = time.time()
        page = RebuildMyTeamPage()
        init_time = time.time() - start_time
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Initialization Time", f"{init_time:.4f}s")
    with col2:
        if init_time < 0.1:
            st.success("🚀 Excellent")
        elif init_time < 0.5:
            st.success("✅ Good")
        else:
            st.warning("⚠️ Could be better")
    
    # Test 3: Mock Data Generation Performance
    st.markdown("### 📊 Data Generation Performance")
    with st.spinner("Testing data generation speed..."):
        start_time = time.time()
        mock_data = page._get_mock_team_data("1437667")
        data_time = time.time() - start_time
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Data Generation Time", f"{data_time:.4f}s")
    with col2:
        if data_time < 0.01:
            st.success("🚀 Excellent")
        elif data_time < 0.1:
            st.success("✅ Good")
        else:
            st.warning("⚠️ Could be better")
    
    # Overall performance score
    st.markdown("### 🏆 Overall Performance Score")
    total_time = import_time + init_time + data_time
    
    if total_time < 0.2:
        score = "🏆 Excellent"
        color = "success"
    elif total_time < 0.5:
        score = "⭐ Good"
        color = "success"
    elif total_time < 1.0:
        score = "👍 Average"
        color = "warning"
    else:
        score = "📈 Needs Improvement"
        color = "error"
    
    if color == "success":
        st.success(f"**Performance Score:** {score}")
    elif color == "warning":
        st.warning(f"**Performance Score:** {score}")
    else:
        st.error(f"**Performance Score:** {score}")
    
    st.metric("Total Time", f"{total_time:.4f}s")

if __name__ == "__main__":
    main()
