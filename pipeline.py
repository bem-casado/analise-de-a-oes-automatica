from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


# ----------------------------
# Config
# ----------------------------

@dataclass
class GordonConfig:
    k: float = 0.10   # taxa de desconto
    g: float = 0.03   # crescimento


# ----------------------------
# Helpers
# ----------------------------

def to_numeric_pt(series: pd.Series) -> pd.Series:
    """Converte strings PT/BR com %, R$, vírgula -> float."""
    return pd.to_numeric(
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace("R$", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip(),
        errors="coerce",
    )


def normalize_column_name(name: str) -> str:
    """Normaliza nomes de colunas para evitar diferenças de acentuação/espaços."""
    no_accent = (
        unicodedata.normalize("NFKD", name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return " ".join(no_accent.strip().upper().split())


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df


def ensure_required_columns(df: pd.DataFrame, required: List[str], *, label: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        available = ", ".join(df.columns)
        raise KeyError(
            f"Colunas ausentes no CSV de {label}: {missing}. "
            f"Disponíveis: [{available}]"
        )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# ----------------------------
# Extract
# ----------------------------

def extract_csv(path: Path, *, sep: str = ";") -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep)
    return normalize_columns(df)


# ----------------------------
# Transform (Ações)
# ----------------------------

def transform_acoes(
    df: pd.DataFrame,
    *,
    dy_min: float = 5,
    roe_min: float = 15,
    pl_max: float = 15,
    pvp_max: float = 1.5,
    apply_graham: bool = True,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], pd.DataFrame]:
    """
    Retorna:
      - df_filtrado_dy_roe
      - df_graham (ou None se apply_graham=False)
      - df_ranking
    """
    df = normalize_columns(df)
    required = ["TICKER", "PRECO", "DY", "ROE", "P/L", "P/VP", "LPA", "VPA", "DL/EBIT"]
    ensure_required_columns(df, required, label="ações")

    # Normalizar numéricos
    for col in ["PRECO", "DY", "ROE", "P/L", "P/VP", "LPA", "VPA"]:
        df[col] = to_numeric_pt(df[col])

    df = df[
        ((df["P/L"] > 0) | df["P/L"].isna()) &
        ((df["ROE"] > 0) | df["ROE"].isna()) &
        ((df["DY"] >= 0) | df["DY"].isna())
    ].copy()

    df_filtrado = df[
        ((df["DY"] >= dy_min) | df["DY"].isna()) &
        ((df["ROE"] >= roe_min) | df["ROE"].isna())
    ].copy()

    if not apply_graham:
        return df_filtrado, None, build_ranking(df_filtrado)

    df_g = df_filtrado[
        (df_filtrado["P/L"] <= pl_max) & (df_filtrado["P/VP"] <= pvp_max)
    ].copy()
    df_g["Valor_Graham"] = np.sqrt(df_g["P/L"] * df_g["P/VP"] * df_g["LPA"] * df_g["VPA"])
    df_g["Diferenca_Graham"] = df_g["Valor_Graham"] - df_g["PRECO"]

    df_g = df_g[["TICKER", "DY", "ROE", "PRECO", "Valor_Graham", "Diferenca_Graham"]].copy()
    return df_filtrado, df_g, build_ranking(df_filtrado)


def normalize_series(series: pd.Series, *, higher_better: bool) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series(1.0, index=series.index)
    if higher_better:
        return (series - min_val) / (max_val - min_val)
    return (max_val - series) / (max_val - min_val)


def build_ranking(df: pd.DataFrame) -> pd.DataFrame:
    df_rank = df[["TICKER", "DY", "ROE", "P/L", "P/VP", "DL/EBIT"]].copy()

    df_rank["Norm_ROE"] = normalize_series(df_rank["ROE"], higher_better=True).fillna(0.5)
    df_rank["Norm_DY"] = normalize_series(df_rank["DY"], higher_better=True).fillna(0.5)
    df_rank["Norm_PL"] = normalize_series(df_rank["P/L"], higher_better=False).fillna(0.5)
    df_rank["Norm_PVP"] = normalize_series(df_rank["P/VP"], higher_better=False).fillna(0.5)
    df_rank["Norm_DL_EBIT"] = normalize_series(df_rank["DL/EBIT"], higher_better=False).fillna(0.5)

    df_rank["Score"] = (
        (df_rank["Norm_ROE"] * 0.30) +
        (df_rank["Norm_DY"] * 0.30) +
        ((df_rank["Norm_PL"] + df_rank["Norm_PVP"]) / 2 * 0.25) +
        (df_rank["Norm_DL_EBIT"] * 0.15)
    )

    df_rank = df_rank.sort_values("Score", ascending=False).copy()
    df_rank["Rank"] = range(1, len(df_rank) + 1)
    return df_rank


# ----------------------------
# Transform (FII)
# ----------------------------

def transform_fii(df: pd.DataFrame, *, gordon: GordonConfig) -> pd.DataFrame:
    df = normalize_columns(df)
    required = [
        "TICKER",
        "PRECO",
        "ULTIMO DIVIDENDO",
        "DY",
        "VALOR PATRIMONIAL COTA",
        "P/VP",
        "CAGR DIVIDENDOS 3 ANOS",
    ]
    ensure_required_columns(df, required, label="FII")

    for col in [
        "PRECO",
        "ULTIMO DIVIDENDO",
        "DY",
        "VALOR PATRIMONIAL COTA",
        "P/VP",
        "CAGR DIVIDENDOS 3 ANOS",
    ]:
        df[col] = to_numeric_pt(df[col])

    df["CAGR DIVIDENDOS 3 ANOS"] = df["CAGR DIVIDENDOS 3 ANOS"] / 100

    denom = (gordon.k - gordon.g)
    if denom <= 0:
        raise ValueError("Parâmetros inválidos no Gordon: (k - g) deve ser > 0")

    df["Preco_Justo_Gordon"] = ((df["ULTIMO DIVIDENDO"] * 12) / denom).round(2)

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["Preco_Justo_Gordon"])
    df = df[df["Preco_Justo_Gordon"] > 0].copy()
    return df


# ----------------------------
# Load
# ----------------------------

def load_acoes_xlsx(
    out_xlsx: Path,
    *,
    df_raw: pd.DataFrame,
    df_filtrado: pd.DataFrame,
    df_graham: Optional[pd.DataFrame] = None,
    df_ranking: Optional[pd.DataFrame] = None,
) -> None:
    """Salva Raw + filtrados em um .xlsx."""
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_raw.to_excel(writer, sheet_name="Raw", index=False)
        df_filtrado.to_excel(writer, sheet_name="Filtrado_DY_ROE", index=False)
        if df_graham is not None:
            df_graham.to_excel(writer, sheet_name="Filtrado_Graham", index=False)
        if df_ranking is not None:
            df_ranking.to_excel(writer, sheet_name="Ranking", index=False)


def load_fii_xlsx(out_xlsx: Path, *, df_final: pd.DataFrame) -> None:
    """Salva a análise de Gordon em um .xlsx."""
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_final.to_excel(writer, sheet_name="Analise_Gordon", index=False)
