import os  # 1. Add this at the very top
from pymongo import MongoClient

# Connect to MongoDB
connection_string = "mongodb://localhost:27017/"
client = MongoClient(connection_string)

# Get the list of all databases
db_names = client.list_database_names()

while True:
    print("\nDatabases:")
    
    # Loop through the databases and number them 1, 2, 3...
    for index, db in enumerate(db_names, start=1):
        print(f" {index}. {db}")
    
    # Add an Exit option at the very bottom
    exit_number = len(db_names) + 1
    print(f" {exit_number}. Exit")
    
    print() # Blank line
    
    # Ask for input
    choice = input("Select a number: ")
    
    # 2. CLEAR THE SCREEN RIGHT AFTER THEY PRESS ENTER
    # We use a clever one-liner here: it runs 'cls' if you ever move this to Windows, 
    # but defaults to 'clear' for Linux/Mac (like your LXC).
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Figure out what they typed
    try:
        choice_num = int(choice)
        
        if choice_num == exit_number:
            print("Goodbye!")
            break
            
        elif 1 <= choice_num <= len(db_names):
            selected_db = db_names[choice_num - 1]
            print(f"✅ You chose: {selected_db}")
            
            # --- Next phase goes here! ---
            
            break 
            
        else:
            print("⚠️ Number out of range. Please try again.")
            
    except ValueError:
        print("⚠️ Please type a number, not letters.")