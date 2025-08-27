from __future__ import annotations
import numpy as np
import pandas as pd

_BIG = {"KJFK","KLAX","EGLL","EDDF","KATL","KORD","KDFW","KDEN"}
_MED = {"KRDU","KSFO","KSEA","KBOS","KMIA","KPHX","KMSP","KDTW"}

def _profile(icao: str):
    icao = (icao or "").upper().strip()
    if icao in _BIG: return {"dep": 450, "arr": 450}
    if icao in _MED: return {"dep": 180, "arr": 180}
    return {"dep": 70, "arr": 70}

def _weights():
    h = np.arange(24)
    g = lambda mu, s: np.exp(-0.5*((h-mu)/s)**2)
    w = 1.0*g(9,2.0) + 1.3*g(18,2.5) + 0.4*g(13,3.0) + 0.15
    return w / w.sum()

def _rng(icao: str, date_str: str):
    return np.random.RandomState((hash((icao.upper(), date_str)) & 0xffffffff))

def _sample(total, w, rng):
    lam = np.maximum(total*w, 0.05)
    return rng.poisson(lam).astype(int)

def gen_demo_hourly_multi_days(icao: str, tz_name: str, start_date: pd.Timestamp, days: int=3) -> pd.DataFrame:
    base = _profile(icao); w = _weights()
    frames = []
    for d in range(days):
        date_local = (start_date + pd.Timedelta(days=d)).date()
        rng = _rng(icao, str(date_local))
        dep_total = int(base["dep"] * rng.uniform(0.9, 1.1))
        arr_total = int(base["arr"] * rng.uniform(0.9, 1.1))
        dep = _sample(dep_total, w, rng)
        arr = _sample(arr_total, w, rng)
        frames.append(pd.DataFrame({
            "date":[pd.Timestamp(date_local)]*24,
            "hour":list(range(24)),
            "arrivals":arr,
            "departures":dep
        }))
    out = pd.concat(frames, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"]).dt.date
    return out[["date","hour","arrivals","departures"]]
