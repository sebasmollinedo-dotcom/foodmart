# FoodMart – ¿Qué hace exitosa a una tienda?

**Repositorio:** https://github.com/sebasmollinedo-dotcom/foodmart

Proyecto 1 de Machine Learning for Business (CRISP-DM + Kedro).
Dataset: [FoodMart (Kaggle)](https://www.kaggle.com/datasets/dermisfit/foodmart-dataset) – 150 supermercados de una cadena ficticia australiana (`data/01_raw/StoresData.xlsx`, hoja `Stores-Data`).

## Problema de negocio

| Elemento | Descripción |
|---|---|
| Contexto | FOODmart es una cadena de supermercados; el Head Office decide dónde abrir tiendas y cómo operarlas. |
| Stakeholder | Dirección de operaciones y expansión. |
| Pregunta | ¿Qué factores determinan la utilidad bruta (`GrossProfit`) de una tienda y qué debe hacer la empresa para aumentar la probabilidad de que una tienda sea exitosa? |
| Objetivo analítico | Regresión para predecir `gross_profit` (millones de $) y, sobre todo, identificar e interpretar las variables que la explican para tomar decisiones. |
| Métrica de éxito | Modelo que supere a la línea base (predecir la media) medido con RMSE / MAE / R², y recomendaciones accionables respaldadas por los datos. |
| Impacto | Elegir mejores ubicaciones y dejar de invertir en palancas que no muestran efecto. |

Decisión importante: **no** se usan `Sales $m` ni `Wages $m` como predictores porque son resultados del negocio, no decisiones.

## Estructura

```
conf/base/catalog.yml       # datasets
conf/base/parameters.yml    # parámetros (target, outliers, selección de variables, bootstrap...)
src/foodmart/pipelines/
  data_processing/          # limpieza + feature engineering
  training/                 # split + selección de variables + entrenamiento (4 modelos)
  evaluation/               # métricas en prueba, validación cruzada e importancia por permutación
  insights/                 # análisis de negocio, efecto de cada variable y perfil de tienda exitosa
tests/                      # pruebas con pytest
.github/workflows/ci.yml    # Ruff + pytest + kedro run en cada push/PR
```

## Cómo ejecutarlo

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

kedro run          # corre todo el pipeline y abre el reporte HTML
pytest             # pruebas
ruff check .       # calidad de código
```

Para ejecutar el notebook del EDA (`notebooks/eda.ipynb`) se necesitan dependencias extra que el pipeline no usa:

```bash
pip install -r requirements-notebook.txt
```

Resultados en `data/08_reporting/`:

| Archivo | Contenido |
|---|---|
| `metrics.csv` | MAE, RMSE y R² de cada modelo en las 30 tiendas de prueba |
| `cv_metrics.csv` | Las mismas métricas con validación cruzada repetida sobre las 150 tiendas |
| `feature_selection.csv` | Variables que entran al modelo compacto y el R² en cada paso |
| `feature_importance.csv` | Importancia por permutación (Random Forest) |
| `driver_effects.csv` | Efecto de cada variable sobre la utilidad, con intervalo de confianza al 95% |
| `success_profile.csv` | Cómo se diferencian las tiendas del cuarto superior de utilidad del resto |
| `success_by_competition.csv` | Utilidad, horas y porcentaje de tiendas exitosas según el número de competidores |
| `classification_metrics.csv`, `confusion_matrix.csv` | F1 y matriz de confusión al clasificar tiendas de alta o baja utilidad |
| `eda_summary.json` | Hallazgos del EDA (calidad, correlaciones, VIF, etc.) que alimentan el reporte |
| `reporte.html` | Reporte interactivo para presentar el proyecto |

El modelo entrenado queda en `data/06_models/models.pkl`.

### Reporte HTML interactivo

Al terminar `kedro run` se genera `data/08_reporting/reporte.html` y se abre en Google Chrome. Es una página autocontenida (funciona sin internet) con tema de supermercado: calculadora de ubicación, problema de negocio, proceso, hallazgos del EDA con gráficos y pruebas estadísticas, modelos (con selector de validación cruzada o prueba), F1 y matriz de confusión, efectos de cada variable con intervalo bootstrap, perfil de la tienda exitosa, recomendaciones, y una sección de **preguntas que puede hacer el profesor** con la tabla de parámetros de entrenamiento y por qué. Tiene modo claro/oscuro, **pantalla completa** (botón o tecla `F`; en pantalla completa, ← → cambian de pasillo) y conclusiones en español guatemalteco. Los hallazgos del EDA los calcula el nodo `summarize_eda`. Para no abrir el navegador: `KEDRO_OPEN_REPORT=0 kedro run`; en CI (GitHub Actions) tampoco se abre.

## Metodología (resumen)

1. **Limpieza**: nombres a snake_case, se descartan columnas de texto duplicadas (ya existe la versión numérica), duplicados y filas sin target. El dataset no trae faltantes ni duplicados, pero el código los maneja.
2. **Outliers**: recorte por IQR (1.5×) solo en features continuos.
3. **Feature engineering**: `basket_growth_pct` (variación % de la canasta 2013→2014).
4. **Selección de variables**: hacia adelante con validación cruzada repetida, usando solo las tiendas de entrenamiento. Se detiene cuando una variable nueva no mejora el R² en al menos 0.003.
5. **Modelos**: línea base (media), Ridge con todas las variables, Ridge compacto (variables seleccionadas) y Random Forest con `GridSearchCV`.
6. **Evaluación**: split 80/20 y validación cruzada repetida (5 particiones, 10 repeticiones) sobre las 150 tiendas, porque 30 tiendas de prueba dan métricas muy variables.
7. **Análisis de negocio**: regresión múltiple con intervalos bootstrap para medir el efecto de cada variable y comparación de tiendas exitosas (cuarto superior de utilidad) contra el resto.

## Resultados

| Modelo | R² (CV, 150 tiendas) | MAE (CV) | R² (prueba, 30 tiendas) |
|---|---|---|---|
| baseline_media | -0.042 | 0.520 | -0.002 |
| ridge (todas las variables) | 0.355 | 0.385 | 0.336 |
| **ridge_compacto** | **0.475** | **0.322** | 0.210 |
| random_forest | 0.412 | 0.353 | 0.212 |

**Modelo final: Ridge compacto** (competidores y apertura en domingo). Es el mejor en validación cruzada y el más simple de explicar. La apertura en domingo entra por una ganancia mínima (R² de 0.508 a 0.512) y su efecto no es distinguible de cero; casi todo el poder predictivo viene del número de competidores. En las 30 tiendas de prueba el Ridge con todas las variables quedó por encima, pero con una prueba tan pequeña la diferencia cae dentro del ruido (la desviación del R² entre particiones es de unos 0.15). Agregar más variables empeora la predicción porque la mayoría solo aporta ruido.

### Vista complementaria: ¿alta o baja utilidad? (F1 y matriz de confusión)

La utilidad es un número continuo, así que la métrica principal es de regresión (MAE, RMSE, R²). F1 y la matriz de confusión son métricas de **clasificación**; para usarlas se convierte la pregunta en «¿esta tienda será de alta utilidad (≥ \$1M)?» (parámetro `profitable_threshold`). Se calculan con predicciones fuera de muestra (validación cruzada de 5 folds sobre las 150 tiendas); las clases están equilibradas (72 altas, 78 bajas), así que F1 no se infla por desbalance.

| Modelo | Exactitud | Precisión | Recall | F1 |
|---|---|---|---|---|
| ridge (todas las variables) | 0.82 | 0.75 | 0.93 | 0.83 |
| **ridge_compacto** | **0.85** | **0.81** | **0.92** | **0.86** |
| random_forest | 0.85 | 0.81 | 0.90 | 0.85 |

Matriz de confusión del modelo final: 62 bajas bien clasificadas, 66 altas bien clasificadas, 16 falsos positivos y 6 falsos negativos. El Random Forest usa hiperparámetros elegidos con el conjunto de entrenamiento, así que su cifra puede ser algo optimista.

## Hallazgos para el negocio

1. **La competencia es la variable que decide.** Cada competidor adicional cerca se asocia con unos **280 mil dólares menos** de utilidad (intervalo 220 a 340 mil), con las demás variables constantes.
2. **Perfil de tienda exitosa** (cuarto superior de utilidad): tiene en promedio 1.1 competidores cerca, contra 3.0 del resto. Con 0 competidores el 68% de las tiendas es exitosa, con 1 el 48%, con 2 el 18% y con 5 o más ninguna.
3. **El horario largo es un síntoma, no una palanca.** Competidores y horas de atención tienen una correlación de 0.97, las tiendas abren unas 12 horas más por cada competidor adicional. No se pueden separar sus efectos y nada indica que ampliar horario aumente la utilidad.
4. **La publicidad no muestra efecto detectable** (intervalo de confianza incluye el cero). Tampoco la apertura en domingo, el personal, la capacitación y experiencia del gerente, el estacionamiento ni la entrega a domicilio.
5. **Antigüedad.** Cada año adicional se asocia con unos 34 mil dólares menos (intervalo 9 a 66 mil), conviene revisar si las tiendas viejas necesitan renovación.

## Recomendaciones para el stakeholder

1. **Usar la competencia cercana como criterio principal para abrir tiendas.** Priorizar zonas con 0 o 1 competidores (48% a 68% de probabilidad de ser exitosa) y ser muy exigente con zonas con 3 o más.
2. **No esperar que más publicidad o más horas rescaten una mala ubicación.** Antes de aumentar ese gasto, hacer un piloto en pocas tiendas y medir.
3. **Revisar el horario de las tiendas en zonas muy competidas.** Abren más horas pero son las de menor utilidad, puede haber costo sin retorno.
4. **Revisar las tiendas más antiguas** para decidir renovaciones.
5. **Recolectar más datos** (costos, tamaño de la zona, tráfico de clientes, más años) para explicar el resto de la utilidad.

## Fuentes

- Dataset: [FoodMart (Kaggle, dermisfit)](https://www.kaggle.com/datasets/dermisfit/foodmart-dataset).
- Librerías: Kedro, scikit-learn, pandas, numpy, Ruff, pytest.
- Íconos del reporte: [Lucide](https://lucide.dev) (licencia ISC), incrustados como SVG.

## Limitaciones

- Solo 150 tiendas y un año (2014): resultados con mucha varianza.
- R² cercano a 0.48: más de la mitad de la utilidad depende de factores no medidos.
- Datos ficticios; correlación no implica causalidad.
- Se hicieron varias comparaciones a la vez, así que alguna variable con intervalo que no incluye el cero (antigüedad, canasta 2013) podría ser casualidad.
- `mng_female` aparece con un efecto negativo, pero son solo 25 tiendas, el resultado es débil y no debe usarse para decisiones de personal. Podría reflejar a qué tiendas se asigna cada gerente.
- La selección de variables usa solo las tiendas de entrenamiento, pero la validación cruzada final incluye todas las tiendas, así que la métrica del modelo compacto puede ser algo optimista.
