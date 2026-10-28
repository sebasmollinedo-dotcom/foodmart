"""Pipeline de entrenamiento."""
from kedro.pipeline import Pipeline, node

from .nodes import select_features, split_data, train_models


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(split_data, ["stores_clean", "parameters"],
             ["X_train", "X_test", "y_train", "y_test"], name="split_data"),
        node(select_features, ["X_train", "y_train", "parameters"],
             ["selected_features", "feature_selection"], name="select_features"),
        node(train_models, ["X_train", "y_train", "parameters", "selected_features"],
             "models", name="train_models"),
    ])
