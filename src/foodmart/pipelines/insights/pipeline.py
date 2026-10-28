"""Pipeline de análisis de negocio."""
from kedro.pipeline import Pipeline, node

from .nodes import driver_effects, success_profile


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(driver_effects, ["stores_clean", "parameters"], "driver_effects",
             name="driver_effects"),
        node(success_profile, ["stores_clean", "parameters"],
             ["success_profile", "success_by_competition"], name="success_profile"),
    ])
