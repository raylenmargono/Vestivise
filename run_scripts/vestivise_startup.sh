#!/bin/bash

# to run do chmod +x file
# then run script by: bash vestivise_startup.sh
source env/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata dashboard/fixtures/module_fix.json
python manage.py collectstatic --noinput
deactivate

service gunicorn reload
sudo supervisorctl restart vestivise_nightly