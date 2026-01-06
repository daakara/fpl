"""
Price Changes Analysis Page - Display price change predictions and alerts
"""

import streamlit as st
import pandas as pd
from datetime import datetime


class PriceChangesPage:
    """Page for displaying price change predictions and transfer trends"""
    
    def __init__(self):
        """Initialize the price changes page"""
        self.title = "💰 Price Changes"
    
    def render(self):
        """Render the price changes analysis page"""
        st.title("💰 Price Changes & Transfer Trends")
        st.markdown("---")
        
        # Get player data from session state
        if 'players_df' not in st.session_state or st.session_state.players_df.empty:
            st.warning("⚠️ No player data available. Please wait for data to load.")
            return
        
        df = st.session_state.players_df.copy()
        
        # Check if price predictions are available
        if 'price_change_probability' not in df.columns:
            st.info("ℹ️ Price change predictions not available. Loading...")
            return
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔥 Hot Picks (Rising)", 
            "❄️ Falling Players", 
            "📊 Transfer Trends",
            "🎯 Price Targets"
        ])
        
        with tab1:
            self._render_rising_players(df)
        
        with tab2:
            self._render_falling_players(df)
        
        with tab3:
            self._render_transfer_trends(df)
        
        with tab4:
            self._render_price_targets(df)
    
    def _render_rising_players(self, df):
        """Render players likely to rise in price"""
        st.subheader("🔥 Players Likely to Rise")
        st.markdown("Players with high probability of price increase based on transfer activity")
        
        # Filter rising players
        rising = df[
            (df.get('net_transfers_event', 0) > 0) &
            (df.get('price_change_probability', 0) > 40)
        ].copy()
        
        if len(rising) == 0:
            st.info("No players currently predicted to rise in price.")
            return
        
        # Sort by probability
        rising = rising.sort_values('price_change_probability', ascending=False)
        
        # Display urgent alerts first
        urgent = rising[rising['price_change_probability'] > 80].head(10)
        
        if len(urgent) > 0:
            st.markdown("### ⚠️ Urgent - Likely Tonight")
            for idx, player in urgent.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{player.get('web_name', 'Unknown')}**")
                    st.caption(f"{self._get_position_name(player.get('element_type', 0))} | {self._get_team_name(player.get('team', 0))}")
                
                with col2:
                    st.metric("Probability", f"{player['price_change_probability']:.0f}%")
                
                with col3:
                    st.metric("Net Transfers", f"{player.get('net_transfers_event', 0):,}")
                
                with col4:
                    price = player.get('now_cost', 0) / 10
                    st.metric("Price", f"£{price:.1f}m")
                
                st.markdown("---")
        
        # Display watch list
        watch = rising[
            (rising['price_change_probability'] >= 40) & 
            (rising['price_change_probability'] <= 80)
        ].head(15)
        
        if len(watch) > 0:
            st.markdown("### 👀 Watch List - Possible Risers")
            
            display_df = watch[[
                'web_name', 'price', 'price_change_probability', 
                'net_transfers_event', 'selected_by_percent', 'form'
            ]].copy()
            
            display_df.columns = ['Player', 'Price (£m)', 'Rise Prob %', 'Net Transfers', 'Ownership %', 'Form']
            display_df['Rise Prob %'] = display_df['Rise Prob %'].round(1)
            display_df['Price (£m)'] = display_df['Price (£m)'].round(1)
            display_df['Ownership %'] = display_df['Ownership %'].round(1)
            display_df['Form'] = display_df['Form'].round(1)
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    def _render_falling_players(self, df):
        """Render players likely to fall in price"""
        st.subheader("❄️ Players Likely to Fall")
        st.markdown("Players with high probability of price decrease - consider selling")
        
        # Filter falling players
        falling = df[
            (df.get('net_transfers_event', 0) < 0) &
            (df.get('price_change_probability', 0) > 40)
        ].copy()
        
        if len(falling) == 0:
            st.info("No players currently predicted to fall in price.")
            return
        
        # Sort by probability
        falling = falling.sort_values('price_change_probability', ascending=False)
        
        # Display urgent alerts
        urgent = falling[falling['price_change_probability'] > 80].head(10)
        
        if len(urgent) > 0:
            st.markdown("### ⚠️ Urgent - Likely Tonight")
            for idx, player in urgent.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{player.get('web_name', 'Unknown')}**")
                    st.caption(f"{self._get_position_name(player.get('element_type', 0))} | {self._get_team_name(player.get('team', 0))}")
                
                with col2:
                    st.metric("Probability", f"{player['price_change_probability']:.0f}%")
                
                with col3:
                    st.metric("Net Transfers", f"{player.get('net_transfers_event', 0):,}")
                
                with col4:
                    price = player.get('now_cost', 0) / 10
                    ownership = player.get('selected_by_percent', 0)
                    st.metric("Ownership", f"{ownership:.1f}%")
                
                # Show reason for fall
                if player.get('form', 0) < 3:
                    st.caption("⚠️ Poor form")
                if player.get('injury_risk_category', '') in ['High', 'Critical']:
                    st.caption("🏥 Injury concern")
                
                st.markdown("---")
        
        # Display watch list
        watch = falling[
            (falling['price_change_probability'] >= 40) & 
            (falling['price_change_probability'] <= 80)
        ].head(15)
        
        if len(watch) > 0:
            st.markdown("### 👀 Watch List - Possible Fallers")
            
            display_df = watch[[
                'web_name', 'price', 'price_change_probability', 
                'net_transfers_event', 'selected_by_percent', 'form'
            ]].copy()
            
            display_df.columns = ['Player', 'Price (£m)', 'Fall Prob %', 'Net Transfers', 'Ownership %', 'Form']
            display_df['Fall Prob %'] = display_df['Fall Prob %'].round(1)
            display_df['Price (£m)'] = display_df['Price (£m)'].round(1)
            display_df['Ownership %'] = display_df['Ownership %'].round(1)
            display_df['Form'] = display_df['Form'].round(1)
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    def _render_transfer_trends(self, df):
        """Render overall transfer trends"""
        st.subheader("📊 Transfer Market Analysis")
        
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_transfers_in = df.get('transfers_in_event', 0).sum()
            st.metric("Total Transfers In", f"{total_transfers_in:,}")
        
        with col2:
            total_transfers_out = df.get('transfers_out_event', 0).sum()
            st.metric("Total Transfers Out", f"{total_transfers_out:,}")
        
        with col3:
            rising_count = len(df[df.get('price_change_probability', 0) > 50])
            st.metric("Players Rising", rising_count)
        
        with col4:
            falling_count = len(df[
                (df.get('net_transfers_event', 0) < 0) & 
                (df.get('price_change_probability', 0) > 50)
            ])
            st.metric("Players Falling", falling_count)
        
        st.markdown("---")
        
        # Most transferred IN
        st.markdown("### 📈 Most Transferred IN (This Gameweek)")
        most_in = df.nlargest(10, 'transfers_in_event')[[
            'web_name', 'price', 'transfers_in_event', 'form', 'selected_by_percent'
        ]].copy()
        most_in.columns = ['Player', 'Price (£m)', 'Transfers In', 'Form', 'Ownership %']
        most_in['Price (£m)'] = most_in['Price (£m)'].round(1)
        most_in['Form'] = most_in['Form'].round(1)
        most_in['Ownership %'] = most_in['Ownership %'].round(1)
        st.dataframe(most_in, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Most transferred OUT
        st.markdown("### 📉 Most Transferred OUT (This Gameweek)")
        most_out = df.nlargest(10, 'transfers_out_event')[[
            'web_name', 'price', 'transfers_out_event', 'form', 'selected_by_percent'
        ]].copy()
        most_out.columns = ['Player', 'Price (£m)', 'Transfers Out', 'Form', 'Ownership %']
        most_out['Price (£m)'] = most_out['Price (£m)'].round(1)
        most_out['Form'] = most_out['Form'].round(1)
        most_out['Ownership %'] = most_out['Ownership %'].round(1)
        st.dataframe(most_out, use_container_width=True, hide_index=True)
    
    def _render_price_targets(self, df):
        """Render price targets within budget"""
        st.subheader("🎯 Price Targets - Beat the Rise")
        st.markdown("Players to target before they rise in price")
        
        # Budget filter
        budget = st.slider("Maximum Price (£m)", 4.0, 15.0, 10.0, 0.5)
        
        # Filter targets
        targets = df[
            (df.get('predicted_price_change', 0) == 1) &
            (df.get('price_change_probability', 0) > 50) &
            (df.get('price', 0) <= budget)
        ].copy()
        
        if len(targets) == 0:
            st.info(f"No price targets found within £{budget}m budget.")
            return
        
        # Sort by value potential
        if 'value_potential' in targets.columns:
            targets = targets.sort_values('value_potential', ascending=False)
        else:
            targets = targets.sort_values('price_change_probability', ascending=False)
        
        # Display top targets
        st.markdown(f"### Top Targets (£{budget}m or less)")
        
        for idx, player in targets.head(15).iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{player.get('web_name', 'Unknown')}**")
                    st.caption(f"{self._get_position_name(player.get('element_type', 0))} | {self._get_team_name(player.get('team', 0))}")
                
                with col2:
                    price = player.get('price', 0)
                    st.metric("Price", f"£{price:.1f}m")
                
                with col3:
                    prob = player.get('price_change_probability', 0)
                    st.metric("Rise Prob", f"{prob:.0f}%")
                
                with col4:
                    form = player.get('form', 0)
                    st.metric("Form", f"{form:.1f}")
                
                with col5:
                    ownership = player.get('selected_by_percent', 0)
                    st.metric("Ownership", f"{ownership:.1f}%")
                
                st.markdown("---")
    
    def _get_position_name(self, element_type):
        """Get position name from element type"""
        positions = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        return positions.get(element_type, "Unknown")
    
    def _get_team_name(self, team_id):
        """Get team name from ID"""
        if 'teams_df' in st.session_state and not st.session_state.teams_df.empty:
            teams_df = st.session_state.teams_df
            team = teams_df[teams_df['id'] == team_id]
            if len(team) > 0:
                return team.iloc[0].get('short_name', 'Unknown')
        return "Unknown"
