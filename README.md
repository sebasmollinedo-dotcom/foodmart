# FoodMart – ¿Qué determina la utilidad bruta de una tienda?

Proyecto 1 de Machine Learning for Business (CRISP-DM + Kedro).
Dataset: [FoodMart (Kaggle)](https://www.kaggle.com/datasets/dermisfit/foodmart-dataset) – 150 supermercados de una cadena ficticia australiana (`data/01_raw/StoresData.xlsx`, hoja `Stores-Data`).

## Problema de negocio

| Elemento | Descripción |
|---|---|
| Contexto | FOODmart es una cadena de supermercados; el Head Office decide dónde abrir y cómo operar tiendas. |
| Stakeholder | Dirección de operaciones / expansión. |
| Pregunta | ¿Qué factores operativos y de ubicación explican la utilidad bruta (`GrossProfit`) de una tienda y podemos predecirla? |
| Objetivo analítico | Regresión: predecir `gross_profit` (millones de $). |
| Métrica de éxito | RMSE / MAE / R² en datos de prueba, y que supere a la línea base (predecir la media). |
| Impacto | Priorizar ubicaciones y decisiones (horario, publicidad) que aumentan la utilidad. |

Decisión importante: **no** se usan `Sales $m` ni `Wages $m` como predictores porque son resultados del negocio, no decisiones.

## Estructura

```
conf/base/catalog.yml       # datasets
conf/base/parameters.yml    # parámetros (target, outliers, modelo final, grid...)
src/foodmart/pipelines/
  data_processing/          # limpieza + feature engineering
  training/                 # split + entrenamiento (línea base, regresión simple, Ridge, Random Forest)
  evaluation/               # métricas e importancia de variables
tests/                      # pruebas con pytest
.github/workflows/ci.yml    # Ruff + pytest + kedro run en cada push/PR
```

## Cómo ejecutarlo

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

kedro run          # corre todo el pipeline
pytest             # pruebas
ruff check .       # calidad de código
```

Resultados en `data/08_reporting/` (`metrics.csv`, `feature_importance.csv`, `classification_metrics.csv`, `confusion_matrix.csv`).

Al terminar `kedro run` se genera `data/08_reporting/reporte.html` y se abre en Google Chrome. Es una página interactiva y autocontenida (funciona sin internet) con tema de supermercado: calculadora de ubicación (mueve el número de competidores y ve la utilidad esperada), problema de negocio, proceso, hallazgos del EDA con gráficos y pruebas estadísticas, modelos con métricas conmutables, F1 y matriz de confusión, importancia de variables, recomendaciones finales y limitaciones; con modo claro/oscuro y conclusiones en español guatemalteco. Los hallazgos del EDA los calcula el nodo `summarize_eda` (`eda_summary.json`). Para no abrir el navegador: `KEDRO_OPEN_REPORT=0 kedro run`. En CI (GitHub Actions) tampoco se abre.

## Metodología (resumen)

1. **Limpieza**: nombres a snake_case, se descartan columnas de texto duplicadas (ya existe la versión numérica), duplicados y filas sin target. El dataset no trae faltantes ni duplicados, pero el código los maneja.
2. **Outliers**: recorte por IQR (1.5×) solo en features continuos.
3. **Feature engineering**: `basket_growth_pct` (variación % de la canasta 2013→2014).
4. **Modelos**: línea base (media), regresión lineal simple (solo competidores), Ridge (todas las variables) y Random Forest (con `GridSearchCV`).
5. **Evaluación**: split 80/20 y métricas MAE, RMSE, R².

## Resultados (test, 30 tiendas)

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| baseline_media | 0.434 | 0.542 | -0.002 |
| regresion_simple | 0.327 | 0.462 | 0.271 |
| ridge | 0.344 | 0.441 | 0.336 |
| random_forest | 0.354 | 0.48 | 0.212 |

**Modelo final: regresión lineal simple con solo competidores** (`utilidad ≈ 1.67 − 0.26 × competidores`, en \$ millones, ajustada con las 150 tiendas; con las 120 de entrenamiento sale 1.73 − 0.28). Se eligió por simplicidad e interpretabilidad, y porque el EDA (sección 9) muestra que las demás variables no aportan señal medible con solo 150 tiendas.

**Cómo leer la tabla:** en esta partición fija de 30 tiendas, la regresión simple tiene el menor MAE, pero Ridge tiene mejor RMSE y R². La diferencia es ruido de un conjunto de prueba pequeño. Con validación cruzada (5 folds × 20 repeticiones, sobre las 150 tiendas), la regresión simple logra R² ≈ 0.47 contra ≈ 0.37 del Ridge con todas las variables, y gana en la mayoría de las particiones (84 % frente al modelo con todas las variables, EDA sección 9).

Variable más influyente (`feature_importance.csv`): **número de competidores** (más competidores → menor utilidad; ≈ \$263 mil menos por competidor).

### Vista complementaria: ¿alta o baja utilidad? (F1 y matriz de confusión)

La utilidad es un número continuo, así que la métrica principal es de regresión (MAE, RMSE, R²). F1 y la matriz de confusión son métricas de **clasificación**; para usarlas se convierte la pregunta en «¿esta tienda será de alta utilidad (≥ \$1M)?» (parámetro `profitable_threshold`). Se calculan con predicciones fuera de muestra (validación cruzada de 5 folds sobre las 150 tiendas); las clases están equilibradas (72 altas, 78 bajas), así que F1 no se infla por desbalance.

| Modelo | Exactitud | Precisión | Recall | F1 |
|---|---|---|---|---|
| regresion_simple | 0.85 | 0.81 | 0.92 | 0.86 |
| ridge | 0.82 | 0.75 | 0.93 | 0.83 |
| random_forest | 0.85 | 0.81 | 0.90 | 0.85 |

Matriz de confusión del modelo final: 62 bajas bien clasificadas, 66 altas bien clasificadas, 16 falsos positivos y 6 falsos negativos. Las diferencias entre modelos son pequeñas; lo relevante es que el modelo simple no pierde frente a los complejos.

## Recomendaciones para el stakeholder

1. **Evaluar la competencia antes de abrir una tienda:** es la variable con mayor efecto en la utilidad; priorizar ubicaciones con pocos competidores.
2. **Usar el modelo como filtro, no como oráculo:** sirve para comparar ubicaciones candidatas, no para predecir cifras exactas (R² ≈ 0.27 en la partición de prueba; ≈ 0.47 en validación cruzada).
3. **No invertir en horario o publicidad sin probar primero:** el EDA muestra que las horas solo reflejan la competencia (sin ella su relación con la utilidad es ≈ 0) y que la publicidad no tiene relación detectable; conviene validarlo con un piloto.
4. **Recolectar más datos** (más tiendas, más años, tráfico de clientes) para mejorar la predicción.

## Fuentes

- Dataset: [FoodMart (Kaggle, dermisfit)](https://www.kaggle.com/datasets/dermisfit/foodmart-dataset).
- Librerías: Kedro, scikit-learn, pandas, Ruff, pytest.
- Íconos del reporte: [Lucide](https://lucide.dev) (licencia ISC), incrustados como SVG.

## Limitaciones

- Solo 150 tiendas y un año (2014): resultados con mucha varianza; el conjunto de prueba son 30 tiendas.
- R² moderado: hay factores no medidos que afectan la utilidad.
- Datos ficticios; correlación no implica causalidad.
