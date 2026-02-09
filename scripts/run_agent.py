import sys
import os
from datetime import datetime

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.services.market_service import MarketService
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService

def main():
    print("🚀 AI Stock Analyzer - Interactive Mode")
    print(f"Loaded Rules from: {Config.RULES_FILE}")
    
    # Initialize Services
    try:
        Config.validate()
        llm_service = LLMService()
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    while True:
        ticker_input = input("\n📝 Enter Ticker (e.g., TEF.MC, GOOGL) or 'exit': ").strip().upper()
        
        if ticker_input in ['EXIT', 'SALIR', 'QUIT']:
            print("👋 Bye!")
            break
            
        if not ticker_input:
            continue

        print(f"🔍 Fetching data for {ticker_input}...")
        
        # 1. Get Data
        market_data = MarketService.get_market_data(ticker_input)
        if not market_data:
            print(f"❌ Could not fetch data for {ticker_input}. Check the ticker symbol.")
            continue
            
        # 2. Get Context
        print("📖 Reading history...")
        history = StorageService.get_recent_history(ticker_input)
        
        # 3. Analyze
        print("🤖 Analyzing with Gemini...")
        analysis_text = llm_service.analyze_stock(market_data, history)
        
        # 4. Output & Save
        print("\n" + "="*50)
        print(analysis_text)
        print("="*50)
        
        saved_path = StorageService.save_analysis(ticker_input, analysis_text)
        print(f"✅ Analysis saved to: {saved_path}")

if __name__ == "__main__":
    main()
