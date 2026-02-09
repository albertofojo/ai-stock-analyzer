import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from app.config import Config

logger = logging.getLogger(__name__)

class WatchlistService:
    """Service to handle the watchlist JSON file."""

    WATCHLIST_FILE: Path = Config.BASE_DIR / "watchlist.json"

    @classmethod
    def load_watchlist(cls) -> List[Dict]:
        """Loads the watchlist from the JSON file."""
        if not cls.WATCHLIST_FILE.exists():
            return []
        try:
            return json.loads(cls.WATCHLIST_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error loading watchlist: {e}")
            return []

    @classmethod
    def save_watchlist(cls, watchlist: List[Dict]):
        """Saves the updated watchlist to the JSON file."""
        try:
            cls.WATCHLIST_FILE.write_text(json.dumps(watchlist, indent=4), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error saving watchlist: {e}")

    @staticmethod
    def should_run_analysis(item: Dict) -> bool:
        """Determines if a stock needs analysis based on frequency."""
        last_run_str = item.get("last_run", "1970-01-01")
        try:
            last_run = datetime.strptime(last_run_str, "%Y-%m-%d")
        except ValueError:
            last_run = datetime(1970, 1, 1)

        days_sincne_last_run = (datetime.now() - last_run).days
        frequency = item.get("frequency_days", 30)

        return days_sincne_last_run >= frequency

    @staticmethod
    def update_item_status(item: Dict, action: str):
        """Updates the item with the latest run date and action."""
        item["last_run"] = datetime.now().strftime("%Y-%m-%d")
        item["last_action"] = action
