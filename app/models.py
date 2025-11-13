"""
Pydantic models for request/response validation
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class PredictionRequest(BaseModel):
    """Request model for price prediction"""
    
    species: str = Field(..., description="Fish species (tilapia or bangus)")
    date_from: str = Field(..., alias="dateFrom", description="Start date (YYYY-MM-DD)")
    date_to: str = Field(..., alias="dateTo", description="End date (YYYY-MM-DD)")
    province: str = Field(..., description="Province name")
    city: str = Field(..., description="City/Municipality name")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "species": "tilapia",
                "dateFrom": "2024-01-01",
                "dateTo": "2024-01-31",
                "province": "Pampanga",
                "city": "Mexico"
            }
        }
    
    @validator("species")
    def validate_species(cls, v):
        """Validate species is either tilapia or bangus"""
        v = v.lower()
        if v not in ["tilapia", "bangus"]:
            raise ValueError("Species must be either 'tilapia' or 'bangus'")
        return v
    
    @validator("date_from", "date_to")
    def validate_date_format(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class PredictionPoint(BaseModel):
    """Single prediction point"""
    
    date: str = Field(..., description="Prediction date (YYYY-MM-DD)")
    predicted_price: float = Field(..., description="Predicted price in PHP")
    confidence_lower: Optional[float] = Field(None, description="Lower confidence bound")
    confidence_upper: Optional[float] = Field(None, description="Upper confidence bound")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "predicted_price": 125.50,
                "confidence_lower": 120.00,
                "confidence_upper": 131.00
            }
        }


class ModelInfo(BaseModel):
    """Information about the ML model used"""
    
    model_name: str = Field(..., description="Name of the model")
    species: str = Field(..., description="Fish species")
    version: str = Field(..., description="Model version")
    last_trained: Optional[str] = Field(None, description="Last training date")
    features_used: Optional[List[str]] = Field(None, description="Features used in the model")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "Tilapia Price Forecast Model",
                "species": "tilapia",
                "version": "1.0.0",
                "last_trained": "2024-01-01",
                "features_used": ["date", "province", "city", "historical_prices"]
            }
        }


class PredictionResponse(BaseModel):
    """Response model for price prediction"""
    
    success: bool = Field(..., description="Whether prediction was successful")
    predictions: List[PredictionPoint] = Field(..., description="List of predictions")
    model_info: ModelInfo = Field(..., description="Information about the model used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "predictions": [
                    {
                        "date": "2024-01-15",
                        "predicted_price": 125.50,
                        "confidence_lower": 120.00,
                        "confidence_upper": 131.00
                    }
                ],
                "model_info": {
                    "model_name": "Tilapia Price Forecast Model",
                    "species": "tilapia",
                    "version": "1.0.0"
                },
                "metadata": {
                    "province": "Pampanga",
                    "city": "Mexico",
                    "prediction_count": 31
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Model not found",
                "detail": "The requested model file does not exist"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    models_loaded: Dict[str, bool] = Field(..., description="Status of loaded models")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "models_loaded": {
                    "tilapia": True,
                    "bangus": True
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ModelListResponse(BaseModel):
    """Response for listing available models"""
    
    models: List[Dict[str, Any]] = Field(..., description="List of available models")
    count: int = Field(..., description="Number of models")
    
    class Config:
        json_schema_extra = {
            "example": {
                "models": [
                    {
                        "species": "tilapia",
                        "name": "Tilapia Price Forecast Model",
                        "status": "loaded",
                        "path": "models/tilapia_forecast_best_model.pkl"
                    },
                    {
                        "species": "bangus",
                        "name": "Bangus Price Forecast Model",
                        "status": "loaded",
                        "path": "models/bangus_forecast_best_model.pkl"
                    }
                ],
                "count": 2
            }
        }
