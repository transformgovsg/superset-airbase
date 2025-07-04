# Deploying Superset on Airbase

A self-contained Docker container that runs Apache Superset with PostgreSQL, Redis, and mock data generation, designed for deployment on Airbase cloud platform.

## Overview

This project packages Apache Superset with all its dependencies into a single Docker container using Supervisor for process management. This approach is specifically designed for cloud platforms like Airbase that only support deploying a single image per instance.

## Architecture

### Why Single Container with Supervisor?

**Airbase Platform Constraints:**
- Airbase only supports deploying a single Docker image per instance
- No support for multi-container orchestration (Docker Compose, Kubernetes)
- Requires all services to run within a single container

**Supervisor Solution:**
- **Process Management:** Supervisor manages multiple processes within a single container
- **Service Coordination:** Ensures proper startup order and dependency management
- **Process Monitoring:** Automatically restarts failed services
- **Log Management:** Centralized logging for all services

### Services Managed by Supervisor

1. **PostgreSQL** (`postgres`) - Database server
2. **Redis** (`redis`) - Caching and session storage
3. **Init-DB** (`init-db`) - Database initialization and setup
4. **Superset** (`superset`) - Apache Superset web application
5. **Debug** (`debug`) - Diagnostic and health check service

## Quick Start

### Prerequisites

- Docker
- Git

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd superset-all-in-one

# Build the Docker image
docker build -t superset-all-in-one .

# Run the container
docker run -d --name superset-all-in-one -p 8088:8088 superset-all-in-one

# View logs
docker logs -f superset-all-in-one
```

### Access Superset
Open http://localhost:8088 in your browser
Username: admin
Password: admin

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8088 | Port for Superset web interface |
| `SUPERSET_CONFIG_PATH` | `/app/superset_config.py` | Path to Superset configuration |
| `SUPERSET_HOME` | `/app/superset_home` | Superset home directory |
| `SECRET_KEY` | `demo_secret_key` | Flask secret key (change in production) |

### Database Configuration

- **Host:** `/tmp` (Unix socket)
- **Database:** `superset`
- **User:** `superset`
- **Password:** `superset`
- **Port:** 5432

### Redis Configuration

- **Host:** `localhost`
- **Port:** 6379
- **Database:** 0 (default)

## Log Files

### Container Logs (Main Output)

All logs are available via `docker logs` or your cloud provider's log viewer:

```bash
docker logs -f superset-all-in-one
```

### Individual Service Logs

| Service | Log File | Description |
|---------|----------|-------------|
| **Supervisor** | `/tmp/supervisord.log` | Main supervisor process logs |
| **PostgreSQL** | `/tmp/postgres.log` | Database server logs |
| **PostgreSQL Errors** | `/tmp/postgres_err.log` | Database error logs |
| **Redis** | `/tmp/redis.log` | Redis server logs |
| **Redis Errors** | `/tmp/redis_err.log` | Redis error logs |
| **Superset** | `/tmp/superset.log` | Superset application logs |
| **Superset Errors** | `/tmp/superset_err.log` | Superset error logs |
| **Init-DB Script** | `/tmp/initdb_superset.log` | Database initialization logs |
| **Mock Data Script** | `/tmp/script.log` | Data generation logs |
| **Debug** | `/tmp/debug.log` | Diagnostic service logs |
| **Debug Errors** | `/tmp/debug_err.log` | Diagnostic error logs |

### Accessing Logs

**From inside the container:**
```bash
docker exec -it superset-all-in-one bash
cat /tmp/superset_err.log
cat /tmp/initdb_superset.log
```

**From host machine:**
```bash
docker exec superset-all-in-one cat /tmp/superset_err.log
```

## Data Generation

### Customizing Data Generation

Edit `superset_mock_data.py` to modify:
- Number of students per class (`STUDENTS_PER_CLASS`)
- School list (`SCHOOLS`)
- Question sets (`QUESTIONS_LOWER`, `QUESTIONS_UPPER`)
- Batch size for database inserts (`BATCH_SIZE`)


## Troubleshooting

### Common Issues

1. **500 Internal Server Error**
   - Check Superset error logs: `/tmp/superset_err.log`
   - Verify database connection: `docker exec -it superset-all-in-one psql -h /tmp -U superset -d superset`
   - Check if admin user exists: `SELECT * FROM ab_user;`

2. **Database Connection Issues**
   - Check PostgreSQL logs: `/tmp/postgres_err.log`
   - Verify PostgreSQL is running: `docker exec -it superset-all-in-one supervisorctl status postgres`

3. **Mock Data Not Generated**
   - Check mock data logs: `/tmp/script.log`
   - Verify table exists: `\dt student_responses`

4. **Cannot Access Superset**
   - Check if Superset is running: `docker exec -it superset-all-in-one supervisorctl status superset`
   - Verify port configuration: Check `$PORT` environment variable
   - Check Superset logs: `/tmp/superset.log`

### Health Checks

```bash
# Check all service status
docker exec -it superset-all-in-one supervisorctl status

# Test database connection
docker exec -it superset-all-in-one psql -h /tmp -U superset -d superset -c "SELECT 1;"

# Test Superset health endpoint
curl http://localhost:8088/health
```

## Security Considerations

### Production Deployment

1. **Change Default Passwords:**
   - Update database password in `superset_config.py`
   - Change admin password after first login
   - Set a strong `SECRET_KEY`

2. **Network Security:**
   - Use HTTPS in production
   - Configure proper firewall rules
   - Limit database access

3. **Data Protection:**
   - Regular database backups
   - Encrypt sensitive data
   - Implement proper access controls

## Performance Tuning

### Database Optimization

- Adjust PostgreSQL settings in `/var/lib/postgresql/data/postgresql.conf`
- Monitor query performance with Superset's SQL Lab
- Consider indexing frequently queried columns

### Superset Configuration

- Adjust worker processes in `superset_config.py`
- Configure caching settings for Redis
- Optimize dashboard refresh intervals

## Airbase Deployment Requirements

### Custom Image Requirements

Airbase has specific requirements for custom Docker images to ensure compatibility and security:

#### **Non-Root User with UID 999**
- **Requirement:** The running user of the container shall not be root, and should have a UID of 999
- **Implementation:** Our Dockerfile creates a non-root user `supersetuser` with UID 999
- **Security Benefits:** Reduces security risks by not running services as root

#### **Dynamic Port Binding**
- **Requirement:** Application should listen on port `$PORT`, which would be passed to the container at runtime
- **Implementation:** Superset is configured to use `${PORT:-8088}` (defaults to 8088 if `$PORT` is not set)
- **Flexibility:** Allows Airbase to assign any available port to your container

### How We Meet These Requirements

#### **Dockerfile Configuration**
```dockerfile
# Create non-root user with UID 999
RUN useradd -u 999 -m -d /home/supersetuser supersetuser

# Switch to non-root user
USER 999
```

#### **Supervisor Configuration**
```ini
[program:superset]
command=sh -c 'superset run -h 0.0.0.0 -p ${PORT:-8088}'
```

# Additional notes

## Using a Separate PostgreSQL Database for Mock Data

By default, mock data is inserted into the main `superset` database. For better separation of concerns, you may wish to use a dedicated database for mock data.

### Step 1: Modify `init_superset_demo.sh` to Create a New Database

Edit `init_superset_demo.sh` and add the following line after the section that creates the `superset` user and database:

Your script should look like this:

```bash
# Create superset user and database if not exists
psql -h /tmp -d postgres -c "CREATE USER superset WITH PASSWORD 'superset';" || true
psql -h /tmp -d postgres -c "CREATE DATABASE superset OWNER superset;" || true
# Create mockdata database for mock data (if not exists)
psql -h /tmp -d postgres -c "CREATE USER mockuser WITH PASSWORD 'mockuser';" || true
psql -h /tmp -d postgres -c "CREATE DATABASE mockdata OWNER mockuser;" || true
```

### Step 2: Update the Mock Data Script

Edit `superset_mock_data.py` to connect to the new database. Locate the database connection string in the script and change the database name from `superset` to `mockdata`. For example:

```python
# Before:
conn = psycopg2.connect(
    dbname="superset",
    user="superset",
    password="superset",
    host="/tmp"
)

# After:
conn = psycopg2.connect(
    dbname="mockdata",
    user="mockuser",
    password="mockuser",
    host="/tmp"
)
```

### Step 3: (Optional) Create Tables in the New Database

If your mock data requires specific tables, add SQL commands to create them in `init_superset_demo.sh` after the new database is created. For example:

```bash
psql -h /tmp -d mockdata <<EOF
CREATE TABLE IF NOT EXISTS random_tables (
    random_column_1 VARCHAR(10),
    random_column_2 VARCHAR(10),
);
EOF
```

### Step 4: Connect to New Database
Connect to the database with the db name, username and password via the Superset UI.