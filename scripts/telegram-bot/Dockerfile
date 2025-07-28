FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY quotes.py .
# RUN apt-get update && apt-get install -y chromium-chromedriver
COPY session.session .
CMD ["python", "bot.py"]