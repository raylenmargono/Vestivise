#!/bin/bash

# to run do chmod +x file
# then run script by: bash vestivise_startup.sh

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py dumpdata dashboard/fixtures/moduleFix.json
python manage.py dumpdata data/fixtures/benchmarkHoldings.json

service gunicorn restart