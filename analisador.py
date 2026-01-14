import argparse
import json
from pathlib import Path
from typing import Optional

from pipeline import (
    GordonConfig,
    ensure_dir,
    extract_csv,
    load_acoes_xlsx,
    load_fii_xlsx,
    transform_acoes,
    transform_fii,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ETL pipeline: ações + FIIs (StatusInvest exports)")
    p.add_argument(
        "--config",
        default="config.json",
        help="Arquivo de configuração JSON (default: ./config.json)",
    )
    p.add_argument("--acoes", required=True, help="Caminho do CSV de ações (sep=';')")
    p.add_argument("--fii", required=False, help="(Opcional) Caminho do CSV de FIIs (sep=';')")
    p.add_argument("--out", default="out", help="Diretório de saída (default: ./out)")

    p.add_argument("--dy", type=float, default=None, help="DY mínimo para ações")
    p.add_argument("--roe", type=float, default=None, help="ROE mínimo para ações")
    p.add_argument("--pl", type=float, default=None, help="P/L máximo para Graham")
    p.add_argument("--pvp", type=float, default=None, help="P/VP máximo para Graham")
    p.add_argument("--no-graham", action="store_true", help="Desativa aba de Graham")

    p.add_argument("--k", type=float, default=None, help="Taxa k do Gordon")
    p.add_argument("--g", type=float, default=None, help="Crescimento g do Gordon")
    return p.parse_args()


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_value(cli_value: Optional[float], config: dict, key: str, default: float) -> float:
    if cli_value is not None:
        return cli_value
    return float(config.get(key, default))


def main() -> None:
    args = parse_args()

    config_path = Path(args.config).expanduser().resolve()
    config = load_config(config_path)
    acoes_config = config.get("acoes", {})
    gordon_config = config.get("gordon", {})

    out_dir = Path(args.out).expanduser().resolve()
    ensure_dir(out_dir)

    # --- Ações
    acoes_path = Path(args.acoes).expanduser().resolve()
    df_acoes_raw = extract_csv(acoes_path, sep=";")

    df_filtrado, df_graham, df_ranking = transform_acoes(
        df_acoes_raw,
        dy_min=resolve_value(args.dy, acoes_config, "dy_min", 5),
        roe_min=resolve_value(args.roe, acoes_config, "roe_min", 15),
        pl_max=resolve_value(args.pl, acoes_config, "pl_max", 15),
        pvp_max=resolve_value(args.pvp, acoes_config, "pvp_max", 1.5),
        apply_graham=not args.no_graham,
    )

    out_acoes = out_dir / "acoes_resultado.xlsx"
    load_acoes_xlsx(
        out_acoes,
        df_raw=df_acoes_raw,
        df_filtrado=df_filtrado,
        df_graham=df_graham,
        df_ranking=df_ranking,
    )

    print(
        f"✅ Ações -> {out_acoes} | "
        f"Filtrado: {len(df_filtrado)} | "
        f"Graham: {0 if df_graham is None else len(df_graham)}"
    )

    # --- FIIs (opcional)
    if args.fii:
        fii_path = Path(args.fii).expanduser().resolve()
        df_fii_raw = extract_csv(fii_path, sep=";")
        df_fii_final = transform_fii(
            df_fii_raw,
            gordon=GordonConfig(
                k=resolve_value(args.k, gordon_config, "k", 0.10),
                g=resolve_value(args.g, gordon_config, "g", 0.03),
            ),
        )

        out_fii = out_dir / "fii_resultado.xlsx"
        load_fii_xlsx(out_fii, df_final=df_fii_final)

        print(f"✅ FIIs  -> {out_fii} | Gordon: {len(df_fii_final)}")


if __name__ == "__main__":
    main()
