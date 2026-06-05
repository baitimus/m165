# M165: Meilenstein 2 — MongoDB Kursverwaltung
> A developer reference guide for building a course management system with Python and MongoDB.
 
---
 
## Table of Contents
 
1. [Setup & Installation](#setup--installation)
2. [Database Structure](#database-structure)
3. [Connecting to MongoDB](#connecting-to-mongodb)
4. [Function Reference](#function-reference)
   - [kurs_suchen — Search for a Course](#1-kurs_suchen--search-for-a-course)
   - [teilnehmer_erfassen — Register a Participant](#2-teilnehmer_erfassen--register-a-participant)
   - [status_aktualisieren — Update Participant Status](#3-status_aktualisieren--update-participant-status)
   - [teilnehmer_loeschen — Delete a Participant](#4-teilnehmer_loeschen--delete-a-participant)
   - [kursdauer_aendern — Change Course Duration](#5-kursdauer_aendern--change-course-duration)
5. [Key MongoDB Operators Explained](#key-mongodb-operators-explained)
6. [Complete Source Code](#complete-source-code)
---
 
## Setup & Installation
 
### 1. Install the Python MongoDB driver
 
```bash
pip install pymongo
```
 
### 2. Start your local MongoDB instance
 
Make sure MongoDB is running before launching the script. On most systems:
 
```bash
# macOS / Linux
mongod
 
# Windows (if installed as a service)
net start MongoDB
```
 
> If you use **MongoDB Atlas** (cloud), replace the connection URI with your Atlas connection string (see [Connecting to MongoDB](#connecting-to-mongodb)).
 
---
 
## Database Structure
 
This project uses a **document-oriented** design. Instead of separate tables for courses and participants (like in SQL), participants are stored as an **embedded array** directly inside the course document.
 
### Why embed participants?
 
- Faster reads — everything in one document, no JOINs needed
- Natural grouping — a participant always belongs to exactly one course
- Simple to update — MongoDB operators like `$push` and `$pull` manipulate the array directly
### Document layout
 
```
Collection: kurse
└── Document (one per course)
    ├── _id         → ObjectId  (auto-generated unique ID)
    ├── kursname    → String    (name of the course)
    ├── dauer_tage  → Integer   (duration in days)
    └── teilnehmer  → Array of objects
        ├── name    → String    (participant full name)
        └── status  → String    ("angemeldet" | "abgeschlossen" | "abgemeldet")
```
 
### Example document
 
```json
{
  "_id": ObjectId("64a1f2c3d4e5f6a7b8c9d0e1"),
  "kursname": "Python Advanced",
  "dauer_tage": 5,
  "teilnehmer": [
    { "name": "Max Muster",  "status": "angemeldet"    },
    { "name": "Anna Meier",  "status": "abgeschlossen" }
  ]
}
```
 
---
 
## Connecting to MongoDB
 
At the top of your script, establish the connection once and reuse it throughout:
 
```python
from pymongo import MongoClient
 
# Connect to a local MongoDB instance on the default port 27017
client = MongoClient("mongodb://localhost:27017/")
 
# Select (or create) the database named "schulungs_db"
db = client["schulungs_db"]
 
# Select (or create) the collection named "kurse"
kurse_col = db["kurse"]
```
 
**How this works step by step:**
- `MongoClient(...)` opens a connection to the MongoDB server.
- `client["schulungs_db"]` selects a database. MongoDB creates it automatically on first use.
- `db["kurse"]` selects a collection (roughly equivalent to a SQL table). Also auto-created.
- `kurse_col` is the object you'll use in every function to run queries.
---
 
## Function Reference
 
---
 
### 1. `kurs_suchen` — Search for a Course
 
**What it does:** Asks the user for a course name and prints the course details and all its participants.
 
**When to use it:** Whenever you need to look up whether a course exists, or display its current state.
 
#### The MongoDB query used
 
```python
kurse_col.find_one({"kursname": {"$regex": suchbegriff, "$options": "i"}})
```
 
| Part | Meaning |
|---|---|
| `find_one(...)` | Returns the first matching document, or `None` if nothing matches |
| `"$regex"` | Treats the search term as a regular expression (partial matches work) |
| `"$options": "i"` | Makes the match case-insensitive (`"python"` finds `"Python Advanced"`) |
 
#### What the result looks like
 
`find_one()` returns a Python dictionary. You access fields with `.get()`:
 
```python
kurs = kurse_col.find_one({"kursname": {"$regex": "python", "$options": "i"}})
 
# kurs is now a dict like:
# { "kursname": "Python Advanced", "dauer_tage": 5, "teilnehmer": [...] }
 
print(kurs.get("kursname"))    # → "Python Advanced"
print(kurs.get("dauer_tage"))  # → 5
 
for t in kurs.get("teilnehmer", []):
    print(t["name"], t["status"])
```
 
> **Tip:** Always use `.get("key", default)` instead of `["key"]` to avoid a `KeyError` if the field is missing.
 
#### How to reuse this pattern yourself
 
```python
# Exact match
result = kurse_col.find_one({"kursname": "Python Basics"})
 
# Partial / fuzzy match (case-insensitive)
result = kurse_col.find_one({"kursname": {"$regex": "python", "$options": "i"}})
 
# Match by a field inside an embedded array
result = kurse_col.find_one({"teilnehmer.name": "Max Muster"})
```
 
---
 
### 2. `teilnehmer_erfassen` — Register a Participant
 
**What it does:** Adds a new participant object to the `teilnehmer` array of an existing course. New participants always start with `"status": "angemeldet"`.
 
**When to use it:** When a person signs up for a course.
 
#### The MongoDB query used
 
```python
kurse_col.update_one(
    {"kursname": {"$regex": f"^{kursname}$", "$options": "i"}},  # filter
    {"$push": {"teilnehmer": neuer_teilnehmer}}                   # update
)
```
 
| Part | Meaning |
|---|---|
| `update_one(filter, update)` | Finds the first document matching `filter` and applies `update` to it |
| `^` and `$` in regex | Anchors the match to the full string — `^Python$` matches `"Python"` but not `"Python Advanced"` |
| `$push` | Appends a new element to an array field without overwriting existing elements |
 
#### Step-by-step breakdown
 
```python
# 1. Build the new participant as a plain dict
neuer_teilnehmer = {
    "name": "Lisa Braun",
    "status": "angemeldet"   # always the default starting status
}
 
# 2. Push it into the array
result = kurse_col.update_one(
    {"kursname": {"$regex": "^Python Basics$", "$options": "i"}},
    {"$push": {"teilnehmer": neuer_teilnehmer}}
)
 
# 3. Check if the document was actually changed
if result.modified_count > 0:
    print("Success!")   # modified_count = 1 means one document was updated
else:
    print("Nothing changed.")  # 0 means the filter found nothing
```
 
> **Important:** Always check if the course exists **before** pushing. If the filter matches nothing, `update_one` does nothing and returns `modified_count = 0`. The code uses `count_documents()` as a pre-check.
 
---
 
### 3. `status_aktualisieren` — Update Participant Status
 
**What it does:** Changes the `status` field of one specific participant inside the embedded array.
 
**When to use it:** When a participant completes, drops out of, or re-joins a course.
 
#### The MongoDB query used
 
```python
kurse_col.update_one(
    {
        "kursname":        {"$regex": f"^{kursname}$",        "$options": "i"},
        "teilnehmer.name": {"$regex": f"^{teilnehmer_name}$", "$options": "i"}
    },
    {"$set": {"teilnehmer.$.status": neuer_status}}
)
```
 
| Part | Meaning |
|---|---|
| `"teilnehmer.name"` | Dot-notation to filter by a field **inside** the embedded array |
| `$set` | Updates a specific field without touching any other fields |
| `"teilnehmer.$.status"` | The `$` is the **positional operator** — it refers to the array element that matched the filter |
 
#### Why the positional operator `$` matters
 
Without `$`, you would overwrite the **entire** array. With `$`, MongoDB knows exactly which array element you meant — the one whose `name` matched — and only updates that element's `status`.
 
```python
# This updates only "Anna Meier"'s status, leaving "Max Muster" untouched
kurse_col.update_one(
    {"kursname": "Python Advanced", "teilnehmer.name": "Anna Meier"},
    {"$set": {"teilnehmer.$.status": "abgeschlossen"}}
)
```
 
#### Valid status values
 
| Status | Meaning |
|---|---|
| `"angemeldet"` | Registered / active |
| `"abgeschlossen"` | Completed the course |
| `"abgemeldet"` | Unregistered / dropped out |
 
---
 
### 4. `teilnehmer_loeschen` — Delete a Participant
 
**What it does:** Completely removes a participant object from the `teilnehmer` array.
 
**When to use it:** When a participant needs to be fully removed from a course (not just status-changed).
 
#### The MongoDB query used
 
```python
kurse_col.update_one(
    {"kursname": {"$regex": f"^{kursname}$", "$options": "i"}},
    {"$pull": {"teilnehmer": {"name": {"$regex": f"^{teilnehmer_name}$", "$options": "i"}}}}
)
```
 
| Part | Meaning |
|---|---|
| `$pull` | Removes all elements from an array that match the given condition |
| Inner `{"name": ...}` | The condition to match against each element in the `teilnehmer` array |
 
#### Step-by-step breakdown
 
```python
# Think of $pull like: "remove from teilnehmer any element where name == 'Max Muster'"
kurse_col.update_one(
    {"kursname": "Python Basics"},
    {"$pull": {"teilnehmer": {"name": "Max Muster"}}}
)
```
 
#### Difference between `$pull` and `$set`
 
| Operator | Effect |
|---|---|
| `$pull` | Removes a matching array element entirely |
| `$set` | Updates a field value (element stays, only value changes) |
 
---
 
### 5. `kursdauer_aendern` — Change Course Duration
 
**What it does:** Updates the `dauer_tage` field (an integer) on the course document itself, not on any embedded participant.
 
**When to use it:** When a course is shortened or extended.
 
#### The MongoDB query used
 
```python
kurse_col.update_one(
    {"kursname": {"$regex": f"^{kursname}$", "$options": "i"}},
    {"$set": {"dauer_tage": neue_dauer}}
)
```
 
This is the simplest update pattern — `$set` on a top-level field. No array logic needed.
 
#### Input validation pattern
 
Always validate numeric input before sending it to the database:
 
```python
try:
    neue_dauer = int(input("Neue Kursdauer in Tagen: "))
except ValueError:
    print("Bitte eine gültige Zahl eingeben.")
    return   # stop the function early, don't proceed to the DB call
```
 
> **Rule of thumb:** Never trust raw user input. Validate type and range before any database operation.
 
---
 
## Key MongoDB Operators Explained
 
Here is a quick-reference summary of every operator used in this project:
 
| Operator | Used in | What it does |
|---|---|---|
| `$regex` | All queries | Pattern-match a string field |
| `$options: "i"` | All queries | Make regex case-insensitive |
| `$push` | `teilnehmer_erfassen` | Add an element to an array |
| `$pull` | `teilnehmer_loeschen` | Remove matching elements from an array |
| `$set` | `status_aktualisieren`, `kursdauer_aendern` | Update a specific field |
| `$.` (positional) | `status_aktualisieren` | Target the array element that matched the filter |
 
### PyMongo return values you should know
 
After every `update_one()` call, inspect the result object:
 
```python
result = kurse_col.update_one(filter, update)
 
result.matched_count   # How many documents matched the filter (0 or 1)
result.modified_count  # How many documents were actually changed
                       # Can be 0 even if matched, e.g. if the value was already the same
```
 
---
 
## Complete Source Code
 
> Copy this into a file named `kursverwaltung.py` and run it with `python kursverwaltung.py`.
 
```python
import os
from pymongo import MongoClient
 
# --- DATABASE CONNECTION ---
client = MongoClient("mongodb://localhost:27017/")
db = client["schulungs_db"]
kurse_col = db["kurse"]
 
 
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")
 
 
def show_menu():
    print("")
    print(" M165: MEILENSTEIN 2 ")
    print("\n")
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
 
    if kurse_col.count_documents({"kursname": {"$regex": f"^{kursname}$", "$options": "i"}}) == 0:
        print("Fehler: Kurs existiert nicht.")
        return
 
    neuer_teilnehmer = {"name": teilnehmer_name, "status": "angemeldet"}
 
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
 
    result = kurse_col.update_one(
        {
            "kursname":        {"$regex": f"^{kursname}$",        "$options": "i"},
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
 