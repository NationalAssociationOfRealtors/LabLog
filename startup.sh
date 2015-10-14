#!/usr/bin/env bash

python manage.py init_app

gunicorn -c /config/gunicorn.conf wsgi:app --reload
