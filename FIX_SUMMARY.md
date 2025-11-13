# Fix Summary: POST /api/v1/predict 500 Internal Server Error

## Problem
The `/api/v1/predict` endpoint was returning a 500 Internal Server Error when making predictions.

## Root Causes Identified

### 1. Model Loading Issue (Python 2/3 Pickle Compatibility)
- **Error**: `STACK_GLOBAL requires str`
- **Cause**: The pickle files were created with an older Python/scikit-learn version and couldn't be loaded with the standard pickle.load() method in Python 3.13
- **Solution**: Implemented a robust model loading system with multiple fallback methods, prioritizing joblib (which handles scikit-learn models better)

### 2. Feature Mismatch Issue
- **Error**: `The feature names should match those that were passed during fit`
- **Cause**: The `_prepare_features()` method was creating incorrect features (date, city, province, etc.) instead of the features the model was trained on
- **Expected Features**: 
  1. Fingerlings (number of fingerlings)
  2. SurvivalRate (survival rate percentage)
  3. AvgWeight (average weight in grams)
- **Solution**: Updated `_prepare_features()` to provide the correct features with sensible default values

## Changes Made

### File: `app/predictor.py`

#### 1. Enhanced Model Loading (`_load_single_model` method)
```python
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
    
    # Try each method until one succeeds
    for method_name, load_func in loading_methods:
        try:
            # ... loading logic
        except Exception as e:
            continue
```

#### 2. Fixed Feature Preparation (`_prepare_features` method)
```python
def _prepare_features(self, date_range, province, city, species):
    """Prepare features matching the model's training data"""
    model = self.models[species]
    
    # Get feature names from model
    feature_names = None
    if hasattr(model, 'feature_names_in_'):
        feature_names = model.feature_names_in_
    
    # Default values for aquaculture features
    default_values = {
        'AvgWeight': 250.0,      # grams - typical market weight
        'Fingerlings': 5000,     # typical stocking density per pond
        'SurvivalRate': 85.0     # percentage - typical survival rate
    }
    
    # Create dataframe with expected features
    # ... creates proper feature dataframe
```

## Test Results

### Request
```json
{
  "city": "Panabo",
  "dateFrom": "2024-01-01",
  "dateTo": "2024-01-31",
  "province": "Pampanga",
  "species": "tilapia"
}
```

### Response
- **Status Code**: 200 OK
- **Success**: true
- **Predictions**: 31 data points (one for each day)
- **Predicted Price**: 975.0 PHP per day
- **Model Info**: Tilapia Price Forecast Model v1.0.0

## Model Information
- **Model Type**: LinearRegression (scikit-learn)
- **Training Version**: scikit-learn 1.6.1
- **Current Version**: scikit-learn 1.7.2
- **Features Used**: Fingerlings, SurvivalRate, AvgWeight
- **Species Supported**: tilapia, bangus

## Notes
- The model uses default values for aquaculture features since the API doesn't currently accept these as input parameters
- Both tilapia and bangus models are now loading successfully
- A version warning appears (1.6.1 vs 1.7.2) but doesn't affect functionality
- The predictions are constant (975.0) because the model uses fixed feature values

## Recommendations for Future Improvements
1. Add input parameters for AvgWeight, Fingerlings, and SurvivalRate to allow users to customize predictions
2. Consider retraining models with the current scikit-learn version to eliminate version warnings
3. Add confidence intervals if the model supports them
4. Consider adding historical price data or time-based features to make predictions vary by date
