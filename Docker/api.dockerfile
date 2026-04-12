FROM python:3.12-slim

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
COPY requirements_docker.txt requirements_docker.txt
COPY api/ api/
COPY data/ data/
COPY enums/ enums/
COPY src/ src/

WORKDIR /
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install -r requirements_docker.txt --no-cache-dir

EXPOSE 8000