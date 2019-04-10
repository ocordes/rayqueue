#!/bin/sh

# this script is used to boot a Docker container

source venv/bin/activate
cd src
export FLASK_APP=rayqueue.py

# special settings for terminal
export TERMINAL_CMD="/bin/sh"

while true; do
	flask db upgrade
	if [[ "$?" == "0" ]]; then
	   break
	fi
	echo Deploy command failed, retrying in 5 secs...
	sleep 5
done

# flask commands
#exec flask run -h 0.0.0.0
#exec gunicorn -b :5000 --access-logfile - --error-logfile - rayqueue:app
exec gunicorn --worker-class eventlet -w 1 -b :5000 --access-logfile - --error-logfile - rayqueue:app
