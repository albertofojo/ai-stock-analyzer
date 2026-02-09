# ⚙️ Especificación Funcional: Analista de Bolsa IA

Este documento detalla a lóxica de negocio, o fluxo de datos e as regras de decisión que gobernan o axente de investimento automatizado. O sistema está deseñado para replicar o proceso de toma de decisións dun investidor de estilo "Value/Swing Trading" conservador.

## 1. Arquitectura do Sistema

O proxecto segue unha arquitectura lineal de procesamento de datos (Pipeline) dividida en 4 etapas:

1. **Entrada (Input):** O usuario introduce o *Ticker* (símbolo bolsista).
2. **Enriquecemento (Data Fetching):** O sistema obtén datos en tempo real e datos históricos locais.
3. **Procesamento Cognitivo (LLM):** O modelo de IA cruza os datos coas regras estáticas.
4. **Persistencia (Output):** O resultado gárdase e indexase para futuras referencias.

---

## 2. Fluxo de Datos (Data Flow)

### 2.1. Adquisición de Datos de Mercado (`yfinance`)

O sistema conecta coa API de Yahoo Finance para descargar os seguintes puntos de datos críticos:

* **Prezo Actual e Divisa:** Para contextualizar o valor.
* **Histórico de 2 Anos:** Utilízase para calcular indicadores técnicos.
* **Media Móbil de 200 Sesións (MA200):** *Indicador Calculado*. Calcúlase a media aritmética dos prezos de peche das últimas 200 sesións.
* **Máximo de 52 Semanas:** Utilízase para calcular o *Drawdown* (porcentaxe de caída dende máximos).
* **Datos Fundamentais:**
* **PER (Trailing & Forward):** Ratio Prezo/Beneficio actual e estimado.
* **Débeda Total e Caixa Total:** Para o test de solvencia.
* **Free Cash Flow (FCF):** Fluxo de caixa libre.
* **Crecemento de Ingresos:** Comparativa interanual.



### 2.2. Sistema de Memoria e Contexto

O axente non analiza a empresa de cero cada vez. Antes de chamar á IA:

1. O sistema busca no directorio `Analisis/[TICKER]/`.
2. Ordena os ficheiros `.md` por data descendente.
3. Selecciona os **2 últimos informes**.
4. Inxecta o texto destes informes no *Prompt* do sistema baixo a sección `### PREVIOUS ANALYSIS HISTORY`.

**Obxectivo Funcional:** Permitir á IA detectar tendencias (*"A débeda baixou respecto ao mes pasado"*) e validar as súas propias predicións anteriores (*"Chegamos ao prezo obxectivo que marcamos hai dúas semanas"*).

---

## 3. Lóxica de Análise (O "Cerebro")

O axente utiliza un **Prompt do Sistema** (definido en `rules.md`) que actúa como un conxunto de instrucións inmutables. A toma de decisións divídese en dúas capas:

### Capa 1: O Filtro Fundamental (Seguridade)

Actúa como unha barreira de entrada. Se a empresa non pasa este filtro, a análise técnica é secundaria.

* **Regra do PER:**
* **PER > 50:** Clasifícase automaticamente como "Especulación perigosa" ou "Locura", salvo excepcións moi xustificadas.
* **PER Óptimo:** Búscase un PER que estea preto do 50% do seu mínimo histórico dos últimos 5 anos (zona de infravaloración).


* **Regra da Débeda ("Test do Algodón"):**
* A empresa debe ser capaz de pagar a súa débeda total con 3 ou 4 anos de *Free Cash Flow*.
* Se `Débeda >> Caixa` e o `FCF` é negativo ou decrecente, emítese unha alerta de "Débeda Criminal".



### Capa 2: O Disparador Técnico (Oportunidade)

Determina o *Timing* (cando comprar).

* **A "Lei" da MA200:**
* **Zona de Compra:** O prezo debe estar **por debaixo** ou **tocando** a Media de 200 sesións.
* **Zona de Venda/Espera:** Se o prezo está moi por riba da MA200 ("Separación Máxima"), o sistema recomenda non comprar e esperar a reversión á media ("Caída a coitelo").


* **Drawdown:** Valórase positivamente se a acción caeu significativamente dende máximos (medo no mercado) mentres os fundamentais seguen intactos.

---

## 4. Estrutura do Prompt (Enxeñaría de Prompts)

Para garantir resultados consistentes, a estrutura que se envía a Google Gemini é a seguinte:

1. **System Persona:** "Ti es Miguel, un analista conservador..."
2. **Knowledge Base:** As regras financeiras estritas (copiadas de `rules.md`).
3. **Input Data Block:**
* Datos de Mercado (Prezo, Distancia MA200%).
* Datos Fundamentais (PER, Débeda, Caixa).


4. **Memory Block:** Resumo das análises anteriores.
5. **Output Instructions:**
* Compara co pasado.
* Aplica filtros.
* Emite veredicto (Comprar/Vender/Agardar).
* Estilo directo e en castelán.



---

## 5. Xestión de Erros e Límites

* **Falta de Datos:** Se `yfinance` non devolve datos (ex: empresa moi pequena ou ticker erróneo), o script detense antes de chamar á IA para non gastar tokens.
* **Alucinacións:** Ao forzar á IA a usar *unicamente* os datos numéricos proporcionados no prompt, redúcese drasticamente o risco de que invente cifras financeiras.
* **Xestión de ficheiros:** O sistema xestiona colisións de nomes engadindo sufixos (`_2`, `_3`) para non sobrescribir análises realizadas o mesmo día.