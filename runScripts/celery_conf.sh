# Name of nodes to start, here we have a single node
CELERYD_NODES="w1"

# Where to chdir at start.
CELERYD_CHDIR="/var/www/some_folder/Myproject/"

# Python interpreter from environment, if using virtualenv
ENV_PYTHON="/somewhere/.virtualenvs/MyProject/bin/python"

# How to call "manage.py celeryd_multi"
CELERYD_MULTI="$ENV_PYTHON $CELERYD_CHDIR/manage.py celeryd_multi"

# How to call "manage.py celeryctl"
CELERYCTL="$ENV_PYTHON $CELERYD_CHDIR/manage.py celeryctl"

# Extra arguments to celeryd
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# Name of the celery config module, don't change this.
CELERY_CONFIG_MODULE="celeryconfig"

# %n will be replaced with the nodename.
CELERYD_LOG_FILE="/var/log/celery/%n.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

# Workers should run as an unprivileged user.
CELERYD_USER="celery"
CELERYD_GROUP="celery"

# Set any other env vars here too!
PROJET_ENV="PRODUCTION"

# Name of the projects settings module.
# in this case is just settings and not the full path because it will change the dir to
# the project folder first.
export DJANGO_SETTINGS_MODULE="settings"