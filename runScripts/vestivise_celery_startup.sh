#!/bin/bash

redis-server --daemonize yes
supervisord -c ./celery.conf