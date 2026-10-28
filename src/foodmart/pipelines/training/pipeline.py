"""Pipeline de entrenamiento."""
from kedro.pipeline import Pipeline, node

from .nodes import split_data, train_models


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(split_data, ["stores_clean", "parameters"],
             ["X_train", "X_test", "y_train", "y_test"], name="split_data"),
        node(train_models, ["X_train", "y_train", "parameters"], "models", name="train_models"),
    ])
