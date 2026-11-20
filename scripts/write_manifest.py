#!/usr/bin/env python3
"""Write public/data/manifest.json (last). Usage: write_manifest.py <generatedAt> <syncId> <assetId> <integrationId>"""
import json, os, sys

gen, sync_id, asset_id, integ = sys.argv[1:5]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sql = open(os.path.join(root, "scripts", "hzl01_consumption.sql")).read().strip()
data = json.load(open(os.path.join(root, "public", "data", "hzl01_net_consumption.json")))
manifest = {
    "schemaVersion": 3,
    "generatedAt": gen,
    "asOf": "2025-12-31",
    "disclaimer": "Simulated POC figure. Not actual Vedanta or Hindustan Zinc performance and not a claim of realised savings.",
    "backcastIncluded": True,
    "files": [{
        "name": "hzl01_net_consumption.json",
        "rows": len(data["rows"]),
        "generatedAt": gen,
        "source": {"integrationId": integ, "syncId": sync_id, "assetId": asset_id, "sql": sql},
    }],
    "forecast": None,
}
with open(os.path.join(root, "public", "data", "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
print("manifest written", manifest["files"][0]["rows"], "rows")
