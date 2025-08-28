from __future__ import annotations
import json, datetime as dt
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

_cache = {}  # (src, code, date) -> rate_to_PLN (float)

def _iso(d):
    if isinstance(d, dt.date): return d.isoformat()
    return str(d)

def _nbp_get(code:str, date:str)->float|None:
    url = f"http://api.nbp.pl/api/exchangerates/rates/A/{code}/{date}?format=json"
    try:
        with urlopen(url, timeout=10) as r:
            j = json.load(r)
            return float(j["rates"][0]["mid"])
    except HTTPError as e:
        if e.code==404:
            return None
        return None
    except URLError:
        return None

def _frankfurter_get(code:str, date:str)->float|None:
    url = f"https://api.frankfurter.app/{date}?from={code}&to=PLN"
    try:
        with urlopen(url, timeout=10) as r:
            j = json.load(r)
            return float(j["rates"]["PLN"])
    except Exception:
        return None

def get_rate(code:str, date:dt.date|str, source:str="nbp")->float|None:
    code = (code or "").upper()
    if code in ("", "PLN"): return 1.0
    date_s = _iso(date)
    key = (source, code, date_s)
    if key in _cache: return _cache[key]

    # NBP z cofaniem do poprzedniego dnia roboczego (max 7 dni)
    if source=="nbp":
        try:
            d = dt.date.fromisoformat(date_s)
        except Exception:
            d = dt.date.today()
        for _ in range(7):
            r = _nbp_get(code, d.isoformat())
            if r:
                _cache[key]=r
                return r
            d -= dt.timedelta(days=1)

    # Frankfurter jako fallback
    r = _frankfurter_get(code, date_s)
    if r:
        _cache[key]=r
        return r

    return None
