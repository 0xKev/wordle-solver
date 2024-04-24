# app/Dockerfile

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
ADD "wordle_stats_dashboard.py" . 
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
CMD ["streamlit", "run", "wordle_stats_dashboard.py"]
EXPOSE 8501