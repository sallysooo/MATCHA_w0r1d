# BASE IMAGE
FROM python:3.10-slim

# WORK DIRECTORY
WORKDIR /app

# COPY FILE
COPY src/ /app/
COPY flag.txt /flag.txt
COPY requirements.txt .

# CREATE uploads folder
RUN mkdir -p /app/app/uploads && \
    chmod -R 700 /app/app/uploads && \
    chmod 400 /flag.txt

# INSTALL DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

# ENV CONFIG
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=916

# RUN SERVER
CMD ["flask", "run"]

