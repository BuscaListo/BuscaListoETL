FROM python:3.11-slim

WORKDIR /app

# Variables de entorno
ENV ETL_PROJECT_PATH=/app
ENV DATA_ETL=data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "webscraping.webscraping_main"]