#!/usr/bin/env bash

set -e

python wait_for_es.py

echo ""
curl -XPUT http://elastic:9200/films -H 'Content-Type: application/json' -d@"./elastic_schema/films.json"
echo ""
curl -XPUT http://elastic:9200/persons -H 'Content-Type: application/json' -d@"./elastic_schema/persons.json"
echo ""
curl -XPUT http://elastic:9200/genres -H 'Content-Type: application/json' -d@"./elastic_schema/genres.json"

python ETL.py