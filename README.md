# Mediathek-Scores

Listet Filme und Serien von ARD und ZDF mit IMDb-Score und Score-Filter. Läuft online und damit auch auf dem Handy.

## Einrichten (einmalig, geht komplett im Browser)
1. **OMDb-Key holen:** https://www.omdbapi.com/apikey.aspx (kostenlos, Bestätigung per E-Mail).
2. **GitHub-Repository anlegen:** auf github.com ein neues, **öffentliches** Repository erstellen (z. B. `mediathek-scores`).
3. **Dateien hochladen:** `index.html`, `update.py`, `data.js`, `README.md` per „Add file → Upload files“ hochladen. Den Workflow zusätzlich über „Add file → Create new file“ mit dem Namen `.github/workflows/update.yml` anlegen und den Inhalt der mitgelieferten Datei einfügen.
4. **Key hinterlegen:** Settings → Secrets and variables → Actions → „New repository secret“. Name: `OMDB_API_KEY`, Wert: dein Key.
5. **Schreibrechte für die Automatik:** Settings → Actions → General → Workflow permissions → „Read and write permissions“ → Save.
6. **Seite veröffentlichen:** Settings → Pages → Source: „Deploy from a branch“ → Branch `main`, Ordner `/ (root)` → Save.
7. **Ersten Lauf starten:** Reiter Actions → „Daten aktualisieren“ → „Run workflow“. Nach einigen Minuten sind die Daten da.

Die Seite erreichst du danach unter `https://DEIN-NAME.github.io/mediathek-scores/`.

## Auf dem Handy
- **iPhone (Safari):** Teilen → „Zum Home-Bildschirm“.
- **Android (Chrome):** Menü → „Zum Startbildschirm hinzufügen“.

## Automatische Updates
Der Workflow läuft täglich von selbst und speichert neue Daten im Repository. Du musst nichts weiter tun.

## Lokal ausführen (optional)
- Mac/Linux: `export OMDB_API_KEY=DEIN_KEY && python3 update.py`
- Windows (PowerShell): `$env:OMDB_API_KEY="DEIN_KEY"; python update.py`
- Danach `index.html` im Browser öffnen.

## Hinweise
- Katalog kommt von MediathekViewWeb (deckt ARD, ZDF, ZDFneo ab). Filme = Sendungen ab 70 Min.; Serien = Sendungen mit mind. 3 Episoden à 20–69 Min.
- Das OMDb-Gratislimit liegt bei 1000 Abfragen/Tag. Treffer werden in `omdb_cache.json` gespeichert, der tägliche Lauf macht am nächsten Tag automatisch weiter.
- Zuordnung erfolgt über den Titel, Fehltreffer sind möglich. Letterboxd ist nicht eingebaut (keine öffentliche API).
- Ein öffentliches Repository ist nötig, damit GitHub Pages kostenlos funktioniert. Der OMDb-Key bleibt als Secret verborgen.
