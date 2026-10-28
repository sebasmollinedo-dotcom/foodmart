"""Nodos de carga, limpieza y transformación."""
import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)


def _snake(name: str) -> str:
    """Convierte un nombre de columna a snake_case.

    Args:
        name: Nombre original, p. ej. "Adv.$'000".

    Returns:
        str: Nombre limpio, p. ej. "adv_000".

    """
    return re.sub(r"[^0-9a-z]+", "_", name.lower()).strip("_")


def clean_stores(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Limpia los datos: nombres, duplicados, faltantes, outliers y feature engineering.

    Args:
        df: Datos crudos de las tiendas (hoja "Stores-Data").
        params: Parámetros del proyecto (target, outlier_iqr_factor, drop_columns).

    Returns:
        pd.DataFrame: Tabla limpia, solo numérica, con ``basket_growth_pct`` añadida.

    """
    df = df.copy()
    n_inicial = len(df)
    df.columns = [_snake(c) for c in df.columns]

    # Nos quedamos con las columnas numéricas (location_num, state_num...) y
    # quitamos las versiones en texto que son duplicado de las mismas.
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    df = df.drop(columns=text_cols)
    df = df.rename(columns={"loc_n_num": "location", "state_num": "state",
                            "sundays_num": "sundays", "mng_sex_num": "mng_female",
                            "homedel_num": "home_delivery", "grossprofit": "gross_profit"})

    df = df.drop_duplicates()
    df = df.dropna(subset=[params["target"]])

    # Outliers: recorte por IQR solo en variables continuas (no binarias ni categóricas)
    skip = {params["target"], "location", "state", "sundays", "mng_female", "home_delivery"}
    k = params["outlier_iqr_factor"]
    for col in df.columns.difference(skip):
        q1, q3 = df[col].quantile([0.25, 0.75])
        df[col] = df[col].clip(q1 - k * (q3 - q1), q3 + k * (q3 - q1))

    # Feature engineering: cuánto subió el precio de la canasta en un año (%)
    df["basket_growth_pct"] = (df["basket_2014"] / df["basket_2013"] - 1) * 100

    df = df.drop(columns=[c for c in params["drop_columns"] if c in df.columns])
    logger.info("Filas: %d -> %d | columnas finales: %d", n_inicial, len(df), df.shape[1])
    return df
