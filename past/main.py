from pymongo import MongoClient
from bson.objectid import ObjectId
import os

def display_records(cursor_obj):
    [print(record) for record in cursor_obj]
def is_document_empty(document):
    return not bool(document)   

connection_string = "mongodb://localhost:27017/"
client = MongoClient(connection_string)



if "academy_system" not in client.list_database_names():
    print("Database not found")

def fetch_all_courses(db_conn):
    return db_conn.courses.find({}, {"_id": 0, "course_id": 1, "title": 1, "category": 1})  

def fetch_members(db_conn, active_only=False):
    search_criteria = {"status": "active"} if active_only else {}
    return db_conn.participants.find(search_criteria, {"_id": 0, "participant_id": 1, "name": 1, "city": 1, "status": 1})



# - P501 | Max Muster | Zürich | active
def courses_per_category(db_conn):
    pipeline = [
        {"$group": {"_id": "$category", "course_count": {"$sum": 1}}}
    ]
    return db_conn.courses.aggregate(pipeline)



target_database = client.academy_system


while True:

  
    

    print("\n1: Kursübersicht anzeigen\n2: Teilnemerübersicht anzeigen\n3: Aktive Teilnehme anzeigen\n4: exit \n5: anzahl Kurse pro Kategorie anzeigen")
 
    selection = input("Enter your choice: ")
    if selection not in ["1", "2", "3", "4", "5"]:
        print("Invalid selection, please try again. use only the numbers watch the space bar and the enter key")

    os.system('cls' if os.name == 'nt' else 'clear')     
    match selection:
        case "1":
            display_records(fetch_all_courses(target_database))
        case "2":
            display_records(fetch_members(target_database))
        case "3":
            display_records(fetch_members(target_database, active_only=True))
        case "4":
           exit()
        case "5":
            display_records(courses_per_category(target_database))

        case _:
            print("Invalid selection")
            
       
    input("Press Enter to continue...")
    os.system('cls' if os.name == 'nt' else 'clear')     


