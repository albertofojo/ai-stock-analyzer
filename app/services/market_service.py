import yfinance as yf
import pandas as pd
import logging
from typing import Optional
from app.models import MarketData

logger = logging.getLogger(__name__)

class MarketService:
    """Service to fetch and process market data."""

    @staticmethod
    def get_market_data(ticker_symbol: str) -> Optional[MarketData]:
        """
        Fetches market data for a given ticker.
        Returns a MarketData object or None if data cannot be retrieved.
        """
        try:
            logger.info(f"Fetching data for {ticker_symbol}...")
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch 2 years of history for MA200 calculation
            hist = ticker.history(period="2y")
            
            if hist.empty:
                logger.warning(f"No history found for {ticker_symbol}")
                return None
                
            current_price = hist['Close'].iloc[-1]
            
            # Calculate Moving Averages (MA200)
            # We need at least 200 data points
            if len(hist) >= 200:
                hist['MA200'] = hist['Close'].rolling(window=200).mean()
                ma200_val = hist['MA200'].iloc[-1]
            else:
                # If not enough data, fallback to current price or specific handling
                ma200_val = current_price 
            
            # Handle NaN in MA200 (if recent IPO, etc.)
            if pd.isna(ma200_val):
                ma200_val = current_price

            dist_ma200_pct = ((current_price - ma200_val) / ma200_val) * 100 if ma200_val else 0.0
            
            # Calculate Drawdown (from 52-week high)
            # Last 252 trading days (~1 year)
            high_52w = hist['Close'].tail(252).max()
            drawdown_pct = ((current_price - high_52w) / high_52w) * 100 if high_52w else 0.0
            
            # Fetch Fundamental Info
            info = ticker.info
            
            return MarketData(
                ticker=ticker_symbol,
                name=info.get('longName', ticker_symbol),
                currency=info.get('currency', 'USD'),
                current_price=current_price,
                ma200=ma200_val,
                dist_ma200_pct=dist_ma200_pct,
                high_52w=high_52w,
                drawdown_pct=drawdown_pct,
                trailing_pe=info.get('trailingPE'),
                forward_pe=info.get('forwardPE'),
                total_debt=str(info.get('totalDebt', 'N/A')),
                total_cash=str(info.get('totalCash', 'N/A')),
                free_cash_flow=str(info.get('freeCashflow', 'N/A')),
                revenue_growth=str(info.get('revenueGrowth', 'N/A'))
            )
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker_symbol}: {e}")
            return None
