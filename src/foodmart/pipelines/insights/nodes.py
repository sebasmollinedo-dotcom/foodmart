"""Nodos de análisis de negocio, qué variables importan y cómo es una tienda exitosa."""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def driver_effects(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Estima el efecto de cada variable sobre la utilidad, con su margen de error.

    Usa una regresión lineal múltiple sobre todas las tiendas. El efecto de cada variable
    es lo que cambia la utilidad por cada unidad adicional, dejando las demás constantes.
    El intervalo de confianza de 95 por ciento se calcula con bootstrap. Si el intervalo
    incluye el cero, el efecto no se puede distinguir de la casualidad.

    Args:
        df: Tabla limpia de tiendas, incluye el objetivo.
        params: Parámetros (target, driver_variables, n_bootstrap, random_state).

    Returns:
        pd.DataFrame: Efecto por unidad, efecto de una desviación estándar e intervalo.

    """
    cols = params["driver_variables"]
    X = df[cols].to_numpy(dtype=float)
    y = df[params["target"]].to_numpy(dtype=float)
    A = np.column_stack([np.ones(len(X)), X])

    def fit(rows: np.ndarray) -> np.ndarray:
        return np.linalg.lstsq(A[rows], y[rows], rcond=None)[0][1:]

    beta = fit(np.arange(len(y)))
    rng = np.random.default_rng(params["random_state"])
    boots = np.array([fit(rng.integers(0, len(y), len(y))) for _ in range(params["n_bootstrap"])])
    low, high = np.percentile(boots, [2.5, 97.5], axis=0)
    out = pd.DataFrame({
        "variable": cols,
        "efecto_por_unidad": beta,
        "efecto_una_desviacion": beta * X.std(axis=0),
        "ic95_inferior": low,
        "ic95_superior": high,
        "distinguible_de_cero": (low * high) > 0,
    })
    out = out.reindex(out["efecto_una_desviacion"].abs().sort_values(ascending=False).index)
    return out.round(4)


def success_profile(df: pd.DataFrame, params: dict):
    """Compara las tiendas más exitosas con el resto.

    Una tienda es exitosa si su utilidad está en el cuarto superior, según
    ``success_quantile``. También calcula cuántas tiendas exitosas hay según el número
    de competidores y cuántas horas abren en promedio.

    Args:
        df: Tabla limpia de tiendas, incluye el objetivo.
        params: Parámetros (target, success_quantile).

    Returns:
        tuple: Perfil promedio de exitosas contra el resto, y tabla por número de competidores.

    """
    target = params["target"]
    data = df.copy()
    data["exitosa"] = data[target] >= data[target].quantile(params["success_quantile"])
    features = [c for c in data.columns if c not in (target, "exitosa")]
    means = data.groupby("exitosa")[features].mean().T
    profile = pd.DataFrame({
        "variable": means.index,
        "tiendas_exitosas": means[True].to_numpy(),
        "resto": means[False].to_numpy(),
    })
    profile["diferencia"] = profile["tiendas_exitosas"] - profile["resto"]
    profile["diferencia_en_desviaciones"] = profile["diferencia"] / data[features].std().to_numpy()
    profile = profile.reindex(
        profile["diferencia_en_desviaciones"].abs().sort_values(ascending=False).index
    )

    by_comp = data.groupby("competitors").agg(
        tiendas=(target, "size"),
        utilidad_media=(target, "mean"),
        porcentaje_exitosas=("exitosa", "mean"),
        horas_medias=("hrstrading", "mean"),
    ).reset_index()
    by_comp["porcentaje_exitosas"] = by_comp["porcentaje_exitosas"] * 100
    logger.info("Perfil de tiendas exitosas:\n%s", profile.head(6).round(2).to_string(index=False))
    return profile.round(3), by_comp.round(2)
