# ⚙️ Especificación Funcional: Analista de Bolsa IA

Este documento detalla a lóxica de negocio, o fluxo de datos e as regras de decisión que gobernan o axente de investimento automatizado. O sistema está deseñado para replicar o proceso de toma de decisións dun investidor de estilo "Value/Swing Trading" conservador.

## 1. Arquitectura do Sistema

O proxecto segue unha arquitectura modular baseada en servizos:

1.  **Capa de Servizos (`app/services`):**
    *   `MarketService`: Abstracción sobre `yfinance`.
    *   `LLMService`: Xestión de modelos de IA (Google/OpenAI).
    *   `StorageService`: Xestión do sistema de ficheiros (Análises).
2.  **Capa de Modelos (`app/models.py`):** Definicións estritas de datos (Pydantic).
3.  **Scripts de Execución (`scripts/`):** Puntos de entrada para diferentes modos de uso.

## 2. Fluxo de Datos (Data Flow)

### 2.1. Adquisición de Datos de Mercado (`yfinance`)

O sistema conecta coa API de Yahoo Finance para descargar:

*   **Prezo Actual e Divisa.**
*   **Media Móbil de 200 Sesións (MA200):** *Indicador Calculado*.
*   **Máximo de 52 Semanas:** Para cálculo de *Drawdown*.
*   **Datos Fundamentais:** PER, Débeda Total, Caixa Total, Free Cash Flow.

### 2.2. Sistema de Memoria e Contexto

O axente non analiza a empresa de cero cada vez. Antes de chamar á IA:

1.  O sistema busca no directorio `Analisis/[TICKER]/`.
2.  Recupera as últimas análises para proporcionar contexto histórico á IA.

**Obxectivo Funcional:** Permitir á IA detectar tendencias e validar as súas propias predicións anteriores.

---

## 3. Lóxica de Análise (O "Cerebro")

O axente utiliza un **Prompt do Sistema** (definido en `rules.md`) que actúa como un conxunto de instrucións. A toma de decisións divídese en dúas capas:

### Capa 1: O Filtro Fundamental (Seguridade)

Actúa como unha barreira de entrada.

*   **Regra do PER:** Evitar accións extremadamente caras (>50x), salvo alto crecemento xustificado.
*   **Solvencia:** A débeda neta debe ser manexable respecto ao Fluxo de Caixa Libre.

### Capa 2: O Disparador Técnico (Oportunidade)

Determina o *Timing* (cando comprar).

*   **Media de 200 Sesións (MA200):** Búscanse entradas en zonas de soporte ou reversión á media.
*   **Drawdown:** Valórase a oportunidade en correccións de mercado.

---

## 4. Estrutura do Prompt

Para garantir resultados consistentes, a estrutura que se envía ao LLM é:

1.  **System Persona:** Analista financeiro conservador e obxectivo.
2.  **Knowledge Base:** Regras financeiras (`rules.md`).
3.  **Input Data Block:** Datos numéricos de mercado.
4.  **Memory Block:** Historial recente.
5.  **Output Instructions:** Formato e idioma (Castelán/Galego/Inglés segundo configuración).
