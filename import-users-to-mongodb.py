#!/usr/bin/env python3
"""Import NeDB user data to MongoDB for DaisyChain"""

import json
import sys

try:
    from pymongo import MongoClient
except ImportError:
    print("pymongo not installed. Install with: pip install pymongo")
    sys.exit(1)

# MongoDB connection details from Railway
MONGO_URL = "mongodb://mongo:LbYDUewIvFujSBBTvGJQmzQtgquIdpti@crossover.proxy.rlwy.net:34978"
DB_NAME = "meshcentral"
COLLECTION_NAME = "meshcentral"

def import_data():
    """Import user and mesh data to MongoDB"""

    print(f"Connecting to MongoDB...")
    print(f"URL: {MONGO_URL}")
    print(f"Database: {DB_NAME}")
    print(f"Collection: {COLLECTION_NAME}")

    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Test connection
        client.admin.command('ping')
        print("Connected successfully!")

        # Load user data
        with open('user-export.json', 'r') as f:
            user_data = json.load(f)

        # Load mesh data (it's JSONL format, one JSON per line)
        mesh_data = []
        with open('mesh-export.json', 'r') as f:
            for line in f:
                if line.strip():
                    mesh_data.append(json.loads(line))

        print(f"\nFound {len(mesh_data)} mesh groups to import")
        print(f"Found 1 user to import")

        # Import user
        print("\nImporting user...")
        result = collection.insert_one(user_data)
        print(f"User inserted with ID: {result.inserted_id}")

        # Import meshes
        print("\nImporting mesh groups...")
        if mesh_data:
            result = collection.insert_many(mesh_data)
            print(f"Inserted {len(result.inserted_ids)} mesh groups")

        # Verify import
        print("\nVerifying import...")
        user_count = collection.count_documents({"type": "user"})
        mesh_count = collection.count_documents({"type": "mesh"})

        print(f"Users in database: {user_count}")
        print(f"Mesh groups in database: {mesh_count}")

        # Show imported user
        user = collection.find_one({"type": "user"})
        if user:
            print(f"\nImported user: {user['name']} ({user['email']})")

        print("\nImport complete!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    import_data()
