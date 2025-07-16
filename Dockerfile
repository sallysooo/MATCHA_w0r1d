FROM python:3.9

COPY . /app
# docker run -v $(pwd)/app/uploads:/app/uploads -p 5000:5000 your-image-name
