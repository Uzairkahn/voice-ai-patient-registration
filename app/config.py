import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Voice AI Patient Registration API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")


settings = Settings()
