# Dockerfile
FROM python:3.12
SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN pip install --upgrade pip

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY School_Diplom ./