#!/bin/bash

export FLASK_APP=pistis
export FLASK_DEBUG=1

if [[ $# -eq "0" ]]; then
    flask run --host=0.0.0.0
fi

if [[ $1 == "shell" ]]; then
    flask shell
fi

if [[ $1 == "test" ]]; then
    flask test
fi
