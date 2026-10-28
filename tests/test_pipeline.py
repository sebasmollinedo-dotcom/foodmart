"""Pruebas básicas de los nodos."""
import json

import pandas as pd
import pytest

from foodmart.pipelines.data_processing.nodes import clean_stores
from foodmart.pipelines.evaluation.eda import summarize_eda
from foodmart.pipelines.evaluation.nodes import (
    cross_validate_models,
    evaluate_classification,
    evaluate_models,
    explain_model,
)
from foodmart.pipelines.evaluation.report import build_report
from foodmart.pipelines.insights.nodes import driver_effects, success_profile
from foodmart.pipelines.training.nodes import select_features, split_data, train_models

PARAMS = {
    "target": "gross_profit",
    "drop_columns": ["store_no", "sales_m", "wages_m"],
    "categorical": ["location", "state"],
    "simple_features": ["competitors"],
    "final_model": "ridge_compacto",
    "importance_model": "random_forest",
    "profitable_threshold": 1.0,
    "outlier_iqr_factor": 1.5,
    "test_size": 0.2,
    "random_state": 42,
    "rf_param_grid": {"n_estimators": [10], "max_depth": [3], "min_samples_leaf": [2]},
    "cv_folds": 2,
    "selection_cv_folds": 2,
    "selection_cv_repeats": 1,
    "selection_min_gain": 0.003,
    "eval_cv_repeats": 1,
    "success_quantile": 0.75,
    "n_bootstrap": 20,
    "driver_variables": ["competitors", "age_yrs", "union"],
}


@pytest.fixture
def raw() -> pd.DataFrame:
    """Mini versión del Excel original (con un duplicado y un outlier)."""
    n = 20
    comp = [i % 4 for i in range(n)]  # la utilidad baja con los competidores (como en los datos)
    df = pd.DataFrame({
        "Store No.": range(n), "Sales $m": 10.0, "Wages $m": 2.0, "No. Staff": 60,
        "Location": "Mall", "Loc'n (Num)": [1, 2] * 10, "State": ["NSW", "Vic"] * 10,
        "State (Num)": [1, 2] * 10, "Age (Yrs)": range(1, n + 1),
        "GrossProfit": [1.8 - 0.4 * c + (i % 3) / 20 for i, c in enumerate(comp)],
        "Adv.$'000": 150, "Competitors": comp,
        "HrsTrading": [70 + 10 * c + i % 5 for i, c in enumerate(comp)],
        "Sundays": "Sun:No", "Sundays (Num)": 0, "Mng-Sex": ["Male", "Male", "Male", "Female"] * 5,
        "Mng-Sex (Num)": [0, 0, 0, 1] * 5, "Mng-Age": 40, "Mng-Exp": 8, "Mng-Train": 2,
        "Union%": 38, "Car Spaces": 40, "HomeDel": "Del:No", "HomeDel (Num)": 0,
        "Basket:2013": [170 + i for i in range(n)],
        "Basket:2014": [(170 + i) * 1.04 + i % 3 for i in range(n)],
    })
    df.loc[0, "Car Spaces"] = 5000  # outlier
    return pd.concat([df, df.iloc[[1]]])  # duplicado


def _trained(raw):
    """Datos limpios, partición y modelos entrenados del fixture."""
    clean = clean_stores(raw, PARAMS)
    X_train, X_test, y_train, y_test = split_data(clean, PARAMS)
    selected, log = select_features(X_train, y_train, PARAMS)
    models = train_models(X_train, y_train, PARAMS, selected)
    return clean, X_train, X_test, y_train, y_test, selected, log, models


def test_clean_stores(raw):
    out = clean_stores(raw, PARAMS)
    assert len(out) == 20  # se quitó el duplicado
    assert out.isna().sum().sum() == 0
    assert out["car_spaces"].max() < 5000  # outlier recortado
    assert "basket_growth_pct" in out.columns
    assert not {"sales_m", "wages_m", "store_no"} & set(out.columns)


def test_split_and_train(raw):
    clean, X_train, X_test, y_train, _, selected, log, models = _trained(raw)
    assert len(X_test) == 4
    assert "gross_profit" not in X_train.columns
    assert 1 <= len(selected) <= X_train.shape[1]
    assert set(selected) <= set(X_train.columns)
    assert list(log["paso"]) == list(range(1, len(selected) + 1))
    assert set(models) == {"baseline_media", "regresion_simple", "ridge", "ridge_compacto",
                           "random_forest"}
    for name in ("ridge", "ridge_compacto", "regresion_simple"):
        assert len(models[name].predict(X_test)) == len(X_test)


def test_evaluate_and_explain(raw):
    clean, _, X_test, _, y_test, _, _, models = _trained(raw)

    metrics = evaluate_models(models, X_test, y_test)
    assert set(metrics["modelo"]) == set(models)
    assert {"MAE", "RMSE", "R2"} <= set(metrics.columns)
    assert (metrics["MAE"] >= 0).all()

    cv = cross_validate_models(models, clean, PARAMS)
    assert set(cv["modelo"]) == set(models)
    assert {"R2", "R2_desviacion"} <= set(cv.columns)

    importance = explain_model(models, X_test, y_test, PARAMS)
    assert set(importance["variable"]) == set(X_test.columns)
    assert importance["caida_r2"].is_monotonic_decreasing


def test_clean_stores_drops_missing_target(raw):
    raw.loc[3, "GrossProfit"] = None
    out = clean_stores(raw, PARAMS)
    assert len(out) == 19
    assert out["gross_profit"].notna().all()


def test_pipelines_build():
    from foodmart.pipelines.data_processing.pipeline import create_pipeline as dp
    from foodmart.pipelines.evaluation.pipeline import create_pipeline as ev
    from foodmart.pipelines.insights.pipeline import create_pipeline as ins
    from foodmart.pipelines.training.pipeline import create_pipeline as tr

    nodes = {n.name for p in (dp(), tr(), ev(), ins()) for n in p.nodes}
    assert nodes == {"clean_stores", "split_data", "select_features", "train_models",
                     "evaluate_models", "cross_validate_models", "explain_model",
                     "evaluate_classification", "summarize_eda", "build_report",
                     "driver_effects", "success_profile"}
    assert ev().nodes[-1].name == "build_report"  # el reporte depende de todo lo demás


def test_driver_effects_detects_negative_effect(raw):
    clean = clean_stores(raw, PARAMS)
    clean["competitors"] = [(i * 3) % 7 for i in range(len(clean))]
    clean["gross_profit"] = 2.0 - 0.1 * clean["competitors"]
    out = driver_effects(clean, PARAMS)
    top = out.iloc[0]
    assert top["variable"] == "competitors"
    assert top["efecto_por_unidad"] == pytest.approx(-0.1, abs=1e-3)
    assert {"ic95_inferior", "ic95_superior", "distinguible_de_cero"} <= set(out.columns)


def test_success_profile(raw):
    clean = clean_stores(raw, PARAMS)
    clean["competitors"] = [i % 4 for i in range(len(clean))]
    profile, by_comp = success_profile(clean, PARAMS)
    assert {"tiendas_exitosas", "resto", "diferencia"} <= set(profile.columns)
    assert by_comp["tiendas"].sum() == len(clean)
    assert by_comp["porcentaje_exitosas"].between(0, 100).all()


def test_classification_and_report(raw):
    clean, X_train, X_test, _, y_test, selected, log, models = _trained(raw)

    cls, cm = evaluate_classification(models, clean, PARAMS)
    assert set(cls["modelo"]) == {"regresion_simple", "ridge", "ridge_compacto", "random_forest"}
    scores = cls[["accuracy", "precision", "recall", "F1"]]
    assert scores.apply(lambda c: c.between(0, 1)).all().all()
    assert cm[["pred_baja", "pred_alta"]].to_numpy().sum() == len(clean)

    metrics = evaluate_models(models, X_test, y_test)
    cv = cross_validate_models(models, clean, PARAMS)
    eda = summarize_eda(raw, clean, models, X_train, X_test, PARAMS)
    json.dumps(eda)  # debe ser serializable para guardarse como JSON
    assert eda["quality"]["duplicates"] == 1  # el fixture trae una fila duplicada
    assert eda["split"] == {"train": len(X_train), "test": len(X_test)}

    effects = driver_effects(clean, PARAMS)
    profile, by_comp = success_profile(clean, PARAMS)
    html = build_report(clean, eda, metrics, cv, log, effects, profile, by_comp, cls, cm, PARAMS)
    assert html.startswith("<!doctype html>")
    secciones = ("F1", "falso positivo", "Pasillo 3", "Dicho en chapín", "TICKET DE RECOMEN",
                 "Parámetros de entrenamiento", "Cómo se controló el sobreajuste",
                 'id="fs"')
    for texto in secciones:
        assert texto in html
    assert "https://" not in html  # autocontenido: sin recursos externos
    assert "Preguntas que te puede hacer" not in html  # las respuestas van dentro del texto


def test_classification_rejects_unevaluable_final_model(raw):
    clean, *_, models = _trained(raw)
    with pytest.raises(ValueError, match="final_model"):
        evaluate_classification(models, clean, {**PARAMS, "final_model": "baseline_media"})
