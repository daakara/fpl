"""
Predictive Analytics Engine for FPL Dashboard
Machine Learning models for performance prediction and analysis
Phase 2: AI-Powered Real-Time Intelligence  
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import warnings
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import pickle
import os

warnings.filterwarnings('ignore')

@dataclass
class PredictionResult:
    """Data class for prediction results"""
    player_id: int
    player_name: str
    prediction_type: str
    predicted_value: float
    confidence_interval: Tuple[float, float]
    confidence_score: float
    model_used: str
    features_importance: Dict[str, float]
    prediction_date: datetime

@dataclass
class ModelPerformance:
    """Data class for model performance metrics"""
    model_name: str
    mae: float
    rmse: float
    r2: float
    cv_score: float
    feature_importance: Dict[str, float]

class PredictiveAnalyticsEngine:
    """Advanced predictive analytics using machine learning"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_performance = {}
        self.is_trained = False
        
        # Model configurations
        self.model_configs = {
            'points_prediction': {
                'target': 'total_points',
                'model_type': 'regression',
                'algorithms': ['rf', 'xgb', 'gb']
            },
            'price_prediction': {
                'target': 'now_cost',
                'model_type': 'regression', 
                'algorithms': ['rf', 'linear']
            },
            'form_prediction': {
                'target': 'form',
                'model_type': 'regression',
                'algorithms': ['rf', 'ridge']
            }
        }
        
        # Feature engineering configuration
        self.feature_config = {
            'player_features': [
                'total_points', 'form', 'now_cost', 'selected_by_percent',
                'minutes', 'goals_scored', 'assists', 'clean_sheets',
                'goals_conceded', 'own_goals', 'penalties_saved',
                'penalties_missed', 'yellow_cards', 'red_cards',
                'saves', 'bonus', 'bps', 'influence', 'creativity', 'threat'
            ],
            'team_features': [
                'team', 'element_type'
            ],
            'derived_features': [
                'points_per_game', 'points_per_million', 'minutes_per_game',
                'goal_involvement', 'defensive_actions', 'attacking_threat'
            ]
        }
    
    def prepare_training_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and engineer features for model training"""
        if df.empty:
            return df
        
        # Create a copy for feature engineering
        training_df = df.copy()
        
        # Handle missing values
        numeric_columns = training_df.select_dtypes(include=[np.number]).columns
        training_df[numeric_columns] = training_df[numeric_columns].fillna(training_df[numeric_columns].median())
        
        # Feature engineering
        training_df = self._engineer_features(training_df)
        
        # Encode categorical variables
        categorical_features = ['team', 'element_type']
        for feature in categorical_features:
            if feature in training_df.columns:
                if feature not in self.encoders:
                    self.encoders[feature] = LabelEncoder()
                    training_df[f'{feature}_encoded'] = self.encoders[feature].fit_transform(training_df[feature])
                else:
                    # Transform using existing encoder
                    try:
                        training_df[f'{feature}_encoded'] = self.encoders[feature].transform(training_df[feature])
                    except ValueError:
                        # Handle unseen categories
                        training_df[f'{feature}_encoded'] = 0
        
        return training_df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer advanced features from basic FPL data"""
        
        # Points per game (avoid division by zero)
        df['points_per_game'] = np.where(
            df['minutes'] > 0,
            df['total_points'] / (df['minutes'] / 90),
            0
        )
        
        # Points per million
        df['points_per_million'] = np.where(
            df['now_cost'] > 0,
            df['total_points'] / (df['now_cost'] / 10),
            0
        )
        
        # Minutes per game (estimated based on current minutes)
        df['games_played'] = np.where(df['minutes'] > 0, df['minutes'] / 90, 1)
        df['minutes_per_game'] = df['minutes'] / df['games_played']
        
        # Goal involvement (goals + assists)
        if 'goals_scored' in df.columns and 'assists' in df.columns:
            df['goal_involvement'] = df['goals_scored'] + df['assists']
        else:
            df['goal_involvement'] = 0
        
        # Defensive actions (for defenders/goalkeepers)
        defensive_cols = ['clean_sheets', 'saves', 'penalties_saved']
        available_def_cols = [col for col in defensive_cols if col in df.columns]
        if available_def_cols:
            df['defensive_actions'] = df[available_def_cols].sum(axis=1)
        else:
            df['defensive_actions'] = 0
        
        # Attacking threat (for midfielders/forwards)
        threat_cols = ['goals_scored', 'assists', 'bonus']
        available_threat_cols = [col for col in threat_cols if col in df.columns]
        if available_threat_cols:
            df['attacking_threat'] = df[available_threat_cols].sum(axis=1)
        else:
            df['attacking_threat'] = 0
        
        # Form momentum (difference from average)
        df['form_vs_average'] = df['form'] - df['total_points'] / df['games_played']
        
        # Price efficiency
        df['price_efficiency'] = np.where(
            df['selected_by_percent'] > 0,
            df['total_points'] / df['selected_by_percent'],
            0
        )
        
        # Minutes reliability (consistency of game time)
        df['minutes_reliability'] = np.where(
            df['minutes'] > 450,  # 5+ games
            1.0,
            df['minutes'] / 450
        )
        
        return df
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, ModelPerformance]:
        """Train all prediction models"""
        if df.empty:
            return {}
        
        # Prepare training data
        training_df = self.prepare_training_data(df)
        
        # Train models for each prediction type
        performance_results = {}
        
        for pred_type, config in self.model_configs.items():
            if config['target'] in training_df.columns:
                performance = self._train_prediction_model(training_df, pred_type, config)
                performance_results[pred_type] = performance
        
        self.is_trained = True
        return performance_results
    
    def _train_prediction_model(self, df: pd.DataFrame, pred_type: str, config: Dict) -> ModelPerformance:
        """Train a specific prediction model"""
        target = config['target']
        
        # Select features for training
        feature_columns = self._select_features(df, pred_type)
        
        if not feature_columns:
            return ModelPerformance(
                model_name=pred_type,
                mae=float('inf'),
                rmse=float('inf'),
                r2=0.0,
                cv_score=0.0,
                feature_importance={}
            )
        
        X = df[feature_columns]
        y = df[target]
        
        # Handle any remaining NaN values
        X = X.fillna(X.median())
        y = y.fillna(y.median())
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers[pred_type] = scaler
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train multiple algorithms and select best
        best_model = None
        best_score = float('inf')
        model_results = {}
        
        for algorithm in config['algorithms']:
            model = self._create_model(algorithm)
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                
                model_results[algorithm] = {
                    'model': model,
                    'mae': mae,
                    'predictions': y_pred
                }
                
                if mae < best_score:
                    best_score = mae
                    best_model = model
            
            except Exception as e:
                print(f"Error training {algorithm} for {pred_type}: {e}")
                continue
        
        if best_model is None:
            # Fallback to simple linear regression
            best_model = LinearRegression()
            best_model.fit(X_train, y_train)
            y_pred = best_model.predict(X_test)
        else:
            y_pred = best_model.predict(X_test)
        
        # Store best model
        self.models[pred_type] = {
            'model': best_model,
            'features': feature_columns,
            'scaler': scaler
        }
        
        # Calculate performance metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation score
        try:
            cv_scores = cross_val_score(best_model, X_scaled, y, cv=5, scoring='neg_mean_absolute_error')
            cv_score = -cv_scores.mean()
        except:
            cv_score = mae
        
        # Feature importance
        feature_importance = self._get_feature_importance(best_model, feature_columns)
        
        return ModelPerformance(
            model_name=pred_type,
            mae=mae,
            rmse=rmse,
            r2=r2,
            cv_score=cv_score,
            feature_importance=feature_importance
        )
    
    def _select_features(self, df: pd.DataFrame, pred_type: str) -> List[str]:
        """Select appropriate features for each prediction type"""
        all_features = []
        
        # Add player features
        for feature in self.feature_config['player_features']:
            if feature in df.columns:
                all_features.append(feature)
        
        # Add encoded categorical features
        for feature in self.feature_config['team_features']:
            encoded_feature = f'{feature}_encoded'
            if encoded_feature in df.columns:
                all_features.append(encoded_feature)
        
        # Add derived features
        for feature in self.feature_config['derived_features']:
            if feature in df.columns:
                all_features.append(feature)
        
        # Remove target variable from features
        target = self.model_configs[pred_type]['target']
        if target in all_features:
            all_features.remove(target)
        
        return all_features
    
    def _create_model(self, algorithm: str):
        """Create model instance based on algorithm name"""
        models = {
            'rf': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'xgb': xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'gb': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear': LinearRegression(),
            'ridge': Ridge(alpha=1.0)
        }
        return models.get(algorithm, LinearRegression())
    
    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Extract feature importance from trained model"""
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
            else:
                return {}
            
            # Create importance dictionary
            importance_dict = dict(zip(feature_names, importance))
            
            # Normalize to percentages
            total_importance = sum(importance_dict.values())
            if total_importance > 0:
                importance_dict = {k: v/total_importance for k, v in importance_dict.items()}
            
            # Sort by importance
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        except Exception as e:
            print(f"Error extracting feature importance: {e}")
            return {}
    
    def predict_player_points(self, df: pd.DataFrame, player_ids: Optional[List[int]] = None) -> List[PredictionResult]:
        """Predict points for specific players or all players"""
        if not self.is_trained or 'points_prediction' not in self.models:
            return []
        
        predictions = []
        
        # Prepare data
        pred_df = self.prepare_training_data(df)
        
        if player_ids:
            pred_df = pred_df[pred_df['id'].isin(player_ids)]
        
        model_info = self.models['points_prediction']
        model = model_info['model']
        features = model_info['features']
        scaler = model_info['scaler']
        
        # Make predictions
        for _, player in pred_df.iterrows():
            try:
                # Extract features
                X = player[features].values.reshape(1, -1)
                X_scaled = scaler.transform(X)
                
                # Predict
                prediction = model.predict(X_scaled)[0]
                
                # Calculate confidence interval (simple approximation)
                confidence_range = prediction * 0.15  # ±15% range
                confidence_interval = (
                    max(0, prediction - confidence_range),
                    prediction + confidence_range
                )
                
                # Calculate confidence score based on feature reliability
                confidence_score = self._calculate_confidence_score(player, features)
                
                # Get feature importance for this prediction
                feature_importance = self.model_performance.get('points_prediction', {}).feature_importance
                
                predictions.append(PredictionResult(
                    player_id=int(player['id']),
                    player_name=player['web_name'],
                    prediction_type='points',
                    predicted_value=float(prediction),
                    confidence_interval=confidence_interval,
                    confidence_score=confidence_score,
                    model_used='points_prediction',
                    features_importance=feature_importance,
                    prediction_date=datetime.now()
                ))
                
            except Exception as e:
                print(f"Error predicting for player {player.get('web_name', 'Unknown')}: {e}")
                continue
        
        return predictions
    
    def predict_price_changes(self, df: pd.DataFrame) -> List[PredictionResult]:
        """Predict price changes for players"""
        if not self.is_trained or 'price_prediction' not in self.models:
            return []
        
        predictions = []
        
        # Focus on players with significant transfer activity
        active_players = df[
            (df['minutes'] > 90) &  # Played at least 1 game
            ((df.get('transfers_in_event', 0) + df.get('transfers_out_event', 0)) > 1000)
        ]
        
        if active_players.empty:
            return predictions
        
        pred_df = self.prepare_training_data(active_players)
        
        model_info = self.models['price_prediction']
        model = model_info['model']
        features = model_info['features']
        scaler = model_info['scaler']
        
        for _, player in pred_df.iterrows():
            try:
                X = player[features].values.reshape(1, -1)
                X_scaled = scaler.transform(X)
                
                predicted_price = model.predict(X_scaled)[0]
                current_price = player['now_cost']
                
                # Only flag significant price changes
                price_diff = predicted_price - current_price
                if abs(price_diff) >= 1:  # 0.1m difference
                    
                    confidence_interval = (
                        predicted_price - abs(price_diff) * 0.3,
                        predicted_price + abs(price_diff) * 0.3
                    )
                    
                    confidence_score = self._calculate_confidence_score(player, features)
                    
                    predictions.append(PredictionResult(
                        player_id=int(player['id']),
                        player_name=player['web_name'],
                        prediction_type='price_change',
                        predicted_value=float(price_diff / 10),  # Convert to millions
                        confidence_interval=tuple(ci / 10 for ci in confidence_interval),
                        confidence_score=confidence_score,
                        model_used='price_prediction',
                        features_importance=self.model_performance.get('price_prediction', {}).feature_importance,
                        prediction_date=datetime.now()
                    ))
                    
            except Exception as e:
                continue
        
        return predictions
    
    def predict_captain_scores(self, df: pd.DataFrame, fixture_difficulty: Optional[Dict[int, float]] = None) -> List[PredictionResult]:
        """Predict captain scores for next gameweek"""
        predictions = []
        
        # Focus on premium players (>£7m) and regular starters
        captain_candidates = df[
            (df['now_cost'] >= 70) &  # £7m+
            (df['minutes'] >= 270) &  # 3+ games
            (df['total_points'] >= 30)  # 30+ points
        ]
        
        if captain_candidates.empty:
            return predictions
        
        for _, player in captain_candidates.iterrows():
            try:
                # Simple captain scoring algorithm
                base_score = (
                    player['form'] * 0.4 +
                    player['total_points'] * 0.02 +
                    (100 - player['selected_by_percent']) * 0.01 +  # Differential bonus
                    player.get('attacking_threat', 0) * 0.1
                )
                
                # Adjust for fixture difficulty if provided
                if fixture_difficulty and player['team'] in fixture_difficulty:
                    difficulty_multiplier = (6 - fixture_difficulty[player['team']]) / 5
                    base_score *= difficulty_multiplier
                
                # Confidence based on recent form consistency
                form_consistency = 1.0 - (abs(player['form'] - player['total_points'] / max(1, player['minutes'] / 90)) / 10)
                confidence_score = min(0.95, max(0.3, form_consistency))
                
                confidence_interval = (
                    max(0, base_score * 0.7),
                    base_score * 1.3
                )
                
                predictions.append(PredictionResult(
                    player_id=int(player['id']),
                    player_name=player['web_name'],
                    prediction_type='captain_score',
                    predicted_value=float(base_score),
                    confidence_interval=confidence_interval,
                    confidence_score=confidence_score,
                    model_used='captain_algorithm',
                    features_importance={'form': 0.4, 'total_points': 0.2, 'differential': 0.1, 'attacking_threat': 0.1, 'fixture': 0.2},
                    prediction_date=datetime.now()
                ))
                
            except Exception as e:
                continue
        
        # Sort by predicted score
        predictions.sort(key=lambda x: x.predicted_value, reverse=True)
        return predictions[:10]  # Top 10 captain options
    
    def _calculate_confidence_score(self, player_data: pd.Series, features: List[str]) -> float:
        """Calculate confidence score for predictions"""
        try:
            # Base confidence on data completeness
            completeness = sum(1 for feature in features if not pd.isna(player_data.get(feature, np.nan))) / len(features)
            
            # Adjust for player activity level
            minutes_factor = min(1.0, player_data.get('minutes', 0) / 1000)  # Up to 1000 minutes
            
            # Form consistency factor
            form = player_data.get('form', 0)
            avg_points = player_data.get('total_points', 0) / max(1, player_data.get('minutes', 90) / 90)
            consistency = 1.0 - min(1.0, abs(form - avg_points) / 10)
            
            # Combine factors
            confidence = (completeness * 0.4 + minutes_factor * 0.3 + consistency * 0.3)
            
            return min(0.95, max(0.1, confidence))
        
        except Exception:
            return 0.5  # Default moderate confidence
    
    def get_model_performance_summary(self) -> Dict[str, ModelPerformance]:
        """Get performance summary for all trained models"""
        return self.model_performance.copy()
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        if not self.is_trained:
            return False
        
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'encoders': self.encoders,
                'performance': self.model_performance,
                'is_trained': self.is_trained
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            return True
        except Exception as e:
            print(f"Error saving models: {e}")
            return False
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.encoders = model_data['encoders']
            self.model_performance = model_data['performance']
            self.is_trained = model_data['is_trained']
            
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False

print("✅ Predictive Analytics Engine created successfully!")
