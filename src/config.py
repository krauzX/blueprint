import os
from dataclasses import dataclass, field

try:
    import streamlit as st
    USE_SECRETS = True
except ImportError:
    USE_SECRETS = False

def get_secret(key, default=""):
    if USE_SECRETS and hasattr(st, 'secrets'):
        try:
            return st.secrets.get(key, default)
        except (FileNotFoundError, KeyError):
            pass
    return os.getenv(key, default)


@dataclass(frozen=True)
class AppConfig:
    APP_NAME: str = "BluePrint"
    APP_SUBTITLE: str = "AI-Powered Water Footprint Analyzer"
    APP_VERSION: str = "1.0.0"
    APP_ICON: str = "💧"
    
    GEMINI_API_KEY: str = field(default_factory=lambda: get_secret("GEMINI_API_KEY", ""))
    GEMINI_MODEL: str = field(
        default_factory=lambda: get_secret("GEMINI_MODEL", "gemini-2.5-flash")
    )
    
    API_TIMEOUT_SECONDS: int = field(
        default_factory=lambda: int(get_secret("API_TIMEOUT_SECONDS", "30"))
    )
    MAX_IMAGE_SIZE_MB: int = field(
        default_factory=lambda: int(get_secret("MAX_IMAGE_SIZE_MB", "10"))
    )
    DAILY_DRINKING_WATER_LITERS: float = 3.0
    SHOWER_LITERS_PER_MINUTE: float = 9.5
    TOILET_FLUSH_LITERS: float = 6.0
    DISHWASHER_CYCLE_LITERS: float = 15.0
    WASHING_MACHINE_CYCLE_LITERS: float = 50.0
    
    PRIMARY_COLOR: str = "#E5B31E"
    SUCCESS_COLOR: str = "#43A047"
    WARNING_COLOR: str = "#FB8C00"
    ERROR_COLOR: str = "#E53935"
    WATER_BLUE: str = "#2196F3"
    WATER_GREEN: str = "#4CAF50"
    WATER_GREY: str = "#9E9E9E"


@dataclass(frozen=True)
class WaterCategoryColors:
    GREEN_WATER: str = "#4CAF50"
    BLUE_WATER: str = "#2196F3"
    GREY_WATER: str = "#757575"


config = AppConfig()
water_colors = WaterCategoryColors()


def validate_config():
    if not config.GEMINI_API_KEY:
        return False, "GEMINI_API_KEY environment variable is not set."
    if len(config.GEMINI_API_KEY) < 10:
        return False, "GEMINI_API_KEY appears to be invalid (too short)."
    return True, None
