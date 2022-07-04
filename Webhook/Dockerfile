# Start from the official Python base image.


FROM python:3.10-alpine

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add --update --no-cache curl py-pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN touch /var/log/cron.log

#
COPY ./ /code/

#
RUN (crontab -l | { cat; echo "0 10 * * * python telegramBot.py >> /var/log/cron.log"; } | crontab -)
CMD cron && tail -f /var/log/cron.log


CMD python3 webhook.py