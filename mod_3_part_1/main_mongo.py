

import argparse
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError

# MongoDB connection
uri = "mongodb+srv://RublovA:135792468@clusterr.dq9i5.mongodb.net/?retryWrites=true&w=majority&appName=ClusterR"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.book

# Argument parser
parser = argparse.ArgumentParser(description="Cats Base")
parser.add_argument('--action', help='create, read, update, delete')  # CRUD
parser.add_argument('--name')
parser.add_argument('--age')
parser.add_argument('--features', nargs='+')

arg = vars(parser.parse_args())

action = arg.get('action')
name = arg.get('name')
age = arg.get('age')
features = arg.get('features')

# Database functions with error handling
def find(name=None):
    """Find cats by name or return all records."""
    try:
        if name:
            return db.cats.find({"name": name})
        return db.cats.find()
    except PyMongoError as e:
        print(f"Error finding documents: {e}")
        return None

def create(name, age, features):
    """Insert a new cat document."""
    try:
        result = db.cats.insert_one({
            "name": name,
            "age": int(age) if age else None,
            "features": features,
        })
        print(f'Inserted ID: {result.inserted_id}')
        return result
    except PyMongoError as e:
        print(f"Error inserting document: {e}")
        return None

def update(name, age=None, features=None):
    """Update an existing cat document."""
    try:
        update_fields = {}
        if age is not None:
            update_fields["age"] = int(age)
        if features is not None:
            if isinstance(features, list):
                update_fields["features"] = {"$each": features}
            else:
                update_fields["features"] = features

        update_query = {}
        if "age" in update_fields:
            update_query["$set"] = {"age": update_fields["age"]}
        if "features" in update_fields:
            update_query["$addToSet"] = {"features": update_fields["features"]} if isinstance(features, list) else {"features": features}

        if update_query:
            result = db.cats.update_one({"name": name}, update_query)
            print(f'Modified count: {result.modified_count}')
            return result
    except PyMongoError as e:
        print(f"Error updating document: {e}")
        return None

def delete(name=None):
    """Delete a cat by name or all documents if no name is provided."""
    try:
        if name:
            result = db.cats.delete_one({"name": name})
            print(f'Deleted count: {result.deleted_count}')
            return result
        result = db.cats.delete_many({})
        print(f'Deleted all documents: {result.deleted_count}')
        return result
    except PyMongoError as e:
        print(f"Error deleting documents: {e}")
        return None

# Main function
def main():
    try:
        match action:
            case 'create':
                create(name, age, features)
            case 'read':
                results = find(name)
                if results:
                    for cat in results:
                        print(cat)
            case 'update':
                update(name, age, features)
            case 'delete':
                delete(name)
            case _:
                print('Unknown command')
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    main()