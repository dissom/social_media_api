# Social Media API

## Overview

The Social Media API is a Django-based application
designed to provide backend services for a social media platform.
It includes user profiles, posts, social links, and follows/followers
functionality.

# Features

- User Profiles: Create and manage user profiles with profile pictures, bios, and social links.
- Posts: Allow users to create, edit, and delete posts with associated media and content.
- Follows/Followers: Enable users to follow and be followed by other users.
- Authentication: Secure user authentication using Django's built-in authentication system.
- Customizable: Easily extendable with Django's powerful ORM and REST framework.

# Technologies Used

- Django: Backend framework for robust web applications.
- Django REST Framework: Toolkit for building Web APIs.
- PostgreSQL: Relational database management system.
- Redis: In-memory data structure store for caching and message brokering.
- Celery: Distributed task queue for background processing.

## Prerequisites

Before you can run this project, make sure you have the following installed:
- Python 3.8 or higher
- Django 3.2 or higher
- pip (Python package installer)
- PostgreSQL (or any other database you are using)

## Instalation

# Running the API with Python
```shell
- git clone `https://github.com/dissom/social_media_api.git`
- cd social_media_api
- python3 -m venv venv
- source venv/bin/activate (on macOS)
- venv\Scripts\activate (on Windows)
- pip install -r requirements.txt

- python manage.py makemigrations
- python manage.py migrate
- python manage.py createsuperuser
- python manage.py runserver

(The API will be available at `http://127.0.0.1:8000/`.)
```

# Start Celery Worker:

`celery -A social_media_api worker -l INFO`

# Start Celery Beat:

`celery -A social_media_api beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`

# Start Flower for Monitoring:

`celery -A social_media_api flower --address=0.0.0.0`



# API Documentation:

Detailed API documentation and usage examples are
available at `http://127.0.0.1:8000/api/doc/swagger/`.


# Running the API with Docker
```shell
git clone `https://github.com/dissom/social_media_api.git`
cd social_media_api

create an .env file in the root directory of project:

    POSTGRES_PASSWORD=POSTGRES_PASSWORD
    POSTGRES_USER=POSTGRES_USER
    POSTGRES_DB=POSTGRES_DB
    POSTGRES_PORT=POSTGRES_PORT
    POSTGRES_HOST=POSTGRES_HOST
    PGDATA=PGDATA
    CELERY_BROKER_URL = CELERY_BROKER_URL
    CELERY_RESULT_BACKEND = CELERY_RESULT_BACKEND
    SECRET_KEY=SECRET_KEY

docker-compose build
docker-compose up
- Create new admin user. `docker-compose exec social_media_api_app python manage.py createsuperuser`;

(The API will be available at `http://127.0.0.1:4000/`.)
```
