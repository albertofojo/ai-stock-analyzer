import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.models import Position, MarketData, PortfolioAnalysis
from app.services.market_service import MarketService
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService
from app.utils import PortfolioParser, TickerMapper

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("🚀 Miguel AI Portfolio Analyzer - Production Ready")
    
    try:
        Config.validate()
        print(f"🤖 Model: {Config.MODEL_NAME}")
        llm_service = LLMService()
        ticker_mapper = TickerMapper()
    except Exception as e:
        logger.critical(f"Initialization Failed: {e}")
        return

    # 1. Select Portfolio File
    files = list(Config.PORTFOLIO_DIR.glob("*.md"))
    if not files:
        logger.error(f"No portfolio files found in {Config.PORTFOLIO_DIR}")
        return

    print("\n📂 Select Portfolio to Analyze:")
    for i, f in enumerate(files):
        print(f"[{i+1}] {f.name}")
        
    try:
        idx = int(input("Number: ")) - 1
        selected_file = files[idx]
    except (ValueError, IndexError):
        logger.error("Invalid selection.")
        return

    # 2. Parse Portfolio
    print(f"📖 Parsing {selected_file.name}...")
    positions = PortfolioParser.parse_file(selected_file)
    print(f"🔍 Found {len(positions)} positions.")

    analysis_results: List[Dict] = [] # Stores data for final report
    portfolio_summary_data = [] # Stores data for global summary

    # 3. Process Positions
    for i, pos in enumerate(positions):
        print(f"\n[{i+1}/{len(positions)}] Processing: {pos.name}")
        
        # Resolve Ticker
        ticker = ticker_mapper.get_ticker(pos.name)
        
        if not ticker:
            print(f"⚠️ Ticker not found for: {pos.name}")
            manual = input(f"   Enter Ticker manually (or ENTER to skip): ").strip().upper()
            if manual:
                ticker = manual
                ticker_mapper.add_mapping(pos.name, ticker)
            else:
                analysis_results.append({
                    "name": pos.name,
                    "price": "-",
                    "dist_ma200": "-",
                    "per": "-",
                    "action": "N/A",
                    "reason": "Ticker Unknown"
                })
                continue
        
        # Fetch Data
        market_data = MarketService.get_market_data(ticker)
        
        if not market_data:
            analysis_results.append({
                "name": pos.name,
                "price": "-",
                "dist_ma200": "-",
                "per": "-",
                "action": "ERROR",
                "reason": "Market Data Failed"
            })
            continue

        # Analyze with LLM
        print(f"🤖 Analyzing {ticker}...")
        analysis: PortfolioAnalysis = llm_service.analyze_portfolio_position(pos, market_data)
        
        # Store Result
        analysis_results.append({
            "name": pos.name,
            "price": f"{market_data.current_price:.4f} {market_data.currency}",
            "dist_ma200": f"{market_data.dist_ma200_pct:.1f}%",
            "per": str(market_data.trailing_pe) if market_data.trailing_pe else "N/A",
            "action": f"**{analysis.action}**",
            "reason": analysis.short_reason
        })

        # Data for Global Summary
        portfolio_summary_data.append({
            "ticker": ticker,
            "name": pos.name,
            "action": analysis.action,
            "market_data": market_data.model_dump()
        })
        
        # Rate Limiting
        if i < len(positions) - 1:
            print(f"⏳ Waiting {Config.DELAY_BETWEEN_STOCKS}s...")
            time.sleep(Config.DELAY_BETWEEN_STOCKS)

    # 4. Generate Global Summary
    print("\n🧠 Generating Executive Summary...")
    global_summary = llm_service.generate_global_summary(portfolio_summary_data)

    # 5. Generate Report
    date_str = datetime.now().strftime("%Y%m%d")
    report_filename = f"{date_str}_new_analysis.md"
    report_path = Config.ANALYSIS_DIR / report_filename
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Portfolio Analysis - {date_str}\n\n")
        f.write("## 1. Executive Summary (Miguel AI)\n")
        f.write(global_summary + "\n\n")
        f.write("## 2. Position Details\n")
        f.write("| Ticker | Price | Dist MA200 | PER | Action | Reason |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for row in analysis_results:
            line = f"| {row['name']} | {row['price']} | {row['dist_ma200']} | {row['per']} | {row['action']} | {row['reason']} |"
            f.write(line + "\n")

    print(f"\n✅ Analysis Complete! Report saved to:\n{report_path}")

if __name__ == "__main__":
    main()
