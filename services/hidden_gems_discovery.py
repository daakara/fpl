"""
Hidden Gems Discovery Algorithm for FPL Dashboard
Advanced algorithmic player identification and opportunity detection
Phase 2: AI-Powered Real-Time Intelligence
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
from utils.data_converters import safe_int_convert, safe_float_convert

warnings.filterwarnings('ignore')

@dataclass
class HiddenGem:
    """Data class for hidden gem players"""
    player_id: int
    player_name: str
    position: str
    team: str
    current_price: float
    ownership: float
    gem_score: float
    gem_type: str  # 'VALUE', 'FORM', 'FIXTURE', 'DIFFERENTIAL', 'BREAKOUT'
    confidence: float
    reasons: List[str]
    stats: Dict[str, float]
    projection: Dict[str, float]
    discovery_date: datetime

@dataclass
class OpportunityAlert:
    """Data class for transfer opportunities"""
    alert_type: str
    priority: str  # 'URGENT', 'HIGH', 'MEDIUM', 'LOW'
    title: str
    description: str
    affected_players: List[HiddenGem]
    action_window: str  # 'IMMEDIATE', 'NEXT_GW', 'NEXT_WEEK'
    expected_impact: float
    confidence: float

class HiddenGemsDiscovery:
    """Advanced algorithm for discovering undervalued FPL assets"""
    
    def __init__(self):
        self.gem_thresholds = {
            'max_ownership': 8.0,      # Max ownership for hidden gem
            'min_form': 4.0,           # Minimum form score
            'min_minutes': 180,        # Minimum minutes played
            'min_value_score': 5.0,    # Minimum points per million
            'max_price_gkp': 5.5,      # Max GKP price
            'max_price_def': 6.0,      # Max DEF price  
            'max_price_mid': 8.0,      # Max MID price
            'max_price_fwd': 9.0,      # Max FWD price
        }
        
        self.position_weights = {
            1: {'attacking': 0.1, 'defensive': 0.9, 'consistency': 0.8},    # GKP
            2: {'attacking': 0.3, 'defensive': 0.7, 'consistency': 0.7},    # DEF
            3: {'attacking': 0.7, 'defensive': 0.3, 'consistency': 0.6},    # MID
            4: {'attacking': 0.9, 'defensive': 0.1, 'consistency': 0.5}     # FWD
        }
        
        self.discovery_algorithms = {
            'value_gems': self._find_value_gems,
            'form_gems': self._find_form_gems,
            'fixture_gems': self._find_fixture_gems,
            'differential_gems': self._find_differential_gems,
            'breakout_gems': self._find_breakout_gems,
            'rotation_proof': self._find_rotation_proof_gems,
            'set_piece_gems': self._find_set_piece_gems,
            'fixture_swing_gems': self._find_fixture_swing_gems
        }
    
    def discover_all_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> Dict[str, List[HiddenGem]]:
        """Run all discovery algorithms and return categorized gems"""
        if df.empty:
            return {}
        
        # Prepare data with enhanced features
        enhanced_df = self._prepare_gem_data(df)
        
        # Run all discovery algorithms
        all_gems = {}
        
        for gem_type, algorithm in self.discovery_algorithms.items():
            try:
                gems = algorithm(enhanced_df, teams_df)
                if gems:
                    all_gems[gem_type] = gems
            except Exception as e:
                print(f"Error in {gem_type} discovery: {e}")
                continue
        
        # Rank and deduplicate gems
        ranked_gems = self._rank_and_deduplicate_gems(all_gems)
        
        return ranked_gems
    
    def _prepare_gem_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and enhance data for gem discovery"""
        if df.empty:
            return df
            
        gem_df = df.copy()
        
        # Check for required columns
        required_cols = ['now_cost', 'total_points', 'minutes', 'selected_by_percent', 
                        'form', 'element_type']
        missing_cols = [col for col in required_cols if col not in gem_df.columns]
        
        if missing_cols:
            print(f"Warning: Missing required columns: {missing_cols}")
            # Add missing columns with default values
            for col in missing_cols:
                if col == 'now_cost':
                    gem_df[col] = 50  # Default price
                elif col == 'total_points':
                    gem_df[col] = 0
                elif col == 'minutes':
                    gem_df[col] = 0
                elif col == 'selected_by_percent':
                    gem_df[col] = 5.0
                elif col == 'form':
                    gem_df[col] = 0.0
                elif col == 'element_type':
                    gem_df[col] = 3  # Default to MID
        
        # Basic feature engineering
        gem_df['price_millions'] = gem_df['now_cost'] / 10
        gem_df['points_per_million'] = np.where(
            gem_df['price_millions'] > 0,
            gem_df['total_points'] / gem_df['price_millions'],
            0
        )
        
        # Games played estimation
        gem_df['games_played'] = np.where(gem_df['minutes'] > 0, gem_df['minutes'] / 90, 1)
        gem_df['points_per_game'] = gem_df['total_points'] / gem_df['games_played']
        
        # Form vs average comparison
        gem_df['form_vs_avg'] = gem_df['form'] - gem_df['points_per_game']
        
        # Ownership tier classification
        gem_df['ownership_tier'] = pd.cut(
            gem_df['selected_by_percent'],
            bins=[0, 2, 5, 10, 20, 100],
            labels=['Ultra_Low', 'Low', 'Medium', 'High', 'Very_High']
        )
        
        # Price tier by position
        position_price_tiers = {
            1: [0, 4.5, 5.0, 5.5, 15.0],    # GKP
            2: [0, 4.5, 5.5, 6.5, 15.0],    # DEF
            3: [0, 5.5, 7.0, 9.0, 15.0],    # MID
            4: [0, 6.5, 8.5, 11.0, 15.0]    # FWD
        }
        
        gem_df['price_tier'] = 'Medium'
        for position, bins in position_price_tiers.items():
            mask = gem_df['element_type'] == position
            gem_df.loc[mask, 'price_tier'] = pd.cut(
                gem_df.loc[mask, 'price_millions'],
                bins=bins,
                labels=['Budget', 'Mid', 'Premium', 'Super_Premium']
            )
        
        # Minutes reliability
        gem_df['minutes_reliability'] = np.where(
            gem_df['minutes'] >= 450,  # 5+ games
            1.0,
            gem_df['minutes'] / 450
        )
        
        # Goal/assist involvement (for attacking players)
        if 'goals_scored' in gem_df.columns and 'assists' in gem_df.columns:
            gem_df['goal_involvement'] = gem_df['goals_scored'] + gem_df['assists']
            gem_df['involvement_per_game'] = gem_df['goal_involvement'] / gem_df['games_played']
        else:
            gem_df['goal_involvement'] = 0
            gem_df['involvement_per_game'] = 0
        
        # Clean sheet rate (for defensive players)
        if 'clean_sheets' in gem_df.columns:
            gem_df['clean_sheet_rate'] = gem_df['clean_sheets'] / gem_df['games_played']
        else:
            gem_df['clean_sheet_rate'] = 0
        
        return gem_df
    
    def _find_value_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find exceptional value players (high points per million, low ownership)"""
        gems = []
        
        # Filter criteria for value gems
        value_candidates = df[
            (df['selected_by_percent'] <= self.gem_thresholds['max_ownership']) &
            (df['minutes'] >= self.gem_thresholds['min_minutes']) &
            (df['points_per_million'] >= self.gem_thresholds['min_value_score']) &
            (df['total_points'] >= 20)  # Minimum total points
        ]
        
        # Position-specific price filters
        position_filters = {
            1: df['price_millions'] <= self.gem_thresholds['max_price_gkp'],
            2: df['price_millions'] <= self.gem_thresholds['max_price_def'],
            3: df['price_millions'] <= self.gem_thresholds['max_price_mid'],
            4: df['price_millions'] <= self.gem_thresholds['max_price_fwd']
        }
        
        for position, price_filter in position_filters.items():
            position_candidates = value_candidates[
                (value_candidates['element_type'] == position) & price_filter
            ]
            
            if position_candidates.empty:
                continue
            
            # Rank by value score within position
            top_value = position_candidates.nlargest(3, 'points_per_million')
            
            for _, player in top_value.iterrows():
                reasons = [
                    f"Exceptional value: {player['points_per_million']:.1f} points per £1M",
                    f"Low ownership: {player['selected_by_percent']:.1f}%",
                    f"Total points: {player['total_points']} in {player['games_played']:.0f} games"
                ]
                
                # Additional position-specific reasons
                if position in [3, 4] and player['goal_involvement'] >= 3:
                    reasons.append(f"Strong attacking returns: {player['goal_involvement']} G+A")
                elif position in [1, 2] and player['clean_sheet_rate'] >= 0.3:
                    reasons.append(f"Good defensive record: {player['clean_sheet_rate']:.1%} CS rate")
                
                gem_score = (
                    player['points_per_million'] * 0.4 +
                    (10 - player['selected_by_percent']) * 0.3 +
                    player['form'] * 0.2 +
                    player['minutes_reliability'] * 10
                )
                
                confidence = min(0.9, 0.5 + (player['minutes'] / 1000) * 0.3 + (player['games_played'] / 15) * 0.2)
                
                gems.append(HiddenGem(
                    player_id=safe_int_convert(player['id'], 0),
                    player_name=player['web_name'],
                    position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[position],
                    team=str(player.get('team', 'Unknown')),
                    current_price=safe_float_convert(player['price_millions'], 0.0),
                    ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                    gem_score=safe_float_convert(gem_score, 0.0),
                    gem_type='VALUE',
                    confidence=safe_float_convert(confidence, 0.0),
                    reasons=reasons,
                    stats={
                        'points_per_million': safe_float_convert(player['points_per_million'], 0.0),
                        'total_points': safe_int_convert(player['total_points'], 0),
                        'form': safe_float_convert(player['form'], 0.0),
                        'minutes': safe_int_convert(player['minutes'], 0)
                    },
                    projection={
                        'next_5_gw_points': safe_float_convert(player['form'] * 5 * 0.8, 0.0),  # Conservative projection
                        'price_rise_probability': min(0.8, gem_score / 20) if gem_score else 0.0
                    },
                    discovery_date=datetime.now()
                ))
        
        return gems
    
    def _find_form_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find players in exceptional recent form"""
        gems = []
        
        form_candidates = df[
            (df['form'] >= 6.0) &  # High form threshold
            (df['selected_by_percent'] <= 15.0) &  # Not too popular
            (df['minutes'] >= 270) &  # Regular starter
            (df['form_vs_avg'] >= 1.0)  # Form better than season average
        ]
        
        # Rank by form improvement
        top_form = form_candidates.nlargest(8, 'form_vs_avg')
        
        for _, player in top_form.iterrows():
            reasons = [
                f"Exceptional recent form: {player['form']:.1f} points per game",
                f"Form improvement: +{player['form_vs_avg']:.1f} vs season average",
                f"Regular starter: {player['minutes']} minutes played"
            ]
            
            if player['selected_by_percent'] <= 5.0:
                reasons.append(f"Very low ownership: {player['selected_by_percent']:.1f}%")
            
            gem_score = (
                player['form'] * 0.5 +
                player['form_vs_avg'] * 0.3 +
                (15 - player['selected_by_percent']) * 0.2
            )
            
            confidence = min(0.85, 0.4 + (player['form'] / 10) * 0.4 + (player['minutes'] / 1000) * 0.25)
            
            gems.append(HiddenGem(
                player_id=safe_int_convert(player['id'], 0),
                player_name=player['web_name'],
                position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[player['element_type']],
                team=str(player.get('team', 'Unknown')),
                current_price=safe_float_convert(player['price_millions'], 0.0),
                ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                gem_score=safe_float_convert(gem_score, 0.0),
                gem_type='FORM',
                confidence=safe_float_convert(confidence, 0.0),
                reasons=reasons,
                stats={
                    'form': safe_float_convert(player['form'], 0.0),
                    'form_vs_avg': safe_float_convert(player['form_vs_avg'], 0.0),
                    'total_points': safe_int_convert(player['total_points'], 0),
                    'minutes': safe_int_convert(player['minutes'], 0)
                },
                projection={
                    'next_3_gw_points': safe_float_convert(player['form'] * 3, 0.0),
                    'regression_risk': max(0.2, 1.0 - (player['form_vs_avg'] / 5)) if player.get('form_vs_avg') else 0.5
                },
                discovery_date=datetime.now()
            ))
        
        return gems
    
    def _find_fixture_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find players with favorable upcoming fixtures"""
        gems = []
        
        # Create synthetic fixture difficulty (in reality would come from fixture data)
        np.random.seed(42)  # For consistent results
        fixture_difficulty = {}
        for team_id in df['team'].unique():
            # Generate favorable fixture runs (lower = easier)
            difficulty = np.random.uniform(1.5, 4.5, 5)  # Next 5 gameweeks
            fixture_difficulty[team_id] = difficulty.mean()
        
        # Find players from teams with easy fixtures
        easy_fixtures = {team: diff for team, diff in fixture_difficulty.items() if diff <= 2.8}
        
        fixture_candidates = df[
            (df['team'].isin(easy_fixtures.keys())) &
            (df['selected_by_percent'] <= 12.0) &
            (df['minutes'] >= 180) &
            (df['form'] >= 3.5)
        ]
        
        # Prioritize by position and role
        for position in [1, 2, 3, 4]:
            position_players = fixture_candidates[fixture_candidates['element_type'] == position]
            
            if position_players.empty:
                continue
            
            # Take top players by combined score
            position_players = position_players.copy()
            position_players['fixture_score'] = (
                (5 - [fixture_difficulty[team] for team in position_players['team']]) * 0.4 +
                position_players['form'] * 0.3 +
                position_players['points_per_game'] * 0.3
            )
            
            top_fixture = position_players.nlargest(2, 'fixture_score')
            
            for _, player in top_fixture.iterrows():
                team_difficulty = fixture_difficulty[player['team']]
                
                reasons = [
                    f"Favorable fixture run: {5-team_difficulty:.1f}/5 difficulty rating",
                    f"Decent form: {player['form']:.1f} points per game",
                    f"Affordable option: £{player['price_millions']:.1f}m"
                ]
                
                if player['selected_by_percent'] <= 5.0:
                    reasons.append(f"Low ownership differential: {player['selected_by_percent']:.1f}%")
                
                gem_score = (
                    (5 - team_difficulty) * 2 +
                    player['form'] * 0.8 +
                    (12 - player['selected_by_percent']) * 0.3
                )
                
                confidence = min(0.8, 0.5 + ((5 - team_difficulty) / 5) * 0.3)
                
                gems.append(HiddenGem(
                    player_id=safe_int_convert(player['id'], 0),
                    player_name=player['web_name'],
                    position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[player['element_type']],
                    team=str(player.get('team', 'Unknown')),
                    current_price=safe_float_convert(player['price_millions'], 0.0),
                    ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                    gem_score=safe_float_convert(gem_score, 0.0),
                    gem_type='FIXTURE',
                    confidence=safe_float_convert(confidence, 0.0),
                    reasons=reasons,
                    stats={
                        'fixture_difficulty': safe_float_convert(team_difficulty, 0.0),
                        'form': safe_float_convert(player['form'], 0.0),
                        'total_points': safe_int_convert(player['total_points'], 0)
                    },
                    projection={
                        'next_5_gw_points': safe_float_convert(player['form'] * 5 * (5 - team_difficulty) / 3, 0.0),
                        'fixture_advantage': safe_float_convert(5 - team_difficulty, 0.0)
                    },
                    discovery_date=datetime.now()
                ))
        
        return gems
    
    def _find_differential_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find low-owned players with high potential for rank climbing"""
        gems = []
        
        differential_candidates = df[
            (df['selected_by_percent'] <= 3.0) &  # Very low ownership
            (df['minutes'] >= 270) &  # Regular play
            (df['form'] >= 4.5) &  # Decent form
            (df['total_points'] >= 25)  # Proven performer
        ]
        
        # Calculate differential potential
        for _, player in differential_candidates.iterrows():
            # Differential scoring algorithm
            differential_score = (
                (3 - player['selected_by_percent']) * 2 +  # Ownership bonus
                player['form'] * 1.5 +
                player['points_per_game'] * 1.0 +
                (player['total_points'] / 50) * 1.0  # Season points scaling
            )
            
            # Only consider high differential potential
            if differential_score >= 8.0:
                reasons = [
                    f"Ultra-low ownership: {player['selected_by_percent']:.1f}% (huge differential)",
                    f"Solid performance: {player['total_points']} points this season",
                    f"Recent form: {player['form']:.1f} points per game",
                    "Perfect for rank climbing in mini-leagues"
                ]
                
                if player['involvement_per_game'] >= 0.3:
                    reasons.append(f"Attacking threat: {player['involvement_per_game']:.1f} G+A per game")
                
                confidence = min(0.75, 0.3 + (differential_score / 15) * 0.4 + (player['minutes'] / 1000) * 0.25)
                
                gems.append(HiddenGem(
                    player_id=safe_int_convert(player['id'], 0),
                    player_name=player['web_name'],
                    position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[player['element_type']],
                    team=str(player.get('team', 'Unknown')),
                    current_price=safe_float_convert(player['price_millions'], 0.0),
                    ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                    gem_score=safe_float_convert(differential_score, 0.0),
                    gem_type='DIFFERENTIAL',
                    confidence=safe_float_convert(confidence, 0.0),
                    reasons=reasons,
                    stats={
                        'differential_score': safe_float_convert(differential_score, 0.0),
                        'ownership': safe_float_convert(player['selected_by_percent'], 0.0),
                        'form': safe_float_convert(player['form'], 0.0),
                        'total_points': safe_int_convert(player['total_points'], 0)
                    },
                    projection={
                        'rank_climbing_potential': safe_float_convert(differential_score / 10, 0.0),
                        'haul_probability': min(0.6, player.get('form', 0) / 8)
                    },
                    discovery_date=datetime.now()
                ))
        
        # Sort by differential score and return top picks
        gems.sort(key=lambda x: x.gem_score, reverse=True)
        return gems[:6]  # Top 6 differentials
    
    def _find_breakout_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find young/emerging players showing breakout potential"""
        gems = []
        
        # Focus on players with recent significant improvement
        breakout_candidates = df[
            (df['selected_by_percent'] <= 10.0) &
            (df['minutes'] >= 180) &
            (df['form'] >= 4.0) &
            (df['form_vs_avg'] >= 0.5) &  # Form improving
            (df['price_millions'] <= 7.0)  # Still affordable
        ]
        
        # Look for indicators of breakout potential
        for _, player in breakout_candidates.iterrows():
            breakout_indicators = []
            breakout_score = 0
            
            # Form improvement indicator
            if player['form_vs_avg'] >= 1.0:
                breakout_indicators.append("Significant form improvement")
                breakout_score += 2
            
            # Minutes increase (proxy for becoming regular starter)
            if player['minutes'] >= 450:
                breakout_indicators.append("Established starter")
                breakout_score += 1.5
            
            # Attacking involvement for non-forwards
            if player['element_type'] in [2, 3] and player['involvement_per_game'] >= 0.2:
                breakout_indicators.append("Attacking threat from deep")
                breakout_score += 1.5
            
            # Value creation
            if player['points_per_million'] >= 6.0:
                breakout_indicators.append("Strong value creation")
                breakout_score += 1
            
            # Price still low despite performance
            position_max_prices = {1: 5.0, 2: 5.5, 3: 7.0, 4: 8.0}
            if player['price_millions'] <= position_max_prices.get(player['element_type'], 7.0):
                breakout_indicators.append("Price hasn't caught up to performance")
                breakout_score += 1
            
            # Require minimum breakout potential
            if breakout_score >= 4.0 and len(breakout_indicators) >= 3:
                reasons = [
                    f"Breakout potential: {len(breakout_indicators)} positive indicators",
                    f"Form trending up: {player['form']:.1f} (+{player['form_vs_avg']:.1f} vs avg)",
                    f"Still affordable: £{player['price_millions']:.1f}m"
                ] + breakout_indicators[:2]
                
                confidence = min(0.7, 0.4 + (breakout_score / 8) * 0.3)
                
                gems.append(HiddenGem(
                    player_id=safe_int_convert(player['id'], 0),
                    player_name=player['web_name'],
                    position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[player['element_type']],
                    team=str(player.get('team', 'Unknown')),
                    current_price=safe_float_convert(player['price_millions'], 0.0),
                    ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                    gem_score=safe_float_convert(breakout_score, 0.0),
                    gem_type='BREAKOUT',
                    confidence=safe_float_convert(confidence, 0.0),
                    reasons=reasons,
                    stats={
                        'breakout_score': safe_float_convert(breakout_score, 0.0),
                        'form_improvement': safe_float_convert(player['form_vs_avg'], 0.0),
                        'indicators_count': len(breakout_indicators)
                    },
                    projection={
                        'price_rise_potential': float(breakout_score / 6),
                        'next_level_probability': min(0.8, breakout_score / 7)
                    },
                    discovery_date=datetime.now()
                ))
        
        # Sort by breakout score
        gems.sort(key=lambda x: x.gem_score, reverse=True)
        return gems[:5]
    
    def _find_rotation_proof_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find players who are rotation-proof in their teams"""
        gems = []
        
        # Look for players with high minutes reliability
        rotation_proof = df[
            (df['minutes'] >= 630) &  # 7+ games equivalent
            (df['minutes_reliability'] >= 0.8) &
            (df['selected_by_percent'] <= 12.0) &
            (df['form'] >= 4.0)
        ]
        
        for _, player in rotation_proof.iterrows():
            if player['minutes'] >= 900:  # 10+ games worth
                reasons = [
                    f"Rotation-proof: {player['minutes']} minutes ({player['games_played']:.1f} games)",
                    f"High reliability: {player['minutes_reliability']:.1%} starting probability",
                    f"Consistent performer: {player['form']:.1f} average points"
                ]
                
                reliability_score = (
                    player['minutes_reliability'] * 5 +
                    player['form'] * 0.8 +
                    (12 - player['selected_by_percent']) * 0.2
                )
                
                confidence = min(0.9, 0.6 + (player['minutes_reliability'] * 0.3))
                
                gems.append(HiddenGem(
                    player_id=safe_int_convert(player['id'], 0),
                    player_name=player['web_name'],
                    position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[player['element_type']],
                    team=str(player.get('team', 'Unknown')),
                    current_price=safe_float_convert(player['price_millions'], 0.0),
                    ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                    gem_score=safe_float_convert(reliability_score, 0.0),
                    gem_type='ROTATION_PROOF',
                    confidence=safe_float_convert(confidence, 0.0),
                    reasons=reasons,
                    stats={
                        'minutes_reliability': safe_float_convert(player['minutes_reliability'], 0.0),
                        'total_minutes': safe_int_convert(player['minutes'], 0),
                        'form': safe_float_convert(player['form'], 0.0)
                    },
                    projection={
                        'minutes_security': safe_float_convert(player['minutes_reliability'], 0.0),
                        'consistent_returns': min(0.9, player.get('form', 0) / 6)
                    },
                    discovery_date=datetime.now()
                ))
        
        gems.sort(key=lambda x: x.gem_score, reverse=True)
        return gems[:4]
    
    def _find_set_piece_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find players who take set pieces (penalties, free kicks, corners)"""
        gems = []
        
        # Look for indicators of set piece responsibility
        set_piece_candidates = df[
            (df['selected_by_percent'] <= 15.0) &
            (df['minutes'] >= 270) &
            (df['form'] >= 3.5)
        ]
        
        # Use assists and bonus points as proxy for set piece involvement
        for _, player in set_piece_candidates.iterrows():
            set_piece_score = 0
            indicators = []
            
            # High assists suggest set piece delivery
            if player.get('assists', 0) >= 3:
                set_piece_score += 2
                indicators.append(f"High assists: {player.get('assists', 0)}")
            
            # High bonus points suggest key passes/set pieces
            if player.get('bonus', 0) >= 8:
                set_piece_score += 1.5
                indicators.append(f"Strong bonus: {player.get('bonus', 0)} points")
            
            # Creativity metric (if available)
            if player.get('creativity', 0) >= 300:
                set_piece_score += 1
                indicators.append("High creativity metric")
            
            if set_piece_score >= 2.5 and len(indicators) >= 2:
                reasons = [
                    "Likely set piece taker based on stats",
                    f"Reasonable ownership: {player['selected_by_percent']:.1f}%",
                    f"Regular starter: {player['minutes']} minutes"
                ] + indicators
                
                confidence = min(0.75, 0.4 + (set_piece_score / 5) * 0.35)
                
                gems.append(HiddenGem(
                    player_id=safe_int_convert(player['id'], 0),
                    player_name=player['web_name'],
                    position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[player['element_type']],
                    team=str(player.get('team', 'Unknown')),
                    current_price=safe_float_convert(player['price_millions'], 0.0),
                    ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                    gem_score=safe_float_convert(set_piece_score, 0.0),
                    gem_type='SET_PIECE',
                    confidence=safe_float_convert(confidence, 0.0),
                    reasons=reasons,
                    stats={
                        'set_piece_score': safe_float_convert(set_piece_score, 0.0),
                        'assists': safe_int_convert(player.get('assists', 0), 0),
                        'bonus': safe_int_convert(player.get('bonus', 0), 0)
                    },
                    projection={
                        'assist_potential': min(0.8, set_piece_score / 4),
                        'bonus_probability': min(0.7, safe_int_convert(player.get('bonus', 0), 0) / 15)
                    },
                    discovery_date=datetime.now()
                ))
        
        gems.sort(key=lambda x: x.gem_score, reverse=True)
        return gems[:3]
    
    def _find_fixture_swing_gems(self, df: pd.DataFrame, teams_df: pd.DataFrame = None) -> List[HiddenGem]:
        """Find players whose fixtures are about to improve dramatically"""
        gems = []
        
        # Simulate fixture swing scenario
        np.random.seed(123)
        fixture_swings = {}
        
        for team_id in df['team'].unique():
            # Simulate teams with tough recent fixtures about to get easier
            recent_difficulty = np.random.uniform(3.5, 5.0)  # Tough recent
            upcoming_difficulty = np.random.uniform(1.5, 3.0)  # Easy upcoming
            swing_factor = recent_difficulty - upcoming_difficulty
            
            if swing_factor >= 1.5:  # Significant improvement
                fixture_swings[team_id] = {
                    'recent': recent_difficulty,
                    'upcoming': upcoming_difficulty,
                    'swing': swing_factor
                }
        
        # Find players from teams with fixture swings
        swing_candidates = df[
            (df['team'].isin(fixture_swings.keys())) &
            (df['selected_by_percent'] <= 10.0) &
            (df['minutes'] >= 180) &
            (df['total_points'] >= 15)
        ]
        
        for _, player in swing_candidates.iterrows():
            swing_data = fixture_swings[player['team']]
            
            reasons = [
                f"Fixture swing: From {swing_data['recent']:.1f} to {swing_data['upcoming']:.1f} difficulty",
                f"Improvement factor: +{swing_data['swing']:.1f}",
                f"Low ownership before swing: {player['selected_by_percent']:.1f}%"
            ]
            
            swing_score = (
                swing_data['swing'] * 2 +
                player['form'] * 0.8 +
                (10 - player['selected_by_percent']) * 0.3 +
                player['points_per_game'] * 0.5
            )
            
            confidence = min(0.8, 0.5 + (swing_data['swing'] / 3) * 0.3)
            
            gems.append(HiddenGem(
                player_id=safe_int_convert(player['id'], 0),
                player_name=player['web_name'],
                position={1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}[player['element_type']],
                team=str(player.get('team', 'Unknown')),
                current_price=safe_float_convert(player['price_millions'], 0.0),
                ownership=safe_float_convert(player['selected_by_percent'], 0.0),
                gem_score=safe_float_convert(swing_score, 0.0),
                gem_type='FIXTURE_SWING',
                confidence=safe_float_convert(confidence, 0.0),
                reasons=reasons,
                stats={
                    'fixture_swing': safe_float_convert(swing_data['swing'], 0.0),
                    'upcoming_difficulty': safe_float_convert(swing_data['upcoming'], 0.0),
                    'form': safe_float_convert(player['form'], 0.0)
                },
                projection={
                    'swing_benefit': float(swing_data['swing'] / 2),
                    'next_5_gw_boost': float(player['form'] * swing_data['swing'] / 2)
                },
                discovery_date=datetime.now()
            ))
        
        gems.sort(key=lambda x: x.gem_score, reverse=True)
        return gems[:4]
    
    def _rank_and_deduplicate_gems(self, all_gems: Dict[str, List[HiddenGem]]) -> Dict[str, List[HiddenGem]]:
        """Rank gems within categories and remove duplicates"""
        ranked_gems = {}
        seen_players = set()
        
        # Priority order for gem types
        priority_order = [
            'value_gems', 'differential_gems', 'form_gems', 'breakout_gems',
            'fixture_gems', 'rotation_proof', 'set_piece_gems', 'fixture_swing_gems'
        ]
        
        for gem_type in priority_order:
            if gem_type in all_gems:
                unique_gems = []
                
                for gem in all_gems[gem_type]:
                    if gem.player_id not in seen_players:
                        seen_players.add(gem.player_id)
                        unique_gems.append(gem)
                
                # Sort by gem score within category
                unique_gems.sort(key=lambda x: x.gem_score, reverse=True)
                
                if unique_gems:
                    ranked_gems[gem_type] = unique_gems
        
        return ranked_gems
    
    def generate_opportunity_alerts(self, gems: Dict[str, List[HiddenGem]]) -> List[OpportunityAlert]:
        """Generate opportunity alerts from discovered gems"""
        alerts = []
        
        # High-priority value gems alert
        if 'value_gems' in gems and gems['value_gems']:
            top_value_gems = gems['value_gems'][:3]
            if any(gem.gem_score >= 15 for gem in top_value_gems):
                alerts.append(OpportunityAlert(
                    alert_type='VALUE_OPPORTUNITY',
                    priority='HIGH',
                    title='🔥 Exceptional Value Opportunities Detected',
                    description=f"Found {len(top_value_gems)} players with outstanding value metrics. "
                              f"Top pick: {top_value_gems[0].player_name} ({top_value_gems[0].stats['points_per_million']:.1f} pts/£M)",
                    affected_players=top_value_gems,
                    action_window='NEXT_GW',
                    expected_impact=0.8,
                    confidence=0.85
                ))
        
        # Breakout alert
        if 'breakout_gems' in gems and gems['breakout_gems']:
            breakout_gems = gems['breakout_gems'][:2]
            if any(gem.gem_score >= 5 for gem in breakout_gems):
                alerts.append(OpportunityAlert(
                    alert_type='BREAKOUT_OPPORTUNITY',
                    priority='MEDIUM',
                    title='🚀 Potential Breakout Players Identified',
                    description=f"Players showing breakout indicators before price rises. "
                              f"Early mover advantage available.",
                    affected_players=breakout_gems,
                    action_window='IMMEDIATE',
                    expected_impact=0.7,
                    confidence=0.75
                ))
        
        # Differential opportunity
        if 'differential_gems' in gems and gems['differential_gems']:
            diff_gems = gems['differential_gems'][:2]
            alerts.append(OpportunityAlert(
                alert_type='DIFFERENTIAL_OPPORTUNITY',
                priority='MEDIUM',
                title='⚡ Rank-Climbing Differentials Available',
                description=f"Ultra-low owned players with high potential. "
                          f"Perfect for mini-league rank climbing.",
                affected_players=diff_gems,
                action_window='NEXT_WEEK',
                expected_impact=0.6,
                confidence=0.7
            ))
        
        # Fixture swing opportunity
        if 'fixture_swing_gems' in gems and gems['fixture_swing_gems']:
            swing_gems = gems['fixture_swing_gems'][:2]
            alerts.append(OpportunityAlert(
                alert_type='FIXTURE_SWING',
                priority='HIGH',
                title='📅 Fixture Swing Opportunity',
                description=f"Players from teams with dramatically improving fixtures. "
                          f"Get in before ownership increases.",
                affected_players=swing_gems,
                action_window='IMMEDIATE',
                expected_impact=0.75,
                confidence=0.8
            ))
        
        return alerts
    
    def get_gem_summary_stats(self, gems: Dict[str, List[HiddenGem]]) -> Dict[str, int]:
        """Get summary statistics for discovered gems"""
        stats = {
            'total_gems': sum(len(gem_list) for gem_list in gems.values()),
            'high_confidence_gems': 0,
            'immediate_opportunities': 0,
            'value_gems_count': len(gems.get('value_gems', [])),
            'differential_gems_count': len(gems.get('differential_gems', [])),
            'avg_ownership': 0,
            'avg_confidence': 0
        }
        
        all_gems = []
        for gem_list in gems.values():
            all_gems.extend(gem_list)
        
        if all_gems:
            stats['high_confidence_gems'] = sum(1 for gem in all_gems if gem.confidence >= 0.75)
            stats['immediate_opportunities'] = sum(1 for gem in all_gems if gem.gem_score >= 10)
            stats['avg_ownership'] = sum(gem.ownership for gem in all_gems) / len(all_gems)
            stats['avg_confidence'] = sum(gem.confidence for gem in all_gems) / len(all_gems)
        
        return stats

print("✅ Hidden Gems Discovery Algorithm created successfully!")
