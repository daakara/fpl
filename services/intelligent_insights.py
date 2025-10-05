"""
Intelligent Insights Engine for FPL Analysis
Provides AI-powered insights, recommendations, and strategic advice
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PlayerInsight:
    """Data class for player insights"""
    player: str
    insight_type: str
    priority: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    confidence: float
    action: str
    stats: Dict

@dataclass
class TeamInsight:
    """Data class for team insights"""
    insight_type: str
    priority: str
    title: str
    description: str
    affected_players: List[str]
    confidence: float
    recommendation: str

class IntelligentInsightsEngine:
    """AI-powered insights and recommendations engine"""
    
    def __init__(self):
        self.insight_thresholds = {
            'high_form': 7.0,
            'low_form': 3.0,
            'high_ownership': 15.0,
            'low_ownership': 5.0,
            'high_value': 7.0,  # points per million
            'price_threshold': 0.1,  # 10% of price
            'minutes_threshold': 270  # 3 games worth
        }
        
        self.position_names = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    
    def generate_all_insights(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> Dict[str, List]:
        """Generate comprehensive insights from FPL data"""
        if df.empty:
            return {'player_insights': [], 'team_insights': [], 'market_insights': []}
        
        insights = {
            'player_insights': [],
            'team_insights': [],
            'market_insights': []
        }
        
        # Generate different types of insights
        insights['player_insights'].extend(self._generate_form_insights(df))
        insights['player_insights'].extend(self._generate_value_insights(df))
        insights['player_insights'].extend(self._generate_ownership_insights(df))
        insights['player_insights'].extend(self._generate_injury_risk_insights(df))
        
        insights['market_insights'].extend(self._generate_market_insights(df))
        insights['market_insights'].extend(self._generate_price_change_insights(df))
        
        if teams_df is not None:
            insights['team_insights'].extend(self._generate_team_insights(df, teams_df))
        
        # Sort by priority and confidence
        for category in insights:
            insights[category] = sorted(
                insights[category], 
                key=lambda x: (x.priority == 'HIGH', x.confidence), 
                reverse=True
            )
        
        return insights
    
    def _generate_form_insights(self, df: pd.DataFrame) -> List[PlayerInsight]:
        """Generate insights based on player form"""
        insights = []
        
        # Hot streaks
        hot_players = df[
            (df['form'] >= self.insight_thresholds['high_form']) & 
            (df['minutes'] >= self.insight_thresholds['minutes_threshold'])
        ].nlargest(5, 'form')
        
        for _, player in hot_players.iterrows():
            insights.append(PlayerInsight(
                player=player['web_name'],
                insight_type='HOT_STREAK',
                priority='HIGH',
                title=f"🔥 {player['web_name']} is on fire!",
                description=f"Averaging {player['form']:.1f} points over last 5 games. "
                           f"Total: {player['total_points']} points this season.",
                confidence=min(0.95, 0.6 + (player['form'] - 5) * 0.1),
                action="CONSIDER_BUYING",
                stats={
                    'form': player['form'],
                    'total_points': player['total_points'],
                    'price': player['now_cost'] / 10,
                    'ownership': player['selected_by_percent']
                }
            ))
        
        # Cold streaks
        cold_players = df[
            (df['form'] <= self.insight_thresholds['low_form']) & 
            (df['minutes'] >= self.insight_thresholds['minutes_threshold']) &
            (df['selected_by_percent'] >= 5.0)  # Only flagging owned players
        ].nsmallest(5, 'form')
        
        for _, player in cold_players.iterrows():
            insights.append(PlayerInsight(
                player=player['web_name'],
                insight_type='COLD_STREAK',
                priority='MEDIUM',
                title=f"❄️ {player['web_name']} struggling for form",
                description=f"Only {player['form']:.1f} points per game recently. "
                           f"Owned by {player['selected_by_percent']:.1f}% despite poor form.",
                confidence=0.7,
                action="CONSIDER_SELLING",
                stats={
                    'form': player['form'],
                    'total_points': player['total_points'],
                    'price': player['now_cost'] / 10,
                    'ownership': player['selected_by_percent']
                }
            ))
        
        return insights
    
    def _generate_value_insights(self, df: pd.DataFrame) -> List[PlayerInsight]:
        """Generate value-based insights"""
        insights = []
        
        # Calculate points per million
        df_value = df.copy()
        df_value['points_per_million'] = np.where(
            df_value['now_cost'] > 0,
            df_value['total_points'] / (df_value['now_cost'] / 10),
            0
        )
        
        # Hidden gems (high value, low ownership)
        hidden_gems = df_value[
            (df_value['points_per_million'] >= self.insight_thresholds['high_value']) &
            (df_value['selected_by_percent'] <= self.insight_thresholds['low_ownership']) &
            (df_value['minutes'] >= self.insight_thresholds['minutes_threshold'])
        ].nlargest(3, 'points_per_million')
        
        for _, player in hidden_gems.iterrows():
            insights.append(PlayerInsight(
                player=player['web_name'],
                insight_type='HIDDEN_GEM',
                priority='HIGH',
                title=f"💎 {player['web_name']} - Exceptional Value",
                description=f"{player['points_per_million']:.1f} points per £1M! "
                           f"Only {player['selected_by_percent']:.1f}% ownership. "
                           f"Potential differential pick.",
                confidence=0.85,
                action="STRONG_BUY",
                stats={
                    'points_per_million': player['points_per_million'],
                    'total_points': player['total_points'],
                    'price': player['now_cost'] / 10,
                    'ownership': player['selected_by_percent']
                }
            ))
        
        # Overpriced players
        overpriced = df_value[
            (df_value['points_per_million'] <= 3.0) &
            (df_value['selected_by_percent'] >= 10.0) &
            (df_value['now_cost'] >= 80)  # 8.0m+
        ].nsmallest(3, 'points_per_million')
        
        for _, player in overpriced.iterrows():
            insights.append(PlayerInsight(
                player=player['web_name'],
                insight_type='OVERPRICED',
                priority='MEDIUM',
                title=f"💸 {player['web_name']} - Poor Value",
                description=f"Only {player['points_per_million']:.1f} points per £1M at £{player['now_cost']/10:.1f}M. "
                           f"Consider alternatives in this price range.",
                confidence=0.75,
                action="AVOID",
                stats={
                    'points_per_million': player['points_per_million'],
                    'total_points': player['total_points'],
                    'price': player['now_cost'] / 10,
                    'ownership': player['selected_by_percent']
                }
            ))
        
        return insights
    
    def _generate_ownership_insights(self, df: pd.DataFrame) -> List[PlayerInsight]:
        """Generate ownership-based insights"""
        insights = []
        
        # Template players (high ownership, good performance)
        template_players = df[
            (df['selected_by_percent'] >= 25.0) &
            (df['total_points'] >= df['total_points'].quantile(0.8))
        ].nlargest(3, 'selected_by_percent')
        
        for _, player in template_players.iterrows():
            insights.append(PlayerInsight(
                player=player['web_name'],
                insight_type='TEMPLATE_PLAYER',
                priority='HIGH',
                title=f"👑 {player['web_name']} - Template Essential",
                description=f"Owned by {player['selected_by_percent']:.1f}% with {player['total_points']} points. "
                           f"Not owning could hurt your rank significantly.",
                confidence=0.9,
                action="ESSENTIAL_HOLD",
                stats={
                    'ownership': player['selected_by_percent'],
                    'total_points': player['total_points'],
                    'price': player['now_cost'] / 10,
                    'form': player['form']
                }
            ))
        
        # Potential differentials
        differentials = df[
            (df['selected_by_percent'] <= 5.0) &
            (df['form'] >= 5.0) &
            (df['minutes'] >= 180)
        ].nlargest(3, 'form')
        
        for _, player in differentials.iterrows():
            insights.append(PlayerInsight(
                player=player['web_name'],
                insight_type='DIFFERENTIAL',
                priority='MEDIUM',
                title=f"⚡ {player['web_name']} - Differential Opportunity",
                description=f"Only {player['selected_by_percent']:.1f}% ownership but {player['form']:.1f} form. "
                           f"Could be a rank-boosting differential.",
                confidence=0.7,
                action="DIFFERENTIAL_PICK",
                stats={
                    'ownership': player['selected_by_percent'],
                    'form': player['form'],
                    'total_points': player['total_points'],
                    'price': player['now_cost'] / 10
                }
            ))
        
        return insights
    
    def _generate_injury_risk_insights(self, df: pd.DataFrame) -> List[PlayerInsight]:
        """Generate injury and rotation risk insights"""
        insights = []
        
        # Players with low minutes despite high ownership
        rotation_risks = df[
            (df['selected_by_percent'] >= 10.0) &
            (df['minutes'] <= 450) &  # Less than 5 games equivalent
            (df['now_cost'] >= 50)  # 5.0m+ players
        ]
        
        for _, player in rotation_risks.iterrows():
            insights.append(PlayerInsight(
                player=player['web_name'],
                insight_type='ROTATION_RISK',
                priority='MEDIUM',
                title=f"⚠️ {player['web_name']} - Rotation Concern",
                description=f"Only {player['minutes']} minutes played despite {player['selected_by_percent']:.1f}% ownership. "
                           f"May not be nailed in the starting XI.",
                confidence=0.8,
                action="MONITOR_CLOSELY",
                stats={
                    'minutes': player['minutes'],
                    'ownership': player['selected_by_percent'],
                    'price': player['now_cost'] / 10,
                    'total_points': player['total_points']
                }
            ))
        
        return insights
    
    def _generate_market_insights(self, df: pd.DataFrame) -> List[PlayerInsight]:
        """Generate market trend insights"""
        insights = []
        
        # Rising stars (good form, increasing ownership)
        if 'transfers_in_event' in df.columns:
            rising_stars = df[
                (df['transfers_in_event'] > df['transfers_out_event'] * 2) &
                (df['form'] >= 5.0)
            ].nlargest(3, 'transfers_in_event')
            
            for _, player in rising_stars.iterrows():
                net_transfers = player['transfers_in_event'] - player['transfers_out_event']
                insights.append(PlayerInsight(
                    player=player['web_name'],
                    insight_type='RISING_STAR',
                    priority='HIGH',
                    title=f"🚀 {player['web_name']} - Trending Up",
                    description=f"+{net_transfers:,.0f} net transfers this week! "
                               f"Form: {player['form']:.1f}. Price rise likely soon.",
                    confidence=0.85,
                    action="BUY_BEFORE_RISE",
                    stats={
                        'net_transfers': net_transfers,
                        'form': player['form'],
                        'price': player['now_cost'] / 10,
                        'ownership': player['selected_by_percent']
                    }
                ))
        
        return insights
    
    def _generate_price_change_insights(self, df: pd.DataFrame) -> List[PlayerInsight]:
        """Generate price change predictions"""
        insights = []
        
        if 'transfers_in_event' in df.columns and 'transfers_out_event' in df.columns:
            # Calculate transfer momentum
            df_price = df.copy()
            df_price['transfer_balance'] = df_price['transfers_in_event'] - df_price['transfers_out_event']
            
            # Players likely to rise
            rise_candidates = df_price[
                df_price['transfer_balance'] > 50000
            ].nlargest(3, 'transfer_balance')
            
            for _, player in rise_candidates.iterrows():
                insights.append(PlayerInsight(
                    player=player['web_name'],
                    insight_type='PRICE_RISE',
                    priority='MEDIUM',
                    title=f"📈 {player['web_name']} - Price Rise Alert",
                    description=f"Strong transfer momentum (+{player['transfer_balance']:,.0f}). "
                               f"Price increase likely within 24-48 hours.",
                    confidence=0.8,
                    action="BUY_NOW",
                    stats={
                        'transfer_balance': player['transfer_balance'],
                        'current_price': player['now_cost'] / 10,
                        'ownership': player['selected_by_percent']
                    }
                ))
            
            # Players likely to fall
            fall_candidates = df_price[
                df_price['transfer_balance'] < -30000
            ].nsmallest(3, 'transfer_balance')
            
            for _, player in fall_candidates.iterrows():
                insights.append(PlayerInsight(
                    player=player['web_name'],
                    insight_type='PRICE_FALL',
                    priority='LOW',
                    title=f"📉 {player['web_name']} - Price Drop Expected",
                    description=f"Heavy selling ({player['transfer_balance']:,.0f}). "
                               f"Price decrease possible soon.",
                    confidence=0.75,
                    action="WAIT_FOR_DROP",
                    stats={
                        'transfer_balance': player['transfer_balance'],
                        'current_price': player['now_cost'] / 10,
                        'ownership': player['selected_by_percent']
                    }
                ))
        
        return insights
    
    def _generate_team_insights(self, df: pd.DataFrame, teams_df: pd.DataFrame) -> List[TeamInsight]:
        """Generate team-based insights"""
        insights = []
        
        # Calculate team performance metrics
        team_stats = []
        
        for _, team in teams_df.iterrows():
            team_players = df[df['team'] == team['id']]
            
            if not team_players.empty:
                stats = {
                    'team_id': team['id'],
                    'team_name': team['name'],
                    'avg_points': team_players['total_points'].mean(),
                    'total_players': len(team_players),
                    'avg_ownership': team_players['selected_by_percent'].mean(),
                    'top_scorer': team_players.loc[team_players['total_points'].idxmax(), 'web_name'],
                    'top_points': team_players['total_points'].max()
                }
                team_stats.append(stats)
        
        # Find best attacking teams
        if team_stats:
            team_df = pd.DataFrame(team_stats)
            top_attacking = team_df.nlargest(3, 'avg_points')
            
            for _, team in top_attacking.iterrows():
                team_players_list = df[df['team'] == team['team_id']]['web_name'].tolist()[:5]
                
                insights.append(TeamInsight(
                    insight_type='ATTACKING_TEAM',
                    priority='HIGH',
                    title=f"⚽ {team['team_name']} - Attacking Powerhouse",
                    description=f"Team averaging {team['avg_points']:.1f} points per player. "
                               f"{team['top_scorer']} leading with {team['top_points']} points.",
                    affected_players=team_players_list,
                    confidence=0.85,
                    recommendation=f"Consider multiple {team['team_name']} attackers"
                ))
        
        return insights
    
    def format_insights_for_display(self, insights: Dict[str, List]) -> str:
        """Format insights for display in Streamlit"""
        formatted = []
        
        # Player insights
        if insights['player_insights']:
            formatted.append("## 👤 Player Insights\n")
            for insight in insights['player_insights'][:10]:  # Top 10
                priority_emoji = "🔴" if insight.priority == "HIGH" else "🟡" if insight.priority == "MEDIUM" else "🟢"
                confidence_bar = "█" * int(insight.confidence * 10)
                
                formatted.append(f"### {priority_emoji} {insight.title}")
                formatted.append(f"**{insight.description}**")
                formatted.append(f"*Action: {insight.action}* | Confidence: {confidence_bar} ({insight.confidence:.0%})")
                formatted.append("---")
        
        # Team insights
        if insights['team_insights']:
            formatted.append("\n## 🏆 Team Insights\n")
            for insight in insights['team_insights'][:5]:
                formatted.append(f"### {insight.title}")
                formatted.append(f"**{insight.description}**")
                formatted.append(f"*Recommendation: {insight.recommendation}*")
                formatted.append("---")
        
        # Market insights
        if insights['market_insights']:
            formatted.append("\n## 📈 Market Intelligence\n")
            for insight in insights['market_insights'][:5]:
                priority_emoji = "🔴" if insight.priority == "HIGH" else "🟡" if insight.priority == "MEDIUM" else "🟢"
                formatted.append(f"### {priority_emoji} {insight.title}")
                formatted.append(f"**{insight.description}**")
                formatted.append(f"*Action: {insight.action}*")
                formatted.append("---")
        
        return "\n".join(formatted)
    
    def get_top_recommendations(self, insights: Dict[str, List], limit: int = 5) -> List[PlayerInsight]:
        """Get top player recommendations across all categories"""
        all_player_insights = insights['player_insights']
        
        # Filter for actionable insights
        actionable = [
            insight for insight in all_player_insights 
            if insight.action in ['STRONG_BUY', 'CONSIDER_BUYING', 'BUY_BEFORE_RISE', 'DIFFERENTIAL_PICK']
        ]
        
        # Sort by priority and confidence
        top_recommendations = sorted(
            actionable,
            key=lambda x: (x.priority == 'HIGH', x.confidence),
            reverse=True
        )[:limit]
        
        return top_recommendations

print("✅ Intelligent Insights Engine created successfully!")
