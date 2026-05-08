from pymongo import MongoClient

connection_string = "mongodb://localhost:27017/"
client = MongoClient(connection_string)


db_name = client.list_database_names()

print("Databases")

for db in db_name: 
    print(f" - {db}")

    