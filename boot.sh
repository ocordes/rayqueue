#!/bin/sh

# this script is used to boot a Docker container

source venv/bin/activate
while true; do
	flask db upgrade
	if [[ "$?" == "0" ]]; then
	   break
	fi
	echo Deploy command failed, retrying in 5 secs...
	sleep 5
done

# flask commands
export FLASK_APP=rayqueue.py
exec flask run
