#!/bin/bash

alembic revision --autogenerate -m "initial migration"
alembic upgrade head
python3 src/create_superuser.py login superuser password superuser
uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 8000
