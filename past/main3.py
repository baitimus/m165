from pymongo import MongoClient
from bson.objectid import ObjectId


connection_string = "mongodb://localhost:27017/"
client = MongoClient(connection_string)
def print_dbandcollectionInfo(collection, document=None):
    db_name = collection.database.name
    col_name = collection.name
    if document:
        print(f"Document '{document['_id']}' is in {db_name}.{col_name}")
    else:
        print(f"Documents in {db_name}.{col_name}:")
dblist = client.list_database_names()
def print_dbs():
    print("Databases:")
    for db_name in dblist:
        print("- " + db_name)
def print_collections(db):
    print("Collections:")
    if db is not None:
        collist = db.list_collection_names()
        for col in collist:
            print("- " + col)
def print_documents(collection):
    print_dbandcollectionInfo(collection)
    if collection is not None:
        documents = collection.find()
        for doc in documents:
            print(f"- {doc['_id']}")
def select_database():
    print("Databases:")
    print_dbs()
    db_name_input = input("Select or create Database: ")
    return client[db_name_input]
def print_document(document):
    if document is not None:
        print_dbandcollectionInfo(collection=selected_collection, document=document)
        print(document)
    else:
        print("Document not found.")      
def select_collection(db):
    print_collections(db)
    col_name_input = input("Select or create Collection: ")
    return db[col_name_input]
def select_document(collection):
    doc_id_input = input("Select Document by _id: ").strip()
    try:
        # Convert the string input to an ObjectId
        obj_id = ObjectId(doc_id_input)
        return collection.find_one({"_id": obj_id})
    except Exception:
        # Handle cases where the input is not a valid ObjectId
        return None
selected_db = select_database()
selected_collection = select_collection(selected_db)
print_documents(selected_collection)
selected_document = select_document(selected_collection)
print_document(selected_document)



