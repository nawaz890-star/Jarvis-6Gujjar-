from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parents[1]

ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    # Basic config loaded from environment variables with defaults
    APP_ENV = os.getenv("APP_ENV", "production")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))
    AI_PROVIDER = os.getenv("AI_PROVIDER", "local")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL = os.getenv("GEMINI_API_URL", "")

    DEFAULT_MICROPHONE = os.getenv("DEFAULT_MICROPHONE", "")
    DEFAULT_SPEAKER = os.getenv("DEFAULT_SPEAKER", "")
