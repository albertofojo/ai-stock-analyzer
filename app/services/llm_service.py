import json
import logging
import google.generativeai as genai
from openai import OpenAI
from app.config import Config
from app.models import MarketData, PortfolioAnalysis, Position

logger = logging.getLogger(__name__)

class LLMService:
    """Service to interact with LLM Providers (Google Gemini or OpenAI-compatible)."""

    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.rules = Config.get_rules_content()

        if self.provider == "google":
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is not set.")
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.MODEL_NAME)
            logger.info(f"Initialized Google Gemini with model: {Config.MODEL_NAME}")
            
        elif self.provider == "openai":
            # For Groq, Ollama, DeepSeek, etc.
            if not Config.OPENAI_API_KEY:
                 # Local models like Ollama might work with empty key, but usually require something
                 logger.warning("OPENAI_API_KEY is empty, ensure your provider supports unauthenticated requests.")
            
            self.client = OpenAI(
                api_key=Config.OPENAI_API_KEY if Config.OPENAI_API_KEY else "dummy",
                base_url=Config.OPENAI_BASE_URL
            )
            self.model_name = Config.MODEL_NAME
            logger.info(f"Initialized OpenAI Compatible Client ({Config.OPENAI_BASE_URL or 'default'}) with model: {self.model_name}")
            
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def analyze_stock(self, data: MarketData, history_context: str) -> str:
        """
        Generates a free-text investment analysis (Interactive Mode).
        """
        prompt = self._build_prompt(data, history_context)
        
        try:
            logger.info(f"Sending request to {self.provider}...")
            
            if self.provider == "google":
                response = self.model.generate_content(prompt)
                return response.text
                
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are Miguel, a conservative financial analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            return f"Error generating analysis: {str(e)}"

    def analyze_portfolio_position(self, position: Position, data: MarketData) -> PortfolioAnalysis:
        """
        Analyzes a specific portfolio position and returns structured JSON data.
        """
        core_prompt = f"""
        {self.rules}
        ---
        ### PORTFOLIO POSITION ANALYSIS
        **Position:** {position.name}
        **Quantity:** {position.quantity}
        **Current Price:** {data.current_price:.2f} {data.currency}
        
        **Technical Data:**
        - MA200: {data.ma200:.2f}
        - Dist to MA200: {data.dist_ma200_pct:.2f}%
        - P/E (Trailing): {data.trailing_pe}
        """

        try:
            if self.provider == "google":
                final_prompt = core_prompt + """
                ### INSTRUCTIONS:
                1. Analyze based on Miguel's rules.
                2. Output valid JSON matching this schema:
                {
                    "ticker": "...",
                    "action": "...",
                    "short_reason": "...",
                    "long_reason": "..."
                }
                """
                response = self.model.generate_content(
                    final_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                result_dict = json.loads(response.text)
                return PortfolioAnalysis(**result_dict)

            elif self.provider == "openai":
                # OpenAI / Groq / Ollama handling
                # Modern OpenAI client supports 'response_format' for JSON
                
                messages = [
                    {"role": "system", "content": "You are a financial analyst. Output strictly in JSON format as requested."},
                    {"role": "user", "content": core_prompt + "\n\nReturn JSON matching schema: {ticker, action, short_reason, long_reason}"}
                ]
                
                # Try to use response_format={"type": "json_object"} if supported
                # Note: Many local/oss models support this if prompted correctly even without the flag
                try:
                    completion = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        response_format={"type": "json_object"}
                    )
                except Exception:
                    # Fallback for models not supporting json_object parameter
                    completion = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages
                    )

                content = completion.choices[0].message.content
                result_dict = json.loads(content)
                
                # Ensure ticker is present (LLM might forget it if not explicitly in prompt context)
                if "ticker" not in result_dict:
                    result_dict["ticker"] = data.ticker
                    
                return PortfolioAnalysis(**result_dict)

        except Exception as e:
            logger.error(f"Error analyzing portfolio position {position.name}: {e}")
            return PortfolioAnalysis(
                ticker=data.ticker or "UNKNOWN",
                action="ERROR",
                short_reason="Analysis Failed",
                long_reason=str(e)
            )

    def generate_global_summary(self, portfolio_data: list) -> str:
        """Generates the executive summary for the whole portfolio."""
        data_json = json.dumps([p if isinstance(p, dict) else p.model_dump() for p in portfolio_data], default=str)
        
        prompt = f"""
        Act as Miguel (Financial Analyst). 
        Review this portfolio data and write a 3-paragraph executive summary in Spanish.
        
        Data:
        {data_json}
        
        Focus on:
        1. Overall Risk.
        2. Specific warnings.
        3. A closing message of prudence.
        """
        
        try:
            if self.provider == "google":
                response = self.model.generate_content(prompt)
                return response.text
                
            elif self.provider == "openai":
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are Miguel, a financial analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return completion.choices[0].message.content
                
        except Exception as e:
            return "Could not generate summary due to AI error."

    def _build_prompt(self, data: MarketData, history_context: str) -> str:
        return f"""
{self.rules}

---

### CURRENT MARKET DATA CHECKPOINT
Target Ticker: **{data.name}** ({data.ticker})

**1. Price Action:**
* Price: {data.current_price:.2f} {data.currency}
* MA200: {data.ma200:.2f}
* Distance to MA200: {data.dist_ma200_pct:.2f}% ({'BELOW' if data.dist_ma200_pct < 0 else 'ABOVE'})
* Drawdown (52w High): {data.drawdown_pct:.2f}%

**2. Fundamentals:**
* Trailing PER: {data.trailing_pe}
* Forward PER: {data.forward_pe}
* Debt: {data.total_debt}
* Cash: {data.total_cash}
* FCF: {data.free_cash_flow}

**3. MEMORY (Previous Context):**
{history_context}

---

### INSTRUCTIONS:
1. **Consistency Check:** Refer to the "Memory" block. Has the thesis changed?
2. **Apply Rules:** Strictly apply the MA200 and PER < 50 rules.
3. **Verdict:** Provide a clear action (BUY, HOLD, SELL, WAIT).
4. **Output Language:** Spanish.
5. **Tone:** Professional but direct (Miguel Persona).
"""
