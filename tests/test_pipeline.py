"""Pruebas básicas de los nodos."""
import pandas as pd
import pytest

from foodmart.pipelines.data_processing.nodes import clean_stores
from foodmart.pipelines.evaluation.nodes import evaluate_models, explain_model
from foodmart.pipelines.training.nodes import split_data, train_models

PARAMS = {
    "target": "gross_profit",
    "drop_columns": ["store_no", "sales_m", "wages_m"],
    "categorical": ["location", "state"],
    "outlier_iqr_factor": 1.5,
    "test_size": 0.2,
    "random_state": 42,
    "rf_param_grid": {"n_estimators": [10], "max_depth": [3], "min_samples_leaf": [2]},
    "cv_folds": 2,
}


@pytest.fixture
def raw() -> pd.DataFrame:
    """Mini versión del Excel original (con un duplicado y un outlier)."""
    n = 20
    df = pd.DataFrame({
        "Store No.": range(n), "Sales $m": 10.0, "Wages $m": 2.0, "No. Staff": 60,
        "Location": "Mall", "Loc'n (Num)": [1, 2] * 10, "State": "NSW", "State (Num)": 1,
        "Age (Yrs)": range(1, n + 1), "GrossProfit": [i / 10 for i in range(n)],
        "Adv.$'000": 150, "Competitors": 2, "HrsTrading": 100, "Sundays": "Sun:No",
        "Sundays (Num)": 0, "Mng-Sex": "Male", "Mng-Sex (Num)": 0, "Mng-Age": 40,
        "Mng-Exp": 8, "Mng-Train": 2, "Union%": 38, "Car Spaces": 40, "HomeDel": "Del:No",
        "HomeDel (Num)": 0, "Basket:2013": 170, "Basket:2014": 180,
    })
    df.loc[0, "Car Spaces"] = 5000  # outlier
    return pd.concat([df, df.iloc[[1]]])  # duplicado


def test_clean_stores(raw):
    out = clean_stores(raw, PARAMS)
    assert len(out) == 20  # se quitó el duplicado
    assert out.isna().sum().sum() == 0
    assert out["car_spaces"].max() < 5000  # outlier recortado
    assert "basket_growth_pct" in out.columns
    assert not {"sales_m", "wages_m", "store_no"} & set(out.columns)


def test_split_and_train(raw):
    clean = clean_stores(raw, PARAMS)
    X_train, X_test, y_train, y_test = split_data(clean, PARAMS)
    assert len(X_test) == 4
    assert "gross_profit" not in X_train.columns
    models = train_models(X_train, y_train, PARAMS)
    assert set(models) == {"baseline_media", "ridge", "random_forest"}
    assert len(models["ridge"].predict(X_test)) == len(X_test)


def test_evaluate_and_explain(raw):
    clean = clean_stores(raw, PARAMS)
    X_train, X_test, y_train, y_test = split_data(clean, PARAMS)
    models = train_models(X_train, y_train, PARAMS)

    metrics = evaluate_models(models, X_test, y_test)
    assert set(metrics["modelo"]) == set(models)
    assert {"MAE", "RMSE", "R2"} <= set(metrics.columns)
    assert (metrics["MAE"] >= 0).all()

    importance = explain_model(models, X_test, y_test, {**PARAMS, "final_model": "ridge"})
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
    from foodmart.pipelines.training.pipeline import create_pipeline as tr

    nodes = [n.name for p in (dp(), tr(), ev()) for n in p.nodes]
    assert nodes == ["clean_stores", "split_data", "train_models", "evaluate_models",
                     "explain_model"]
