FROM python:3.10-slim-buster

ENV PYTHONBUFFERED 1
WORKDIR /django_app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
