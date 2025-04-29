#!/bin/bash
set -e

# Wait for the database to be ready
echo "Waiting for PostgreSQL to start..."
sleep 5

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Check if data already exists before seeding
echo "Checking if database needs seeding..."
python -c "
from sqlalchemy import text
from src.database import SessionLocal
db = SessionLocal()
# Check if destinations table has data
result = db.execute(text('SELECT COUNT(*) FROM destinations')).scalar()
db.close()
if result == 0:
    print('No data found, seeding required')
    exit(1)
else:
    print('Data already exists, skipping seed')
    exit(0)
"

if [ $? -eq 1 ]; then
    echo "Seeding database with sample data..."
    python -m src.scripts.seed_data
else
    echo "Database already contains data, skipping seed step."
fi

# Start the application
echo "Starting the application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000