FROM python:3.7-alpine

# written by: Oliver Cordes 2019-03-01
# changed by: Oliver Cordes 2019-03-24

RUN adduser -D rayqueue

WORKDIR /home/rayqueue

COPY requirements.dat requirements.dat

# add graphics and sqlite
RUN apk --no-cache add libjpeg-turbo sqlite linux-headers

# add a build structure for python modules
RUN apk --no-cache add --virtual .build-dependencies zlib-dev jpeg-dev gcc libc-dev

RUN python -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.dat
RUN venv/bin/pip install --no-cache-dir gunicorn

# remove build structure
RUN apk del .build-dependencies

COPY src src
RUN rm -rf src/data/*
RUN rm src/logs/*
COPY boot.sh .
RUN chmod +x boot.sh

RUN chown -R rayqueue:rayqueue ./

# this is the default user
USER rayqueue

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
