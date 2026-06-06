FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV TASKHUB_DATA=/app/data/tasks.json

CMD ["python", "app.py"]
