"""Pipeline de evaluación."""
from kedro.pipeline import Pipeline, node

from .nodes import evaluate_models, explain_model


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(evaluate_models, ["models", "X_test", "y_test"], "metrics", name="evaluate_models"),
        node(explain_model, ["models", "X_test", "y_test", "parameters"],
             "feature_importance", name="explain_model"),
    ])
