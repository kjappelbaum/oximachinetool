# oxiMACHINE tools entry

[![Actions Status](https://github.com/kjappelbaum/oximachinetool/workflows/Docker%20Image%20Build%20CI/badge.svg)](https://github.com/kjappelbaum/oximachinetool/actions)
[![](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/download/releases/3.6.0/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<img src='oximachine_logo.png' width=200px, text-align=center> </img>

> ⚠️ **Warning**: Alpha version

Flask app that uses `jsmol` to visualize the structure (and predictions). The code builds heavily ontop of the implementation of the [seekpath web app](https://github.com/giovannipizzi/seekpath).

## How to run the code

You have to options to run the code: You can either clone the repository and directly run the flask app. 

### Directly run flask app
- clone the repository 

- copy `compute` and `user_templates` to `webservice`

- install the requirements listed in both `requirements.txt` files 

- python `run_app.py`

### Run docker image

- Build the docker image for the app based on the modified `tools-barebone` image (`docker build -t oximachine .`). You can use the `/build-docker.sh` scripts to do this. 
```
./build-docker.sh # to build the tools-barbone
cd oximachine
./build-docker.sh # to build the oximachine
```

- Run the image `docker run -p 8091:80 -it oximachine` (and go to
        `localhost:8091`)
- Then you can use it as shown in the screencast. 

![oximachine screencast]('_static/oximachine.gif')


## ToDo

- [ ] Add more examples

- [x] Add the colorcoding for the uncertainty

- [ ] Precompute feature vectors for example

- [ ] Add some explainability plots

- [ ] Couple details with structure

- [ ] Add plot of feature distribution in trainin set (e.g. violin plot) and the metal site as dots

- [ ] Potentially add a Explore section for the EDA

- [x] add a test for the container build


# Acknowledgment

- Materials Cloud team, especially [Leopold Talirz](https://github.com/ltalirz) for help with deployment and giving valuable feedback and providing a good template. 
