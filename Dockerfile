# syntax=docker/dockerfile:1

FROM python:3.12
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["streamlit", "run", "wordle_stats_dashboard.py"]
EXPOSE 3000