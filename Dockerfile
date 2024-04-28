# app/Dockerfile

FROM python:3.12    -slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/0xKev/wordle-solver.git .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir database
COPY database/stats.csv database/stats.csv
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "wordle_stats_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]