FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]

