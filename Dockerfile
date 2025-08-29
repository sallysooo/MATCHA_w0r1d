# sudo docker compose build --no-cache
# sudo docker compose up -d

# BASE IMAGE
FROM python:3.11-slim

# Speed & cleanliness
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 
ENV PIP_NO_CACHE_DIR=1

# WORK DIRECTORY
WORKDIR /app

# Install deps first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure CPU-only PyTorch is present (remove if already in requirements.txt)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# COPY FILE
COPY src/ /app/

# Dev-build fallback flag (compose will bind-mount the real one as read-only)
# My repo keeps flag at src/flag.txt, so copy from there:
COPY src/flag.txt /flag.txt

# Prepare writable upload dir & flag perms
RUN mkdir -p /app/app/uploads && \
    chmod -R 700 /app/app/uploads && \
    chmod 0444 /flag.txt

# drop root
RUN useradd -m -u 10001 appuser \
 && chown -R appuser:appuser /app
USER appuser

# ENV CONFIG
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=916

EXPOSE 916

# RUN SERVER
CMD ["python", "-m", "gunicorn.app.wsgiapp", "-w", "2", "-b", "0.0.0.0:916", "app:app"]

