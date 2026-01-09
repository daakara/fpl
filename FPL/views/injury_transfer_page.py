"""
Injury and Transfer Data Page
Displays real-time injury and transfer information from Premier League
"""

import streamlit as st
import pandas as pd
from services.external_data_integrator_service import ExternalDataIntegratorService


class InjuryTransferPage:
    """Page for displaying injury and transfer data"""
    
    def __init__(self):
        """Initialize the page"""
        self.external_service = ExternalDataIntegratorService()
    
    def render(self):
        """Render the injury and transfer data page"""
        st.title("⚕️ Injury & Transfer Centre")
        st.markdown("*Real-time updates from Premier League Official*")
        
        # Create tabs for injuries and transfers
        tab1, tab2 = st.tabs(["🏥 Injuries", "🔄 Transfers"])
        
        with tab1:
            self._render_injuries()
        
        with tab2:
            self._render_transfers()
    
    def _render_injuries(self):
        """Render injury data section"""
        st.markdown("### 🏥 Latest Player Injuries")
        st.markdown("*Data sourced from Premier League Official Website*")
        
        # Add refresh button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh Data", key="refresh_injuries"):
                # Clear cache to force refresh
                self.external_service.injury_data_cache = None
                self.external_service.cache_timestamp = None
                st.rerun()
        
        with st.spinner("Fetching latest injury data..."):
            injuries = self.external_service.fetch_premier_league_injuries()
        
        if injuries:
            # Display summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Injuries", len(injuries))
            
            with col2:
                # Count unique teams
                unique_teams = len(set([inj['team'] for inj in injuries]))
                st.metric("Affected Teams", unique_teams)
            
            with col3:
                # Show last updated time
                if injuries and 'last_updated' in injuries[0]:
                    st.metric("Last Updated", injuries[0]['last_updated'].split()[1])
            
            # Display injuries in a dataframe
            st.markdown("---")
            
            # Convert to DataFrame for better display
            df_injuries = pd.DataFrame(injuries)
            
            # Add search functionality
            search_term = st.text_input("🔍 Search by player or team name", key="injury_search")
            
            if search_term:
                mask = (
                    df_injuries['player_name'].str.contains(search_term, case=False, na=False) |
                    df_injuries['team'].str.contains(search_term, case=False, na=False)
                )
                df_display = df_injuries[mask]
            else:
                df_display = df_injuries
            
            # Group by team option
            if st.checkbox("Group by Team", key="group_injuries"):
                teams = sorted(df_display['team'].unique())
                for team in teams:
                    team_injuries = df_display[df_display['team'] == team]
                    with st.expander(f"**{team}** ({len(team_injuries)} injured)", expanded=False):
                        for _, injury in team_injuries.iterrows():
                            st.markdown(f"""
                            **{injury['player_name']}**  
                            - Status: {injury['injury_status']}  
                            - Expected Return: {injury['expected_return']}
                            """)
                            st.markdown("---")
            else:
                # Display as table
                display_columns = ['player_name', 'team', 'injury_status', 'expected_return']
                available_columns = [col for col in display_columns if col in df_display.columns]
                
                st.dataframe(
                    df_display[available_columns],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "player_name": st.column_config.TextColumn("Player", width="medium"),
                        "team": st.column_config.TextColumn("Team", width="medium"),
                        "injury_status": st.column_config.TextColumn("Status", width="medium"),
                        "expected_return": st.column_config.TextColumn("Expected Return", width="medium")
                    }
                )
            
            # Download option
            st.markdown("---")
            csv = df_injuries.to_csv(index=False)
            st.download_button(
                label="📥 Download Injury Data (CSV)",
                data=csv,
                file_name=f"pl_injuries_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
        else:
            st.info("No injury data available. This could mean:")
            st.markdown("""
            - No current injuries reported
            - The website structure has changed
            - Connection issue with the Premier League website
            
            Please try refreshing or check back later.
            """)
            
            st.markdown("**Data Source:** [Premier League Injuries](https://www.premierleague.com/en/latest-player-injuries)")
    
    def _render_transfers(self):
        """Render transfer data section"""
        st.markdown("### 🔄 Latest Transfers")
        st.markdown("*Data sourced from Premier League Official Website*")
        
        # Add refresh button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh Data", key="refresh_transfers"):
                # Clear cache to force refresh
                self.external_service.transfer_data_cache = None
                self.external_service.cache_timestamp = None
                st.rerun()
        
        with st.spinner("Fetching latest transfer data..."):
            transfers = self.external_service.fetch_premier_league_transfers()
        
        if transfers:
            # Display summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Transfers", len(transfers))
            
            with col2:
                # Count loans vs permanent
                transfer_types = pd.DataFrame(transfers)['transfer_type'].value_counts()
                st.metric("Transfer Types", len(transfer_types))
            
            with col3:
                # Show last updated time
                if transfers and 'last_updated' in transfers[0]:
                    st.metric("Last Updated", transfers[0]['last_updated'].split()[1])
            
            # Display transfers in a dataframe
            st.markdown("---")
            
            # Convert to DataFrame for better display
            df_transfers = pd.DataFrame(transfers)
            
            # Add search functionality
            search_term = st.text_input("🔍 Search by player or club name", key="transfer_search")
            
            if search_term:
                mask = (
                    df_transfers['player_name'].str.contains(search_term, case=False, na=False) |
                    df_transfers['from_club'].str.contains(search_term, case=False, na=False) |
                    df_transfers['to_club'].str.contains(search_term, case=False, na=False)
                )
                df_display = df_transfers[mask]
            else:
                df_display = df_transfers
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                transfer_type_filter = st.multiselect(
                    "Filter by Transfer Type",
                    options=df_transfers['transfer_type'].unique().tolist(),
                    key="transfer_type_filter"
                )
            
            with col2:
                club_filter = st.multiselect(
                    "Filter by Club (To/From)",
                    options=list(set(df_transfers['to_club'].tolist() + df_transfers['from_club'].tolist())),
                    key="club_filter"
                )
            
            # Apply filters
            if transfer_type_filter:
                df_display = df_display[df_display['transfer_type'].isin(transfer_type_filter)]
            
            if club_filter:
                df_display = df_display[
                    df_display['to_club'].isin(club_filter) | 
                    df_display['from_club'].isin(club_filter)
                ]
            
            # Display as cards or table
            view_mode = st.radio("View Mode", ["Table", "Cards"], horizontal=True, key="transfer_view")
            
            if view_mode == "Cards":
                for _, transfer in df_display.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 2])
                        
                        with col1:
                            st.markdown(f"**{transfer['player_name']}**")
                            st.caption(f"From: {transfer['from_club']}")
                        
                        with col2:
                            st.markdown("➡️")
                            st.caption(transfer['transfer_type'])
                        
                        with col3:
                            st.markdown(f"**{transfer['to_club']}**")
                            st.caption(f"Fee: {transfer['transfer_fee']}")
                        
                        st.markdown("---")
            else:
                # Display as table
                display_columns = ['player_name', 'from_club', 'to_club', 'transfer_type', 'transfer_fee', 'transfer_date']
                available_columns = [col for col in display_columns if col in df_display.columns]
                
                st.dataframe(
                    df_display[available_columns],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "player_name": st.column_config.TextColumn("Player", width="medium"),
                        "from_club": st.column_config.TextColumn("From", width="medium"),
                        "to_club": st.column_config.TextColumn("To", width="medium"),
                        "transfer_type": st.column_config.TextColumn("Type", width="small"),
                        "transfer_fee": st.column_config.TextColumn("Fee", width="small"),
                        "transfer_date": st.column_config.TextColumn("Date", width="small")
                    }
                )
            
            # Download option
            st.markdown("---")
            csv = df_transfers.to_csv(index=False)
            st.download_button(
                label="📥 Download Transfer Data (CSV)",
                data=csv,
                file_name=f"pl_transfers_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
        else:
            st.info("No transfer data available. This could mean:")
            st.markdown("""
            - No recent transfers reported
            - The website structure has changed
            - Connection issue with the Premier League website
            
            Please try refreshing or check back later.
            """)
            
            st.markdown("**Data Source:** [Premier League Transfers](https://www.premierleague.com/en/transfers)")
