FROM ubuntu
MAINTAINER DreamAndDead <favorofife@yeah.net>

MKDIR /app
ADD . /app
WORKDIR /app

RUN apt update && apt install -y python3 python3-pip && pip3 install virtualenv \
    && virtualenv -p python3 .venv && source .venv/bin/activate \
    && pip install -r requirements.txt

CMD ["uwsgi --http :9090 --virtualenv=.venv --manage-script-name --mount /=pistis:app"]