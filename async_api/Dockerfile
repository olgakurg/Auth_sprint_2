FROM python:3.10

WORKDIR /var/www/async_api

COPY requirements.txt requirements.txt
COPY . .

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]

