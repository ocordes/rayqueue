FROM python:3.7-alpine

# written by: Oliver Cordes 2019-03-01
# changed by: Oliver Cordes 2019-03-24

RUN adduser -D rayqueue

WORKDIR /home/rayqueue

COPY requirements.dat requirements.dat


# add a build structure
RUN apk add --virtual .build-dependencies zlib-dev jpeg-dev gcc libc-dev

RUN python -m venv venv
RUN venv/bin/pip install -r requirements.dat
RUN venv/bin/pip install gunicorn

# remove build structure
RUN apk del .build-dependencies

COPY src src
RUN rm src/data/app.db
RUN rm src/logs/*
COPY boot.sh .
RUN chmod +x boot.sh

RUN chown -R rayqueue:rayqueue ./

# this is the default user
USER rayqueue

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
