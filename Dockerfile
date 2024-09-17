# app/Dockerfile

FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    wget \
    unzip \
    && curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get -y update \
    && apt-get -y install google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip \
&& unzip chromedriver-linux64.zip \
&& mv chromedriver-linux64/chromedriver /usr/bin/ \
&& chown root:root /usr/bin/chromedriver \
&& chmod +x /usr/bin/chromedriver

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY database/ ./database
COPY data/ ./data

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health
EXPOSE 8502
ENTRYPOINT ["streamlit", "run", "src/wordle_stats_dashboard.py", "--server.port=8502", "--server.address=0.0.0.0", "--server.headless=true"]