# Vestivise

##Requisites

Python version 2.7.11

1. Have NodeJS installed onto your local machine
   * Install webpack globally
   * npm install webpack -g
2. Have python 2.0 installed
3. Clone "development" repo
4. In root directory Vestivise/ install virtual environment
   * pip install virtualenv
   * link for info - http://docs.python-guide.org/en/latest/dev/virtualenvs/
   * enter your virtual environment - source "virtual env name"/bin/activate
5. In root directory while in virtual env run pip install -r requirements.txt

##Development

1. Enter virtual env
2. Open one terminal window
   * In root of directory enter staticfiles/src and run webpack -w
3. Open another terminal window
   * If fresh pull run python manage.py makemigrations and python manage.py migrate
   * In root directory run python manage.py runserver
4. Ask Ray for django keys :)

###Project Structure

staticfiles/src/ - javascript files that will bundle into single script for production
staticfiles/build/css - css files
templates/ - html files to be served by django


##Production

do 'sudo chmod -R 777 /var/log' for logging
