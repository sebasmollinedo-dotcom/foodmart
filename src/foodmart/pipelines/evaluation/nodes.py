"""Nodos de evaluación e interpretación."""
import logging

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)


def evaluate_models(models: dict, X_test: pd.DataFrame, y_test: pd.DataFrame) -> pd.DataFrame:
    """Calcula MAE, RMSE y R2 de cada modelo sobre el conjunto de prueba.

    Args:
        models: Diccionario de modelos entrenados.
        X_test: Features de prueba.
        y_test: Objetivo de prueba (una columna).

    Returns:
        pd.DataFrame: Una fila por modelo con sus métricas.

    """
    y = y_test.iloc[:, 0]
    rows = []
    for name, model in models.items():
        pred = model.predict(X_test)
        rows.append({
            "modelo": name,
            "MAE": mean_absolute_error(y, pred),
            "RMSE": np.sqrt(mean_squared_error(y, pred)),
            "R2": r2_score(y, pred),
        })
    metrics = pd.DataFrame(rows).round(3)
    logger.info("Métricas en prueba:\n%s", metrics.to_string(index=False))
    return metrics


def explain_model(
    models: dict, X_test: pd.DataFrame, y_test: pd.DataFrame, params: dict
) -> pd.DataFrame:
    """Calcula la importancia por permutación del modelo final.

    Mide cuánto cae el R2 al desordenar cada variable.

    Args:
        models: Diccionario de modelos entrenados.
        X_test: Features de prueba.
        y_test: Objetivo de prueba (una columna).
        params: Parámetros (final_model, random_state).

    Returns:
        pd.DataFrame: Variables ordenadas de mayor a menor importancia.

    """
    result = permutation_importance(
        models[params["final_model"]], X_test, y_test.iloc[:, 0],
        n_repeats=20, random_state=params["random_state"],
    )
    out = pd.DataFrame({"variable": X_test.columns, "caida_r2": result.importances_mean})
    return out.sort_values("caida_r2", ascending=False).round(4)
