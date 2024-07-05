FROM python:3.12-alpine3.20

LABEL maintainer="dissom1987@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /social_media_api
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /social_media_api/
