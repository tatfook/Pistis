FROM ubuntu:16.04
MAINTAINER DreamAndDead <favorofife@yeah.net>

EXPOSE 5000
VOLUME /app/store
WORKDIR /app

RUN apt update && apt install -y python3 python3-pip

COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install .

CMD [ "uwsgi", "--http", "0.0.0.0:5000", \
               "--manage-script-name", \
               "--mount", "/=pistis:app"]
