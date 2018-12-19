# tools-barebone

## A template for new tools on Materials Cloud

Use the tools-barebone Docker image to kickstart the development
of your tool for materialscloud.org/tools .

## Prerequisites

* [docker](https://www.docker.com/) >= v18.09

## Usage

Clone the tools-barebone repository and build the `tools-barebone` docker image:

```
git clone https://github.com/materialscloud-org/tools-barebone
cd tools-barebone
./build-docker.sh
```

Continue by adapting the [tools-example](https://github.com/materialscloud-org/tools-example) to your needs (see instructions there).
