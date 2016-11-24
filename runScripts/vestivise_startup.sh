#!/bin/bash

# to run do chmod +x file
# then run script by: bash vestivise_startup.sh

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata dashboard/fixtures/moduleFix.json
python manage.py loaddata data/fixtures/benchmarkHoldings.json
python manage.py collectstatic


service gunicorn restart