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

# 取得範囲（WGS84）—広め
JAPAN_ENVELOPE_4326 = {
    "xmin": 100.0, "ymin": -10.0,
    "xmax": 170.0, "ymax": 60.0,
    "spatialReference": {"wkid": 4326}
}

# 共通セッション（キーはヘッダで送る。クエリにも付けて実装差に対応）
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
    MapServer/{LayerSelection}/query (f=geojson) をページングし FeatureCollection を返す。
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
                raise RuntimeError(f"{r.status_code} {r.text[:500]}")
            except requests.RequestException:
                if attempt == retry - 1:
                    raise
                time.sleep(2 * (attempt + 1))

        got = chunk.get("features", [])
        features.extend(got)
        exceeded = chunk.get("exceededTransferLimit")
        print(f"{base_url} LAYER {layer_selection} fetched {len(got)}  total {len(features)}  offset {offset}"
              + (f"  exceededTransferLimit={exceeded}" if exceeded is not None else ""))

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
    expected = get_count(base_url, layer_selection)
    print(f"[{name}] expected count (by returnCountOnly) = {expected}")

    fc = fetch_geojson(base_url, layer_selection)
    actual = len(fc.get("features", []))
    print(f"[{name}] actual fetched features         = {actual}")

    save_geojson(fc, outfile)

    if expected != actual:
        print(f"⚠️ [{name}] count mismatch: expected={expected}, actual={actual}  → 取りこぼしの可能性あり")
    else:
        print(f"✅ [{name}] counts match. 全件取得できています。")

    return fc, expected, actual


def main():
    # 1) 島名（Point = 1）
    islands, _, _ = fetch_and_verify(
        name="island (point)",
        base_url="https://api.msil.go.jp/island/v2/MapServer",
        layer_selection=1,
        outfile=OUTPUT_DIR / "islands.geojson",
    )

    # 2) 海底地形名（Point = 1）
    undersea_points, _, _ = fetch_and_verify(
        name="undersea-features (point)",
        base_url="https://api.msil.go.jp/undersea-features/v2/MapServer",
        layer_selection=1,
        outfile=OUTPUT_DIR / "undersea_features.geojson",
    )

    # 3) 海底ケーブル（Polyline = 2）
    cables, _, _ = fetch_and_verify(
        name="submarine-cable-line (polyline)",
        base_url="https://api.msil.go.jp/submarine-cable-line/v2/MapServer",
        layer_selection=2,
        outfile=OUTPUT_DIR / "submarine_cables.geojson",
    )

    # 4) 等深線（Polyline：10=20m, 11=50m, 12=100m, 13=150m, 14=200m）
    contour_layers = {
        10: 20,
        11: 50,
        12: 100,
        13: 150,
        14: 200,
    }

    merged_contours = {"type": "FeatureCollection", "features": []}

    for lid, interval in contour_layers.items():
        name = f"depth-contour {interval}m (polyline)"
        outfile = OUTPUT_DIR / f"depth_contour_{interval}m.geojson"

        fc, expected, actual = fetch_and_verify(
            name=name,
            base_url="https://api.msil.go.jp/depth-contour/v2/MapServer",
            layer_selection=lid,
            outfile=outfile,
        )

        # 統合用に interval_m を properties へ付与してから追加
        for feat in fc.get("features", []):
            props = feat.get("properties") or {}
            props["interval_m"] = interval
            feat["properties"] = props
            merged_contours["features"].append(feat)

    # 等深線の統合GeoJSON
    save_geojson(merged_contours, OUTPUT_DIR / "depth_contours_all.geojson")

    print("done")


if __name__ == "__main__":
    main()
