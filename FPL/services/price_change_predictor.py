"""
Price Change Predictor - Predict FPL player price changes

Predicts which players are likely to rise or fall in price based on:
- Net transfers (transfers_in_event - transfers_out_event)
- Ownership percentage
- Form and recent performance
- Simple threshold-based algorithm

Example:
    >>> predictor = PriceChangePredictor()
    >>> predictions = predictor.predict_price_changes(players_df)
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from utils.error_handling import logger


class PriceChangePredictor:
    """
    Predict FPL player price changes using transfer data.
    
    Thresholds (based on FPL price change mechanics):
    - Rise: Net transfers > 100,000
    - Fall: Net transfers < -100,000
    - Probable rise: Net transfers > 50,000
    - Probable fall: Net transfers < -50,000
    """
    
    # Thresholds for price changes
    DEFINITE_RISE_THRESHOLD = 100000
    PROBABLE_RISE_THRESHOLD = 50000
    DEFINITE_FALL_THRESHOLD = -100000
    PROBABLE_FALL_THRESHOLD = -50000
    
    # Ownership thresholds
    HIGH_OWNERSHIP = 10.0  # %
    LOW_OWNERSHIP = 2.0    # %
    
    def __init__(self):
        """Initialize the price change predictor."""
        self.logger = logger
    
    def predict_price_changes(
        self,
        df: pd.DataFrame,
        include_probable: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Predict which players will rise or fall in price.
        
        Args:
            df: DataFrame with player data including transfer data
            include_probable: Include probable changes (not just definite)
            
        Returns:
            Dict with:
                - risers: List of players likely to rise
                - fallers: List of players likely to fall
                - watchlist: Players on the edge
                - stats: Summary statistics
        """
        try:
            # Validate required columns
            required_cols = ['web_name', 'transfers_in_event', 'transfers_out_event']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing required columns: {required_cols}")
            
            # Calculate net transfers
            df = df.copy()
            df['net_transfers'] = (
                pd.to_numeric(df['transfers_in_event'], errors='coerce').fillna(0) -
                pd.to_numeric(df['transfers_out_event'], errors='coerce').fillna(0)
            )
            
            # Calculate price change probability
            df['change_probability'] = self._calculate_change_probability(df)
            
            # Categorize players
            risers = self._identify_risers(df, include_probable)
            fallers = self._identify_fallers(df, include_probable)
            watchlist = self._identify_watchlist(df)
            
            # Calculate statistics
            stats = self._calculate_stats(df, risers, fallers)
            
            return {
                'risers': risers,
                'fallers': fallers,
                'watchlist': watchlist,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting price changes: {e}")
            return self._get_empty_result()
    
    def _calculate_change_probability(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate probability of price change (0-100%).
        
        Higher probability for:
        - High absolute net transfers
        - High ownership players (rises)
        - Low ownership players (falls)
        - Good recent form (rises)
        
        Args:
            df: Player DataFrame with net_transfers
            
        Returns:
            Series with probability percentages
        """
        net = df['net_transfers']
        ownership = pd.to_numeric(df.get('selected_by_percent', 0), errors='coerce').fillna(0)
        form = pd.to_numeric(df.get('form', 0), errors='coerce').fillna(0)
        
        # Base probability from net transfers
        base_prob = (abs(net) / 150000 * 100).clip(0, 100)
        
        # Ownership modifier
        ownership_mod = 1.0
        for idx in df.index:
            if net[idx] > 0:  # Rising
                # High ownership makes rises more likely
                if ownership[idx] > self.HIGH_OWNERSHIP:
                    ownership_mod = 1.2
                elif ownership[idx] < self.LOW_OWNERSHIP:
                    ownership_mod = 0.8
            else:  # Falling
                # Low ownership makes falls more likely
                if ownership[idx] < self.LOW_OWNERSHIP:
                    ownership_mod = 1.2
                elif ownership[idx] > self.HIGH_OWNERSHIP:
                    ownership_mod = 0.8
        
        # Form modifier for rises
        form_mod = pd.Series(1.0, index=df.index)
        form_mod[net > 0] = 1 + (form[net > 0] / 10 * 0.2)
        
        return (base_prob * ownership_mod * form_mod).clip(0, 100)
    
    def _identify_risers(
        self,
        df: pd.DataFrame,
        include_probable: bool
    ) -> List[Dict]:
        """
        Identify players likely to rise in price.
        
        Args:
            df: Player DataFrame
            include_probable: Include probable rises
            
        Returns:
            List of riser dicts sorted by probability
        """
        # Filter for rising players
        threshold = self.PROBABLE_RISE_THRESHOLD if include_probable else self.DEFINITE_RISE_THRESHOLD
        risers_df = df[df['net_transfers'] > threshold].copy()
        
        # Sort by net transfers (strongest signal)
        risers_df = risers_df.sort_values('net_transfers', ascending=False)
        
        # Build result list
        risers = []
        for _, player in risers_df.head(20).iterrows():  # Top 20 risers
            net = int(player['net_transfers'])
            
            # Determine confidence level
            if net >= self.DEFINITE_RISE_THRESHOLD:
                confidence = 'HIGH'
                emoji = '🔥'
            else:
                confidence = 'MEDIUM'
                emoji = '📈'
            
            risers.append({
                'name': player['web_name'],
                'team': player.get('team_name', 'Unknown'),
                'position': player.get('position', 'Unknown'),
                'current_price': float(player.get('now_cost', 0)) / 10,
                'net_transfers': net,
                'transfers_in': int(player['transfers_in_event']),
                'ownership': float(player.get('selected_by_percent', 0)),
                'form': float(player.get('form', 0)),
                'probability': round(float(player['change_probability']), 1),
                'confidence': confidence,
                'emoji': emoji,
                'display': f"{emoji} {player['web_name']} - {net//1000}K net ({confidence})"
            })
        
        return risers
    
    def _identify_fallers(
        self,
        df: pd.DataFrame,
        include_probable: bool
    ) -> List[Dict]:
        """
        Identify players likely to fall in price.
        
        Args:
            df: Player DataFrame
            include_probable: Include probable falls
            
        Returns:
            List of faller dicts sorted by probability
        """
        # Filter for falling players
        threshold = self.PROBABLE_FALL_THRESHOLD if include_probable else self.DEFINITE_FALL_THRESHOLD
        fallers_df = df[df['net_transfers'] < threshold].copy()
        
        # Sort by net transfers (most negative first)
        fallers_df = fallers_df.sort_values('net_transfers', ascending=True)
        
        # Build result list
        fallers = []
        for _, player in fallers_df.head(20).iterrows():  # Top 20 fallers
            net = int(player['net_transfers'])
            
            # Determine confidence level
            if net <= self.DEFINITE_FALL_THRESHOLD:
                confidence = 'HIGH'
                emoji = '🔻'
            else:
                confidence = 'MEDIUM'
                emoji = '📉'
            
            fallers.append({
                'name': player['web_name'],
                'team': player.get('team_name', 'Unknown'),
                'position': player.get('position', 'Unknown'),
                'current_price': float(player.get('now_cost', 0)) / 10,
                'net_transfers': net,
                'transfers_out': int(player['transfers_out_event']),
                'ownership': float(player.get('selected_by_percent', 0)),
                'form': float(player.get('form', 0)),
                'probability': round(float(player['change_probability']), 1),
                'confidence': confidence,
                'emoji': emoji,
                'display': f"{emoji} {player['web_name']} - {abs(net)//1000}K net ({confidence})"
            })
        
        return fallers
    
    def _identify_watchlist(self, df: pd.DataFrame) -> List[Dict]:
        """
        Identify players on the edge of price changes.
        
        Args:
            df: Player DataFrame
            
        Returns:
            List of watchlist players
        """
        # Players close to thresholds
        watchlist_df = df[
            ((df['net_transfers'] > 30000) & (df['net_transfers'] < self.PROBABLE_RISE_THRESHOLD)) |
            ((df['net_transfers'] < -30000) & (df['net_transfers'] > self.PROBABLE_FALL_THRESHOLD))
        ].copy()
        
        watchlist_df = watchlist_df.sort_values(
            'net_transfers',
            ascending=False,
            key=lambda x: abs(x)
        )
        
        watchlist = []
        for _, player in watchlist_df.head(10).iterrows():
            net = int(player['net_transfers'])
            direction = 'Rising' if net > 0 else 'Falling'
            
            watchlist.append({
                'name': player['web_name'],
                'team': player.get('team_name', 'Unknown'),
                'current_price': float(player.get('now_cost', 0)) / 10,
                'net_transfers': net,
                'direction': direction,
                'probability': round(float(player['change_probability']), 1),
                'display': f"⚠️ {player['web_name']} - {abs(net)//1000}K net ({direction})"
            })
        
        return watchlist
    
    def _calculate_stats(
        self,
        df: pd.DataFrame,
        risers: List[Dict],
        fallers: List[Dict]
    ) -> Dict:
        """
        Calculate summary statistics.
        
        Args:
            df: Player DataFrame
            risers: List of risers
            fallers: List of fallers
            
        Returns:
            Dict with statistics
        """
        total_transfers_in = df['transfers_in_event'].sum()
        total_transfers_out = df['transfers_out_event'].sum()
        
        return {
            'total_players': len(df),
            'likely_risers': len(risers),
            'likely_fallers': len(fallers),
            'total_transfers_in': int(total_transfers_in),
            'total_transfers_out': int(total_transfers_out),
            'net_transfers': int(total_transfers_in - total_transfers_out),
            'avg_ownership': round(df.get('selected_by_percent', pd.Series([0])).mean(), 2)
        }
    
    def _get_empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'risers': [],
            'fallers': [],
            'watchlist': [],
            'stats': {
                'total_players': 0,
                'likely_risers': 0,
                'likely_fallers': 0,
                'total_transfers_in': 0,
                'total_transfers_out': 0,
                'net_transfers': 0,
                'avg_ownership': 0.0
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def format_predictions_display(self, predictions: Dict) -> str:
        """
        Format predictions for display.
        
        Args:
            predictions: Result from predict_price_changes()
            
        Returns:
            Formatted string for display
        """
        lines = [
            "📊 **Price Change Predictions**",
            f"⏰ Updated: {datetime.fromisoformat(predictions['timestamp']).strftime('%H:%M:%S')}",
            "",
            f"**Statistics:**",
            f"- Likely Risers: {predictions['stats']['likely_risers']}",
            f"- Likely Fallers: {predictions['stats']['likely_fallers']}",
            f"- Total Transfers In: {predictions['stats']['total_transfers_in']:,}",
            f"- Total Transfers Out: {predictions['stats']['total_transfers_out']:,}",
            ""
        ]
        
        if predictions['risers']:
            lines.append("**🔥 Likely Risers:**")
            for riser in predictions['risers'][:5]:
                lines.append(f"- {riser['display']}")
            lines.append("")
        
        if predictions['fallers']:
            lines.append("**🔻 Likely Fallers:**")
            for faller in predictions['fallers'][:5]:
                lines.append(f"- {faller['display']}")
            lines.append("")
        
        if predictions['watchlist']:
            lines.append("**⚠️ Watchlist (On The Edge):**")
            for player in predictions['watchlist'][:3]:
                lines.append(f"- {player['display']}")
        
        return "\n".join(lines)


# Convenience function
def predict_price_changes(df: pd.DataFrame, include_probable: bool = True) -> Dict:
    """
    Predict price changes (convenience function).
    
    Args:
        df: Player DataFrame
        include_probable: Include probable changes
        
    Returns:
        Dict with predictions
    """
    predictor = PriceChangePredictor()
    return predictor.predict_price_changes(df, include_probable)
