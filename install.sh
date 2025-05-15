#!/bin/bash

if ! [ -d /venv ]; then
    virtualenv venv
fi

source venv/bin/activate

pip install pillow
pip install Flask
pip install Werkzeug

