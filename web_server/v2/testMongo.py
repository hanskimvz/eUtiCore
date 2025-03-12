from pymongo import MongoClient
from datetime import datetime
from pprint import pprint

def connect_to_mongodb():
    # Connect to MongoDB (default localhost:27017)
    client = MongoClient('mongodb://gas_user:13579@47.56.150.14:5090/', authSource='admin')
    
    # Create/access a database
    db = client['gas_common']
    
    # Create/access a collection
    collection = db['user_route']
    
    return client, db, collection

def basic_operations():
    # Connect to MongoDB
    client, db, users = connect_to_mongodb()
    
    # Insert One Document
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "created_at": datetime.utcnow()
    }
    insert_result = users.insert_one(user_data)
    print(f"Inserted document ID: {insert_result.inserted_id}")
    
    # Insert Multiple Documents
    multiple_users = [
        {"name": "Alice", "email": "alice@example.com", "age": 25},
        {"name": "Bob", "email": "bob@example.com", "age": 35}
    ]
    insert_many_result = users.insert_many(multiple_users)
    print(f"Inserted document IDs: {insert_many_result.inserted_ids}")
    
    # Find One Document
    user = users.find_one({"name": "John Doe"})
    print("\nFound user:")
    pprint(user)
    
    # Find Multiple Documents
    print("\nAll users aged 30 or younger:")
    for user in users.find({"age": {"$lte": 30}}):
        pprint(user)
    
    # Update One Document
    update_result = users.update_one(
        {"name": "John Doe"},
        {"$set": {"age": 31}}
    )
    print(f"\nModified {update_result.modified_count} document")
    
    # Update Multiple Documents
    update_many_result = users.update_many(
        {"age": {"$lt": 30}},
        {"$inc": {"age": 1}}
    )
    print(f"Modified {update_many_result.modified_count} documents")
    
    # Delete One Document
    delete_result = users.delete_one({"name": "Bob"})
    print(f"\nDeleted {delete_result.deleted_count} document")
    
    # Query with Multiple Conditions
    print("\nUsers aged between 25 and 35:")
    query = {
        "age": {"$gte": 25, "$lte": 35}
    }
    for user in users.find(query):
        pprint(user)
    
    # Sorting
    print("\nUsers sorted by age descending:")
    for user in users.find().sort("age", -1):
        pprint(user)
    
    # Close the connection
    client.close()

if __name__ == "__main__":
    client, db, users = connect_to_mongodb()
    print (db.list_collection_names())
    # user = users.find_one({})
    for user in users.find({}):
        pprint(user)    


    client.close()
    # basic_operations()