FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./requirements.txt
# Install and use uv, a much faster package installer, to handle dependencies
RUN pip install uv && \
    uv pip install --system --no-cache -r requirements.txt 

# Copy the rest of the application
COPY . .

RUN mkdir -p /app/data/generated_images

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 