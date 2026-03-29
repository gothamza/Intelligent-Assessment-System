FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (much faster than pip)
RUN pip install uv

# Install Python dependencies with uv
COPY requirements.txt .
# Install PyTorch first with longer timeout
ENV UV_HTTP_TIMEOUT=600
RUN uv pip install --system --no-cache torch==2.1.1+cpu --index-url https://download.pytorch.org/whl/cpu

RUN uv pip install --system --no-cache -r requirements.txt

# Clean up to reduce image size
RUN apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p Data models

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]