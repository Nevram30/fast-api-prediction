"""
ML Prediction Logic
Handles loading models and making harvest forecasts
"""
import os
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from app.config import settings
from app.models import PredictionPoint, ModelInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    """Handles ML model loading and predictions"""
    
    def __init__(self):
        """Initialize the predictor"""
        self.models: Dict[str, Any] = {}
        self.model_info: Dict[str, Dict] = {}
        self._load_models()
    
    def _load_models(self):
        """Load all available models"""
        logger.info("Loading ML models...")
        
        # Load Tilapia model
        if os.path.exists(settings.tilapia_model_path):
            self._load_single_model('tilapia', settings.tilapia_model_path, 'Tilapia Harvest Forecast Model')
        else:
            logger.warning(f"✗ Tilapia model not found at {settings.tilapia_model_path}")
        
        # Load Bangus model
        if os.path.exists(settings.bangus_model_path):
            self._load_single_model('bangus', settings.bangus_model_path, 'Bangus Harvest Forecast Model')
        else:
            logger.warning(f"✗ Bangus model not found at {settings.bangus_model_path}")
        
        logger.info(f"Models loaded: {list(self.models.keys())}")
    
    def _load_single_model(self, species: str, model_path: str, model_name: str):
        """Load a single model with multiple fallback methods"""
        loading_methods = [
            ('latin1', lambda f: pickle.load(f, encoding='latin1')),
            ('bytes', lambda f: pickle.load(f, encoding='bytes')),
            ('default', lambda f: pickle.load(f)),
        ]
        
        # Try joblib if available (common for scikit-learn models)
        try:
            import joblib
            loading_methods.insert(0, ('joblib', lambda f: joblib.load(model_path)))
        except ImportError:
            pass
        
        for method_name, load_func in loading_methods:
            try:
                logger.info(f"   Attempting to load {species} model with method: {method_name}")
                if method_name == 'joblib':
                    model = load_func(None)
                else:
                    with open(model_path, 'rb') as f:
                        model = load_func(f)
                
                self.models[species] = model
                self.model_info[species] = {
                    'name': model_name,
                    'species': species,
                    'version': '1.0.0',
                    'path': model_path
                }
                logger.info(f"✓ {species.capitalize()} model loaded successfully using {method_name}")
                return
            except Exception as e:
                logger.debug(f"   Method {method_name} failed: {e}")
                continue
        
        logger.error(f"✗ Failed to load {species} model with all methods")
    
    def is_model_loaded(self, species: str) -> bool:
        """Check if a model is loaded"""
        return species.lower() in self.models
    
    def get_model_info(self, species: str) -> Optional[Dict]:
        """Get information about a loaded model"""
        return self.model_info.get(species.lower())
    
    def get_all_models_info(self) -> List[Dict]:
        """Get information about all loaded models"""
        models_list = []
        for species, info in self.model_info.items():
            model_data = info.copy()
            model_data['status'] = 'loaded' if self.is_model_loaded(species) else 'not_loaded'
            models_list.append(model_data)
        return models_list
    
    def predict(
        self,
        species: str,
        date_from: str,
        date_to: str,
        province: str,
        city: str
    ) -> List[PredictionPoint]:
        """
        Make harvest forecasts for the specified date range (by month)
        
        Args:
            species: Fish species (tilapia or bangus)
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            province: Province name
            city: City/Municipality name
        
        Returns:
            List of prediction points with harvest forecasts
        """
        species = species.lower()
        
        # Check if model is loaded
        if not self.is_model_loaded(species):
            raise ValueError(f"Model for {species} is not loaded")
        
        # Parse dates
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
        
        # Validate date range
        if end_date < start_date:
            raise ValueError("End date must be after start date")
        
        days_diff = (end_date - start_date).days + 1
        if days_diff > settings.max_forecast_days:
            raise ValueError(f"Date range exceeds maximum of {settings.max_forecast_days} days")
        
        # Generate date range (monthly basis for harvest forecasts)
        date_range = pd.date_range(start=start_date, end=end_date, freq='MS')  # MS = Month Start
        
        # Prepare features for prediction
        features_df = self._prepare_features(
            date_range=date_range,
            province=province,
            city=city,
            species=species
        )
        
        # Get model
        model = self.models[species]
        
        # Make predictions
        try:
            predictions = model.predict(features_df)
            
            # If model supports prediction intervals, get them
            confidence_intervals = None
            if hasattr(model, 'predict_interval'):
                try:
                    confidence_intervals = model.predict_interval(features_df, alpha=0.05)
                except:
                    pass
            
            # Create prediction points (harvest forecasts by month)
            prediction_points = []
            for i, date in enumerate(date_range):
                point = PredictionPoint(
                    date=date.strftime("%Y-%m-%d"),
                    predicted_harvest=float(predictions[i])  # This represents harvest amount in kg
                )
                
                # Add confidence intervals if available
                if confidence_intervals is not None:
                    point.confidence_lower = float(confidence_intervals[i][0])
                    point.confidence_upper = float(confidence_intervals[i][1])
                
                prediction_points.append(point)
            
            return prediction_points
            
        except Exception as e:
            logger.error(f"Harvest forecast error: {e}")
            raise ValueError(f"Failed to make harvest forecast: {str(e)}")
    
    def _prepare_features(
        self,
        date_range: pd.DatetimeIndex,
        province: str,
        city: str,
        species: str
    ) -> pd.DataFrame:
        """
        Prepare features for harvest forecast model
        
        Creates features that match the model's training data:
        - AvgWeight: Average weight of fish
        - Fingerlings: Number of fingerlings
        - SurvivalRate: Survival rate percentage
        - Month-based features for harvest forecasting
        """
        # Get the model to check what features it expects
        model = self.models[species]
        
        # Try to get feature names from the model
        feature_names = None
        if hasattr(model, 'feature_names_in_'):
            feature_names = model.feature_names_in_
        elif hasattr(model, 'get_feature_names_out'):
            try:
                feature_names = model.get_feature_names_out()
            except:
                pass
        
        # Create base dataframe with the number of predictions needed
        n_predictions = len(date_range)
        
        # Default values for aquaculture features (these are typical averages)
        # These can be adjusted based on historical data or user input
        default_values = {
            'AvgWeight': 250.0,  # grams - typical market weight for tilapia/bangus
            'Fingerlings': 5000,  # typical stocking density per pond
            'SurvivalRate': 85.0  # percentage - typical survival rate
        }
        
        # Create dataframe with expected features
        if feature_names is not None:
            df = pd.DataFrame(index=range(n_predictions))
            for feature in feature_names:
                if feature in default_values:
                    df[feature] = default_values[feature]
                else:
                    # For any other features, use 0 as default
                    df[feature] = 0.0
        else:
            # Fallback: create dataframe with the known required features
            df = pd.DataFrame({
                'AvgWeight': [default_values['AvgWeight']] * n_predictions,
                'Fingerlings': [default_values['Fingerlings']] * n_predictions,
                'SurvivalRate': [default_values['SurvivalRate']] * n_predictions
            })
        
        return df


# Global predictor instance
predictor = ModelPredictor()
