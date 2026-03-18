"""
00_fetch.py
-----------
Downloads all raw datasets needed for the pipeline.
Safe to re-run — overwrites existing files in data/raw/.

Sources:
  - BLS Occupational Projections (bls.gov) — updates every ~2 years
  - Frey & Osborne automation scores (GitHub) — static, 2013 paper

Usage:
  python src/00_fetch.py
  python src/00_fetch.py --bls-url https://... (override BLS URL if they update it)
"""

import argparse
import os
import sys
import urllib.request

os.makedirs("data/raw", exist_ok=True)

SOURCES = {
    "bls": {
        "url": "https://www.bls.gov/emp/ind-occ-matrix/occupation.xlsx",
        "dest": "data/raw/bls_occupational_projections_2024_2034.xlsx",
        "label": "BLS Occupational Projections",
        # BLS blocks default Python user-agent
        "headers": {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
    },
    "frey_osborne": {
        "url": (
            "https://raw.githubusercontent.com/Ludhol/"
            "Occupations-Under-Threat/master/Data_Labour/osborne_frey_data.csv"
        ),
        "dest": "data/raw/frey_osborne_automation_scores.csv",
        "label": "Frey & Osborne Automation Scores",
        "headers": {},
    },
}


def download(key: str, url_override: str | None = None) -> None:
    source = SOURCES[key]
    url = url_override or source["url"]
    dest = source["dest"]
    label = source["label"]

    print(f"Downloading {label}...")
    print(f"  URL:  {url}")
    print(f"  Dest: {dest}")

    req = urllib.request.Request(url, headers=source["headers"])
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, \
             open(dest, "wb") as f:
            f.write(resp.read())
        size_kb = os.path.getsize(dest) / 1024
        print(f"  ✓ {size_kb:.0f} KB saved.\n")
    except Exception as e:
        print(f"  ✗ Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch raw datasets.")
    parser.add_argument(
        "--bls-url",
        default=None,
        help="Override BLS download URL (use when BLS releases a new projection cycle)",
    )
    args = parser.parse_args()

    download("frey_osborne")
    download("bls", url_override=args.bls_url)

    print("All datasets downloaded successfully.")
