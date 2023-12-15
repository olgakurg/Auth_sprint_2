FROM python:3.10

WORKDIR /var/www/movies_admin

COPY requirements.txt requirements.txt
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt
COPY . .

ENTRYPOINT ["sh", "start.sh"]

