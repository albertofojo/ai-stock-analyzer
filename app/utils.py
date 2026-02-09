import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
from app.config import Config
from app.models import Position

logger = logging.getLogger(__name__)

class TickerMapper:
    """Handles mapping between portfolio names and Yahoo tickers."""
    
    def __init__(self):
        self._map = self._load_map()

    def _load_map(self) -> Dict[str, str]:
        if Config.TICKER_MAP_FILE.exists():
            try:
                return json.loads(Config.TICKER_MAP_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Error loading ticker map: {e}")
        return {}

    def save_map(self):
        Config.TICKER_MAP_FILE.write_text(json.dumps(self._map, indent=4), encoding="utf-8")

    def get_ticker(self, name: str) -> Optional[str]:
        clean_name = name.strip().upper()
        
        # 1. Exact Match
        if clean_name in self._map:
            return self._map[clean_name]
        
        # 2. Fuzzy / Partial Match (e.g. "TELEFONICA" in "TELEFONICA SA")
        for key, val in self._map.items():
            if key in clean_name or clean_name in key:
                return val
        return None

    def add_mapping(self, name: str, ticker: str):
        self._map[name.strip().upper()] = ticker.strip().upper()
        self.save_map()


class PortfolioParser:
    """Parses portfolio files into structured Position objects."""

    @staticmethod
    def parse_file(filepath: Path) -> List[Position]:
        positions = []
        if not filepath.exists():
            raise FileNotFoundError(f"Portfolio file not found: {filepath}")

        lines = filepath.read_text(encoding="utf-8").splitlines()
        start_reading = False
        
        # Regex: [ISIN] [NAME with spaces] [QUANTITY]
        # Example: ES0178430E18 TELEFONICA 150
        regex = re.compile(r"^([A-Z0-9]+)\s+(.+?)\s+(\d+)$")

        for line in lines:
            line = line.strip()
            
            # Simple header detection logic
            if "Valor" in line and "Nº de Títulos" in line:
                start_reading = True
                continue
            
            if not start_reading or not line or line.startswith("--"):
                continue

            # User requested feature: Skip lines starting with "NO"
            if line.upper().startswith("NO ") or line.upper() == "NO":
                logger.info(f"Skipping line explicitly marked with NO: {line}")
                continue

            match = regex.match(line)
            if match:
                isin, name, qty = match.groups()
                positions.append(Position(
                    isin=isin,
                    name=name.strip(),
                    quantity=int(qty)
                ))
            else:
                # Log parsing failure for debugging but don't crash
                logger.debug(f"Skipping line (no match): {line}")

        return positions
