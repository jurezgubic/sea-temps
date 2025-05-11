#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read sea_temps.csv and make time-series plots.

usage:
    python sea_temp_plot.py --all
    python sea_temp_plot.py --station "Dubrovnik"
    python sea_temp_plot.py            # → interactive prompt
"""

from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import re, unicodedata

CSV = Path(__file__).with_name("sea_temps.csv")   # same folder as script
OUT_DIR = Path(__file__).parent                   # save PNGs here

# ─── name normaliser (same rules as the scraper) ──────────────────────────────

_DIACRITIC_FIX = str.maketrans({"đ": "d", "Đ": "D"})

def normalise_station(name: str) -> str:
    name = name.replace("/", " ")
    name = re.sub(r"\s*A$", "", name)
    name = re.sub(r"\bSv\.\s*", "Sveti ", name, flags=re.I)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.translate(_DIACRITIC_FIX)
    name = re.sub(r"\s+", " ", name).strip()
    return name

# ─── data loader ──────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV, parse_dates=["datetime"], dayfirst=True)
    df["station"] = df["station"].apply(normalise_station)
    df["temp"]    = pd.to_numeric(df["temp"], errors="coerce")

    # Remove duplicate entries for the same station and datetime, keeping the last one
    df.drop_duplicates(subset=['datetime', 'station'], keep='last', inplace=True)

    wide = df.pivot(index="datetime", columns="station", values="temp")
    wide.sort_index(inplace=True)
    return wide

# ─── plotting helpers ─────────────────────────────────────────────────────────

def plot_station(series: pd.Series) -> None:
    """Draw a single line chart and save it as PNG."""
    station = series.name
    fname   = OUT_DIR / f"{station.replace(' ', '_').lower()}_timeseries.png"

    plt.figure()
    series.plot(marker="o", linestyle="-")
    plt.title(f"Sea-water temperature — {station}")
    plt.ylabel("°C")
    plt.xlabel("Date & time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()
    print(f"saved: {fname.name}")

# ─── main driver ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--all",     action="store_true",
                     help="plot every station (default if you type 'all' at the prompt)")
    grp.add_argument("--station", type=str,
                     help="name of one station to plot (e.g. 'Dubrovnik')")
    args = parser.parse_args()

    wide = load_data()
    stations = wide.columns.tolist()

    # decide what we’re plotting
    if args.all:
        chosen = stations

    elif args.station:
        name   = normalise_station(args.station)
        if name not in stations:
            raise SystemExit(f"✗ station '{args.station}' not found.\n"
                             f"  available: {', '.join(stations)}")
        chosen = [name]

    else:   # interactive prompt
        print("Available stations:")
        for s in stations:
            print(" •", s)
        choice = input("\nType station name (or 'all'): ").strip()
        if choice.lower() == "all":
            chosen = stations
        else:
            name = normalise_station(choice)
            if name not in stations:
                raise SystemExit(f"✗ station '{choice}' not found.")
            chosen = [name]

    # generate the plots
    for stn in chosen:
        plot_station(wide[stn])

if __name__ == "__main__":
    main()

