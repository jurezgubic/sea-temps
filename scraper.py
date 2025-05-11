#!/usr/bin/env python3
# -*- coding: utf-8 -*-i

"""
Grab Croatia sea-water temperatures from DHMZ and append to sea_temps.csv
Run daily at 18:00.
"""

from datetime import datetime, date
from pathlib import Path

import pandas as pd
import requests
import re, unicodedata

URL = "https://meteo.hr/podaci.php?section=podaci_vrijeme&param=more_n"
OUTFILE = Path(__file__).with_name("sea_temps.csv")   # same folder as script

def fetch_table() -> pd.DataFrame:
    """Download the table and return a tidy long DataFrame."""
    # pull HTML (explicit User-Agent just in case)
    html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}).text

    # the page has a single table → read_html returns [DataFrame]
    wide = pd.read_html(html, flavor="lxml")[0]

    # give the first col a nicer name
    wide.rename(columns={wide.columns[0]: "station"}, inplace=True)
    
    # normalise station names
    wide["station"] = wide["station"].apply(normalise_station)

    long = wide.melt(id_vars="station", var_name="hour", value_name="temp")

    #  convert *before* dropping, so '-' → NaN, numbers → floats
    long["temp"] = pd.to_numeric(long["temp"], errors="coerce")
    long.dropna(subset=["temp"], inplace=True)

    long["datetime"] = pd.to_datetime(
        long["hour"].astype(str).str.zfill(2).radd(date.today().isoformat() + " ")
    )

    # reorder for readability
    return long[["datetime", "station", "temp"]]

def append_csv(df: pd.DataFrame, path: Path = OUTFILE) -> None:
    """Append df to CSV, writing header only the first time."""
    header_needed = not path.exists()
    df.to_csv(path, mode="a", index=False, header=header_needed)


def normalise_station(name: str) -> str:
    """Normalise station names to ASCII."""
    name = name.replace("/", "-")
    name = re.sub(r"\s*A$", "", name)
    name = re.sub(r"\bSv\.\s*", "Sveti", name, flags=re.I)
    name = (
        unicodedata.normalize("NFKD", name)      # split base + accents
                  .encode("ascii", "ignore")     # drop accents
                  .decode("ascii")
    )
    return name.strip()



def main() -> None:
    df = fetch_table()
    append_csv(df)
    print(f"Appended {len(df)} rows → {OUTFILE}")

if __name__ == "__main__":
    main()

