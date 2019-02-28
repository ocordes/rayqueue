FROM python:3.7-alpine

RUN adduser -D rayqueue

WORKDIR /home/rayqueue

COPY requirements.dat requirements.dat

RUN python -m venv venv
RUN venv/bin/pip install -r requirements.dat
RUN venv/bin/pip install gunicorn

COPY src src
COPY boot.sh .
RUN chmod +x boot.sh

RUN chown -R rayqueue:rayqueue ./
USER rayqueue

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
