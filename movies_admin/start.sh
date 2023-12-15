#!/bin/bash

python3 manage.py migrate --fake
python3 manage.py migrate
python3 manage.py runserver

