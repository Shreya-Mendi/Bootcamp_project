from __future__ import annotations
import os, requests
import pandas as pd
from dotenv import load_dotenv
from typing import Tuple, Optional

OPENSKY_ARR = "https://opensky-network.org/api/flights/arrival"
OPENSKY_DEP = "https://opensky-network.org/api/flights/departure"

def _auth() -> Optional[Tuple[str, str]]:
    # Optional basic auth; if OPENSKY_USER/OPENSKY_PWD not set, run anonymously
    load_dotenv()
    u = os.getenv("OPENSKY_USER"); p = os.getenv("OPENSKY_PWD")
    return (u, p) if u and p else None

def _epoch_range_for_day(tz_name: str, date_ymd: pd.Timestamp) -> tuple[int,int]:
    # Begin/end of the local day -> UTC epoch seconds
    start_local = pd.Timestamp(date_ymd.date(), tz=tz_name)
    end_local   = start_local + pd.Timedelta(days=1)
    return int(start_local.tz_convert("UTC").timestamp()), int(end_local.tz_convert("UTC").timestamp())

def _fetch_hour_slice(endpoint: str, icao: str, begin: int, end: int, auth) -> list:
    params = {"airport": icao, "begin": begin, "end": end}
    try:
        r = requests.get(endpoint, params=params, timeout=30, auth=auth)
        if r.status_code != 200:
            return []
        return r.json()
    except Exception:
        return []

def _fetch_day(endpoint: str, icao: str, tz_name: str, date_ymd: pd.Timestamp, auth) -> pd.DataFrame:
    begin, end = _epoch_range_for_day(tz_name, date_ymd)
    frames = []
    for h in range(24):
        b = begin + h*3600
        e = min(b+3600, end)
        data = _fetch_hour_slice(endpoint, icao, b, e, auth)
        if data:
            frames.append(pd.DataFrame(data))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

def _count_by_hour(ts_series: pd.Series, tz_name: str) -> pd.Series:
    if ts_series is None or len(ts_series) == 0:
        return pd.Series([0]*24, index=range(24))
    hours = pd.to_datetime(ts_series, unit="s", utc=True).dt.tz_convert(tz_name).dt.hour
    out = hours.value_counts().reindex(range(24), fill_value=0).sort_index()
    return out.astype(int)

def hourly_counts_for_day(icao: str, tz_name: str, date_ymd: pd.Timestamp) -> pd.DataFrame:
    """
    Return DataFrame with columns: hour(0-23), arrivals, departures
    Note: OpenSky arrivals/departures endpoints update nightly; use yesterday/earlier dates for data.
    """
    icao = (icao or "").upper().strip()
    if len(icao) != 4:
        raise ValueError("ICAO must be 4 letters, e.g., KRDU / KJFK / KLAX")
    auth = _auth()
    df_arr = _fetch_day(OPENSKY_ARR, icao, tz_name, date_ymd, auth)
    df_dep = _fetch_day(OPENSKY_DEP, icao, tz_name, date_ymd, auth)
    arr = _count_by_hour(df_arr.get("lastSeen") if not df_arr.empty else pd.Series([], dtype="int64"), tz_name)
    dep = _count_by_hour(df_dep.get("firstSeen") if not df_dep.empty else pd.Series([], dtype="int64"), tz_name)
    return pd.DataFrame({"hour": range(24), "arrivals": arr.values, "departures": dep.values})
