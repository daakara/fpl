"""
Interactive Filter System for FPL Dashboard
Implements dynamic data exploration with advanced filters
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import plotly.express as px
import plotly.graph_objects as go

class InteractiveFilterSystem:
    """Advanced filtering system for FPL data exploration"""
    
    def __init__(self):
        self.active_filters = {}
        self.filter_presets = self._create_filter_presets()
    
    def render_filter_controls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Render interactive filter controls and return filtered data"""
        st.markdown("### 🎛️ Interactive Filters & Controls")
        
        # Quick filter presets
        self._render_filter_presets()
        
        # Main filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtered_df = self._render_primary_filters(df)
        
        with col2:
            filtered_df = self._render_performance_filters(filtered_df)
        
        with col3:
            filtered_df = self._render_advanced_filters(filtered_df)
        
        # Filter summary
        self._render_filter_summary(df, filtered_df)
        
        return filtered_df
    
    def _create_filter_presets(self) -> Dict:
        """Create predefined filter combinations"""
        return {
            "Budget Gems": {
                "price_range": (4.0, 7.0),
                "form_threshold": 4.5,
                "ownership_max": 10.0,
                "minutes_min": 200
            },
            "Premium Options": {
                "price_range": (9.0, 15.0),
                "form_threshold": 5.0,
                "ownership_min": 10.0,
                "minutes_min": 500
            },
            "Form Players": {
                "form_threshold": 6.0,
                "minutes_min": 300,
                "recent_points": 25
            },
            "Differential Picks": {
                "ownership_max": 5.0,
                "form_threshold": 4.0,
                "minutes_min": 300,
                "price_range": (4.5, 10.0)
            },
            "Safe Picks": {
                "ownership_min": 15.0,
                "form_threshold": 4.5,
                "minutes_min": 400,
                "consistency_min": 0.7
            }
        }
    
    def _render_filter_presets(self):
        """Render quick filter preset buttons"""
        st.markdown("#### ⚡ Quick Filter Presets")
        
        cols = st.columns(len(self.filter_presets))
        
        for i, (preset_name, preset_filters) in enumerate(self.filter_presets.items()):
            with cols[i]:
                if st.button(f"🎯 {preset_name}", key=f"preset_{preset_name}"):
                    self._apply_filter_preset(preset_filters)
                    st.rerun()
    
    def _render_primary_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Render primary filter controls"""
        st.markdown("#### 🎯 Primary Filters")
        
        # Position filter
        positions = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        position_options = ['All'] + list(positions.values())
        
        selected_position = st.selectbox(
            "Position",
            position_options,
            index=0,
            key="position_filter"
        )
        
        if selected_position != 'All':
            position_id = [k for k, v in positions.items() if v == selected_position][0]
            df = df[df['element_type'] == position_id]
        
        # Price range filter
        if 'now_cost' in df.columns:
            price_min = float(df['now_cost'].min()) / 10
            price_max = float(df['now_cost'].max()) / 10
            
            price_range = st.slider(
                "Price Range (£m)",
                min_value=price_min,
                max_value=price_max,
                value=(price_min, price_max),
                step=0.1,
                key="price_filter"
            )
            
            df = df[
                (df['now_cost'] / 10 >= price_range[0]) & 
                (df['now_cost'] / 10 <= price_range[1])
            ]
        
        # Team filter
        if not df.empty and 'team' in df.columns:
            teams = sorted(df['team'].unique())
            selected_teams = st.multiselect(
                "Teams",
                teams,
                default=teams,
                key="team_filter"
            )
            
            if selected_teams:
                df = df[df['team'].isin(selected_teams)]
        
        return df
    
    def _render_performance_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Render performance-based filters"""
        st.markdown("#### 📈 Performance Filters")
        
        # Form filter
        if 'form' in df.columns and not df.empty:
            form_periods = {"Last 3 games": 3, "Last 5 games": 5, "Last 10 games": 10}
            selected_period = st.selectbox(
                "Form Period",
                list(form_periods.keys()),
                index=1,
                key="form_period_filter"
            )
            
            form_threshold = st.slider(
                "Minimum Form",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.5,
                key="form_threshold_filter"
            )
            
            df = df[df['form'] >= form_threshold]
        
        # Ownership filter
        if 'selected_by_percent' in df.columns and not df.empty:
            ownership_filter_type = st.radio(
                "Ownership Filter",
                ["No Filter", "Low Ownership (<10%)", "Medium Ownership (10-25%)", "High Ownership (>25%)", "Custom Range"],
                index=0,
                key="ownership_type_filter"
            )
            
            if ownership_filter_type == "Low Ownership (<10%)":
                df = df[df['selected_by_percent'] < 10.0]
            elif ownership_filter_type == "Medium Ownership (10-25%)":
                df = df[(df['selected_by_percent'] >= 10.0) & (df['selected_by_percent'] <= 25.0)]
            elif ownership_filter_type == "High Ownership (>25%)":
                df = df[df['selected_by_percent'] > 25.0]
            elif ownership_filter_type == "Custom Range":
                ownership_range = st.slider(
                    "Ownership Range (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=(0.0, 100.0),
                    step=0.5,
                    key="ownership_range_filter"
                )
                df = df[
                    (df['selected_by_percent'] >= ownership_range[0]) & 
                    (df['selected_by_percent'] <= ownership_range[1])
                ]
        
        # Minutes played filter
        if 'minutes' in df.columns and not df.empty:
            minutes_threshold = st.slider(
                "Minimum Minutes Played",
                min_value=0,
                max_value=int(df['minutes'].max()) if df['minutes'].max() > 0 else 1000,
                value=300,
                step=50,
                key="minutes_filter"
            )
            
            df = df[df['minutes'] >= minutes_threshold]
        
        return df
    
    def _render_advanced_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Render advanced filter controls"""
        st.markdown("#### 🔬 Advanced Filters")
        
        # Value filter (points per million)
        if not df.empty and 'total_points' in df.columns and 'now_cost' in df.columns:
            df_temp = df.copy()
            df_temp['points_per_million'] = np.where(
                df_temp['now_cost'] > 0,
                df_temp['total_points'] / (df_temp['now_cost'] / 10),
                0
            )
            
            value_threshold = st.slider(
                "Minimum Value (Pts/£m)",
                min_value=0.0,
                max_value=float(df_temp['points_per_million'].max()) if df_temp['points_per_million'].max() > 0 else 50.0,
                value=15.0,
                step=1.0,
                key="value_filter"
            )
            
            df = df_temp[df_temp['points_per_million'] >= value_threshold]
        
        # Fixture difficulty weighting
        fixture_difficulty = st.selectbox(
            "Fixture Difficulty Focus",
            ["All Fixtures", "Easy Fixtures (1-2)", "Medium Fixtures (3)", "Hard Fixtures (4-5)"],
            index=0,
            key="fixture_difficulty_filter"
        )
        
        # Transfer activity filter
        if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
            transfer_activity = st.selectbox(
                "Transfer Activity",
                ["All Players", "Trending In", "Trending Out", "High Activity", "Low Activity"],
                index=0,
                key="transfer_activity_filter"
            )
            
            if not df.empty:
                df['transfer_balance'] = df['transfers_in_event'] - df['transfers_out_event']
                
                if transfer_activity == "Trending In":
                    df = df[df['transfer_balance'] > df['transfer_balance'].quantile(0.7)]
                elif transfer_activity == "Trending Out":
                    df = df[df['transfer_balance'] < df['transfer_balance'].quantile(0.3)]
                elif transfer_activity == "High Activity":
                    df = df[abs(df['transfer_balance']) > abs(df['transfer_balance']).quantile(0.8)]
                elif transfer_activity == "Low Activity":
                    df = df[abs(df['transfer_balance']) <= abs(df['transfer_balance']).quantile(0.2)]
        
        # Injury status filter
        injury_filter = st.checkbox(
            "Exclude Injured Players",
            value=False,
            key="injury_filter"
        )
        
        if injury_filter and 'status' in df.columns:
            df = df[df['status'] == 'a']  # Available players only
        
        return df
    
    def _apply_filter_preset(self, preset_filters: Dict):
        """Apply a filter preset to session state"""
        for filter_name, filter_value in preset_filters.items():
            if filter_name == "price_range":
                st.session_state["price_filter"] = filter_value
            elif filter_name == "form_threshold":
                st.session_state["form_threshold_filter"] = filter_value
            elif filter_name == "ownership_max":
                st.session_state["ownership_range_filter"] = (0.0, filter_value)
            elif filter_name == "ownership_min":
                st.session_state["ownership_range_filter"] = (filter_value, 100.0)
            elif filter_name == "minutes_min":
                st.session_state["minutes_filter"] = filter_value
    
    def _render_filter_summary(self, original_df: pd.DataFrame, filtered_df: pd.DataFrame):
        """Render filter summary and statistics"""
        st.markdown("---")
        st.markdown("#### 📊 Filter Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Players Shown",
                len(filtered_df),
                delta=len(filtered_df) - len(original_df)
            )
        
        with col2:
            if not filtered_df.empty and 'now_cost' in filtered_df.columns:
                avg_price = filtered_df['now_cost'].mean() / 10
                st.metric("Avg Price", f"£{avg_price:.1f}m")
        
        with col3:
            if not filtered_df.empty and 'total_points' in filtered_df.columns:
                avg_points = filtered_df['total_points'].mean()
                st.metric("Avg Points", f"{avg_points:.1f}")
        
        with col4:
            if not filtered_df.empty and 'selected_by_percent' in filtered_df.columns:
                avg_ownership = filtered_df['selected_by_percent'].mean()
                st.metric("Avg Ownership", f"{avg_ownership:.1f}%")
        
        # Clear filters button
        if st.button("🗑️ Clear All Filters", key="clear_filters"):
            self._clear_all_filters()
            st.rerun()
    
    def _clear_all_filters(self):
        """Clear all active filters"""
        filter_keys = [
            "position_filter", "price_filter", "team_filter", "form_period_filter",
            "form_threshold_filter", "ownership_type_filter", "ownership_range_filter",
            "minutes_filter", "value_filter", "fixture_difficulty_filter",
            "transfer_activity_filter", "injury_filter"
        ]
        
        for key in filter_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    def create_filter_visualization(self, original_df: pd.DataFrame, filtered_df: pd.DataFrame) -> go.Figure:
        """Create visualization showing filter impact"""
        
        # Position distribution comparison
        positions = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        
        original_counts = original_df['element_type'].value_counts().reindex(positions.keys(), fill_value=0)
        filtered_counts = filtered_df['element_type'].value_counts().reindex(positions.keys(), fill_value=0)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[positions[i] for i in positions.keys()],
            y=original_counts.values,
            name='All Players',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        fig.add_trace(go.Bar(
            x=[positions[i] for i in positions.keys()],
            y=filtered_counts.values,
            name='Filtered Players',
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title="📊 Filter Impact: Player Distribution by Position",
            xaxis_title="Position",
            yaxis_title="Number of Players",
            barmode='overlay',
            height=400
        )
        
        return fig
    
    def create_advanced_search(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create natural language search interface"""
        st.markdown("#### 🔍 Smart Search")
        
        search_query = st.text_input(
            "Natural Language Search",
            placeholder="e.g., 'cheap midfielders in good form' or 'defenders under 6m with clean sheets'",
            key="smart_search"
        )
        
        if search_query:
            # Simple keyword-based search (could be enhanced with NLP)
            filtered_df = self._process_natural_language_query(df, search_query)
            return filtered_df
        
        return df
    
    def _process_natural_language_query(self, df: pd.DataFrame, query: str) -> pd.DataFrame:
        """Process natural language search query"""
        query_lower = query.lower()
        filtered_df = df.copy()
        
        # Position keywords
        if 'goalkeeper' in query_lower or 'gkp' in query_lower:
            filtered_df = filtered_df[filtered_df['element_type'] == 1]
        elif 'defender' in query_lower or 'def' in query_lower:
            filtered_df = filtered_df[filtered_df['element_type'] == 2]
        elif 'midfielder' in query_lower or 'mid' in query_lower:
            filtered_df = filtered_df[filtered_df['element_type'] == 3]
        elif 'forward' in query_lower or 'striker' in query_lower or 'fwd' in query_lower:
            filtered_df = filtered_df[filtered_df['element_type'] == 4]
        
        # Price keywords
        if 'cheap' in query_lower or 'budget' in query_lower:
            filtered_df = filtered_df[filtered_df['now_cost'] / 10 <= 6.0]
        elif 'expensive' in query_lower or 'premium' in query_lower:
            filtered_df = filtered_df[filtered_df['now_cost'] / 10 >= 9.0]
        
        # Form keywords
        if 'good form' in query_lower or 'in form' in query_lower:
            filtered_df = filtered_df[filtered_df['form'] >= 5.0]
        elif 'poor form' in query_lower or 'bad form' in query_lower:
            filtered_df = filtered_df[filtered_df['form'] <= 3.0]
        
        # Performance keywords
        if 'high scoring' in query_lower or 'top scorer' in query_lower:
            filtered_df = filtered_df[filtered_df['total_points'] >= filtered_df['total_points'].quantile(0.8)]
        
        # Ownership keywords
        if 'differential' in query_lower or 'low owned' in query_lower:
            filtered_df = filtered_df[filtered_df['selected_by_percent'] <= 10.0]
        elif 'popular' in query_lower or 'highly owned' in query_lower:
            filtered_df = filtered_df[filtered_df['selected_by_percent'] >= 20.0]
        
        return filtered_df

print("✅ Interactive Filter System created successfully!")
