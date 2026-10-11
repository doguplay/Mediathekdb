#!/usr/bin/env python3
"""Holt Filme/Serien aus ARD- und ZDF-Mediathek (via MediathekViewWeb)
und ergänzt IMDb-Bewertungen (via OMDb). Schreibt data.js für index.html.

Nutzung:
    export OMDB_API_KEY=dein_key     (kostenlos: https://www.omdbapi.com/apikey.aspx)
    python3 update.py
Nur Standardbibliothek nötig (Python 3.8+).
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime

OMDB_KEY = os.environ.get("OMDB_API_KEY", "")
CHANNELS = ["ARD", "ZDF", "ZDFneo"]
FILM_MIN_SECONDS = 70 * 60          # ab 70 Min. = Film
SERIES_EPISODE_RANGE = (20 * 60, 69 * 60)
SERIES_MIN_EPISODES = 3
PAGE_SIZE = 500
MAX_PAGES = 10                      # pro Kanal und Kategorie
CACHE_FILE = "omdb_cache.json"

MVW_URL = "https://mediathekviewweb.de/api/query"
NOISE = re.compile(
    r"\s*[-–(\[]\s*(Hörfassung|Audiodeskription|mit Gebärdensprache|"
    r"Untertitel|OmU|Originalversion|Film)\b.*$", re.I)


def mvw_query(channel, dmin, dmax=None):
    results, offset = [], 0
    for _ in range(MAX_PAGES):
        body = {
            "queries": [{"fields": ["channel"], "query": channel}],
            "sortBy": "timestamp", "sortOrder": "desc", "future": False,
            "offset": offset, "size": PAGE_SIZE, "duration_min": dmin,
        }
        if dmax:
            body["duration_max"] = dmax
        req = urllib.request.Request(
            MVW_URL, data=json.dumps(body).encode(),
            headers={"Content-Type": "text/plain"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)["result"]
        batch = data.get("results", [])
        results += batch
        offset += len(batch)
        if len(batch) < PAGE_SIZE:
            break
        time.sleep(1)
    return results


def clean(title):
    return NOISE.sub("", title).strip()


def load_cache():
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def omdb(title, kind, cache):
    key = f"{kind}:{title.lower()}"
    if key in cache:
        return cache[key]
    if not OMDB_KEY:
        return None
    url = "https://www.omdbapi.com/?" + urllib.parse.urlencode(
        {"apikey": OMDB_KEY, "t": title, "type": kind})
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.load(r)
    except Exception as e:
        print("OMDb-Fehler:", e, file=sys.stderr)
        return None
    if d.get("Error") and "limit" in d["Error"].lower():
        print("OMDb-Tageslimit erreicht – morgen erneut ausführen (Cache bleibt).")
        raise SystemExit(save_and_exit(cache))
    if d.get("Response") == "True":
        try:
            rating = float(d.get("imdbRating"))
        except (TypeError, ValueError):
            rating = None
        res = {"imdb": rating, "imdbId": d.get("imdbID"),
               "year": d.get("Year"), "poster": d.get("Poster")}
    else:
        res = {"imdb": None}
    cache[key] = res
    time.sleep(0.1)
    return res


def save_and_exit(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    return 0


def main():
    if not OMDB_KEY:
        print("Hinweis: OMDB_API_KEY fehlt – es werden keine IMDb-Scores geladen.")
    cache = load_cache()
    items = {}

    # Filme
    for ch in CHANNELS:
        print("Lade Filme", ch)
        for e in mvw_query(ch, FILM_MIN_SECONDS):
            t = clean(e["title"])
            items.setdefault(("movie", t.lower()), {
                "type": "movie", "title": t, "channel": e["channel"],
                "duration": e["duration"], "url": e.get("url_website"),
                "date": e.get("timestamp")})

    # Serien: Sendungsthema mit mehreren mittellangen Episoden
    topics = defaultdict(list)
    for ch in CHANNELS:
        print("Lade Serien", ch)
        for e in mvw_query(ch, *SERIES_EPISODE_RANGE):
            topics[(e["topic"], e["channel"])].append(e)
    for (topic, ch), eps in topics.items():
        if len(eps) >= SERIES_MIN_EPISODES:
            items.setdefault(("tv", topic.lower()), {
                "type": "tv", "title": topic, "channel": ch,
                "episodes": len(eps), "url": eps[0].get("url_website"),
                "date": max(x.get("timestamp", 0) for x in eps)})

    out = []
    for i, it in enumerate(items.values(), 1):
        kind = "movie" if it["type"] == "movie" else "series"
        info = omdb(it["title"], kind, cache) or {}
        it.update({k: v for k, v in info.items() if v is not None})
        out.append(it)
        if i % 50 == 0:
            print(f"{i}/{len(items)} verarbeitet")
            save_and_exit(cache)
    save_and_exit(cache)

    payload = {"updated": datetime.now().isoformat(timespec="minutes"),
               "items": out}
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.MEDIATHEK_DATA = " + json.dumps(payload, ensure_ascii=False) + ";")
    print(f"Fertig: {len(out)} Titel in data.js")


if __name__ == "__main__":
    main()
