import os
import sys
import datetime
import glob
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN ---
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
# Si falla el modelo preview, usa 'gemini-1.5-flash'
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash") 

if not API_KEY:
    print("❌ ERROR: Falta GOOGLE_API_KEY en el archivo .env")
    sys.exit(1)

genai.configure(api_key=API_KEY)
try:
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"🤖 Cerebro activado: {MODEL_NAME}")
except Exception as e:
    print(f"❌ Error modelo: {e}")
    sys.exit(1)

# --- 2. GESTIÓN DE REGLAS ---
def cargar_reglas(nombre_archivo="rules.md"):
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ No encuentro '{nombre_archivo}'.")
        return None

# --- 3. GESTIÓN DE MEMORIA (NUEVO) ---
def get_previous_history(ticker, limit=2):
    """
    Busca análisis anteriores en la carpeta del ticker,
    los ordena por fecha y devuelve el texto de los últimos 'limit' análisis.
    """
    base_folder = "Analisis"
    ticker_folder = os.path.join(base_folder, ticker)
    
    if not os.path.exists(ticker_folder):
        return "No previous analysis found. This is the first time we look at this stock."

    # Buscar todos los .md
    files = glob.glob(os.path.join(ticker_folder, "*.md"))
    
    if not files:
        return "No previous analysis found."

    # Ordenar por fecha de modificación (o por nombre, ya que tienen fecha YYYYMMDD)
    # Usamos nombre para que el orden sea cronológico estricto del nombre del archivo
    files.sort(reverse=True) # El más reciente primero ('2025...' antes que '2024...')
    
    # Seleccionar los últimos N
    recent_files = files[:limit]
    
    history_context = ""
    for file_path in recent_files:
        try:
            filename = os.path.basename(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                history_context += f"\n--- PREVIOUS ANALYSIS ({filename}) ---\n{content}\n"
        except Exception as e:
            print(f"⚠️ No se pudo leer historial {file_path}: {e}")

    return history_context

# --- 4. OBTENCIÓN DE DATOS ---
def fetch_data(ticker_symbol):
    print(f"📥 Descargando datos de {ticker_symbol}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="2y")
        
        if hist.empty: return None, "Ticker no encontrado o sin datos."
            
        current_price = hist['Close'].iloc[-1]
        
        # Medias
        hist['MA200'] = hist['Close'].rolling(window=200).mean()
        ma200_val = hist['MA200'].iloc[-1] if not pd.isna(hist['MA200'].iloc[-1]) else 0
        dist_ma200_pct = ((current_price - ma200_val) / ma200_val) * 100 if ma200_val else 0
        
        # Drawdown
        high_52w = hist['Close'].tail(252).max()
        drawdown_pct = ((current_price - high_52w) / high_52w) * 100
        
        info = ticker.info
        return {
            "name": info.get('longName', ticker_symbol),
            "ticker": ticker_symbol,
            "currency": info.get('currency', 'USD'),
            "current_price": current_price,
            "ma200": ma200_val,
            "dist_ma200_pct": dist_ma200_pct,
            "drawdown_from_high": drawdown_pct,
            "trailing_pe": info.get('trailingPE', 'N/A'),
            "forward_pe": info.get('forwardPE', 'N/A'),
            "total_debt": info.get('totalDebt', 'N/A'),
            "total_cash": info.get('totalCash', 'N/A'),
            "free_cash_flow": info.get('freeCashflow', 'N/A'),
            "revenue_growth": info.get('revenueGrowth', 'N/A')
        }, None
    except Exception as e:
        return None, str(e)

# --- 5. GENERACIÓN CON IA ---
def generate_analysis(data, system_prompt, history_context):
    
    user_message = f"""
    Please analyze the company **{data['name']}** ({data['ticker']}).
    
    ### 1. CURRENT MARKET DATA:
    * **Price:** {data['current_price']:.2f} {data['currency']}
    * **MA200:** {data['ma200']:.2f}
    * **Distance to MA200:** {data['dist_ma200_pct']:.2f}%
    * **Drawdown:** {data['drawdown_from_high']:.2f}%
    
    ### 2. FUNDAMENTAL DATA:
    * **Trailing PER:** {data['trailing_pe']}
    * **Forward PER:** {data['forward_pe']}
    * **Total Debt:** {data['total_debt']}
    * **Total Cash:** {data['total_cash']}
    * **Free Cash Flow:** {data['free_cash_flow']}
    * **Revenue Growth:** {data['revenue_growth']}

    ### 3. PREVIOUS ANALYSIS HISTORY (MEMORY):
    {history_context}

    ### INSTRUCTIONS:
    1.  **Consistency Check:** Start by referencing the previous analysis (if it exists). Has the situation improved or worsened? Did the price reach the target mentioned before?
    2.  **Filter Check:** Apply the PER < 50 and Debt rules.
    3.  **Technical Check:** Is it in a buy zone relative to MA200?
    4.  **Verdict:** Buy, Wait, or Sell? 
    5.  **Tone:** Use Miguel's persona (direct, cautious, focus on not losing money).
    6.  **Language:** Spanish.
    """

    full_prompt = system_prompt + "\n\n" + user_message

    print("🧠 Miguel AI está pensando (comparando con el pasado)...")
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error API: {e}"

# --- 6. GUARDADO ---
def save_analysis_to_file(ticker, content):
    base_folder = "Analisis"
    ticker_folder = os.path.join(base_folder, ticker)
    if not os.path.exists(ticker_folder): os.makedirs(ticker_folder)
    
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"{ticker}-{today_str}.md"
    full_path = os.path.join(ticker_folder, filename)
    
    counter = 2
    while os.path.exists(full_path):
        full_path = os.path.join(ticker_folder, f"{ticker}-{today_str}_{counter}.md")
        counter += 1
        
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Guardado en: {full_path}")

# --- MAIN ---
if __name__ == "__main__":
    reglas = cargar_reglas()
    if not reglas: sys.exit(1)

    while True:
        t = input("\nTicker (ej: GOOGL, TEF.MC) o 'salir': ").upper().strip()
        if t == 'SALIR': break
        if not t: continue

        data, err = fetch_data(t)
        if err:
            print(f"❌ {err}")
            continue

        # Recuperar memoria
        historial = get_previous_history(t)
        
        # Generar
        analisis = generate_analysis(data, reglas, historial)
        
        print("\n" + "—"*40)
        print(analisis)
        print("—"*40)
        
        save_analysis_to_file(t, analisis)