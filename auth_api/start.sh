#!/bin/bash

alembic revision --autogenerate -m "initial migrations"
alembic upgrade head
sleep 4
python3 src/create_superuser.py login superuser password superuser
uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 8000 --debug
