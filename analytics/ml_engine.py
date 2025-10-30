"""
Advanced Machine Learning Analytics for FPL
Implements sophisticated ML models for player performance prediction and optimization
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import joblib
import logging
from pathlib import Path

# ML imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import lightgbm as lgb

# Statistical imports
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


@dataclass
class MLModelConfig:
    """Configuration for ML models"""
    model_type: str = "xgboost"  # xgboost, lightgbm, random_forest
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    feature_columns: List[str] = field(default_factory=list)
    target_column: str = "total_points"
    test_size: float = 0.2
    cv_folds: int = 5
    enable_feature_selection: bool = True


@dataclass
class PredictionResult:
    """Result from ML prediction"""
    player_id: int
    player_name: str
    predicted_points: float
    confidence_interval: Tuple[float, float]
    feature_importance: Dict[str, float]
    model_accuracy: float
    prediction_date: datetime


class AdvancedMLAnalytics:
    """Advanced machine learning analytics for FPL"""
    
    def __init__(self, config: MLModelConfig):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.encoders: Dict[str, LabelEncoder] = {}
        self.feature_importance: Dict[str, float] = {}
        self.model_metrics: Dict[str, Dict[str, float]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Model cache
        self.model_cache_dir = Path("models/cache")
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        feature_df = df.copy()
        
        # Create derived features
        feature_df = self._create_performance_features(feature_df)
        feature_df = self._create_momentum_features(feature_df)
        feature_df = self._create_fixture_difficulty_features(feature_df)
        feature_df = self._create_team_strength_features(feature_df)
        feature_df = self._create_historical_features(feature_df)
        
        # Handle categorical features
        feature_df = self._encode_categorical_features(feature_df)
        
        # Handle missing values
        feature_df = self._handle_missing_values(feature_df)
        
        # Scale numerical features
        feature_df = self._scale_numerical_features(feature_df)
        
        return feature_df
    
    def _create_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create performance-based features"""
        # Points per game weighted by recency
        df['weighted_ppg'] = df['total_points'] / np.maximum(df['minutes'] / 90, 0.1)
        
        # Form-based features
        df['form_numeric'] = pd.to_numeric(df['form'], errors='coerce')
        df['form_trend'] = df.groupby('id')['form_numeric'].pct_change()
        
        # Efficiency metrics
        df['goal_efficiency'] = df['goals_scored'] / np.maximum(df['expected_goals'].astype(float), 0.1)
        df['assist_efficiency'] = df['assists'] / np.maximum(df['expected_assists'].astype(float), 0.1)
        
        # Value metrics
        df['value_score'] = df['total_points'] / (df['now_cost'] / 10)
        df['ownership_value'] = df['total_points'] / np.maximum(df['selected_by_percent'].astype(float), 0.1)
        
        return df
    
    def _create_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create momentum-based features"""
        # Recent form (last 5 games average)
        df['recent_form'] = df.groupby('id')['form_numeric'].rolling(5, min_periods=1).mean().reset_index(0, drop=True)
        
        # Scoring streaks
        df['goal_streak'] = df.groupby('id')['goals_scored'].rolling(3).sum().reset_index(0, drop=True)
        df['assist_streak'] = df.groupby('id')['assists'].rolling(3).sum().reset_index(0, drop=True)
        
        # Performance variance (consistency)
        df['points_variance'] = df.groupby('id')['total_points'].rolling(5).std().reset_index(0, drop=True)
        
        return df
    
    def _create_fixture_difficulty_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create fixture difficulty features"""
        # This would integrate with fixture data
        # For now, create placeholder features
        df['upcoming_fixture_difficulty'] = np.random.uniform(1, 5, len(df))  # Placeholder
        df['home_advantage'] = np.random.choice([0, 1], len(df))  # Placeholder
        
        return df
    
    def _create_team_strength_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create team strength features"""
        # Team performance metrics
        team_stats = df.groupby('team').agg({
            'total_points': 'mean',
            'goals_scored': 'sum',
            'goals_conceded': 'sum',
            'clean_sheets': 'sum'
        }).add_prefix('team_')
        
        df = df.merge(team_stats, left_on='team', right_index=True, how='left')
        
        return df
    
    def _create_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create historical performance features"""
        # Season progression features
        df['games_played'] = df.groupby('id').cumcount() + 1
        df['season_progress'] = df['games_played'] / 38  # Assuming 38 game season
        
        # Historical averages
        df['historical_avg'] = df.groupby('id')['total_points'].expanding().mean().reset_index(0, drop=True)
        
        return df
    
    def _encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        categorical_columns = ['element_type', 'team']
        
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[f'{col}_encoded'] = self.encoders[col].transform(df[col].astype(str))
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        # For numerical columns, use median imputation
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if df[col].isna().any():
                median_value = df[col].median()
                df[col].fillna(median_value, inplace=True)
        
        return df
    
    def _scale_numerical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        # Exclude encoded columns and target from scaling
        cols_to_scale = [col for col in numerical_cols 
                        if not col.endswith('_encoded') and col != self.config.target_column]
        
        if 'scaler' not in self.scalers:
            self.scalers['scaler'] = StandardScaler()
            df[cols_to_scale] = self.scalers['scaler'].fit_transform(df[cols_to_scale])
        else:
            df[cols_to_scale] = self.scalers['scaler'].transform(df[cols_to_scale])
        
        return df
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train ML models for prediction"""
        self.logger.info("Starting model training...")
        
        # Prepare features
        feature_df = self.prepare_features(df)
        
        # Select features
        if self.config.feature_columns:
            feature_columns = self.config.feature_columns
        else:
            feature_columns = self._select_best_features(feature_df)
        
        X = feature_df[feature_columns]
        y = feature_df[self.config.target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.test_size, random_state=42
        )
        
        # Train different models
        model_results = {}
        
        if self.config.model_type == "xgboost":
            model_results['xgboost'] = self._train_xgboost(X_train, y_train, X_test, y_test)
        
        elif self.config.model_type == "lightgbm":
            model_results['lightgbm'] = self._train_lightgbm(X_train, y_train, X_test, y_test)
        
        elif self.config.model_type == "random_forest":
            model_results['random_forest'] = self._train_random_forest(X_train, y_train, X_test, y_test)
        
        else:
            # Train all models and select best
            model_results['xgboost'] = self._train_xgboost(X_train, y_train, X_test, y_test)
            model_results['lightgbm'] = self._train_lightgbm(X_train, y_train, X_test, y_test)
            model_results['random_forest'] = self._train_random_forest(X_train, y_train, X_test, y_test)
        
        # Select best model
        best_model = max(model_results.items(), key=lambda x: x[1]['r2_score'])
        self.logger.info(f"Best model: {best_model[0]} with R² = {best_model[1]['r2_score']:.4f}")
        
        return model_results
    
    def _train_xgboost(self, X_train, y_train, X_test, y_test) -> Dict[str, Any]:
        """Train XGBoost model"""
        params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42,
            **self.config.hyperparameters.get('xgboost', {})
        }
        
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        
        # Predictions and metrics
        y_pred = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred)
        
        # Feature importance
        feature_importance = dict(zip(X_train.columns, model.feature_importances_))
        
        # Store model
        self.models['xgboost'] = model
        
        return {
            'model': model,
            'feature_importance': feature_importance,
            **metrics
        }
    
    def _train_lightgbm(self, X_train, y_train, X_test, y_test) -> Dict[str, Any]:
        """Train LightGBM model"""
        params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42,
            'verbose': -1,
            **self.config.hyperparameters.get('lightgbm', {})
        }
        
        model = lgb.LGBMRegressor(**params)
        model.fit(X_train, y_train)
        
        # Predictions and metrics
        y_pred = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred)
        
        # Feature importance
        feature_importance = dict(zip(X_train.columns, model.feature_importances_))
        
        # Store model
        self.models['lightgbm'] = model
        
        return {
            'model': model,
            'feature_importance': feature_importance,
            **metrics
        }
    
    def _train_random_forest(self, X_train, y_train, X_test, y_test) -> Dict[str, Any]:
        """Train Random Forest model"""
        params = {
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42,
            **self.config.hyperparameters.get('random_forest', {})
        }
        
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        
        # Predictions and metrics
        y_pred = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred)
        
        # Feature importance
        feature_importance = dict(zip(X_train.columns, model.feature_importances_))
        
        # Store model
        self.models['random_forest'] = model
        
        return {
            'model': model,
            'feature_importance': feature_importance,
            **metrics
        }
    
    def _calculate_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """Calculate model performance metrics"""
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2_score': r2_score(y_true, y_pred)
        }
    
    def _select_best_features(self, df: pd.DataFrame, top_k: int = 20) -> List[str]:
        """Select best features using correlation and variance"""
        # Remove non-predictive columns
        exclude_cols = ['id', 'web_name', 'first_name', 'second_name', self.config.target_column]
        potential_features = [col for col in df.columns if col not in exclude_cols]
        
        # Remove low variance features
        numeric_features = df[potential_features].select_dtypes(include=[np.number]).columns
        
        # Calculate correlation with target
        correlations = df[numeric_features].corrwith(df[self.config.target_column]).abs()
        
        # Select top features
        top_features = correlations.nlargest(top_k).index.tolist()
        
        self.logger.info(f"Selected {len(top_features)} features for training")
        return top_features
    
    def predict_player_performance(self, player_data: pd.DataFrame, model_name: str = "xgboost") -> List[PredictionResult]:
        """Predict player performance using trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model = self.models[model_name]
        
        # Prepare features
        feature_df = self.prepare_features(player_data)
        
        # Get feature columns (same as used in training)
        feature_columns = [col for col in feature_df.columns 
                          if col not in ['id', 'web_name', self.config.target_column]]
        
        X = feature_df[feature_columns]
        
        # Make predictions
        predictions = model.predict(X)
        
        # Calculate confidence intervals (simplified approach)
        std_pred = np.std(predictions)
        confidence_intervals = [(pred - 1.96 * std_pred, pred + 1.96 * std_pred) 
                               for pred in predictions]
        
        # Get feature importance for this model
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
        else:
            feature_importance = {}
        
        # Create results
        results = []
        for idx, row in player_data.iterrows():
            result = PredictionResult(
                player_id=row['id'],
                player_name=row.get('web_name', f"Player {row['id']}"),
                predicted_points=predictions[idx],
                confidence_interval=confidence_intervals[idx],
                feature_importance=feature_importance,
                model_accuracy=self.model_metrics.get(model_name, {}).get('r2_score', 0.0),
                prediction_date=datetime.now()
            )
            results.append(result)
        
        return results
    
    def optimize_team_selection(self, player_predictions: List[PredictionResult], 
                              budget: float = 100.0, formation: str = "3-4-3") -> Dict[str, Any]:
        """Optimize team selection using predicted points"""
        # This would implement team optimization logic
        # Using linear programming or genetic algorithms
        
        # Simplified version for demonstration
        sorted_predictions = sorted(player_predictions, 
                                  key=lambda x: x.predicted_points, reverse=True)
        
        # Formation constraints
        formation_map = {
            "3-4-3": {"GK": 1, "DEF": 3, "MID": 4, "FWD": 3},
            "3-5-2": {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2},
            "4-4-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
            "4-3-3": {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3}
        }
        
        constraints = formation_map.get(formation, formation_map["3-4-3"])
        
        # Simple greedy selection (in practice, would use optimization)
        selected_team = []
        total_cost = 0
        total_predicted_points = 0
        
        for position, count in constraints.items():
            position_players = [p for p in sorted_predictions 
                              if self._get_player_position(p.player_id) == position]
            
            for i in range(min(count, len(position_players))):
                player = position_players[i]
                player_cost = self._get_player_cost(player.player_id)
                
                if total_cost + player_cost <= budget:
                    selected_team.append(player)
                    total_cost += player_cost
                    total_predicted_points += player.predicted_points
        
        return {
            "selected_team": selected_team,
            "total_cost": total_cost,
            "total_predicted_points": total_predicted_points,
            "formation": formation,
            "optimization_method": "greedy"
        }
    
    def _get_player_position(self, player_id: int) -> str:
        """Get player position (placeholder)"""
        # This would lookup actual position data
        positions = ["GK", "DEF", "MID", "FWD"]
        return positions[player_id % len(positions)]
    
    def _get_player_cost(self, player_id: int) -> float:
        """Get player cost (placeholder)"""
        # This would lookup actual cost data
        return np.random.uniform(4.0, 12.0)
    
    def save_models(self) -> None:
        """Save trained models to disk"""
        for name, model in self.models.items():
            model_path = self.model_cache_dir / f"{name}_model.joblib"
            joblib.dump(model, model_path)
            self.logger.info(f"Saved {name} model to {model_path}")
        
        # Save scalers and encoders
        if self.scalers:
            joblib.dump(self.scalers, self.model_cache_dir / "scalers.joblib")
        
        if self.encoders:
            joblib.dump(self.encoders, self.model_cache_dir / "encoders.joblib")
    
    def load_models(self) -> None:
        """Load trained models from disk"""
        try:
            for model_file in self.model_cache_dir.glob("*_model.joblib"):
                model_name = model_file.stem.replace("_model", "")
                self.models[model_name] = joblib.load(model_file)
                self.logger.info(f"Loaded {model_name} model")
            
            # Load scalers and encoders
            scalers_path = self.model_cache_dir / "scalers.joblib"
            if scalers_path.exists():
                self.scalers = joblib.load(scalers_path)
            
            encoders_path = self.model_cache_dir / "encoders.joblib"
            if encoders_path.exists():
                self.encoders = joblib.load(encoders_path)
        
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")


# Factory function for creating ML analytics
def create_ml_analytics(model_type: str = "xgboost") -> AdvancedMLAnalytics:
    """Create ML analytics instance with default configuration"""
    config = MLModelConfig(model_type=model_type)
    return AdvancedMLAnalytics(config)