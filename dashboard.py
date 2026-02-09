import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# --- 1. Configuración da Páxina ---
st.set_page_config(
    page_title="AI Stock Analyzer Dashboard",
    page_icon="📈",
    layout="wide"
)

# Definir rutas relativas ao script actual (standalone)
BASE_DIR = Path(__file__).resolve().parent
WATCHLIST_PATH = BASE_DIR / "watchlist.json"
ANALYSIS_DIR = BASE_DIR / "Analisis"

# --- 2. Funcións de Carga de Datos ---
@st.cache_data
def load_watchlist():
    """Carga o ficheiro watchlist.json e convérteo nun DataFrame de Pandas."""
    if not WATCHLIST_PATH.exists():
        st.error(f"Non se atoupa o ficheiro: {WATCHLIST_PATH}")
        return []
    
    try:
        with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Erro ao cargar watchlist: {e}")
        return []

def get_latest_report(ticker: str) -> str:
    """Busca e le o último informe de análise dispoñible para un ticker."""
    ticker_dir = ANALYSIS_DIR / ticker
    if not ticker_dir.exists():
        return "Aínda non hai análises para esta acción."
    
    # Busca todos os ficheiros .md
    files = list(ticker_dir.glob("*.md"))
    if not files:
        return "Aínda non hai análises para esta acción."
    
    # Ordena por nome (o máis recente primeiro, grazas á data no nome)
    files.sort(key=lambda x: x.name, reverse=True)
    latest_file = files[0]
    
    return latest_file.read_text(encoding="utf-8")

# --- 3. Interface Principal (UI) ---

st.title("📈 AI Stock Analyzer Dashboard")
st.markdown("Visión xeral da túa carteira e vixilancia automatizada.")

# Cargar datos
watchlist_data = load_watchlist()

if not watchlist_data:
    st.warning("Non se atoparon datos na watchlist. Asegúrate de ter `watchlist.json` configurado.")
    st.stop()

# Converter a DataFrame para facilitar a manipulación
df = pd.DataFrame(watchlist_data)

# --- 4. Métricas Clave (KPIs) ---
# Calculamos cantas accións hai en cada estado
if "last_action" in df.columns:
    col1, col2, col3, col4 = st.columns(4)
    
    total_stocks = len(df)
    buy_signals = len(df[df["last_action"].str.contains("BUY", case=False, na=False)])
    hold_signals = len(df[df["last_action"].str.contains("HOLD", case=False, na=False)])
    sell_signals = len(df[df["last_action"].str.contains("SELL", case=False, na=False)])
    
    col1.metric("Total Accións", total_stocks)
    col2.metric("Oportunidades (BUY)", buy_signals, delta_color="normal")
    col3.metric("Manter (HOLD)", hold_signals, delta_color="off")
    col4.metric("Vender (SELL)", sell_signals, delta_color="inverse")

st.divider()

# --- 5. Táboa Interactiva ---
st.subheader("📋 Estado da Watchlist")

# Mostramos a táboa con algunhas melloras visuais
st.dataframe(
    df[["ticker", "name", "last_action", "last_run", "frequency_days"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "ticker": "Símbolo",
        "name": "Nome",
        "last_action": st.column_config.TextColumn(
            "Última Acción",
            help="Recomendación da IA baseada na última análise",
            validate="^(BUY|HOLD|SELL|WAIT).*$"
        ),
        "last_run": "Última Análise",
        "frequency_days": st.column_config.NumberColumn(
            "Frecuencia (Días)",
            format="%d días"
        )
    }
)

# --- 6. Detalle da Selección ---
st.divider()
st.subheader("🔍 Detalle da Análise")

selected_ticker = st.selectbox(
    "Selecciona unha acción para ver o informe completo:",
    options=df["ticker"].tolist(),
    format_func=lambda x: f"{x} - {df[df['ticker'] == x]['name'].iloc[0]}"
)

if selected_ticker:
    report_content = get_latest_report(selected_ticker)
    
    with st.expander(f"Ver informe completo de {selected_ticker}", expanded=True):
        st.markdown(report_content)
