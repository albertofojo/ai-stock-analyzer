from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class MarketData(BaseModel):
    """Standardized market data structure."""
    ticker: str
    name: str = "Unknown"
    currency: str = "USD"
    current_price: float
    
    # Moving Averages
    ma200: float
    dist_ma200_pct: float
    
    # Drawdown
    high_52w: Optional[float] = None
    drawdown_pct: float = 0.0
    
    # Fundamentals
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    total_debt: Optional[str] = None
    total_cash: Optional[str] = None
    free_cash_flow: Optional[str] = None
    revenue_growth: Optional[str] = None

    @property
    def is_below_ma200(self) -> bool:
        return self.current_price <= self.ma200

class AnalysisResult(BaseModel):
    """Structure for the main interactive AI output."""
    ticker: str
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    action: str  # BUY, HOLD, SELL, WAIT
    reasoning: str
    raw_response: str
    
class PortfolioAnalysis(BaseModel):
    """
    Structured response for portfolio items.
    """
    ticker: str
    action: str
    short_reason: Optional[str] = Field(default="No reason provided", description="Short reason for table (max 10 words)")
    long_reason: str = Field(..., description="Details reasoning")

class Position(BaseModel):
    """Represents a portfolio position."""
    isin: str
    name: str
    quantity: int
