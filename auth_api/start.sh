#!/bin/bash

alembic revision --autogenerate -m "initial migrations"
sleep 5
alembic upgrade head
sleep 5
python3 src/create_superuser.py
uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 8000 --debug
