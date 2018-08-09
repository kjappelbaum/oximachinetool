#!/bin/bash

TOOLS_EXAMPLE_DIR="../tools-example"

rm webservice/static/config.yaml
rm user_requirements.txt
rm -r webservice/templates/user_templates/*
rm -r webservice/compute/*
find webservice/user_static/ -type f ! -name '.gitignore' -delete

cp $TOOLS_EXAMPLE_DIR/config.yaml webservice/static/config.yaml
cp $TOOLS_EXAMPLE_DIR/user_requirements.txt user_requirements.txt
cp -r $TOOLS_EXAMPLE_DIR/user_templates/* webservice/templates/user_templates/
cp -r $TOOLS_EXAMPLE_DIR/user_static/* webservice/user_static/
cp -r $TOOLS_EXAMPLE_DIR/compute/* webservice/compute/

echo "Installing user requirements.."
pip install -r user_requirements.txt

echo "Running" $TOOLS_EXAMPLE_DIR "application.."
python webservice/run_app.py
