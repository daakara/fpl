"""
Integration Example - How to Use the Refactored Components
This demonstrates how to integrate the performance improvements into the main application
"""
import streamlit as st
from datetime import datetime

# Import refactored components
from core.refactored_app_controller import PerformanceAwareController, CachingStrategy
from services.enhanced_fpl_data_service import get_enhanced_fpl_service
from utils.advanced_cache_manager import get_cache_manager, smart_cache
from utils.enhanced_performance_monitor import get_performance_monitor

# Import existing components
from utils.error_handling import logger
from config.secure_config import get_secure_config


class IntegratedFPLApp(PerformanceAwareController):
    """Integrated FPL App with all performance improvements"""
    
    def __init__(self):
        """Initialize the integrated application"""
        super().__init__()
        
        # Initialize enhanced services
        self.fpl_service = get_enhanced_fpl_service()
        self.cache_manager = get_cache_manager()
        self.config = get_secure_config()
        
        logger.info("Integrated FPL App initialized with performance enhancements")
    
    def setup_streamlit_page(self):
        """Setup Streamlit page with enhanced configuration"""
        st.set_page_config(
            page_title="FPL Analytics Dashboard - Enhanced",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #00ff87, #60efff);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .performance-metrics {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @smart_cache(ttl_seconds=1800)  # 30 minutes
    def load_enhanced_fpl_data(self):
        """Load FPL data using enhanced caching"""
        try:
            logger.info("Loading FPL data with enhanced caching...")
            
            # Use the enhanced service
            players_df, teams_df = self.fpl_service.load_fpl_data()
            
            # Update session state
            st.session_state.players_df = players_df
            st.session_state.teams_df = teams_df
            st.session_state.data_loaded = True
            st.session_state.last_update = datetime.now()
            
            logger.info(f"Successfully loaded {len(players_df)} players, {len(teams_df)} teams")
            return players_df, teams_df
            
        except Exception as e:
            logger.error(f"Failed to load FPL data: {str(e)}")
            st.error("Failed to load FPL data. Please try again.")
            return None, None
    
    def render_performance_dashboard(self):
        """Render performance monitoring dashboard"""
        with st.expander("🔍 Performance Monitor", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("System Performance")
                self.performance_monitor.render_streamlit_dashboard()
            
            with col2:
                st.subheader("Cache Management")
                self.cache_manager.render_streamlit_dashboard()
    
    def render_data_status(self):
        """Render enhanced data status indicators"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.session_state.get('data_loaded', False):
                st.success("🟢 Data Loaded")
                if st.session_state.get('last_update'):
                    last_update = st.session_state.last_update
                    if isinstance(last_update, str):
                        last_update = datetime.fromisoformat(last_update)
                    
                    time_diff = datetime.now() - last_update
                    st.caption(f"Updated {time_diff.seconds // 60}m ago")
            else:
                st.error("🔴 No Data")
        
        with col2:
            cache_stats = self.cache_manager.get_cache_statistics()
            hit_rate = cache_stats.get('hit_rate', 0)
            if hit_rate > 80:
                st.success(f"🚀 Cache: {hit_rate:.1f}%")
            elif hit_rate > 60:
                st.warning(f"⚡ Cache: {hit_rate:.1f}%")
            else:
                st.error(f"🐌 Cache: {hit_rate:.1f}%")
        
        with col3:
            performance_summary = self.get_performance_summary()
            cpu_usage = performance_summary['system'].get('current_cpu', 0)
            if cpu_usage < 50:
                st.success(f"💻 CPU: {cpu_usage:.1f}%")
            elif cpu_usage < 80:
                st.warning(f"💻 CPU: {cpu_usage:.1f}%")
            else:
                st.error(f"💻 CPU: {cpu_usage:.1f}%")
        
        with col4:
            memory_usage = performance_summary['system'].get('current_memory', 0)
            if memory_usage < 70:
                st.success(f"🧠 RAM: {memory_usage:.1f}%")
            elif memory_usage < 85:
                st.warning(f"🧠 RAM: {memory_usage:.1f}%")
            else:
                st.error(f"🧠 RAM: {memory_usage:.1f}%")
    
    def run_enhanced_application(self):
        """Run the enhanced application with all improvements"""
        try:
            # Setup page
            self.setup_streamlit_page()
            
            # Main header
            st.markdown('<div class="main-header">', unsafe_allow_html=True)
            st.title("⚽ FPL Analytics Dashboard - Enhanced")
            st.markdown("*Powered by advanced caching and performance monitoring*")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Status indicators
            self.render_data_status()
            
            # Main content area
            if not st.session_state.get('data_loaded', False):
                if st.button("🔄 Load FPL Data", type="primary"):
                    with st.spinner("Loading enhanced FPL data..."):
                        self.load_enhanced_fpl_data()
                        st.rerun()
            else:
                # Render navigation using optimized method
                self.render_navigation_optimized()
                
                # Get current page
                current_page = st.session_state.get('nav_selection', 'dashboard')
                
                # Render page content
                if current_page in self.page_registry:
                    page_instance = self.page_registry[current_page]()
                    if hasattr(page_instance, 'render'):
                        page_instance.render()
                    else:
                        st.info(f"Page {current_page} is being developed...")
                
                # Performance dashboard
                self.render_performance_dashboard()
            
            # Footer with system info
            with st.container():
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if hasattr(st.session_state, 'data_metadata'):
                        metadata = st.session_state.data_metadata
                        st.caption(f"Players: {metadata.get('players_count', 0)}")
                
                with col2:
                    performance_summary = self.get_performance_summary()
                    session_time = performance_summary['session'].get('session_start', 0)
                    if session_time:
                        uptime = (datetime.now().timestamp() - session_time) / 60
                        st.caption(f"Session: {uptime:.1f}m")
                
                with col3:
                    st.caption("Enhanced FPL Analytics v2.0")
            
        except Exception as e:
            logger.error(f"Application error: {str(e)}", exc_info=True)
            st.error(f"Application error: {str(e)}")


def main_enhanced():
    """Enhanced main function with all improvements"""
    try:
        # Initialize the integrated app
        if 'enhanced_app' not in st.session_state:
            with st.spinner("Initializing enhanced application..."):
                st.session_state.enhanced_app = IntegratedFPLApp()
        
        # Run the application
        st.session_state.enhanced_app.run_enhanced_application()
        
    except Exception as e:
        logger.error(f"Failed to initialize enhanced app: {str(e)}", exc_info=True)
        st.error("Failed to initialize application. Please refresh the page.")


if __name__ == "__main__":
    main_enhanced()
