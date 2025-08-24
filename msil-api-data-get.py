import os, time, json, requests

API_KEY = os.getenv("MSIL_API_KEY") or "0e83ad5d93214e04abf37c970c32b641"
session = requests.Session()
session.headers.update({"Ocp-Apim-Subscription-Key": API_KEY})

def fetch_geojson(base):
    envelope = {"xmin":122,"ymin":20,"xmax":154,"ymax":46,"spatialReference":{"wkid":4326}}
    features, offset, pagesize = [], 0, 1000
    while True:
        params = {
            "f":"geojson",
            "where":"1=1",
            "geometry": json.dumps(envelope, ensure_ascii=False),
            "geometryType":"esriGeometryEnvelope",
            "inSR":"4326",
            "outSR":"4326",          # 念のためWGS84指定
            "spatialRel":"esriSpatialRelIntersects",
            "outFields":"*",
            "returnGeometry":"true",
            "resultOffset":offset,
            "resultRecordCount":pagesize,
            "subscription-key":API_KEY
        }
        r = session.get(f"{base}/1/query", params=params, timeout=60)  # 1 = Point
        r.raise_for_status()
        chunk = r.json()
        feats = chunk.get("features", [])
        features.extend(feats)
        print(base, "fetched", len(feats), "total", len(features), "offset", offset)
        if len(feats) < pagesize:
            break
        offset += pagesize
        time.sleep(0.2)
    return {"type":"FeatureCollection","features":features}

# 島名
islands = fetch_geojson("https://api.msil.go.jp/island/v2/MapServer")
with open("./geojson/islands.geojson","w",encoding="utf-8") as f:
    json.dump(islands, f, ensure_ascii=False)

# 海底地形名
undersea = fetch_geojson("https://api.msil.go.jp/undersea-features/v2/MapServer")
with open("./geojson/undersea_features.geojson","w",encoding="utf-8") as f:
    json.dump(undersea, f, ensure_ascii=False)

print("done")
