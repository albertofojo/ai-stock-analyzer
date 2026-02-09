# 📈 Analista de Bolsa IA (Metodoloxía "Cosas de Bolsa")

Este proxecto é un axente de intelixencia artificial deseñado para automatizar a análise fundamental e técnica de accións en bolsa. O "cerebro" do sistema baséase estritamente na filosofía de investimento de valor e *swing trading* conservador destilada dos coñecementos de **Miguel (Canle de Youtube "Cosas de Bolsa")**.

O obxectivo é ter un copiloto financeiro que non se deixe levar polas emocións, aplicando regras heurísticas claras para detectar oportunidades de investimento seguras.

## 🚀 Funcionalidades Principais

* **Destilación de Coñecemento Experto:** O axente non "alucina"; segue unhas regras estritas (definidas en `rules.md`) sobre PER máximo, niveis de débeda aceptables e zonas de compra técnica.
* **Datos en Tempo Real:** Conexión directa con Yahoo Finance (`yfinance`) para obter prezo actual, medias móbiles, PER, Cash Flow e débeda.
* **Motor de IA (LLM):** Utiliza os modelos **Google Gemini** (1.5 Flash ou Pro) para interpretar os datos numéricos e redactar un veredicto en linguaxe natural e estilo directo.
* **Sistema de Memoria:** O axente é capaz de ler as análises que fixo no pasado sobre unha empresa. Antes de emitir un novo xuízo, compara a situación actual coa anterior ("*Mellorou a débeda dende o mes pasado?*", "*O prezo achegouse á media de 200?*").
* **Persistencia de Datos:** Xera automaticamente informes en formato Markdown (`.md`) organizados por `Ticker` e data.

## 🧠 A Metodoloxía (O "Filtro" e o "Disparador")

O sistema funciona en dúas fases, imitando o proceso mental do experto humano:

1. **O Filtro (Fundamental):**
* **PER < 50:** Regra de ouro. Descartar accións extremadamente caras.
* **Test do Algodón:** A débeda neta debe ser pagable co Free Cash Flow en menos de 3-4 anos.
* **Marxes:** Vixilancia de compresión de marxes e estancamento de ingresos.


2. **O Disparador (Técnico):**
* **Media de 200 Sesións (MA200):** O axente busca compras por baixo ou tocando a media. Alerta sobre a "Separación Máxima" (sobrecompra).
* **Drawdown:** Análise da caída dende máximos de 52 semanas.



## 🛠️ Requisitos Técnicos

* **Python 3.8+**
* Unha **API Key de Google AI Studio** (Gratuíta).

### Librarías necesarias

O proxecto utiliza as seguintes dependencias:

* `google-generativeai`: Para conectar co cerebro da IA.
* `yfinance`: Para a descarga de datos financeiros.
* `pandas`: Para o cálculo de indicadores técnicos.
* `python-dotenv`: Para a xestión segura de claves.

## ⚙️ Instalación e Uso

1. **Clonar o repositorio:**
```bash
git clone https://github.com/o-teu-usuario/analista-bolsa-ia.git
cd analista-bolsa-ia

```


2. **Instalar dependencias:**
```bash
pip install yfinance pandas google-generativeai python-dotenv

```


3. **Configuración:**
Crea un ficheiro chamado `.env` na raíz do proxecto e engade as túas credenciais:
```ini
GOOGLE_API_KEY="A_TUA_CLAVE_AIza..."
MODEL_NAME="gemini-1.5-flash"

```


4. **Executar o Axente:**
```bash
python agent.py

```


O programa pedirache o *Ticker* da empresa (ex: `ITX.MC` para Inditex, `GOOGL` para Google).

## 📂 Estrutura do Proxecto

```text
/
├── agent.py           # O script principal (Lóxica, IA e Xestión de ficheiros)
├── rules.md           # Base de coñecemento (Prompt do Sistema con todas as regras)
├── .env               # Ficheiro de configuración (API Keys - NON SUBIR A GIT)
└── Analisis/          # Cartafol xerado automaticamente
    ├── TEF.MC/        # Subcartafol por empresa
    │   ├── TEF.MC-20231025.md
    │   └── TEF.MC-20231102.md
    └── ...

```

## ⚠️ Aviso Legal (Disclaimer)

Esta ferramenta é un proxecto de software con fins educativos e experimentais. **O axente de IA pode cometer erros de cálculo ou alucinacións.**

* Non constitúe asesoramento financeiro profesional.
* Os rendementos pasados non garanten rendementos futuros.
* Utilízao baixo o teu propio risco e contrasta sempre a información.

