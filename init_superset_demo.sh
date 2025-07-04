#!/bin/bash
set -e
set -o pipefail

exec > >(tee -a /tmp/initdb_superset.log) 2>&1

echo "=== Starting Superset initialization ==="
echo "=== Checking for Postgres binary ==="
ls -l /usr/lib/postgresql/15/bin/postgres || echo "Postgres binary not found!"

echo "=== Printing Superset error log (if exists) ==="
cat /var/log/superset_err.log || echo "Superset error log not found!"

# Wait for Postgres to be ready
until psql -h /tmp -d postgres -c '\q' 2>/dev/null; do
  echo "Waiting for Postgres to be ready..."
  sleep 2
done

# Create superset user and database if not exists
echo "=== Creating database and user ==="
psql -h /tmp -d postgres -c "CREATE USER superset WITH PASSWORD 'superset';" || true
psql -h /tmp -d postgres -c "CREATE DATABASE superset OWNER superset;" || true

# Wait for the superset DB and user to be ready
until psql -h /tmp -U superset -d superset -c '\q' 2>/dev/null; do
  echo "Waiting for superset DB and user to be ready..."
  sleep 2
done

# Create the student_responses table and grant privileges
echo "=== Creating student_responses table ==="
psql -h /tmp -d superset <<EOF
CREATE TABLE IF NOT EXISTS student_responses (
    school_code VARCHAR(10),
    school_name VARCHAR(100),
    level_code VARCHAR(10),
    level_name VARCHAR(50),
    class_code VARCHAR(10),
    class_name VARCHAR(50),
    student_id VARCHAR(50),
    student_name VARCHAR(100),
    academic_year INT,
    question_id INT,
    question_text TEXT,
    competency VARCHAR(100),
    intent_id VARCHAR(10),
    response_value INT,
    response_text VARCHAR(50),
    published_at TIMESTAMPTZ
);
EOF

psql -h /tmp -d superset -c "GRANT ALL PRIVILEGES ON TABLE student_responses TO superset;"
echo "Table created successfully!"

# Initialize Superset
echo "Running superset db upgrade..."
superset db upgrade

echo "Running superset fab create-admin..."
superset fab create-admin --username admin --firstname Superset --lastname Admin --email admin@superset.com --password admin

echo "Running superset init..."
superset init

# Run mock data script
echo "=== Starting mock data generation ==="
python3 -u /app/superset_mock_data.py || true

echo "Init script completed"