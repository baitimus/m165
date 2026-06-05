# M165: Meilenstein 2 - NoSQL-Datenbanken einsetzen

Dieses Dokument enthält die vollständige Dokumentation der MongoDB-Abfragen sowie den kompletten, lauffähigen Python-Code zur Umsetzung von Meilenstein 2.

---

## 1. Voraussetzungen & Datenbankschema

**Voraussetzung:**
Das Python-Modul `pymongo` muss installiert sein, um die Verbindung zwischen dem Python-Skript und der MongoDB herzustellen:
```bash
pip install pymongo
```

**MongoDB Schema (Dokumentenorientiert):**
Für diese Implementierung verwenden wir ein Design, bei dem die Teilnehmer als Array direkt in das jeweilige Kurs-Dokument eingebettet werden.

*Beispiel eines Kurs-Dokuments:*
```json
{
  "_id": "ObjectId(...)",
  "kursname": "Python Advanced",
  "dauer_tage": 5,
  "teilnehmer": [
    {"name": "Max Muster", "status": "angemeldet"},
    {"name": "Anna Meier", "status": "abgeschlossen"}
  ]
}
```

---

## 2. Funktionsdokumentation & MongoDB Abfragen

Hier sind die Erklärungen und die zugrundeliegenden MongoDB-Konzepte für jede Menü-Option.

### Option 1: Kurs suchen (`kurs_suchen`)
* **Beschreibung:** Sucht nach einem Kursnamen und gibt die Kursdetails sowie die Liste der Teilnehmer aus.
* **MongoDB Konzept:** Verwendet `find_one()` mit einem regulären Ausdruck (`$regex`), um die Suche unabhängig von Gross-/Kleinschreibung (Case-Insensitive) durchzuführen.
* **Beispiel-Query:** `db.kurse.find_one({"kursname": {"$regex": suchbegriff, "$options": "i"}})`

### Option 2: Teilnehmer/in erfassen (`teilnehmer_erfassen`)
* **Beschreibung:** Fügt einen neuen Teilnehmer zu einem bestehenden Kurs hinzu.
* **MongoDB Konzept:** Nutzt den `$push`-Operator, um ein neues Dictionary an das eingebettete Array `teilnehmer` anzuhängen.
* **Beispiel-Query:** `db.kurse.update_one({"kursname": kurs}, {"$push": {"teilnehmer": neuer_teilnehmer}})`

### Option 3: Teilnehmerstatus aktualisieren (`status_aktualisieren`)
* **Beschreibung:** Ändert den Status (z.B. von "angemeldet" auf "abgeschlossen") eines spezifischen Teilnehmers in einem bestimmten Kurs.
* **MongoDB Konzept:** Verwendet den Positions-Operator `$`, um das spezifische Array-Element zu identifizieren, das den Suchkriterien entspricht, und aktualisiert es mit `$set`.
* **Beispiel-Query:** `db.kurse.update_one({"kursname": kurs, "teilnehmer.name": name}, {"$set": {"teilnehmer.$.status": neuer_status}})`

### Option 4: Teilnehmer/in löschen (Bonus) (`teilnehmer_loeschen`)
* **Beschreibung:** Entfernt einen Teilnehmer komplett aus einem Kurs.
* **MongoDB Konzept:** Verwendet den `$pull`-Operator, um ein Element, das einer bestimmten Bedingung entspricht, aus einem Array zu entfernen.
* **Beispiel-Query:** `db.kurse.update_one({"kursname": kurs}, {"$pull": {"teilnehmer": {"name": name}}})`

### Option 5: Kursdauer ändern (Bonus) (`kursdauer_aendern`)
* **Beschreibung:** Aktualisiert die Kursdauer (Integer) eines bestehenden Kurses.
* **MongoDB Konzept:** Verwendet den `$set`-Operator auf ein Feld der obersten Ebene (Root-Level).
* **Beispiel-Query:** `db.kurse.update_one({"kursname": kurs}, {"$set": {"dauer_tage": neue_dauer}})`

---

## 3. Kompletter Python-Code

Kopiere den folgenden Code in deine Python-Datei (z.B. `main.py`). Stelle sicher, dass deine lokale MongoDB läuft.

```python
import os
from pymongo import MongoClient

# --- DATABASE CONNECTION ---
# Verbindung zur lokalen MongoDB-Instanz.
client = MongoClient("mongodb://localhost:27017/")
db = client["schulungs_db"]  # Datenbankname
kurse_col = db["kurse"]      # Collectionname

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def show_menu():
    print("***************************")
    print("*** M165: MEILENSTEIN 2 ***")
    print("***************************\n")
    print("1: Kurs suchen")
    print("2: Teilnehmer/in erfassen")
    print("3: Teilnehmerstatus aktualisieren")
    print("4: Teilnehmer/in löschen (Bonus)")
    print("5: Kursdauer ändern (Bonus)")
    print()
    print("Deine Auswahl: ", end="")

def return_to_menu():
    input("\nEine Taste drücken, um zum Menü zurückzukehren...")
    clear_console()

# --- FUNCTION IMPLEMENTATIONS ---

def kurs_suchen():
    suchbegriff = input("Kursname eingeben: ")
    # Case-insensitive Suche nach dem Kursnamen
    kurs = kurse_col.find_one({"kursname": {"$regex": suchbegriff, "$options": "i"}})
    
    if kurs:
        print(f"\n--- Kurs gefunden: {kurs.get('kursname')} ---")
        print(f"Dauer: {kurs.get('dauer_tage')} Tage")
        print("Teilnehmer:")
        teilnehmer_liste = kurs.get("teilnehmer", [])
        if not teilnehmer_liste:
            print("  - Keine Teilnehmer erfasst.")
        else:
            for t in teilnehmer_liste:
                print(f"  - {t['name']} (Status: {t['status']})")
    else:
        print("Kurs nicht gefunden.")

def teilnehmer_erfassen():
    kursname = input("Zu welchem Kurs soll die Person hinzugefügt werden?: ")
    teilnehmer_name = input("Name der Teilnehmer/in: ")
    
    # Prüfen, ob der Kurs existiert
    if kurse_col.count_documents({"kursname": {"$regex": f"^{kursname}$", "$options": "i"}}) == 0:
        print("Fehler: Kurs existiert nicht.")
        return

    neuer_teilnehmer = {"name": teilnehmer_name, "status": "angemeldet"}
    
    # Teilnehmer mit $push zum Array hinzufügen
    result = kurse_col.update_one(
        {"kursname": {"$regex": f"^{kursname}$", "$options": "i"}},
        {"$push": {"teilnehmer": neuer_teilnehmer}}
    )
    
    if result.modified_count > 0:
        print("Teilnehmer/in erfolgreich erfasst!")
    else:
        print("Fehler beim Erfassen.")

def status_aktualisieren():
    kursname = input("Kursname: ")
    teilnehmer_name = input("Name der Teilnehmer/in: ")
    neuer_status = input("Neuer Status (z.B. abgeschlossen, abgemeldet): ")
    
    # Status mit $set und dem Positions-Operator ($) aktualisieren
    result = kurse_col.update_one(
        {
            "kursname": {"$regex": f"^{kursname}$", "$options": "i"}, 
            "teilnehmer.name": {"$regex": f"^{teilnehmer_name}$", "$options": "i"}
        },
        {"$set": {"teilnehmer.$.status": neuer_status}}
    )
    
    if result.modified_count > 0:
        print("Status erfolgreich aktualisiert!")
    else:
        print("Fehler: Kurs oder Teilnehmer nicht gefunden, oder Status war bereits gleich.")

def teilnehmer_loeschen():
    kursname = input("Kursname: ")
    teilnehmer_name = input("Name der zu löschenden Teilnehmer/in: ")
    
    # Teilnehmer mit $pull aus dem Array entfernen
    result = kurse_col.update_one(
        {"kursname": {"$regex": f"^{kursname}$", "$options": "i"}},
        {"$pull": {"teilnehmer": {"name": {"$regex": f"^{teilnehmer_name}$", "$options": "i"}}}}
    )
    
    if result.modified_count > 0:
        print("Teilnehmer/in erfolgreich gelöscht!")
    else:
        print("Fehler: Kurs oder Teilnehmer nicht gefunden.")

def kursdauer_aendern():
    kursname = input("Kursname: ")
    try:
        neue_dauer = int(input("Neue Kursdauer in Tagen: "))
    except ValueError:
        print("Bitte eine gültige Zahl eingeben.")
        return
        
    # Kursdauer mit $set anpassen
    result = kurse_col.update_one(
        {"kursname": {"$regex": f"^{kursname}$", "$options": "i"}},
        {"$set": {"dauer_tage": neue_dauer}}
    )
    
    if result.modified_count > 0:
        print("Kursdauer erfolgreich geändert!")
    else:
        print("Fehler: Kurs nicht gefunden oder Dauer war bereits gleich.")

# --- MAIN LOOP ---

def main():
    # Setup: Testdaten generieren, falls die Datenbank komplett leer ist
    if kurse_col.count_documents({}) == 0:
        kurse_col.insert_one({
            "kursname": "Python Basics",
            "dauer_tage": 3,
            "teilnehmer": [{"name": "Max Muster", "status": "angemeldet"}]
        })
        print("Test-Datenbank erstellt. Starte Programm...\n")

    while True:
        show_menu()
        user_choice = input()
        clear_console()

        if user_choice == "1":
            kurs_suchen()
        elif user_choice == "2":
            teilnehmer_erfassen()
        elif user_choice == "3":
            status_aktualisieren()
        elif user_choice == "4":
            teilnehmer_loeschen()
        elif user_choice == "5":
            kursdauer_aendern()
        else:
            print("Ungültige Eingabe.")

        return_to_menu()

if __name__ == "__main__":
    main()
```