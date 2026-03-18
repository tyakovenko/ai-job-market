"""
00_fetch.py
-----------
Downloads all raw datasets needed for the pipeline.
Safe to re-run — overwrites existing files in data/raw/.

Sources:
  - BLS Occupational Projections (bls.gov) — updates every ~2 years
  - Frey & Osborne automation scores (GitHub) — static, 2013 paper
  - ILO GenAI Exposure Index 2025 (GitHub, Gmyrek et al.) — ISCO-08 occupation scores
  - BLS ISCO-08 × SOC 2010 Crosswalk (bls.gov) — maps ILO ISCO codes to our SOC codes

Usage:
  python src/00_fetch.py
  python src/00_fetch.py --bls-url https://... (override BLS URL if they update it)

Notes on authentication:
  - BLS blocks the default Python urllib user-agent; all BLS requests use a browser UA.
  - GitHub raw URLs for xlsx files follow redirects automatically via urllib.
"""

import argparse
import os
import sys
import urllib.request

os.makedirs("data/raw", exist_ok=True)

# Browser user-agent string — required for BLS requests, which block Python's default UA.
_BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

SOURCES = {
    "bls": {
        "url": "https://www.bls.gov/emp/ind-occ-matrix/occupation.xlsx",
        "dest": "data/raw/bls_occupational_projections_2024_2034.xlsx",
        "label": "BLS Occupational Projections 2024–2034",
        "headers": {"User-Agent": _BROWSER_UA},
    },
    "frey_osborne": {
        "url": (
            "https://raw.githubusercontent.com/Ludhol/"
            "Occupations-Under-Threat/master/Data_Labour/osborne_frey_data.csv"
        ),
        "dest": "data/raw/frey_osborne_automation_scores.csv",
        "label": "Frey & Osborne Automation Scores (2013)",
        "headers": {},
    },
    # ── Then vs. Now extension ────────────────────────────────────────────────
    "ilo_genai_2025": {
        # Gmyrek et al. (2025), ILO Working Paper 140.
        # "Generative AI and Jobs: A Refined Global Index of Occupational Exposure"
        # 427 ISCO-08 4-digit occupations; task-level rows with occupation-level
        # mean scores pre-computed in mean_score_2025 / mean_score_2023 columns.
        "url": (
            "https://github.com/pgmyrek/2025_GenAI_scores_ISCO08"
            "/raw/main/Final_Scores_ISCO08_Gmyrek_et_al_2025.xlsx"
        ),
        "dest": "data/raw/ilo_genai_exposure_2025.xlsx",
        "label": "ILO GenAI Occupational Exposure Index 2025 (Gmyrek et al.)",
        "headers": {"User-Agent": _BROWSER_UA},
    },
    "isco_soc_crosswalk": {
        # BLS official crosswalk: ISCO-08 4-digit codes → SOC 2010 codes.
        # Used to bridge the ILO dataset (ISCO-08) to our pipeline (SOC codes).
        # Published August 2012, updated June 2015. Static — no versioned updates.
        # Crosswalk coverage against our 606 SOC codes: 600/606 matched (99%).
        # 6 unmatched are residual "all other" and niche categories with no ISCO-08
        # equivalent; they are assigned NaN and excluded from then/now charts only.
        "url": "https://www.bls.gov/soc/ISCO_SOC_Crosswalk.xls",
        "dest": "data/raw/bls_isco_soc_crosswalk.xls",
        "label": "BLS ISCO-08 × SOC 2010 Crosswalk",
        "headers": {"User-Agent": _BROWSER_UA},
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

    # Original datasets
    download("frey_osborne")
    download("bls", url_override=args.bls_url)

    # Then vs. Now extension — ILO 2025 GenAI exposure + crosswalk
    download("ilo_genai_2025")
    download("isco_soc_crosswalk")

    print("All datasets downloaded successfully.")
