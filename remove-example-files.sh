#!/bin/bash

TOOLS_EXAMPLE_DIR="../tools-example"

rm webservice/static/config.yaml
rm user_requirements.txt
rm -r webservice/templates/user_templates/*
rm -r webservice/compute/*
find webservice/user_static/ -type f ! -name '.gitignore' -delete