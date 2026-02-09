# 📈 AI Stock Analyzer (Value & Swing Trading)

Este proxecto é un axente de intelixencia artificial deseñado para automatizar a análise fundamental e técnica de accións en bolsa. O sistema baséase en filosofías de investimento de valor e *swing trading* conservador, aplicando regras estritas para detectar oportunidades.

O obxectivo é ter un copiloto financeiro obxectivo, capaz de procesar grandes cantidades de datos e emitir veredictos fundamentados sen sesgos emocionais.

## 🚀 Funcionalidades Principais

*   **Análise Automatizada:** O axente segue regras estritas (definidas en `rules.md`) sobre PER máximo, niveis de débeda e zonas de compra técnica.
*   **Datos en Tempo Real:** Conexión con Yahoo Finance (`yfinance`) para obter prezos, medias móbiles e fundamentais.
*   **Multi-Modelo (LLM Agnostic):** Soporta tanto **Google Gemini** como modelos compatibles con **OpenAI** (Groq, Ollama, DeepSeek).
*   **Modo Vixilancia (Watchlist):** Script autónomo que monitoriza unha lista de accións e alerta de cambios de tendencia.
*   **Análise de Carteira:** Capacidade de procesar carteiras completas e xerar informes executivos estructurados.
*   **Persistencia:** Xera informes históricos en Markdown e mantén un estado das análises.

## 🛠️ Requisitos Técnicos

*   **Python 3.10+**
*   Unha API Key dun provedor de LLM (Google Gemini, OpenAI, Groq, etc) ou un modelo local (Ollama).

## ⚙️ Instalación e Uso

1.  **Clonar o repositorio:**
    ```bash
    git clone https://github.com/albertofojo/ai-stock-analyzer.git
    cd ai-stock-analyzer
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuración:**
    Crea un ficheiro `.env` na raíz (podes usar o exemplo proporcionado no código como guía) e configura o teu provedor de IA.

4.  **Uso Interactivo (Unha acción):**
    ```bash
    python scripts/run_agent.py
    ```

5.  **Análise de Carteira:**
    ```bash
    python scripts/run_portfolio.py
    ```

6.  **Modo Vixilancia (Automático):**
    Edita `watchlist.json` e executa:
    ```bash
    python scripts/run_watchlist.py
    ```

## 📂 Estrutura do Proxecto

```text
/
├── app/
│   ├── config.py          # Configuración central
│   ├── models.py          # Definición de datos (Pydantic)
│   ├── services/          # Services (LLM, Market, Storage)
│   └── utils.py           # Utilidades
├── scripts/
│   ├── run_agent.py       # Modo Interactivo
│   ├── run_portfolio.py   # Modo Carteira
│   └── run_watchlist.py   # Modo Vixilancia
├── Analisis/              # Informes xerados
├── Cartera/               # Ficheiros de carteira (.md)
├── watchlist.json         # Configuración de vixilancia
├── rules.md               # Prompt do Sistema (Regras de Investimento)
└── .env                   # Segredos (NON SUBIR A GIT)
```

## ⚠️ Aviso Legal (Disclaimer)

Esta ferramenta é un proxecto de software con fins educativos. **O axente de IA pode cometer erros.**
*   Non constitúe asesoramento financeiro profesional.
*   Utilízao baixo o teu propio risco.
