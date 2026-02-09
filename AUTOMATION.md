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
