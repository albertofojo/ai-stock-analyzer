from datetime import datetime
from pathlib import Path
from typing import List
from app.config import Config

class StorageService:
    """Service to handle file system operations for analysis history."""

    @staticmethod
    def get_ticker_dir(ticker: str) -> Path:
        """Helper to get the directory for a specific ticker."""
        ticker_dir = Config.ANALYSIS_DIR / ticker
        if not ticker_dir.exists():
            ticker_dir.mkdir(parents=True, exist_ok=True)
        return ticker_dir

    @classmethod
    def get_recent_history(cls, ticker: str, limit: int = 2) -> str:
        """
        Retrieves the content of the most recent analysis files for context.
        """
        ticker_dir = cls.get_ticker_dir(ticker)
        
        # Get all .md files
        files = list(ticker_dir.glob("*.md"))
        
        if not files:
            return "No previous analysis found. This is the first time we look at this stock."

        # Sort by name (descending) assuming YYYYMMDD prefix format
        # e.g. TEF.MC-20231025.md
        files.sort(key=lambda p: p.name, reverse=True)
        
        recent_files = files[:limit]
        history_context = ""
        
        for file_path in recent_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                history_context += f"\n--- PREVIOUS ANALYSIS ({file_path.name}) ---\n{content}\n"
            except Exception as e:
                return f"Error reading history file: {e}"
                
        return history_context

    @classmethod
    def save_analysis(cls, ticker: str, content: str, suffix: str = "") -> Path:
        """
        Saves the analysis to a file with versioning if needed.
        suffix: Optional string to append to filename (e.g. "-WATCH")
        """
        ticker_dir = cls.get_ticker_dir(ticker)
        today_str = datetime.now().strftime("%Y%m%d")
        
        # Base filename: TICKER-YYYYMMDD[-SUFFIX].md
        base_name = f"{ticker}-{today_str}{suffix}"
        file_path = ticker_dir / f"{base_name}.md"
        
        # Versioning handling
        counter = 2
        while file_path.exists():
            file_path = ticker_dir / f"{base_name}_{counter}.md"
            counter += 1
            
        file_path.write_text(content, encoding="utf-8")
        return file_path
