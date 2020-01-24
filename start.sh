#!/bin/bash
/redis-5.0.7/src/redis-server &
cd /data
python3 manage.py makemigrations
python3 manage.py migrate
celery -A root worker -l info &
python3 manage.py runserver 0.0.0.0:8000
