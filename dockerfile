FROM python:3.10-slim

# Install dependencies for Tesseract & OpenCV
RUN apt-get update && \
    apt-get install -y tesseract-ocr libglib2.0-0 libsm6 libxext6 libxrender-dev \
    firefox-esr wget curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Optionally install geckodriver (for selenium use)
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz && \
    tar -xzf geckodriver-v0.36.0-linux64.tar.gz && \
    mv geckodriver /usr/local/bin && \
    rm geckodriver-v0.36.0-linux64.tar.gz

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Entry point 
CMD ["python", "mqtt_sender.py"]
