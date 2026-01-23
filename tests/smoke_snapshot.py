from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from fetch_brapi import load_snapshot_acoes  # noqa: E402


def main() -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "brapi_snapshot_sample.json"
    df = load_snapshot_acoes(fixture)
    expected_columns = {
        "TICKER",
        "PRECO",
        "DY",
        "ROE",
        "P/L",
        "P/VP",
        "LPA",
        "VPA",
        "DL/EBIT",
    }
    missing = expected_columns.difference(df.columns)
    if missing:
        raise SystemExit(f"Missing columns: {sorted(missing)}")
    if df.empty:
        raise SystemExit("Snapshot dataframe is empty.")
    print("Snapshot smoke test ok.")


if __name__ == "__main__":
    main()
