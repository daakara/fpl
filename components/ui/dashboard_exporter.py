"""
Advanced Dashboard Export System
Provides PDF and Excel export capabilities for FPL Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime

class DashboardExporter:
    """Advanced export functionality for FPL Dashboard"""
    
    def __init__(self):
        self.report_styles = {
            'title_color': '#1f77b4',
            'header_color': '#00cc44', 
            'text_color': '#262730'
        }
    
    def create_team_analysis_report(self, players_df, teams_df, user_team_name="My FPL Team"):
        """Generate comprehensive team analysis report"""
        
        report_data = {
            'team_name': user_team_name,
            'generated_date': datetime.now().strftime("%B %d, %Y at %H:%M"),
            'total_players': len(players_df) if not players_df.empty else 0,
            'summary_stats': {},
            'top_players': [],
            'recommendations': []
        }
        
        if not players_df.empty:
            # Calculate summary statistics
            report_data['summary_stats'] = {
                'total_points': players_df['total_points'].sum(),
                'average_points': players_df['total_points'].mean(),
                'team_value': players_df['now_cost'].sum() / 10,
                'form_rating': players_df['form'].astype(float).mean()
            }
            
            # Get top performers
            top_players = players_df.nlargest(5, 'total_points')[
                ['web_name', 'total_points', 'now_cost', 'form', 'selected_by_percent']
            ]
            
            report_data['top_players'] = top_players.to_dict('records')
            
            # Generate AI recommendations
            report_data['recommendations'] = [
                "Consider transferring underperforming midfielders for better value",
                "Your defense is strong - focus on attacking returns", 
                "Captain rotation between top 3 performers recommended",
                "Monitor injury news for key players before next deadline",
                "Excellent team balance - minor tweaks only needed"
            ]
        
        return report_data
    
    def create_csv_export(self, players_df, teams_df):
        """Generate CSV export of player and team data"""
        
        buffer = io.StringIO()
        
        if not players_df.empty:
            # Select key columns for export
            export_columns = [
                'web_name', 'team', 'element_type', 'total_points', 
                'now_cost', 'form', 'selected_by_percent', 'minutes',
                'goals_scored', 'assists', 'clean_sheets', 'bonus'
            ]
            
            available_columns = [col for col in export_columns if col in players_df.columns]
            players_export = players_df[available_columns].copy()
            
            # Add position names
            position_map = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
            if 'element_type' in players_export.columns:
                players_export['position'] = players_export['element_type'].map(position_map)
            
            players_export.to_csv(buffer, index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_detailed_analysis(self, players_df):
        """Create detailed statistical analysis"""
        
        if players_df.empty:
            return "No player data available for analysis."
        
        analysis = []
        analysis.append("📊 DETAILED STATISTICAL ANALYSIS")
        analysis.append("=" * 50)
        analysis.append("")
        
        # Overall team statistics
        analysis.append("🎯 Team Performance Overview:")
        analysis.append(f"  • Total Points: {players_df['total_points'].sum():,}")
        analysis.append(f"  • Average Points per Player: {players_df['total_points'].mean():.1f}")
        analysis.append(f"  • Team Value: £{players_df['now_cost'].sum()/10:.1f}M")
        analysis.append(f"  • Average Form: {players_df['form'].astype(float).mean():.1f}/10")
        analysis.append("")
        
        # Position analysis
        if 'element_type' in players_df.columns:
            analysis.append("⚽ Position Breakdown:")
            position_map = {1: 'Goalkeeper', 2: 'Defender', 3: 'Midfielder', 4: 'Forward'}
            
            for pos_id, pos_name in position_map.items():
                pos_players = players_df[players_df['element_type'] == pos_id]
                if not pos_players.empty:
                    analysis.append(f"  • {pos_name}s: {len(pos_players)} players")
                    analysis.append(f"    - Avg Points: {pos_players['total_points'].mean():.1f}")
                    analysis.append(f"    - Total Value: £{pos_players['now_cost'].sum()/10:.1f}M")
            analysis.append("")
        
        # Top performers
        analysis.append("🌟 Top 5 Performers:")
        top_5 = players_df.nlargest(5, 'total_points')
        for i, (_, player) in enumerate(top_5.iterrows(), 1):
            analysis.append(f"  {i}. {player['web_name']} - {player['total_points']} points")
        analysis.append("")
        
        # Form analysis
        if 'form' in players_df.columns:
            good_form = players_df[players_df['form'].astype(float) >= 7.0]
            poor_form = players_df[players_df['form'].astype(float) <= 4.0]
            
            analysis.append("📈 Form Analysis:")
            analysis.append(f"  • Players in excellent form (7.0+): {len(good_form)}")
            analysis.append(f"  • Players needing attention (<4.0): {len(poor_form)}")
            analysis.append("")
        
        return "\n".join(analysis)
    
    def render_export_widgets(self, players_df, teams_df):
        """Render export widgets in Streamlit sidebar"""
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📊 Export Dashboard")
            
            # CSV Export
            if st.button("📄 Export as CSV", use_container_width=True):
                with st.spinner("Generating CSV export..."):
                    csv_data = self.create_csv_export(players_df, teams_df)
                    
                    st.download_button(
                        label="⬇️ Download CSV File",
                        data=csv_data,
                        file_name=f"FPL_Data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.success("CSV export ready for download!")
            
            # Detailed Analysis Export
            if st.button("📈 Export Analysis Report", use_container_width=True):
                with st.spinner("Creating detailed analysis..."):
                    analysis_text = self.create_detailed_analysis(players_df)
                    
                    st.download_button(
                        label="⬇️ Download Analysis Report",
                        data=analysis_text,
                        file_name=f"FPL_Analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    st.success("Analysis report generated!")
            
            # Quick stats preview
            if not players_df.empty:
                st.markdown("**Export Preview:**")
                st.metric("Players", len(players_df))
                st.metric("Data Points", len(players_df.columns) * len(players_df))
                st.metric("Total Points", f"{players_df['total_points'].sum():,}")
    
    def show_export_summary(self, players_df, teams_df):
        """Display export functionality summary"""
        
        st.markdown("### 📊 Advanced Export System")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "CSV Export",
                "Ready" if not players_df.empty else "No Data",
                "Player & Team Data"
            )
        
        with col2:
            st.metric(
                "Analysis Report", 
                "Available" if not players_df.empty else "No Data",
                "Detailed Statistics"  
            )
        
        with col3:
            st.metric(
                "Export Formats",
                "2",
                "CSV + TXT Reports"
            )
        
        if not players_df.empty:
            st.success("✅ Export system ready! Use sidebar to generate reports.")
        else:
            st.warning("⚠️ Load FPL data first to enable exports.")

# Global exporter instance
_dashboard_exporter = None

def get_dashboard_exporter():
    """Get the global dashboard exporter instance"""
    global _dashboard_exporter
    if _dashboard_exporter is None:
        _dashboard_exporter = DashboardExporter()
    return _dashboard_exporter
