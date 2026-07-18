from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Centralized configuration management.
    Values are automatically loaded from environment variables or a .env file.
    """
    # API Keys (loaded from .env)
    HF_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # ML Engine Settings
    CONFIDENCE_THRESHOLD: float = 0.70
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instantiate globally so other modules can import `config`
config = Settings()
