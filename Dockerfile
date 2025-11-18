# Dockerfile for HF Space — Gradio + Selenium + Chromium
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system deps and chromium
RUN apt-get update && apt-get install -y \
    wget ca-certificates unzip git \
    fonts-liberation libnss3 libgconf-2-4 libxss1 libasound2 libatk1.0-0 libgtk-3-0 libgbm1 \
    chromium chromium-driver \
  && rm -rf /var/lib/apt/lists/*

# Set Chrome binary path env (webdriver-manager will use driver)
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/bin/chromium

# Create app dir
WORKDIR /app
COPY . /app

# Install python deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port used by Gradio
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]
