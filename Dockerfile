FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql postgresql-contrib \
    redis-server \
    build-essential \
    libpq-dev \
    curl \
    wget \
    supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with UID 999
RUN useradd -u 999 -m -d /home/supersetuser supersetuser

# Set up directories and permissions
RUN mkdir -p /var/lib/postgresql/data /var/log /app/superset_home
RUN chown -R 999:999 /var/lib/postgresql /var/lib/postgresql/data /var/log /app /app/superset_home

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy configs and scripts
COPY superset_config.py /app/superset_config.py
COPY superset_mock_data.py /app/superset_mock_data.py
COPY init_superset_demo.sh /app/init_superset_demo.sh
RUN chmod +x /app/init_superset_demo.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set environment variables
ENV SUPERSET_CONFIG_PATH=/app/superset_config.py
ENV SUPERSET_HOME=/app/superset_home
ENV PATH="/usr/local/bin:/usr/lib/postgresql/15/bin:$PATH"
ENV FLASK_APP="superset.app:create_app()"

# Switch to non-root user
USER 999

RUN /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/data

# Expose default port (for documentation)
EXPOSE 8088

# Entrypoint
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]