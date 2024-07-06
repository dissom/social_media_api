FROM python:3.12-alpine3.20

LABEL maintainer="dissom1987@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /social_media_api
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /social_media_api/

RUN mkdir -p /vol/web/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN chown -R django-user:django-user /vol/
RUN chmod -R 755 /vol/web/

USER django-user
