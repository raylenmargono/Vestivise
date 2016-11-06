#!/bin/bash

# to run do chmod +x file
# then run script by: vestivise_celery_startup.sh

# to start celeryd
#/etc/init.d/celeryd start

# to stop
#/etc/init.d/celeryd stop

# see the status
#/etc/init.d/celeryd status

# print the log in the screen
#cat /var/log/celery/w1.log

redis-server --daemonize yes
/etc/init.d/celery_conf start
cat /var/log/celery/w1.log
