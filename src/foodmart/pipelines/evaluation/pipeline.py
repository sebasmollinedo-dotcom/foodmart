"""Pipeline de evaluación."""
from kedro.pipeline import Pipeline, node

from .eda import summarize_eda
from .nodes import evaluate_classification, evaluate_models, explain_model
from .report import build_report


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(evaluate_models, ["models", "X_test", "y_test"], "metrics", name="evaluate_models"),
        node(explain_model, ["models", "X_test", "y_test", "parameters"],
             "feature_importance", name="explain_model"),
        node(evaluate_classification, ["models", "stores_clean", "parameters"],
             ["classification_metrics", "confusion_matrix"], name="evaluate_classification"),
        node(summarize_eda,
             ["stores_raw", "stores_clean", "models", "X_train", "X_test", "parameters"],
             "eda_summary", name="summarize_eda"),
        node(build_report,
             ["stores_clean", "eda_summary", "metrics", "feature_importance",
              "classification_metrics", "confusion_matrix", "parameters"],
             "report_html", name="build_report"),
    ])
