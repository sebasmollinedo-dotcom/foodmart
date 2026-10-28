"""Nodos de partición y entrenamiento."""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


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


def _preprocessor(X: pd.DataFrame, categorical: list, scale: bool) -> ColumnTransformer:
    """Crea el preprocesamiento: one-hot para categóricas y escalado opcional.

    Args:
        X: Features de entrenamiento.
        categorical: Columnas categóricas codificadas como número.
        scale: Si es True, estandariza las columnas numéricas.

    Returns:
        ColumnTransformer: Transformador listo para usarse en un Pipeline.

    """
    numeric = [c for c in X.columns if c not in categorical]
    return ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", StandardScaler() if scale else "passthrough", numeric),
    ])


def train_models(X_train: pd.DataFrame, y_train: pd.DataFrame, params: dict) -> dict:
    """Entrena la línea base (media), una regresión simple, una regresión Ridge y un Random Forest.

    Args:
        X_train: Features de entrenamiento.
        y_train: Objetivo de entrenamiento (una columna).
        params: Parámetros (categorical, simple_features, random_state, rf_param_grid, cv_folds).

    Returns:
        dict: Modelos entrenados, con llaves baseline_media, regresion_simple, ridge y
        random_forest.

    """
    y = y_train.iloc[:, 0]
    cat = params["categorical"]
    seed = params["random_state"]

    baseline = Pipeline([("prep", _preprocessor(X_train, cat, False)),
                         ("model", DummyRegressor(strategy="mean"))])
    # Regresión lineal que usa solo las variables de `simple_features` (el EDA muestra que
    # competidores concentra casi toda la señal); el resto de columnas se descarta.
    simple = Pipeline([
        ("prep", ColumnTransformer([("sel", "passthrough", params["simple_features"])])),
        ("model", LinearRegression()),
    ])
    ridge = Pipeline([("prep", _preprocessor(X_train, cat, True)),
                      ("model", Ridge(alpha=1.0))])
    forest = GridSearchCV(
        Pipeline([("prep", _preprocessor(X_train, cat, False)),
                  ("model", RandomForestRegressor(random_state=seed))]),
        param_grid={f"model__{k}": v for k, v in params["rf_param_grid"].items()},
        cv=params["cv_folds"], scoring="neg_root_mean_squared_error",
    )

    models = {"baseline_media": baseline, "regresion_simple": simple, "ridge": ridge,
              "random_forest": forest}
    for model in models.values():
        model.fit(X_train, y)
    return models
