from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # App
    app_name: str = "Device Health Monitoring System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    secret_key: str = "your-secret-key-change-in-production"
    
    # Database
    database_url: str = "postgresql://dhm_user:dhm_password@localhost:5432/device_health_db"
    db_pool_size: int = 20
    db_echo: bool = False
    
    # API
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Slack
    slack_webhook_url: Optional[str] = None
    slack_enabled: bool = True
    
    # SMTP
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "alerts@devicehealth.com"
    email_alerts_enabled: bool = False
    
    # Scheduler
    scheduler_enabled: bool = True
    analyzer_interval_seconds: int = 300
    rca_interval_seconds: int = 600
    
    # Battery thresholds
    battery_warning_threshold: int = 40
    battery_critical_threshold: int = 20
    battery_degradation_warning: int = 10
    battery_degradation_critical: int = 20
    
    # Temperature thresholds (Celsius)
    temp_min_threshold: float = -20
    temp_max_threshold: float = 80
    temp_warning_threshold: float = 75
    
    # Firmware
    firmware_update_check_enabled: bool = True
    firmware_eol_days: int = 180
    
    # Observability
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_enabled: bool = True
    log_level: str = "INFO"
    
    # JWT
    jwt_secret_key: str = "your-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Feature flags
    enable_advanced_rca: bool = True
    enable_fleet_aggregation: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
