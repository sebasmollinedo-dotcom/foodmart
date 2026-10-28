"""Nodos de evaluación e interpretación."""
import logging

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import KFold, cross_val_predict

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


def evaluate_classification(
    models: dict, stores_clean: pd.DataFrame, params: dict
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evalúa los modelos como clasificadores de tiendas de alta utilidad.

    Una tienda es "alta" si su utilidad real es >= ``profitable_threshold``. La predicción
    del modelo de regresión se convierte con el mismo umbral. Se usan predicciones fuera de
    muestra (validación cruzada de 5 folds sobre todas las tiendas), no las 30 de prueba.
    Los hiperparámetros del Random Forest se eligieron con el conjunto de entrenamiento, así que
    su cifra puede ser algo optimista frente a la de los modelos lineales.

    Args:
        models: Diccionario de modelos entrenados.
        stores_clean: Tabla limpia de tiendas (features + target).
        params: Parámetros (target, profitable_threshold, final_model, random_state).

    Returns:
        tuple: Métricas por modelo (exactitud, precisión, recall, F1) y la matriz de
        confusión del modelo final con columnas ``real``, ``pred_baja`` y ``pred_alta``.

    """
    thr = params["profitable_threshold"]
    X = stores_clean.drop(columns=[params["target"]])
    y = stores_clean[params["target"]]
    real = (y >= thr).astype(int)
    cv = KFold(n_splits=5, shuffle=True, random_state=params["random_state"])

    rows, cm_final = [], None
    for name, model in models.items():
        if name == "baseline_media":  # predice una constante: no tiene sentido clasificar con él
            continue
        estimator = getattr(model, "best_estimator_", model)
        pred = (cross_val_predict(clone(estimator), X, y, cv=cv) >= thr).astype(int)
        rows.append({
            "modelo": name,
            "accuracy": accuracy_score(real, pred),
            "precision": precision_score(real, pred, zero_division=0),
            "recall": recall_score(real, pred, zero_division=0),
            "F1": f1_score(real, pred, zero_division=0),
        })
        if name == params["final_model"]:
            cm_final = confusion_matrix(real, pred, labels=[0, 1])

    if cm_final is None:
        raise ValueError(
            f"final_model='{params['final_model']}' no se puede evaluar como clasificador; "
            f"usa uno de: {[m for m in models if m != 'baseline_media']}"
        )
    cm = pd.DataFrame(cm_final, columns=["pred_baja", "pred_alta"])
    cm.insert(0, "real", ["baja", "alta"])
    metrics = pd.DataFrame(rows).round(3)
    logger.info("Clasificación alta/baja utilidad (umbral %.2f):\n%s", thr,
                metrics.to_string(index=False))
    return metrics, cm
