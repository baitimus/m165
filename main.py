from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")

dblist = client.list_database_names()

db_name = "restaurant_db"

if db_name in dblist:
    print(f"Datenbank '{db_name}' gefunden und verbunden.\n")
else:
    print(f"Hinweis: Datenbank '{db_name}' existiert noch nicht. Sie wird beim ersten Speichern erstellt.\n")

db = client[db_name]

