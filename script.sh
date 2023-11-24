#!/bin/bash

############## CHANGE HERE ################
FORUM_COOKIES_VALUE="YOUR FORUM COOKIES HERE"
###########################################

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Creating Python environment."
python3 -m venv venv
source venv/bin/activate

echo "Installing the required packages. This might take a while."
pip3 install -q -r src/requirements.txt

export FORUM_COOKIES=$FORUM_COOKIES_VALUE
echo "Running the script. This might also take a while."
python3 src/main.py

deactivate
