FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
#set environment variables
ENV WORKDIR=/app
RUN pip install -r requirements.txt
RUN apt-get update
COPY . .
EXPOSE 80
CMD ["waitress-serve","--port=80","--threads=8","--url-prefix=/api/v1/rag","--call","run:run_app"]