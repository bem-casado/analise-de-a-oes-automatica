from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

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


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# ----------------------------
# Extract
# ----------------------------

def extract_csv(path: Path, *, sep: str = ";") -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep)
    df.columns = df.columns.str.strip()
    return df


# ----------------------------
# Transform (Ações)
# ----------------------------

def transform_acoes(
    df: pd.DataFrame,
    *,
    dy_min: float = 5,
    roe_min: float = 15,
    apply_graham: bool = True,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Retorna:
      - df_filtrado_dy_roe
      - df_graham (ou None se apply_graham=False)
    """
    required = ["TICKER", "PRECO", "DY", "ROE", "P/L", "P/VP", "LPA", "VPA"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Colunas ausentes no CSV de ações: {missing}")

    # Normalizar numéricos
    for col in ["PRECO", "DY", "ROE", "P/L", "P/VP", "LPA", "VPA"]:
        df[col] = to_numeric_pt(df[col])

    df_filtrado = df[(df["DY"] >= dy_min) & (df["ROE"] >= roe_min)].copy()

    if not apply_graham:
        return df_filtrado, None

    df_g = df_filtrado[(df_filtrado["P/L"] <= 15) & (df_filtrado["P/VP"] <= 1.5)].copy()
    df_g["Valor_Graham"] = np.sqrt(df_g["P/L"] * df_g["P/VP"] * df_g["LPA"] * df_g["VPA"])
    df_g["Diferenca_Graham"] = df_g["Valor_Graham"] - df_g["PRECO"]

    df_g = df_g[["TICKER", "DY", "ROE", "PRECO", "Valor_Graham", "Diferenca_Graham"]].copy()
    return df_filtrado, df_g


# ----------------------------
# Transform (FII)
# ----------------------------

def transform_fii(df: pd.DataFrame, *, gordon: GordonConfig) -> pd.DataFrame:
    required = [
        "TICKER",
        "PRECO",
        "ULTIMO DIVIDENDO",
        "DY",
        "VALOR PATRIMONIAL COTA",
        "P/VP",
        "CAGR DIVIDENDOS 3 ANOS",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Colunas ausentes no CSV de FII: {missing}")

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
) -> None:
    """Salva Raw + filtrados em um .xlsx."""
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_raw.to_excel(writer, sheet_name="Raw", index=False)
        df_filtrado.to_excel(writer, sheet_name="Filtrado_DY_ROE", index=False)
        if df_graham is not None:
            df_graham.to_excel(writer, sheet_name="Filtrado_Graham", index=False)


def load_fii_xlsx(out_xlsx: Path, *, df_final: pd.DataFrame) -> None:
    """Salva a análise de Gordon em um .xlsx."""
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df_final.to_excel(writer, sheet_name="Analise_Gordon", index=False)
