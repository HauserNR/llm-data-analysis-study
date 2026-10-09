"""Reproduce the proposal's structural audit; no analysis or network requests."""

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILENAME = "kbo_batting_stats_season_1982-2025.csv"
EXPECTED_SHA256 = "0c6278049dc62132bad73ecf7f4b925c81e999715c6d847ccd508389b563e3ad"
REQUIRED = ["Id", "Season", "Team", "Age", "PA", "AB", "H", "HR", "BB", "SO", "SF"]
COUNTS = ["PA", "AB", "H", "HR", "BB", "SO", "SF"]


def inspect(path):
    raw = path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    if sha256 != EXPECTED_SHA256:
        raise ValueError("CSV differs from the checked Version 5 file. Check the download version.")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames
        rows = list(reader)
    absent = set(REQUIRED) - set(columns or [])
    if absent or not rows:
        raise ValueError(f"Empty CSV or missing required columns: {sorted(absent)}")

    keys = collections.Counter((r["Id"], r["Season"]) for r in rows)
    missing = {c: sum(r[c] in ("", "-") for r in rows) for c in REQUIRED}
    by_player_year = {}
    invalid = []
    for row in rows:
        try:
            record = {c: int(row[c]) for c in ["Season", "Age", *COUNTS]}
        except ValueError:
            invalid.append((row["Id"], row["Season"]))
            continue
        record["bip"] = record["AB"] - record["SO"] - record["HR"] + record["SF"]
        if (
            min(record[c] for c in COUNTS) < 0
            or record["H"] < record["HR"]
            or record["H"] > record["AB"]
        ):
            invalid.append((row["Id"], row["Season"]))
            continue
        by_player_year[(row["Id"], record["Season"])] = record

    candidates = []
    pairs = []
    for (player_id, year), current in by_player_year.items():
        if not (2015 <= year <= 2024 and current["PA"] >= 200 and current["bip"] >= 100):
            continue
        prior = [
            by_player_year[(player_id, season)]
            for season in range(year - 3, year)
            if (player_id, season) in by_player_year
            and by_player_year[(player_id, season)]["bip"] > 0
        ]
        if len(prior) < 2 or sum(r["bip"] for r in prior) < 300:
            continue
        candidates.append((player_id, year))
        future = by_player_year.get((player_id, year + 1))
        if future and future["PA"] >= 200 and future["AB"] > 0:
            pairs.append((player_id, year))

    seasons = [int(r["Season"]) for r in rows]
    return {
        "checked_date": "2026-10-09",
        "dataset_ref": "netsong/kbo-player-stats-19822025",
        "dataset_version": 5,
        "filename": SOURCE_FILENAME,
        "sha256": sha256,
        "bytes": len(raw),
        "rows": len(rows),
        "columns": columns,
        "unique_players": len({r["Id"] for r in rows}),
        "min_season": min(seasons),
        "max_season": max(seasons),
        "duplicate_player_season_keys": sum(v > 1 for v in keys.values()),
        "required_missing": missing,
        "invalid_count_stats_rows": len(invalid),
        "recent_2012_2025_rows": sum(2012 <= y <= 2025 for y in seasons),
        "feature_2015_2024_rows": sum(2015 <= y <= 2024 for y in seasons),
        "candidate_rows": len(candidates),
        "eligible_next_year_pairs": len(pairs),
        "eligible_unique_players": len({p for p, _ in pairs}),
        "candidates_by_feature_season": dict(sorted(collections.Counter(y for _, y in candidates).items())),
        "pairs_by_feature_season": dict(sorted(collections.Counter(y for _, y in pairs).items())),
        "split_counts": {
            "train_2015_2021": sum(2015 <= y <= 2021 for _, y in pairs),
            "validation_2022": sum(y == 2022 for _, y in pairs),
            "test_2023_2024": sum(y >= 2023 for _, y in pairs),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=PROJECT_ROOT / "data/raw" / SOURCE_FILENAME)
    args = parser.parse_args()
    print(json.dumps(inspect(args.csv_path), ensure_ascii=False, indent=2))
