#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import requests
from pathlib import Path

# === 設定 ===
API_KEY = os.getenv("MSIL_API_KEY") or "0e83ad5d93214e04abf37c970c32b641"
OUTPUT_DIR = Path("./geojson")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 日本全域（WGS84）

JAPAN_ENVELOPE_4326 = {
    "xmin": 100.0, "ymin": -10.0,
    "xmax": 170.0, "ymax": 60.0,
    "spatialReference": {"wkid": 4326}
}

# 共通セッション（キーはヘッダで送るが、クエリにも付けて実装差に対応）
session = requests.Session()
session.headers.update({"Ocp-Apim-Subscription-Key": API_KEY})
TIMEOUT = 60
PAGE_SIZE = 1000


def get_count(base_url: str, layer_selection: int, envelope: dict = JAPAN_ENVELOPE_4326) -> int:
    """bbox条件で総件数のみを返す（取りこぼし検知用）"""
    params = {
        "f": "json",
        "where": "1=1",
        "geometry": json.dumps(envelope, ensure_ascii=False),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnCountOnly": "true",
        "subscription-key": API_KEY,
    }
    r = session.get(f"{base_url}/{layer_selection}/query", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    js = r.json()
    return int(js.get("count", 0))


def fetch_geojson(base_url: str, layer_selection: int, envelope: dict = JAPAN_ENVELOPE_4326,
                  page_size: int = PAGE_SIZE, retry: int = 5, sleep_sec: float = 0.2) -> dict:
    """
    海しるAPIの MapServer/{LayerSelection}/query (f=geojson) をページングして
    FeatureCollection を作って返す。
    """
    features = []
    offset = 0

    while True:
        params = {
            "f": "geojson",
            "where": "1=1",
            "geometry": json.dumps(envelope, ensure_ascii=False),
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "outSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "true",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            # 念のためクエリにもキーを付ける（APIゲートウェイ実装差の吸収）
            "subscription-key": API_KEY,
        }

        # リトライ（429/503向けの軽い指数バックオフ）
        for attempt in range(retry):
            try:
                r = session.get(f"{base_url}/{layer_selection}/query", params=params, timeout=TIMEOUT)
                if r.status_code == 200:
                    chunk = r.json()
                    break
                if r.status_code in (429, 503):
                    time.sleep(2 * (attempt + 1))
                    continue
                # 他のステータスは即エラー
                raise RuntimeError(f"{r.status_code} {r.text[:500]}")
            except requests.RequestException:
                if attempt == retry - 1:
                    raise
                time.sleep(2 * (attempt + 1))

        got = chunk.get("features", [])
        features.extend(got)

        # exceededTransferLimit のヒントも出力（jsonの時のみ入ることが多いが、参考ログ）
        exceeded = chunk.get("exceededTransferLimit")
        print(f"{base_url} LAYER {layer_selection} fetched {len(got)}  total {len(features)}  offset {offset}"
              + (f"  exceededTransferLimit={exceeded}" if exceeded is not None else ""))

        # 1レスポンスが page_size 未満なら最後のページ
        if len(got) < page_size:
            break

        offset += page_size
        time.sleep(sleep_sec)

    return {"type": "FeatureCollection", "features": features}


def save_geojson(fc: dict, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False)
    print(f"Saved: {path}")


def fetch_and_verify(name: str, base_url: str, layer_selection: int, outfile: Path):
    """取得→保存→件数検証まで一気通貫"""
    # 期待件数（count）を先に取得
    expected = get_count(base_url, layer_selection)
    print(f"[{name}] expected count (by returnCountOnly) = {expected}")

    # データ取得
    fc = fetch_geojson(base_url, layer_selection)
    actual = len(fc.get("features", []))
    print(f"[{name}] actual fetched features         = {actual}")

    # 保存
    save_geojson(fc, outfile)

    # 照合
    if expected != actual:
        print(f"⚠️ [{name}] count mismatch: expected={expected}, actual={actual}  → 取りこぼしの可能性あり")
    else:
        print(f"✅ [{name}] counts match. 全件取得できています。")


def main():
    # 1) 島名（Point = LayerSelection 1）
    fetch_and_verify(
        name="island",
        base_url="https://api.msil.go.jp/island/v2/MapServer",
        layer_selection=1,
        outfile=OUTPUT_DIR / "islands.geojson",
    )

    # 2) 海底地形名（Point = LayerSelection 1）
    fetch_and_verify(
        name="undersea-features (point)",
        base_url="https://api.msil.go.jp/undersea-features/v2/MapServer",
        layer_selection=1,
        outfile=OUTPUT_DIR / "undersea_features.geojson",
    )

    # 3) 海底ケーブル（Polyline = LayerSelection 2）
    fetch_and_verify(
        name="submarine-cable-line (polyline)",
        base_url="https://api.msil.go.jp/submarine-cable-line/v2/MapServer",
        layer_selection=2,
        outfile=OUTPUT_DIR / "submarine_cables.geojson",
    )

    print("done")


if __name__ == "__main__":
    main()
