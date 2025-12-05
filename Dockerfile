# Build Pandoc Converter Service
FROM pandoc/latex:3.8.3-ubuntu

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python 3.13
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.13 python3.13-venv python3.13-dev && \
    rm -rf /var/lib/apt/lists/*

# Create symlink for python3 and install pip for Python 3.13
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 && \
    python3.13 -m ensurepip --upgrade && \
    python3.13 -m pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using python3.13
RUN python3.13 -m pip install --no-cache-dir --upgrade pip && \
    python3.13 -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/app/

# Expose port
EXPOSE 8000

# Set timezone
RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# Override ENTRYPOINT from base image (pandoc/latex sets pandoc as entrypoint)
ENTRYPOINT []

# Run the application
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

