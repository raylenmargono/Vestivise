#!/bin/bash

redis-server --daemonize yes
celery -A Vestivise worker -l info
supervisord -c ./celery.conf
