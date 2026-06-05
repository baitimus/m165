from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")

dblist = client.list_database_names()

db_name = "db_restaurants"

if db_name in dblist:
    print(f"Datenbank '{db_name}' gefunden und verbunden.\n")
else:
    print(f"Hinweis: Datenbank '{db_name}' existiert noch nicht. Sie wird beim ersten Speichern erstellt.\n")

db = client[db_name]

def aufgabe1():
    print("bezirke ausgeben ohne dopplung")
    segments = db.restaurants.distinct("borough")
    for segment in segments:
        print(segment)

def aufgabe2():
    print("best top 3 ratet restaurant")
    pipeline = [
    # Step 1: Break apart the grades array
    {"$unwind": "$grades"},
    
    # Step 2: Group by ID/Name and calculate the average score
    {"$group": {
        "_id": "$_id", 
        "name": {"$first": "$name"}, # Keep the name for the final output
        "avg_score": {"$avg": "$grades.score"}
    }},
    
    # Step 3: Sort by the new 'avg_score' field, descending (-1)
    {"$sort": {"avg_score": -1}},
    
    # Step 4: Keep only the top 3
    {"$limit": 3}
    ]

    top_restaurants = list(db.restaurants.aggregate(pipeline))
    for restaurant in top_restaurants:
        print(f"Name: {restaurant['name']}, Average Score: {restaurant['avg_score']:.2f}")
    

def aufgabe3():
    print("restaurant closest to le perigord")
    le_perigord = db.restaurants.find_one({"name": "Le Perigord"})
    
    if not le_perigord:
        print("Le Perigord not found!")
        return
    
    coords = le_perigord["address"]["coord"]
    print(f"Le Perigord coordinates: {coords}")
    db.restaurants.create_index([("address.coord", "2d")])
    results = db.restaurants.find(
        {
            "_id": {"$ne": le_perigord["_id"]},
            "address.coord": {
                "$near": coords
            }
        }
    ).limit(1)
    closest = next(results, None)

    if closest:
        print(f"Closest restaurant to Le Perigord:")
        print(f"  Name:    {closest['name']}")
        print(f"  Borough: {closest['borough']}")
        print(f"  Address: {closest['address']['building']} {closest['address']['street']}")
        print(f"  Coord:   {closest['address']['coord']}")
    else:
        print("No nearby restaurant found.")

def aufgabe4():
    print("restaurant search")

    name_query = input("Suche nach Name (leer lassen zum Ignorieren): ").strip()
    cuisine_query = input("Suche nach Küche (leer lassen zum Ignorieren): ").strip()

    query = {}
    if name_query:
        query["name"] = {"$regex": name_query, "$options": "i"}
    if cuisine_query:
        query["cuisine"] = {"$regex": cuisine_query, "$options": "i"}

    if not query:
        print("Keine Suchkriterien eingegeben. Abbruch.")
        return
    
    results = list(db.restaurants.find(query).limit(20))
    if not results:
        print("Keine Restaurants gefunden.")
        return
    
    print(f"\nEs wurden {len(results)} Restaurants gefunden (max. 20 angezeigt):")
    for i, res in enumerate(results):
        print(f"[{i}] {res.get('name')} | Küche: {res.get('cuisine')} | Stadtteil: {res.get('borough')}")
    # Aufgabe 5: Bewerten
    auswahl = input("\nMöchtest du einem dieser Restaurants eine Bewertung geben? Gib die Zahl in der Klammer ein (oder 'x' zum Abbrechen): ").strip()
    
    if auswahl.isdigit() and int(auswahl) < len(results):
        selected_doc = results[int(auswahl)]
        
        try:
            neuer_score = int(input(f"Welchen Score möchtest du dem Restaurant '{selected_doc['name']}' geben? (Zahl): "))
        except ValueError:
            print("Ungültige Eingabe für den Score. Abbruch.")
            return

        # Neues Bewertungs-Objekt erstellen
        neue_bewertung = {
            "date": datetime.now(),
            "grade": "Not specified", # Da nur Score verlangt wurde
            "score": neuer_score
        }

        # Document in der Datenbank updaten (Wir pushen das Objekt in das Array 'grades')
        db.restaurants.update_one(
            {"_id": selected_doc["_id"]},
            {"$push": {"grades": neue_bewertung}}
        )
        print("Die Bewertung wurde erfolgreich hinzugefügt!")
    else:
        print("Keine Bewertung vorgenommen.")



def aufgabe_6_restaurant_hinzufuegen():
    print("--- Aufgabe 6: Neues Restaurant anlegen ---")

    # Hilfsfunktion für Pflichtfelder
    def get_valid_input(prompt, min_len=2, exact_len=None):
        while True:
            val = input(prompt).strip()
            if exact_len and len(val) != exact_len:
                print(f"Fehler: Die Eingabe muss exakt {exact_len} Zeichen lang sein.")
            elif len(val) < min_len:
                print(f"Fehler: Die Eingabe muss mindestens {min_len} Zeichen lang sein.")
            else:
                return val

    # Felder abfragen
    name = get_valid_input("Name des Restaurants (min. 2 Zeichen): ")
    borough = get_valid_input("Stadtbezirk/Borough (min. 2 Zeichen): ")
    cuisine = get_valid_input("Küche/Cuisine (min. 2 Zeichen): ")
    street = get_valid_input("Strasse (min. 2 Zeichen): ")
    zip_code = get_valid_input("Postleitzahl (genau 5 Zeichen): ", exact_len=5)
    
    # Hausnummer ist laut Vorgabe kein explizites Pflichtfeld mit Einschränkung
    building = input("Hausnummer: ").strip()

    # Document zusammensetzen
    new_restaurant = {
        "name": name,
        "borough": borough,
        "cuisine": cuisine,
        "address": {
            "building": building,
            "street": street,
            "zipcode": zip_code,
            "coord": [] 
        },
        "grades": []
    }

    # Einfügen
    result = db.restaurants.insert_one(new_restaurant)
    print(f"\nErfolg! Restaurant wurde angelegt. Die zugewiesene ID lautet: {result.inserted_id}")

def aufgabe_7_restaurant_loeschen():
    print("--- Aufgabe 7: Restaurant löschen ---")
    
    suchbegriff = ""
    while len(suchbegriff) < 2:
        suchbegriff = input("Gib den Namen (oder einen Teil) des zu löschenden Restaurants ein (min. 2 Zeichen): ").strip()

    # Query aufbauen (case-insensitive)
    query = {"name": {"$regex": suchbegriff, "$options": "i"}}
    
    # Anzahl der betroffenen Dokumente prüfen
    treffer_anzahl = db.restaurants.count_documents(query)

    if treffer_anzahl == 0:
        print(f"Es wurden keine Restaurants gefunden, die '{suchbegriff}' enthalten.")
        return

    # Sicherheitsfrage
    print(f"\nACHTUNG: Es wurden {treffer_anzahl} Restaurant(s) gefunden, die auf '{suchbegriff}' zutreffen.")
    bestaetigung = input("Möchtest du diese wirklich UNWIDERRUFLICH löschen? (ja / nein): ").strip().lower()

    if bestaetigung == 'ja':
        result = db.restaurants.delete_many(query)
        print(f"Erfolgreich gelöscht. Anzahl gelöschter Einträge: {result.deleted_count}")
    else:
        print("Der Löschvorgang wurde vom Benutzer abgebrochen. Es wurde nichts gelöscht.")   


#aufgabe1()
#aufgabe2()
#aufgabe3()
#aufgabe4()
#aufgabe_6_restaurant_hinzufuegen()
aufgabe_7_restaurant_loeschen()

