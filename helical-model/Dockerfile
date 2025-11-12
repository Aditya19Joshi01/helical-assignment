FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements-model.txt .
RUN pip install --no-cache-dir -r requirements-model.txt

# Only copy data (optional)
COPY ./data /app/data

# Default command
CMD ["python", "scripts/run_model.py"]
