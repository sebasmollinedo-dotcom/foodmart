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
  training/                 # split + entrenamiento (línea base, Ridge, Random Forest)
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

Resultados en `data/08_reporting/` (`metrics.csv`, `feature_importance.csv`).

## Metodología (resumen)

1. **Limpieza**: nombres a snake_case, se descartan columnas de texto duplicadas (ya existe la versión numérica), duplicados y filas sin target. El dataset no trae faltantes ni duplicados, pero el código los maneja.
2. **Outliers**: recorte por IQR (1.5×) solo en features continuos.
3. **Feature engineering**: `basket_growth_pct` (variación % de la canasta 2013→2014).
4. **Modelos**: línea base (media), Ridge (interpretable) y Random Forest (con `GridSearchCV`).
5. **Evaluación**: split 80/20 y métricas MAE, RMSE, R².

## Resultados (test, 30 tiendas)

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| baseline_media | 0.434 | 0.542 | -0.002 |
| ridge | 0.344 | 0.441 | 0.336 |
| random_forest | 0.354 | 0.48 | 0.212 |

**Modelo final: Ridge.** Es el mejor en las tres métricas, además de ser el más simple e interpretable. Con solo 150 tiendas, el Random Forest no logra mejorarlo.

Variable más influyente (`feature_importance.csv`): **número de competidores** (más competidores → menor utilidad).

## Recomendaciones para el stakeholder

1. **Evaluar la competencia antes de abrir una tienda:** es la variable con mayor efecto en la utilidad; priorizar ubicaciones con pocos competidores.
2. **Usar el modelo como filtro, no como oráculo:** sirve para comparar ubicaciones candidatas, no para predecir cifras exactas (R² ≈ 0.34).
3. **No invertir en horario o publicidad sin probar primero:** su efecto en el modelo es pequeño; conviene validarlo con un piloto.
4. **Recolectar más datos** (más tiendas, más años, tráfico de clientes) para mejorar la predicción.

## Fuentes

- Dataset: [FoodMart (Kaggle, dermisfit)](https://www.kaggle.com/datasets/dermisfit/foodmart-dataset).
- Librerías: Kedro, scikit-learn, pandas, Ruff, pytest.

## Limitaciones

- Solo 150 tiendas y un año (2014): resultados con mucha varianza; el conjunto de prueba son 30 tiendas.
- R² moderado: hay factores no medidos que afectan la utilidad.
- Datos ficticios; correlación no implica causalidad.
