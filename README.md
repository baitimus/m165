Projekt: MongoDB Verbindungstest

Anleitung:

- Passe bei Bedarf die Verbindungszeichenfolge in `connect_db.py` an (`connection_string`).
- Erstelle ein virtuelles Environment (optional): `python -m venv .venv` und aktiviere es.
- Installiere Abhängigkeiten:

```bash
pip install -r requirements.txt
```

- Skript ausführen:

```bash
python connect_db.py
```

Falls eine MongoDB unter `mongodb://localhost:27017/` läuft, wird die Server-Info (z.B. Version) ausgegeben.

Zusätzlich enthält `connect_db.py` Hilfsfunktionen, die das bestehende `client`-Objekt wiederverwenden.