FROM python:3.9-slim

RUN mkdir /app
WORKDIR /app

RUN pip install bottle

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
