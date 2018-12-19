# tools-barebone

## A template for new tools on Materials Cloud

Use the tools-barebone Docker image to kickstart the development
of your tool for materialscloud.org/tools .

## Prerequisites

* [docker](https://www.docker.com/) >= v18.09

## Usage

 1. Clone the tools-barebone repository and build the `tools-barebone` docker image:
    ```
    git clone https://github.com/materialscloud-org/tools-barebone
    cd tools-barebone
    ./build-docker.sh
    ```
 1. Fork the [tools-example](https://github.com/materialscloud-org/tools-example) repository and rename it
    ```
    git clone https://github.com/materialscloud-org/tools-example
    mv tools-example my-tool  # also rename on github!
    cd my-tool
    ./build-docker.sh   # build the tools-example docker image
    ```
 1. Running the example app:
    * `./run-docker.sh` and open open http://localhost:8091 to check the web interface
    * `./enter-docker.sh` to get a shell on the container
   
 1. Start editing the example to fit your needs

   * `config.yml`
   * `user_templates` folder
   * ...
