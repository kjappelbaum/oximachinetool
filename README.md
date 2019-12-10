# oxiMACHINE tools entry

> ⚠️ **Warning**: Alpha version

Flask app that uses `jsmol` to visualize the structure (and predictions).

## Directly run flask app

- copy `compute` and `user_templates` to `webservice`
- install both `requirements.txt`
- python `run_app.py`

## Run docker image

- Build the docker image for the app based on the modified `tools-barebone` image (`docker build -t oximachine .`). Note that

  - you need to use ubuntu 16.04 version in the `tools-barebone`, otherwise there are some issues with Apache
  - and run everything python related with `python3.6` (or higher) as the ML tools do not work with older python versions.

- Run the image `docker run -p 8091:80 -it oximachine`
