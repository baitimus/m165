import pymongo

def display_records(cursor_obj):
    [print(record) for record in cursor_obj]

def fetch_all_courses(db_conn):
    return db_conn.courses.find({}, {"_id": 0, "course_id": 1, "title": 1, "category": 1})

def fetch_members(db_conn, active_only=False):
    search_criteria = {"status": "active"} if active_only else {}
    return db_conn.participants.find(search_criteria, {"participant_id": 1, "name": 1, "city": 1, "status": 1})

def compute_mean_duration(db_conn):
    valid_lengths = [
        doc.get("duration_days") 
        for doc in db_conn.courses.find({}, {"_id": 0, "duration_days": 1}) 
        if doc.get("duration_days")
    ]
    return sum(valid_lengths) / len(valid_lengths)

db_client = pymongo.MongoClient("mongodb://localhost:27017/")
target_database = db_client.academy_system

if "academy_system" not in db_client.list_database_names():
    print("Database not found")

while True:
    print("\n1: Kursübersicht anzeigen\n2: Teilnemerübersicht anzeigen\n3: Aktive Teilnehme anzeigen\n4: Durchschnitliche Kursdauer anzeigen")
    
    selection = input("Enter your choice: ")
    
    match selection:
        case "1":
            display_records(fetch_all_courses(target_database))
        case "2":
            display_records(fetch_members(target_database))
        case "3":
            display_records(fetch_members(target_database, active_only=True))
        case "4":
            print(compute_mean_duration(target_database))
        case _:
            continue


