import os
import sys
import json
import re
import glob
import datetime
import time
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
DELAY_BETWEEN_STOCKS = 30  # Segundos entre cada análise de acción

# Mapeo inicial baseado no teu exemplo (Podes amplialo no ticker_map.json)
DEFAULT_TICKER_MAP = {
    "BERKELEY": "BKY.MC",
    "ABENGOA.B": "ABG.P.MC", # Ojo, cotización complexa
    "LINEA DIRECT": "LDA.MC",
    "INTERCITY": "CITY.MC", # BME Growth
    "NATURGY": "NTGY.MC",
    "AUDAX": "ADX.MC",
    "D.FELGUERA": "MDF.MC",
    "PHARMAMAR": "PHM.MC",
    "INT.CONS.AIR": "IAG.MC",
    "TELEFONICA": "TEF.MC",
    "TELEPERFORMANCE": "TEP.PA",
    "PLUXEE FRANCE SA": "PLX.PA",
    "EURONET WORLDWIDE INC": "EEFT",
    "PAYPAL HOLDINGS INC": "PYPL",
    "QFIN HLDGS SP ADS-A": "QFIN"
}

MAP_FILE = "ticker_map.json"

# Configurar Gemini
if not API_KEY:
    print("❌ Falta GOOGLE_API_KEY no .env")
    sys.exit(1)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# --- FUNCIÓNS DE MAPEO ---
def load_ticker_map():
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_TICKER_MAP

def save_ticker_map(mapping):
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4)

def resolve_ticker(name, mapping):
    # Limpeza básica do nome
    clean_name = name.strip().upper()
    
    # 1. Busca directa
    if clean_name in mapping:
        return mapping[clean_name]
    
    # 2. Busca parcial (se "TELEFONICA" está en "TELEFONICA SA")
    for key, val in mapping.items():
        if key in clean_name or clean_name in key:
            return val
            
    return None

# --- PARSEO DO FICHEIRO DE CARTEIRA ---
def parse_portfolio_file(filepath):
    positions = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    start_reading = False
    
    # Expresión regular para: [ISIN] [NOME CON ESPAZOS] [CANTIDADE]
    # Exemplo: ES0178430E18 TELEFONICA 150
    regex = r"^([A-Z0-9]+)\s+(.+?)\s+(\d+)$"
    
    for line in lines:
        line = line.strip()
        
        # Detectar onde empezan os datos (saltar cabeceiras)
        if "Valor" in line and "Nº de Títulos" in line:
            start_reading = True
            continue
            
        if not start_reading or not line or line.startswith("--"):
            continue
            
        match = re.match(regex, line)
        if match:
            isin, name, qty = match.groups()
            positions.append({
                "isin": isin,
                "name": name.strip(),
                "quantity": int(qty)
            })
            
    return positions

# --- OBTENCIÓN DE DATOS DE MERCADO ---
def fetch_mini_data(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y") # Só necesitamos 1 ano para ver tendencia e MA200
        
        if hist.empty: return None
        
        price = hist['Close'].iloc[-1]
        ma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        if pd.isna(ma200): ma200 = price # Se non hai suficientes datos
        
        dist_ma200 = ((price - ma200) / ma200) * 100
        
        info = t.info
        return {
            "price": price,
            "currency": info.get('currency', '?'),
            "ma200": ma200,
            "dist_ma200": dist_ma200,
            "per": info.get('trailingPE', 'N/A'),
            "f_per": info.get('forwardPE', 'N/A')
        }
    except:
        return None

# --- ANÁLISE CON IA ---
def analyze_portfolio_item(pos, market_data, system_prompt):
    if not market_data:
        return f"| {pos['name']} | - | - | - | ERROR | No market data |"

    # Calculamos o valor total da posición
    total_value = pos['quantity'] * market_data['price']
    
    # Prompt optimizado en INGLÉS para máxima coherencia
    user_message = f"""
    This is a REAL position in my portfolio. I ALREADY OWN these shares.
    Analyze the best action to take based on Miguel's rules.
    
    STOCK DATA:
    - Name: {pos['name']}
    - Quantity: {pos['quantity']}
    - Price: {market_data['price']:.4f} {market_data['currency']}
    - MA200: {market_data['ma200']:.4f}
    - Distance to MA200: {market_data['dist_ma200']:.2f}%
    - PER: {market_data['per']}
    
    TASK:
    Decide the action: HOLD, ACCUMULATE (Buy more), TRIM (Sell partial), EXIT (Sell all), or WAIT TO SELL AT [Price].
    
    OUTPUT FORMAT (Markdown Row):
    | {pos['name']} | {market_data['price']:.4f} | {market_data['dist_ma200']:.1f}% | {market_data['per']} | **ACTION** | Reason + Target if applicable (max 12 words) |
    
    Style: Miguel (Direct, focused on capital protection). Reasoning in Spanish.
    """

    full_prompt = system_prompt + "\n\n" + user_message

    try:
        res = model.generate_content(full_prompt)
        return res.text.strip().replace("\n", "")
    except Exception as e:
        return f"| {pos['name']} | Error | - | - | ERROR | {str(e)} |"


def generate_global_summary(positions_data):
    # Unha segunda chamada para unha conclusión xeral
    prompt = f"""
    Tes esta carteira de accións:
    {json.dumps(positions_data, indent=2)}
    
    Dame unha conclusión xeral de 3 parágrafos en castelán (estilo Miguel):
    1. Calidade xeral da carteira (estamos moi expostos a risco ou ben?).
    2. Aviso sobre as accións máis perigosas (PER alto ou moi lonxe da MA200).
    3. Unha mensaxe de ánimo ou prudencia.
    """
    try:
        res = model.generate_content(prompt)
        return res.text
    except:
        return "Non se puido xerar o resumo global."

def cargar_reglas(nombre_archivo="rules.md"):
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Erro: Non se atopa o ficheiro '{nombre_archivo}'.")
        return None


# --- MAIN ---
if __name__ == "__main__":

    reglas = cargar_reglas("rules.md")
    if not reglas: sys.exit(1)

    # 1. Seleccionar Ficheiro
    folder = os.path.join("Cartera", "Portafolios")
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"📁 Cartafol creado: {folder}. Pon aí os teus ficheiros .md")
        sys.exit()
        
    files = glob.glob(os.path.join(folder, "*.md"))
    if not files:
        print("❌ Non hai ficheiros en /Cartera/Portafolios/")
        sys.exit()
        
    print("\n📂 Selecciona a carteira a analizar:")
    for i, f in enumerate(files):
        print(f"[{i+1}] {os.path.basename(f)}")
        
    try:
        idx = int(input("Número: ")) - 1
        selected_file = files[idx]
    except:
        print("Opción inválida.")
        sys.exit()

    # 2. Ler e Mapear
    positions = parse_portfolio_file(selected_file)
    mapping = load_ticker_map()
    
    print(f"\n🔍 Analizando {len(positions)} posicións...")
    
    analysis_rows = []
    enriched_data = [] # Para o resumo final
    
    for pos in positions:
        ticker = resolve_ticker(pos['name'], mapping)
        
        if not ticker:
            print(f"⚠️ Ticker non atopado para: {pos['name']}")
            manual = input(f"   Introduce o Ticker manual para {pos['name']} (ou ENTER para saltar): ").strip().upper()
            if manual:
                ticker = manual
                mapping[pos['name']] = ticker # Gardar para a próxima
                save_ticker_map(mapping)
            else:
                analysis_rows.append(f"| {pos['name']} | - | - | - | N/A | Ticker descoñecido |")
                continue
                
        print(f"   Processing: {pos['name']} -> {ticker}")
        data = fetch_mini_data(ticker)
        
        if data:
            row = analyze_portfolio_item(pos, data, reglas)
            analysis_rows.append(row)
            
            # Gardamos datos para o resumo final
            enriched_data.append({
                "name": pos['name'],
                "value": pos['quantity'] * data['price'],
                "dist_ma200": data['dist_ma200'],
                "per": data['per']
            })
        else:
            analysis_rows.append(f"| {pos['name']} | - | - | - | ERROR | Erro en datos |")

        if i < len(positions) - 1:
            time.sleep(DELAY_BETWEEN_STOCKS)

    # 3. Xerar Informe
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    report_filename = f"{date_str}_analisis_cartera.md"
    report_path = os.path.join("Cartera", "Analisis", report_filename)
    
    if not os.path.exists(os.path.dirname(report_path)):
        os.makedirs(os.path.dirname(report_path))
        
    global_summary = generate_global_summary(enriched_data)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Análise de Carteira - {date_str}\n\n")
        f.write("## 1. Resumo Executivo (Miguel AI)\n")
        f.write(global_summary + "\n\n")
        f.write("## 2. Detalle de Posicións\n")
        f.write("| Valor | Prezo | Dist. MA200 | PER | ACCIÓN | Razón |\n")
        f.write("|---|---|---|---|---|---|\n")
        for row in analysis_rows:
            # Limpeza por se a IA mete pipes extra
            clean_row = row.replace("| |", "|").strip() 
            f.write(clean_row + "\n")
            
    print(f"\n✅ Análise completada! Ficheiro gardado en:\n{report_path}")