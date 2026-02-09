# 🤖 Automatización con GitHub Actions

Este proxecto inclúe un fluxo de traballo automatizado para realizar a vixilancia de accións na nube, sen necesidade de ter o teu ordenador acendido.

## 1. Como funciona

O ficheiro de configuración atópase en `.github/workflows/daily_analysis.yml`.

1.  **Activación:**
    *   **Automática:** Execútase tódolos días ás 08:00 UTC.
    *   **Manual:** Podes lanzalo dende a pestana "Actions" en GitHub pulsando "Run workflow".
2.  **Execución:**
    *   O servidor de GitHub descarga o teu código.
    *   Instala Python e as librarías necesarias.
    *   Executa `python scripts/run_watchlist.py`.
    *   O script lee `watchlist.json`, comproba que accións toca analizar hoxe, e consulta á IA.
3.  **Persistencia:**
    *   Se o script xera novas análises ou actualiza as datas en `watchlist.json`, **o "bot" fai un commit e sube os cambios ao teu repositorio automaticamente**.
    *   Poderás ver os novos ficheiros aparecendo na carpeta `Analisis/`.
    *   **Formato de ficheiro:** As análises automáticas terán o sufixo `-WATCH` (ex: `TEF.MC-20240210-WATCH.md`) para distinguilas das manuais.

## 2. Configuración Necesaria (Seguridade)

Para que isto funcione, GitHub necesita permiso para usar a túa API Key (que non está no repositorio por seguridade).

### Pasos para configurar os Segredos:

1.  Vai ao teu repositorio en GitHub.
2.  Entra en **Settings** > **Secrets and variables** > **Actions**.
3.  Pulsa **New repository secret**.
4.  Crea os seguintes segredos (segundo o provedor que uses):

| Nome | Valor (Exemplo) | Descrición |
| :--- | :--- | :--- |
| `GOOGLE_API_KEY` | `AIzaSy...` | Obrigatorio se usas Gemini. |
| `OPENAI_API_KEY` | `sk-...` ou `gsk_...` | Obrigatorio se usas OpenAI ou Groq. |

### Pasos para configurar Variables (Opcional):

Se queres cambiar a configuración sen editar o código, vai a **Settings** > **Secrets and variables** > **Actions** > **Variables** e crea:

| Nome | Valor por defecto | Descrición |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `google` | Podes cambialo a `openai` para usar Groq/Outros. |
| `MODEL_NAME` | `gemini-1.5-flash` | Podes cambialo polo modelo que desexes. |
| `OPENAI_BASE_URL` | (Baleiro) | Se usas Groq (`https://api.groq.com/openai/v1`) ou outro endpoint. |

## 3. Monitorización

Podes ver o historial de execucións na pestana **Actions** do teu repositorio.
*   ✅ **Verde:** A análise completouse correctamente.
*   ❌ **Vermello:** Houbo un erro (podes pulsar para ver os logs e depurar).

## 4. Visualización de Resultados (Dashboard)

Para ver o estado da túa carteira e ler os informes xerados sen ter que navegar polos ficheiros do repositorio, creouse un **Dashboard Web** interactivo.

### 💻 Execución Local

Podes executar o panel no teu propio ordenador:

1.  Asegúrate de ter as dependencias instaladas: `pip install -r requirements.txt` (inclúe `streamlit`).
2.  Executa o seguinte comando:
    ```bash
    python -m streamlit run dashboard.py
    ```
3.  Abrirase o teu navegador en `http://localhost:8501`.

### ☁️ Despregue na Nube (Streamlit Community Cloud)

A forma recomendada de usar isto é aloxalo gratuitamente na nube de Streamlit, conectado ao teu repositorio GitHub. Así terás unha URL pública (e privada se o repo o é) para consultar dende o móbil.

**Pasos:**

1.  Vai a [share.streamlit.io](https://share.streamlit.io) e inicia sesión coa túa conta de GitHub.
2.  Pulsa en **"New app"**.
3.  Selecciona o teu repositorio (`albertofojo/ai-stock-analyzer`).
4.  Branch: `main`.
5.  Main file path: `dashboard.py`.
6.  Pulsa **"Deploy!"**.

En uns minutos, a túa web estará lista. Cada vez que o "bot" de GitHub Actions actualice `watchlist.json` ou cree novos informes na carpeta `Analisis/`, a web actualizarase automaticamente.
