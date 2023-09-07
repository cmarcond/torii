FROM python:3.9

USER root

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    wkhtmltopdf

ADD ./requirements.txt /
RUN pip install -r /requirements.txt
ADD . .

CMD uwsgi --enable-threads --ini uwsgi.ini