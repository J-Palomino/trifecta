#!/bin/bash
# Import NeDB data to MongoDB for DaisyChain migration

MONGO_URL="${MONGODB_URL}"
DB_NAME="${MONGODB_NAME:-meshcentral}"

echo "Importing user and mesh data to MongoDB..."
echo "Database: $DB_NAME"

# Extract connection details
MONGO_HOST=$(echo $MONGO_URL | sed -n 's|.*@\([^:]*\):\([0-9]*\)|\1|p')
MONGO_PORT=$(echo $MONGO_URL | sed -n 's|.*@\([^:]*\):\([0-9]*\)|\2|p')
MONGO_USER=$(echo $MONGO_URL | sed -n 's|mongodb://\([^:]*\):.*|\1|p')
MONGO_PASS=$(echo $MONGO_URL | sed -n 's|mongodb://[^:]*:\([^@]*\)@.*|\1|p')

echo "Connecting to MongoDB at $MONGO_HOST:$MONGO_PORT"

# Import user data
mongoimport --host="$MONGO_HOST" --port="$MONGO_PORT" \
  --username="$MONGO_USER" --password="$MONGO_PASS" \
  --db="$DB_NAME" --collection="meshcentral" \
  --file=user-export.json --jsonArray

# Import mesh data
mongoimport --host="$MONGO_HOST" --port="$MONGO_PORT" \
  --username="$MONGO_USER" --password="$MONGO_PASS" \
  --db="$DB_NAME" --collection="meshcentral" \
  --file=mesh-export.json --jsonArray

echo "Import complete!"
