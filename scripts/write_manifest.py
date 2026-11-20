#!/usr/bin/env python3
"""Write public/data/manifest.json (last). Usage: write_manifest.py <generatedAt ISO>
Keeps the existing hzl01_net_consumption.json entry and forecast block, rewrites the six dashboard files."""
import json, os, sys

gen = sys.argv[1]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = os.path.join(root, "public", "data")
INTEG = "6af2dc1871a5bb8b758f2312"
old = json.load(open(os.path.join(D, "manifest.json")))
keep = [f for f in old["files"] if f["name"] == "hzl01_net_consumption.json"]


def sql(n):
    return open(os.path.join(root, "scripts", "sql", n + ".sql")).read().strip()


def rows(n):
    d = json.load(open(os.path.join(D, n + ".json")))
    return len(d["plants"]) if n == "dims" else len(d["rows"])


SYNCS = {  # name: (syncId, assetId) from the 2026-11-20 Context Flow syncs
    "kpis": ("f4ce953c-d750-4b5a-9457-f2f33218e380", "6afc52acbdd8300f408de665"),
    "inventory_summary": ("5c2499e4-8003-4d48-97e5-467de522fc8d", "6b004ad68f3d5c97414146ed"),
    "materials": ("e9c774de-7e34-414a-b858-8839dcf1771f", "6b004af28f3d5c97414146ee"),
    "reorder": ("041d4603-0744-4019-8c47-135360c1402a", "6b004b568f3d5c97414146f0"),
    "plan_vs_actual": ("23e6d51c-94b5-41df-af2a-40282ab43d80", "6b004b2b8f3d5c97414146ef"),
}
files = [{"name": "dims.json", "rows": rows("dims"), "generatedAt": gen,
          "source": {"integrationId": INTEG, "syncId": None, "assetId": None, "sql": sql("dims")}}]
for n in ("kpis", "inventory_summary", "materials", "reorder", "plan_vs_actual"):
    files.append({"name": n + ".json", "rows": rows(n), "generatedAt": gen,
                  "source": {"integrationId": INTEG, "syncId": SYNCS[n][0], "assetId": SYNCS[n][1], "sql": sql(n)}})
manifest = {
    "schemaVersion": 3,
    "generatedAt": gen,
    "asOf": "2025-12-31",
    "disclaimer": "Simulated POC figure. Not actual Vedanta or Hindustan Zinc performance and not a claim of realised savings.",
    "backcastIncluded": True,
    "files": files + keep,
    "forecast": old.get("forecast"),
}
with open(os.path.join(D, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
print("manifest written", [(x["name"], x["rows"]) for x in manifest["files"]])
