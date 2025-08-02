# BASE IMAGE
FROM python:3.10-slim

# WORK DIRECTORY
WORKDIR /app

# COPY FILE
COPY . /app

COPY flag.txt /flag.txt

RUN mkdir -p /app/app/uploads

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=916

CMD ["flask", "run"]

# 1. IMAGE BUILD
# docker build -t matcha_world .

# RUN CONTAINER
# docker run -p 916:916 matcha_world