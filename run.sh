#!/bin/bash


export FLASK_APP=pistis

EXE_ROOT=/home/zdw/project/Pistis
pushd $EXE_ROOT || exit


export PISTIS_ENV=DEBUG
export FLASK_DEBUG=1
if [[ $1 == "debug" ]]; then
    flask run --host='0.0.0.0'
fi
unset FLASK_DEBUG

if [[ $1 == "shell" ]]; then
    flask shell
fi

export PISTIS_ENV=TEST
if [[ $1 == "test" ]]; then
    flask test
fi

export PISTIS_ENV=PROD
if [[ $1 == "profile" ]]; then
    python app_profiler.py
fi

if [[ $1 == "freeze" ]]; then
    pip freeze | sed -e '/-e git/d' > requirements.txt
fi

popd
