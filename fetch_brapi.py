from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import pandas as pd
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from pipeline import ensure_dir


BRAPI_BASE_URL = "https://brapi.dev/api/quote"


@dataclass
class BrapiResult:
    ticker: str
    data: Dict[str, Any]


def load_tickers(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de tickers não encontrado: {path}")
    tickers: List[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            ticker = line.strip().upper()
            if not ticker or ticker.startswith("#"):
                continue
            tickers.append(ticker)
    return tickers


def _fetch_single_ticker(ticker: str, *, token: Optional[str] = None) -> Optional[BrapiResult]:
    params: Dict[str, str] = {"fundamental": "true"}
    if token:
        params["token"] = token
    query = urllib_parse.urlencode(params)
    url = f"{BRAPI_BASE_URL}/{ticker}?{query}"
    try:
        with urllib_request.urlopen(url, timeout=20) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
    except urllib_error.HTTPError as exc:
        print(f"⚠️ Ticker inválido ou erro na API ({ticker}): {exc.code}")
        return None
    except urllib_error.URLError as exc:
        print(f"⚠️ Erro ao consultar {ticker}: {exc.reason}")
        return None
    if status_code != 200:
        print(f"⚠️ Ticker inválido ou erro na API ({ticker}): {status_code}")
        return None
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        print(f"⚠️ Resposta inválida da API para {ticker}.")
        return None
    return BrapiResult(ticker=ticker, data=payload)


def _get_first(data: Dict[str, Any], keys: Iterable[str]) -> Optional[float]:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return float(value)
    return None


def _get_nested_first(data: Dict[str, Any], keys: Iterable[str]) -> Optional[float]:
    primary = _get_first(data, keys)
    if primary is not None:
        return primary
    return _get_first(data.get("fundamentalData", {}), keys)


def _normalize_percent(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if 0 <= value <= 1:
        return value * 100
    return value


def _parse_brapi_result(result: Dict[str, Any]) -> Dict[str, Optional[float]]:
    symbol = result.get("symbol") or result.get("shortName") or "N/A"

    price = _get_first(result, ["regularMarketPrice", "price", "regularMarketPreviousClose"])
    dy = _normalize_percent(_get_nested_first(result, ["dividendYield", "dividendYieldPercent"]))
    roe = _normalize_percent(_get_nested_first(result, ["roe", "returnOnEquity"]))

    pl = _get_nested_first(result, ["priceEarnings", "peRatio", "trailingPE"])
    pvp = _get_nested_first(result, ["priceToBook"])

    lpa = _get_nested_first(result, ["earningsPerShare", "eps"])
    vpa = _get_nested_first(result, ["bookValue"])

    dl_ebit = _get_nested_first(result, ["debtToEbitda"])

    if pl is None and price is not None and lpa:
        pl = price / lpa
    if pvp is None and price is not None and vpa:
        pvp = price / vpa

    return {
        "TICKER": symbol,
        "PRECO": price,
        "DY": dy,
        "ROE": roe,
        "P/L": pl,
        "P/VP": pvp,
        "LPA": lpa,
        "VPA": vpa,
        "DL/EBIT": dl_ebit,
    }


def fetch_brapi_acoes(tickers: List[str], *, raw_dir: Path) -> pd.DataFrame:
    token = os.getenv("BRAPI_TOKEN")
    ensure_dir(raw_dir)
    results: List[BrapiResult] = []

    for ticker in tickers:
        payload = _fetch_single_ticker(ticker, token=token)
        if payload is None:
            continue
        results.append(payload)

    if not results:
        print("⚠️ Nenhum ticker válido encontrado na API.")
        return pd.DataFrame(
            columns=["TICKER", "PRECO", "DY", "ROE", "P/L", "P/VP", "LPA", "VPA", "DL/EBIT"]
        )

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "results": [{"ticker": item.ticker, "data": item.data} for item in results],
    }
    snapshot_path = raw_dir / f"brapi_snapshot_{datetime.now():%Y%m%d_%H%M%S}.json"
    with snapshot_path.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2)
    print(f"✅ Snapshot brapi salvo em: {snapshot_path}")

    parsed_rows = []
    for item in results:
        api_results = item.data.get("results", [])
        if not api_results:
            print(f"⚠️ Sem resultados para {item.ticker}.")
            continue
        parsed_rows.append(_parse_brapi_result(api_results[0]))

    return pd.DataFrame(parsed_rows)


def _parse_snapshot_results(results: Sequence[Dict[str, Any]]) -> pd.DataFrame:
    parsed_rows = []
    for item in results:
        api_results = item.get("data", {}).get("results", [])
        if not api_results:
            print(f"⚠️ Snapshot sem resultados para {item.get('ticker', 'N/A')}.")
            continue
        parsed_rows.append(_parse_brapi_result(api_results[0]))
    return pd.DataFrame(parsed_rows)


def load_snapshot_acoes(snapshot_path: Path) -> pd.DataFrame:
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot não encontrado: {snapshot_path}")
    with snapshot_path.open("r", encoding="utf-8") as handle:
        snapshot = json.load(handle)
    results = snapshot.get("results", [])
    if not results:
        print("⚠️ Snapshot vazio ou sem resultados.")
        return pd.DataFrame(
            columns=["TICKER", "PRECO", "DY", "ROE", "P/L", "P/VP", "LPA", "VPA", "DL/EBIT"]
        )
    return _parse_snapshot_results(results)
