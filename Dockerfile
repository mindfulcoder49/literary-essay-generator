FROM node:20-slim AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
COPY --from=frontend /app/static ./app/static/

# Create a seed database with the correct schema during the build
RUN python scripts/create_seed_db.py

ENV PYTHONPATH=/app

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script to manage startup
ENTRYPOINT ["/entrypoint.sh"]
# The CMD will be passed as an argument to the entrypoint
CMD ["web"]
