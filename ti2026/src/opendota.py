"""Minimal, polite OpenDota API client with disk cache and rate limiting.

Free tier: keyless, ~60 calls/min and a daily cap; set OPENDOTA_API_KEY to raise
limits. Every GET is cached to ti2026/data/cache/ so re-runs are free and the
notebooks work offline once data is pulled. This sandbox may block opendota.com
entirely — the client raises a clear error and the notebooks fall back to cache.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import requests

BASE = "https://api.opendota.com/api"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_DIR = DATA_DIR / "cache"


class OpenDotaError(RuntimeError):
    pass


class OpenDota:
    def __init__(self, min_interval: float = 1.1, api_key: str | None = None):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "polly-ti2026-research (github.com/hhhhhwlcrd/Polly)"
        self.api_key = api_key or os.environ.get("OPENDOTA_API_KEY")
        # keyless: 60/min; keyed: 300/min (limits verified from odota/core source;
        # exact daily quota is server-side — read GET /metadata at startup)
        self.min_interval = 0.25 if self.api_key else min_interval
        self._last_call = 0.0
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, path: str, params: dict) -> Path:
        key = hashlib.sha1(f"{path}?{sorted(params.items())}".encode()).hexdigest()
        return CACHE_DIR / f"{key}.json"

    def get(self, path: str, use_cache: bool = True, **params):
        cp = self._cache_path(path, params)
        if use_cache and cp.exists():
            return json.loads(cp.read_text())
        if self.api_key:
            params = {**params, "api_key": self.api_key}
        wait = self.min_interval - (time.time() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(5):
            try:
                r = self.session.get(f"{BASE}{path}", params=params, timeout=30)
            except requests.ConnectionError as e:
                raise OpenDotaError(
                    f"Cannot reach OpenDota ({e}). If you are in a sandboxed "
                    f"environment, run this notebook where api.opendota.com is "
                    f"reachable; cached data (if any) keeps the rest working."
                ) from e
            self._last_call = time.time()
            if r.status_code == 200:
                data = r.json()
                cp.write_text(json.dumps(data))
                return data
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2**attempt)
                continue
            raise OpenDotaError(f"GET {path} -> HTTP {r.status_code}: {r.text[:200]}")
        raise OpenDotaError(f"GET {path}: retries exhausted (rate limit?)")

    # ---- convenience wrappers -------------------------------------------
    def metadata(self):
        """Live quota info: {freeCallLimit, freeRateLimit, premRateLimit, ...}."""
        return self.get("/metadata", use_cache=False)

    def leagues(self):
        return self.get("/leagues")

    def league_matches(self, league_id: int):
        return self.get(f"/leagues/{league_id}/matches")

    def match(self, match_id: int):
        return self.get(f"/matches/{match_id}")

    def teams(self):
        return self.get("/teams")

    def team_matches(self, team_id: int):
        return self.get(f"/teams/{team_id}/matches")

    def team_players(self, team_id: int):
        return self.get(f"/teams/{team_id}/players")

    def player(self, account_id: int):
        return self.get(f"/players/{account_id}")

    def player_heroes(self, account_id: int, **params):
        return self.get(f"/players/{account_id}/heroes", **params)

    def heroes(self):
        return self.get("/heroes")

    def pro_matches(self, less_than_match_id: int | None = None):
        params = {}
        if less_than_match_id:
            params["less_than_match_id"] = less_than_match_id
        return self.get("/proMatches", use_cache=False, **params)
