#!/bin/bash


export FLASK_APP=pistis
export FLASK_DEBUG=1

EXE_ROOT=/home/zdw/project/Pistis
pushd $EXE_ROOT || exit


export PISTIS_SETTINGS=config/debug.cfg
if [[ $# -eq "0" ]]; then
    flask run --host='0.0.0.0'
fi

if [[ $1 == "shell" ]]; then
    flask shell
fi
unset PISTIS_SETTINGS

export PISTIS_SETTINGS=config/test.cfg
if [[ $1 == "test" ]]; then
    flask test
fi
unset PISTIS_SETTINGS


if [[ $1 == "freeze" ]]; then
    pip freeze | sed -e '/-e git/d' > requirements.txt
fi

popd
