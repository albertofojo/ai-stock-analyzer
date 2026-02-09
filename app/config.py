import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

class Config:
    """Project configuration management."""
    
    # Project Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    RULES_FILE: Path = BASE_DIR / "rules.md"
    ANALYSIS_DIR: Path = BASE_DIR / "Analisis"
    PORTFOLIO_DIR: Path = BASE_DIR / "Cartera" / "Portafolios"
    TICKER_MAP_FILE: Path = BASE_DIR / "ticker_map.json"
    
    # External APIs
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "google").lower() # google, openai
    
    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    
    # OpenAI Compatible (Groq, Ollama, etc)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL") # Optional, e.g. http://localhost:11434/v1
    
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    
    # App Settings
    DELAY_BETWEEN_STOCKS: int = int(os.getenv("DELAY_BETWEEN_STOCKS", "30"))
    
    @classmethod
    def get_rules_content(cls) -> str:
        """Reads the rules file content."""
        if not cls.RULES_FILE.exists():
            raise FileNotFoundError(f"Rules file not found at: {cls.RULES_FILE}")
        return cls.RULES_FILE.read_text(encoding="utf-8")

    @classmethod
    def validate(cls):
        """Validates critical configuration."""
        if cls.LLM_PROVIDER == "google":
            if not cls.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is missing in .env file for provider 'google'")
        elif cls.LLM_PROVIDER == "openai":
             if not cls.OPENAI_API_KEY and not cls.OPENAI_BASE_URL:
                 # Ollama might not need API Key but usually needs Base URL
                 raise ValueError("OPENAI_API_KEY or OPENAI_BASE_URL is required for provider 'openai'")
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {cls.LLM_PROVIDER}. Use 'google' or 'openai'.")
