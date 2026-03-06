# --- Build Stage (Frontend) ---
FROM node:18-alpine AS build-stage
WORKDIR /app/ui
COPY ui/package*.json ./
RUN npm install
COPY ui/ ./
RUN npm run build

# --- Production Stage (Backend + Frontend Static) ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn

# Copy project files
COPY . .

# Copy the built frontend from build-stage
COPY --from=build-stage /app/ui/dist ./ui/dist

# Ensure the upload directory exists
RUN mkdir -p temp_uploads && chmod 777 temp_uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["python", "api/local_api.py"]
