"""Resumen estadístico del EDA, calculado con los datos reales para el reporte final."""
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.model_selection import RepeatedKFold, cross_val_score

RAW_TARGET = "GrossProfit"
BINARY = ["Sundays (Num)", "Mng-Sex (Num)", "HomeDel (Num)", "Loc'n (Num)", "State (Num)"]
CATEGORICAL = ["Location", "State", "Sundays", "HomeDel", "Mng-Sex"]


def _num(x) -> float | None:
    """Convierte a float de Python (apto para JSON); None si no es un número finito."""
    return float(x) if x is not None and np.isfinite(x) else None


def _ols(y: np.ndarray, *xs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mínimos cuadrados con intercepto; devuelve coeficientes y estadísticos t."""
    X = np.column_stack([np.ones(len(y)), *xs])
    b = np.linalg.pinv(X) @ y
    e = y - X @ b
    dof = len(y) - X.shape[1]
    if dof <= 0:
        return b, np.full(len(b), np.nan)
    se = np.sqrt(np.abs(np.diag(e @ e / dof * np.linalg.pinv(X.T @ X))))
    with np.errstate(all="ignore"):
        return b, b / se


def _quality(df: pd.DataFrame, k: float) -> dict:
    """Faltantes, duplicados y valores atípicos por la regla del IQR."""
    num = df.drop(columns=["Store No."] + BINARY, errors="ignore").select_dtypes("number")
    q1, q3 = num.quantile(0.25), num.quantile(0.75)
    iqr = q3 - q1
    flags = (num < q1 - k * iqr) | (num > q3 + k * iqr)
    per_var = flags.sum().sort_values(ascending=False)
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "missing": int(df.isna().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "outliers": int(flags.values.sum()),
        "outlier_cells": int(flags.size),
        "outliers_top": {str(c): int(n) for c, n in per_var.head(3).items() if n > 0},
    }


def _correlations(df: pd.DataFrame) -> list[dict]:
    """Correlación de Pearson (con p-valor) de cada variable numérica con la utilidad."""
    out = []
    for col in df.select_dtypes("number").columns.difference([RAW_TARGET, "Store No."]):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r, p = stats.pearsonr(df[col], df[RAW_TARGET])
        if np.isfinite(r):
            out.append({"variable": col, "r": float(r), "p": float(p)})
    return sorted(out, key=lambda d: d["r"])


def _competitors(df: pd.DataFrame) -> dict:
    """Utilidad por número de competidores y papel de las horas de operación."""
    comp, y = df["Competitors"].to_numpy(float), df[RAW_TARGET].to_numpy(float)
    groups = df.groupby("Competitors")[RAW_TARGET].agg(["mean", "count"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slope, intercept = np.polyfit(comp, y, 1)
        corr = np.corrcoef(comp, y)[0, 1]
        hrs = df["HrsTrading"].to_numpy(float)
        hrs_resid = hrs - np.polyval(np.polyfit(comp, hrs, 1), comp)
        return {
            "corr": _num(corr),
            "r2": _num(corr**2),
            "slope": _num(slope),
            "intercept": _num(intercept),
            "groups": [{"n_comp": int(i), "mean": float(r["mean"]), "stores": int(r["count"])}
                       for i, r in groups.iterrows()],
            "points": [[float(a), float(b)] for a, b in zip(comp, y)],
            "corr_hours_competitors": _num(np.corrcoef(comp, hrs)[0, 1]),
            "corr_hours_profit": _num(np.corrcoef(hrs, y)[0, 1]),
            "corr_hours_profit_adjusted": _num(np.corrcoef(hrs_resid, y)[0, 1]),
        }


def _categoricals(df: pd.DataFrame) -> list[dict]:
    """Prueba de Kruskal-Wallis de la utilidad entre grupos de cada variable categórica."""
    out = []
    for col in CATEGORICAL:
        groups = [g.to_numpy() for _, g in df.groupby(col)[RAW_TARGET]]
        if len(groups) < 2:
            continue
        try:
            p = stats.kruskal(*groups).pvalue
        except ValueError:
            continue
        out.append({"variable": col, "groups": len(groups), "min_group": min(map(len, groups)),
                    "p": _num(p)})
    return out


def _manager_sex(df: pd.DataFrame) -> dict | None:
    """Efecto bruto y ajustado por competidores del sexo del gerente."""
    if df["Mng-Sex (Num)"].nunique() < 2:
        return None
    y = df[RAW_TARGET].to_numpy(float)
    fem = df["Mng-Sex (Num)"].to_numpy(float)
    b0, t0 = _ols(y, fem)
    b1, t1 = _ols(y, fem, df["Competitors"].to_numpy(float))
    by_sex = df.groupby("Mng-Sex")[["Competitors", RAW_TARGET]].mean()
    return {
        "raw_effect": _num(b0[1]), "raw_t": _num(t0[1]),
        "adj_effect": _num(b1[1]), "adj_t": _num(t1[1]),
        "female_stores": int(fem.sum()),
        "competitors_by_sex": {str(k): float(v) for k, v in by_sex["Competitors"].items()},
        "profit_by_sex": {str(k): float(v) for k, v in by_sex[RAW_TARGET].items()},
    }


def _baskets(df: pd.DataFrame) -> dict:
    """Relación entre las canastas de 2013 y 2014."""
    growth = (df["Basket:2014"] / df["Basket:2013"] - 1) * 100
    return {
        "corr_2013_2014": _num(df["Basket:2013"].corr(df["Basket:2014"])),
        "growth_mean": _num(growth.mean()),
        "growth_min": _num(growth.min()),
        "growth_max": _num(growth.max()),
        "corr_profit": _num(df["Basket:2013"].corr(df[RAW_TARGET])),
    }


def _vif(df: pd.DataFrame) -> list[dict]:
    """Factor de inflación de la varianza de las variables candidatas (> 10 = colinealidad)."""
    drop = [RAW_TARGET, "Store No.", "Sales $m", "Wages $m", "Loc'n (Num)", "State (Num)"]
    X = df.drop(columns=drop, errors="ignore").select_dtypes("number")
    X = X.loc[:, X.std() > 0]
    if X.shape[1] < 2:
        return []
    Z = (X - X.mean()) / X.std()
    vif = pd.Series(np.diag(np.linalg.pinv(np.corrcoef(Z.to_numpy().T))), index=X.columns)
    return [{"variable": str(k), "vif": float(v)} for k, v in vif.nlargest(4).items()]


def _cv_comparison(models: dict, stores_clean: pd.DataFrame, params: dict) -> dict:
    """Compara regresión simple y Ridge con validación cruzada repetida (5 folds × 10)."""
    X = stores_clean.drop(columns=[params["target"]])
    y = stores_clean[params["target"]]
    cv = RepeatedKFold(n_splits=5, n_repeats=10, random_state=params["random_state"])
    r2 = {name: cross_val_score(clone(models[name]), X, y, cv=cv, scoring="r2")
          for name in ("regresion_simple", "ridge")}
    diff = r2["regresion_simple"] - r2["ridge"]
    return {
        "r2_simple": float(r2["regresion_simple"].mean()),
        "r2_ridge": float(r2["ridge"].mean()),
        "simple_wins": float((diff > 0).mean()),
        "splits": int(len(diff)),
    }


def summarize_eda(
    stores_raw: pd.DataFrame,
    stores_clean: pd.DataFrame,
    models: dict,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    params: dict,
) -> dict:
    """Calcula los hallazgos del EDA que se muestran en el reporte HTML.

    Args:
        stores_raw: Datos crudos de las tiendas (hoja "Stores-Data").
        stores_clean: Tabla limpia de tiendas (features + target).
        models: Modelos entrenados.
        X_train: Features de entrenamiento (para informar el tamaño real de la partición).
        X_test: Features de prueba.
        params: Parámetros del proyecto.

    Returns:
        dict: Resumen serializable a JSON con calidad de datos, correlaciones, competidores,
        categóricas, sexo del gerente, canastas, VIF y comparación por validación cruzada.

    """
    # Las estadísticas descriptivas usan las tiendas con utilidad registrada y sin duplicados
    # (como el pipeline); la calidad de datos se mide sobre los datos tal como llegaron.
    base = stores_raw.dropna(subset=[RAW_TARGET]).drop_duplicates()
    return {
        "quality": _quality(stores_raw, params["outlier_iqr_factor"]),
        "split": {"train": len(X_train), "test": len(X_test)},
        "correlations": _correlations(base),
        "competitors": _competitors(base),
        "categoricals": _categoricals(base),
        "manager_sex": _manager_sex(base),
        "baskets": _baskets(base),
        "vif": _vif(base),
        "cv": _cv_comparison(models, stores_clean, params),
    }
