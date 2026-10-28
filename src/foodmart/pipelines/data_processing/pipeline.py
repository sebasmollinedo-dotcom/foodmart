"""Pipeline de limpieza."""
from kedro.pipeline import Pipeline, node

from .nodes import clean_stores


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(clean_stores, ["stores_raw", "parameters"], "stores_clean", name="clean_stores"),
    ])
