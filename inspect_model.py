import pickle
import joblib

# Load the tilapia model
model_path = "app/models/tilapia_forecast_best_model.pkl"

try:
    model = joblib.load(model_path)
    print("Model loaded successfully with joblib")
    
    # Check if model has feature names
    if hasattr(model, 'feature_names_in_'):
        print(f"\nFeature names expected by model:")
        for i, feature in enumerate(model.feature_names_in_, 1):
            print(f"  {i}. {feature}")
        print(f"\nTotal features: {len(model.feature_names_in_)}")
    else:
        print("\nModel does not have feature_names_in_ attribute")
    
    # Check model type
    print(f"\nModel type: {type(model)}")
    
    # Check if it's a pipeline
    if hasattr(model, 'steps'):
        print("\nModel is a Pipeline with steps:")
        for step_name, step_obj in model.steps:
            print(f"  - {step_name}: {type(step_obj)}")
    
except Exception as e:
    print(f"Error loading model: {e}")
