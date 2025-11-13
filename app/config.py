"""
Configuration management for the ML Service
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Fish Price Forecast ML Service"
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.railway.app",
        "https://*.vercel.app",
    ]
    
    # Model Configuration
    models_dir: str = "app/models"
    tilapia_model_path: str = "app/models/tilapia_forecast_best_model.pkl"
    bangus_model_path: str = "app/models/bangus_forecast_best_model.pkl"
    
    # Prediction Configuration
    max_forecast_days: int = 365
    default_forecast_days: int = 30
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "")
    database_echo: bool = debug  # Log SQL queries in debug mode
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
