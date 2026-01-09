"""
Best Team Generator - Optimal FPL Squad Selection

Generates the best possible 15-player FPL squad based on:
- Budget constraint (£100m)
- Position limits (2 GK, 5 DEF, 5 MID, 3 FWD)
- Max 3 players per team
- Form, points, and value metrics

Example:
    >>> generator = BestTeamGenerator()
    >>> best_squad = generator.generate_best_team(players_df)
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
from utils.error_handling import logger


class BestTeamGenerator:
    """
    Generate optimal FPL squad within constraints.
    
    Constraints:
    - Budget: £100.0m
    - Positions: 2 GKP, 5 DEF, 5 MID, 3 FWD
    - Max 3 players from same team
    """
    
    BUDGET = 100.0  # Million
    POSITIONS = {
        'GKP': 2,
        'DEF': 5,
        'MID': 5,
        'FWD': 3
    }
    MAX_PER_TEAM = 3
    
    def __init__(self):
        """Initialize the best team generator."""
        self.logger = logger
    
    def generate_best_team(
        self,
        df: pd.DataFrame,
        strategy: str = 'balanced'
    ) -> Dict:
        """
        Generate the best possible FPL squad.
        
        Args:
            df: DataFrame with player data
            strategy: 'balanced', 'form', 'value', or 'points'
            
        Returns:
            Dict with:
                - squad: List of 15 player dicts
                - total_cost: Total squad cost
                - formation: Best starting XI formation
                - bench: Best bench players
                - stats: Squad statistics
        """
        try:
            # Validate data
            required_cols = ['web_name', 'position', 'now_cost', 'team', 'total_points', 'form']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing required columns. Need: {required_cols}")
            
            # Calculate selection score based on strategy
            df = df.copy()
            df['selection_score'] = self._calculate_selection_score(df, strategy)
            
            # Sort by selection score
            df = df.sort_values('selection_score', ascending=False)
            
            # Select best squad within constraints
            squad = self._select_optimal_squad(df)
            
            if not squad:
                return self._get_empty_result()
            
            # Calculate squad statistics
            squad_df = pd.DataFrame(squad)
            total_cost = squad_df['now_cost'].sum() / 10  # Convert to millions
            
            # Determine best starting XI and bench
            starting_xi, bench, formation = self._select_starting_xi(squad)
            
            # Calculate statistics
            stats = self._calculate_squad_stats(squad_df, starting_xi, bench)
            
            return {
                'squad': squad,
                'total_cost': round(total_cost, 1),
                'starting_xi': starting_xi,
                'bench': bench,
                'formation': formation,
                'stats': stats,
                'strategy': strategy
            }
            
        except Exception as e:
            self.logger.error(f"Error generating best team: {e}")
            return self._get_empty_result()
    
    def _calculate_selection_score(
        self,
        df: pd.DataFrame,
        strategy: str
    ) -> pd.Series:
        """
        Calculate selection score for each player based on strategy.
        
        Args:
            df: Player DataFrame
            strategy: Selection strategy
            
        Returns:
            Series with selection scores
        """
        # Ensure numeric types
        points = pd.to_numeric(df['total_points'], errors='coerce').fillna(0)
        form = pd.to_numeric(df['form'], errors='coerce').fillna(0)
        cost = pd.to_numeric(df['now_cost'], errors='coerce').fillna(40) / 10  # To millions
        
        # Value score (points per million)
        value = points / cost.replace(0, 999)  # Avoid division by zero
        
        if strategy == 'form':
            # Prioritize in-form players
            return form * 20 + value
        elif strategy == 'value':
            # Prioritize value players
            return value * 2 + points * 0.1
        elif strategy == 'points':
            # Prioritize total points
            return points + value * 0.5
        else:  # balanced
            # Balanced approach
            return points * 0.4 + form * 5 + value * 0.6
    
    def _select_optimal_squad(self, df: pd.DataFrame) -> List[Dict]:
        """
        Select optimal 15-player squad within all constraints.
        
        Args:
            df: Sorted DataFrame by selection score
            
        Returns:
            List of 15 player dictionaries
        """
        squad = []
        remaining_budget = self.BUDGET * 10  # Convert to 0.1m units
        positions_needed = self.POSITIONS.copy()
        team_counts = {}
        
        for _, player in df.iterrows():
            # Check if position is still needed
            position = player['position']
            if positions_needed.get(position, 0) <= 0:
                continue
            
            # Check budget
            cost = float(player['now_cost'])
            if cost > remaining_budget:
                continue
            
            # Check team limit
            team = player['team']
            if team_counts.get(team, 0) >= self.MAX_PER_TEAM:
                continue
            
            # Add player to squad
            squad.append({
                'web_name': player['web_name'],
                'position': position,
                'team': player.get('team_name', team),
                'now_cost': cost,
                'total_points': float(player.get('total_points', 0)),
                'form': float(player.get('form', 0)),
                'selection_score': float(player.get('selection_score', 0)),
                'selected_by_percent': float(player.get('selected_by_percent', 0))
            })
            
            # Update constraints
            remaining_budget -= cost
            positions_needed[position] -= 1
            team_counts[team] = team_counts.get(team, 0) + 1
            
            # Check if squad is complete
            if len(squad) == 15:
                break
        
        return squad
    
    def _select_starting_xi(
        self,
        squad: List[Dict]
    ) -> Tuple[List[Dict], List[Dict], str]:
        """
        Select best starting XI and bench from 15-player squad.
        
        Args:
            squad: 15-player squad
            
        Returns:
            Tuple of (starting_xi, bench, formation)
        """
        # Sort squad by selection score
        sorted_squad = sorted(squad, key=lambda x: x['selection_score'], reverse=True)
        
        # Separate by position
        by_position = {}
        for player in sorted_squad:
            pos = player['position']
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(player)
        
        # Select starting XI (must have at least 1 GK, 3 DEF, 2 MID, 1 FWD)
        starting_xi = []
        bench = []
        
        # Always start top GK
        if 'GKP' in by_position and len(by_position['GKP']) > 0:
            starting_xi.append(by_position['GKP'][0])
            bench.extend(by_position['GKP'][1:])
        
        # Determine best formation from available players
        formations = self._get_valid_formations()
        best_formation = self._find_best_formation(
            by_position, formations, starting_xi
        )
        
        return starting_xi, bench, best_formation
    
    def _get_valid_formations(self) -> List[Tuple[int, int, int]]:
        """
        Get list of valid FPL formations (DEF-MID-FWD).
        
        Returns:
            List of valid formations as (def, mid, fwd) tuples
        """
        return [
            (3, 4, 3), (3, 5, 2), (4, 3, 3), (4, 4, 2),
            (4, 5, 1), (5, 3, 2), (5, 4, 1)
        ]
    
    def _find_best_formation(
        self,
        by_position: Dict[str, List[Dict]],
        formations: List[Tuple[int, int, int]],
        starting_xi: List[Dict]
    ) -> str:
        """
        Find the best formation based on available players.
        
        Args:
            by_position: Players grouped by position
            formations: Valid formations
            starting_xi: Current starting XI (will be modified)
            
        Returns:
            Formation string (e.g., "3-4-3")
        """
        best_score = 0
        best_formation = "3-4-3"
        best_xi = starting_xi.copy()
        
        for def_count, mid_count, fwd_count in formations:
            # Check if we have enough players
            if (len(by_position.get('DEF', [])) < def_count or
                len(by_position.get('MID', [])) < mid_count or
                len(by_position.get('FWD', [])) < fwd_count):
                continue
            
            # Calculate formation score
            xi = starting_xi.copy()  # Start with GK
            
            # Add outfield players
            xi.extend(by_position['DEF'][:def_count])
            xi.extend(by_position['MID'][:mid_count])
            xi.extend(by_position['FWD'][:fwd_count])
            
            # Calculate total score
            score = sum(p['selection_score'] for p in xi)
            
            if score > best_score:
                best_score = score
                best_formation = f"{def_count}-{mid_count}-{fwd_count}"
                best_xi = xi
        
        # Update starting XI
        starting_xi.clear()
        starting_xi.extend(best_xi)
        
        # Set bench (remaining players not in starting XI)
        all_players = []
        for players in by_position.values():
            all_players.extend(players)
        
        bench_players = [p for p in all_players if p not in starting_xi]
        bench_players.sort(key=lambda x: x['selection_score'], reverse=True)
        
        return best_formation
    
    def _calculate_squad_stats(
        self,
        squad_df: pd.DataFrame,
        starting_xi: List[Dict],
        bench: List[Dict]
    ) -> Dict:
        """
        Calculate squad statistics.
        
        Args:
            squad_df: Squad DataFrame
            starting_xi: Starting XI players
            bench: Bench players
            
        Returns:
            Dict with squad statistics
        """
        starting_df = pd.DataFrame(starting_xi) if starting_xi else pd.DataFrame()
        
        return {
            'total_points': int(squad_df['total_points'].sum()),
            'avg_form': round(squad_df['form'].mean(), 2),
            'starting_xi_points': int(starting_df['total_points'].sum()) if len(starting_df) > 0 else 0,
            'bench_points': int(sum(p['total_points'] for p in bench)),
            'avg_ownership': round(squad_df['selected_by_percent'].mean(), 1),
            'team_distribution': squad_df.groupby('team').size().to_dict()
        }
    
    def _get_empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'squad': [],
            'total_cost': 0.0,
            'starting_xi': [],
            'bench': [],
            'formation': '3-4-3',
            'stats': {
                'total_points': 0,
                'avg_form': 0.0,
                'starting_xi_points': 0,
                'bench_points': 0,
                'avg_ownership': 0.0,
                'team_distribution': {}
            },
            'strategy': 'balanced'
        }
    
    def format_squad_display(self, result: Dict) -> str:
        """
        Format squad result for display.
        
        Args:
            result: Result from generate_best_team()
            
        Returns:
            Formatted string for display
        """
        if not result['squad']:
            return "❌ Could not generate a valid squad"
        
        lines = [
            f"✨ **Best FPL Squad** ({result['strategy'].title()} Strategy)",
            f"💰 **Total Cost:** £{result['total_cost']}m",
            f"⚽ **Formation:** {result['formation']}",
            f"📊 **Total Points:** {result['stats']['total_points']:,}",
            "",
            "**Starting XI:**"
        ]
        
        for i, player in enumerate(result['starting_xi'], 1):
            lines.append(
                f"{i}. {player['web_name']} ({player['position']}) - "
                f"£{player['now_cost']/10:.1f}m - {player['total_points']} pts"
            )
        
        lines.append("")
        lines.append("**Bench:**")
        for i, player in enumerate(result['bench'], 1):
            lines.append(
                f"{i}. {player['web_name']} ({player['position']}) - "
                f"£{player['now_cost']/10:.1f}m - {player['total_points']} pts"
            )
        
        return "\n".join(lines)


# Convenience function for direct use
def generate_best_team(df: pd.DataFrame, strategy: str = 'balanced') -> Dict:
    """
    Generate best FPL squad (convenience function).
    
    Args:
        df: Player DataFrame
        strategy: 'balanced', 'form', 'value', or 'points'
        
    Returns:
        Dict with squad details
    """
    generator = BestTeamGenerator()
    return generator.generate_best_team(df, strategy)
