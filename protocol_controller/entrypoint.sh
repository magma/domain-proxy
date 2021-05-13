#!/bin/bash

export FLASK_APP="wsgi:application"

flask run --host=0.0.0.0 --port=8080 || exit 1