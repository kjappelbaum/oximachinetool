# oxiMACHINE tools entry

[![Actions Status](https://github.com/kjappelbaum/oximachinetool/workflows/Docker%20Image%20Build%20CI/badge.svg)](https://github.com/kjappelbaum/oximachinetool/actions)

<img src='oximachine_logo.png' width=200px, text-align=center> </img>

> ⚠️ **Warning**: Alpha version

Flask app that uses `jsmol` to visualize the structure (and predictions). The code builts heavily ontop of the implementation of the [seekpath web app](https://github.com/giovannipizzi/seekpath).

## Directly run flask app

- copy `compute` and `user_templates` to `webservice`

- install both `requirements.txt`

- python `run_app.py`

## Run docker image

- Build the docker image for the app based on the modified `tools-barebone` image (`docker build -t oximachine .`). Note that

  - Note that the ML packages are actually built for `python>=3.6`. In this flask app, we use `python==3.5` wherefore you might run into some issues (e.g., due to f strings)

    <!-- - you need to use ubuntu 16.04 version in the `tools-barebone`, otherwise there are some issues with Apache
    - note that `libapache2-mod-wsgi-py3` is compiled with the wrong python version (3.5), we install it with pip for this reason -->

  - and run everything python related with `python3.6` (or higher) as the ML tools do not work with older python versions.

- Run the image `docker run -p 8091:80 -it oximachine` (and go to
        `localhost:8091`)

```
./build-docker.sh # to build the tools-barbone
cd oximachine
./build-docker.sh # to build the oximachine
```

## ToDo

- [ ] Add more examples

- [x] Add the colorcoding for the uncertainty

- [ ] Precompute feature vectors for example

- [ ] Add some explainability plots

- [ ] Couple details with structure

- [ ] Add plot of feature distribution in trainin set (e.g. violin plot) and the metal site as dots

- [ ] Potentially add a Explore section for the EDA

- [ ] add a test for the container build
