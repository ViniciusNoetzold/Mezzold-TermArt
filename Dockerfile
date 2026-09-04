FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . .

# Environment variables
ENV PYTHONPATH=/app/src
ENV PORT=7860
ENV HEADLESS=1

EXPOSE 7860

CMD ["python", "termstudio.py"]
