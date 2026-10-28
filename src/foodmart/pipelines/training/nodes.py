"""Nodos de partición, selección de variables y entrenamiento."""
import logging

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV, RepeatedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger(__name__)


def split_data(df: pd.DataFrame, params: dict):
    """Separa features (X) y objetivo (y) en train/test.

    Args:
        df: Tabla limpia de tiendas.
        params: Parámetros (target, test_size, random_state).

    Returns:
        tuple: ``X_train, X_test, y_train, y_test``.

    """
    X = df.drop(columns=[params["target"]])
    y = df[[params["target"]]]
    return train_test_split(
        X, y, test_size=params["test_size"], random_state=params["random_state"]
    )


def _preprocessor(columns: list, categorical: list, scale: bool) -> ColumnTransformer:
    """Crea el preprocesamiento: one-hot para categóricas y escalado opcional.

    Args:
        columns: Columnas que el modelo debe usar, el resto se descarta.
        categorical: Columnas categóricas codificadas como número.
        scale: Si es True, estandariza las columnas numéricas.

    Returns:
        ColumnTransformer: Transformador listo para usarse en un Pipeline.

    """
    cat = [c for c in columns if c in categorical]
    numeric = [c for c in columns if c not in categorical]
    steps = []
    if cat:
        steps.append(("cat", OneHotEncoder(handle_unknown="ignore"), cat))
    if numeric:
        steps.append(("num", StandardScaler() if scale else "passthrough", numeric))
    return ColumnTransformer(steps)


def select_features(X_train: pd.DataFrame, y_train: pd.DataFrame, params: dict):
    """Elige las variables que realmente mejoran la predicción (selección hacia adelante).

    En cada paso se agrega la variable que más sube el R2 medio en validación cruzada
    repetida, y se detiene cuando la mejora es menor a ``selection_min_gain``. Solo usa
    las tiendas de entrenamiento, para no contaminar la evaluación final.

    Args:
        X_train: Features de entrenamiento.
        y_train: Objetivo de entrenamiento (una columna).
        params: Parámetros (categorical, selection_*, random_state).

    Returns:
        tuple: Lista de variables elegidas y tabla con el detalle de cada paso.

    """
    y = y_train.iloc[:, 0]
    cat = params["categorical"]
    cv = RepeatedKFold(
        n_splits=params["selection_cv_folds"], n_repeats=params["selection_cv_repeats"],
        random_state=params["random_state"],
    )

    def score(cols: list) -> float:
        model = Pipeline([("prep", _preprocessor(cols, cat, True)), ("model", Ridge(alpha=1.0))])
        return cross_val_score(model, X_train[cols], y, cv=cv, scoring="r2").mean()

    selected, best, log = [], -np.inf, []
    while len(selected) < X_train.shape[1]:
        scores = {c: score(selected + [c]) for c in X_train.columns if c not in selected}
        candidate = max(scores, key=scores.get)
        if selected and scores[candidate] < best + params["selection_min_gain"]:
            break
        selected.append(candidate)
        best = scores[candidate]
        log.append({"paso": len(selected), "variable_agregada": candidate,
                    "r2_validacion_cruzada": round(best, 3)})
    logger.info("Variables seleccionadas: %s", selected)
    return selected, pd.DataFrame(log)


def train_models(
    X_train: pd.DataFrame, y_train: pd.DataFrame, params: dict, selected_features: list
) -> dict:
    """Entrena la línea base, una regresión simple, dos regresiones Ridge y un Random Forest.

    Args:
        X_train: Features de entrenamiento.
        y_train: Objetivo de entrenamiento (una columna).
        params: Parámetros (categorical, random_state, rf_param_grid, cv_folds).
        selected_features: Variables elegidas por ``select_features``.

    Returns:
        dict: Modelos entrenados, con llaves baseline_media, regresion_simple, ridge,
        ridge_compacto y random_forest.

    """
    y = y_train.iloc[:, 0]
    cat = params["categorical"]
    seed = params["random_state"]
    allc = list(X_train.columns)

    baseline = Pipeline([("prep", _preprocessor(allc, cat, False)),
                         ("model", DummyRegressor(strategy="mean"))])
    # Regresión lineal que usa solo las variables de `simple_features` (el EDA muestra que
    # competidores concentra casi toda la señal); el resto de columnas se descarta.
    simple = Pipeline([
        ("prep", ColumnTransformer([("sel", "passthrough", params["simple_features"])])),
        ("model", LinearRegression()),
    ])
    ridge = Pipeline([("prep", _preprocessor(allc, cat, True)),
                      ("model", Ridge(alpha=1.0))])
    ridge_compacto = Pipeline([("prep", _preprocessor(list(selected_features), cat, True)),
                               ("model", Ridge(alpha=1.0))])
    forest = GridSearchCV(
        Pipeline([("prep", _preprocessor(allc, cat, False)),
                  ("model", RandomForestRegressor(random_state=seed))]),
        param_grid={f"model__{k}": v for k, v in params["rf_param_grid"].items()},
        cv=params["cv_folds"], scoring="neg_root_mean_squared_error",
    )

    models = {"baseline_media": baseline, "regresion_simple": simple, "ridge": ridge,
              "ridge_compacto": ridge_compacto, "random_forest": forest}
    for model in models.values():
        model.fit(X_train, y)
    return models
