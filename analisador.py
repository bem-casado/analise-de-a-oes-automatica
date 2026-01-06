import argparse
from pathlib import Path

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
    p.add_argument("--acoes", required=True, help="Caminho do CSV de ações (sep=';')")
    p.add_argument("--fii", required=False, help="(Opcional) Caminho do CSV de FIIs (sep=';')")
    p.add_argument("--out", default="out", help="Diretório de saída (default: ./out)")

    p.add_argument("--dy", type=float, default=5, help="DY mínimo para ações (default: 5)")
    p.add_argument("--roe", type=float, default=15, help="ROE mínimo para ações (default: 15)")
    p.add_argument("--no-graham", action="store_true", help="Desativa aba de Graham")

    p.add_argument("--k", type=float, default=0.10, help="Taxa k do Gordon (default: 0.10)")
    p.add_argument("--g", type=float, default=0.03, help="Crescimento g do Gordon (default: 0.03)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    out_dir = Path(args.out).expanduser().resolve()
    ensure_dir(out_dir)

    # --- Ações
    acoes_path = Path(args.acoes).expanduser().resolve()
    df_acoes_raw = extract_csv(acoes_path, sep=";")

    df_filtrado, df_graham = transform_acoes(
        df_acoes_raw,
        dy_min=args.dy,
        roe_min=args.roe,
        apply_graham=not args.no_graham,
    )

    out_acoes = out_dir / "acoes_resultado.xlsx"
    load_acoes_xlsx(out_acoes, df_raw=df_acoes_raw, df_filtrado=df_filtrado, df_graham=df_graham)

    print(
        f"✅ Ações -> {out_acoes} | "
        f"Filtrado: {len(df_filtrado)} | "
        f"Graham: {0 if df_graham is None else len(df_graham)}"
    )

    # --- FIIs (opcional)
    if args.fii:
        fii_path = Path(args.fii).expanduser().resolve()
        df_fii_raw = extract_csv(fii_path, sep=";")
        df_fii_final = transform_fii(df_fii_raw, gordon=GordonConfig(k=args.k, g=args.g))

        out_fii = out_dir / "fii_resultado.xlsx"
        load_fii_xlsx(out_fii, df_final=df_fii_final)

        print(f"✅ FIIs  -> {out_fii} | Gordon: {len(df_fii_final)}")


if __name__ == "__main__":
    main()
