#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py create_hospital_admin --username "bmh_hospital" --email "sudharshgk@gmail.com"