# tools-barebone

Tools-barebone is a framework implemented in Python using Flask framework. 
It can be used as an starting point to develop new tools for 
[Materials Cloud Tools section](https://www.materialscloud.org/work/tools/options).

It provides:

* Common layout used for every tool in Materials cloud
* Materials Cloud theme
* Common REST API endpoints
* Common widgets e.g. file upload functionality
* Web server settings
* Scripts to deploy tool in docker container

## Prerequisites

* [docker](https://www.docker.com/) >= v18.09

## How to use a tools-barebone framework

The _tools-barebone_ framework provides basic template to extend it further to develop 
a new tool for Materials Cloud. Here we will explain how the _tools-barebone_ template (shown
at left side) can be extended to develop a new tool called _custom-tool_ (shown at
right side).

![tools-barebone => custom-tool](https://github.com/materialscloud-org/tools-barebone/blob/master/webservice/static/img/tool_templates.png)

#### 1. create a parent directory which will contain both _tools-barebone_ and _custom-tool_ directories. 

For this example we will call it as _materialscloud-tools_. 

```
mkdir materialscloud-tools
cd materialscloud-tools
```


#### 2. _tools-barebone_ framework

Lets clone the _tools-barebone_ repository to extend it further in _materialscloud-tools_ directory.

```
cd materialscloud-tools
git clone https://github.com/materialscloud-org/tools-barebone
```

In _tools-barebone_ _SECRET KEY_ is used to handle data in session. _SECTRE KEY_ is a 
randomly generated string used as a key to encrypt cookies before sending them to browser. Create 
the file called _SECRET_KEY_ in the folder _tools-barebone/webservice_ containing a random
string of at least 16 characters. Also change the permissions of the _SECRET_KEY_ file to 600.
For example:

```
echo "sakjfdjfjdfhsdbfsfbsbdlbfsd,lbgsfbgbskjgkjs" > webservice/SECRET_KEY
chmod 600 webservice/SECRET_KEY
```

_tools-barebone_ can be used either locally or in docker. There are shell scripts provided 
to build the docker, to run it, to get the apache log from running docker container, etc.

For example to build the docker:

```
cd tools-barebone
./build-docker.sh
```


To run _tools-barebone_ framework locally, one needs to install all the dependencies provided 
in _requirements.txt_ file. Run below command to install the _tools-barebone_ dependencies using pip:

```
cd tools-barebone
pip install -r requirements.txt
```

Once your app _custom-tool_ is ready, update its path in _run-example.sh_ file as shown below.

```
vim run-example.sh

# inside run-example.sh file update below line
TOOLS_EXAMPLE_DIR="../custom-tools"
```

Now you can run your app locally by running the _run-example.sh_ script. The script copies the files from
_custom-tool_ app to the _tools-barebone_ framework in predefined places and runs the app 
at http://localhost:5000.

```
./run-example.sh   # launch the server at http://127.0.0.1:5000
```


### 3. New tool: _custom-tool_

To write new tool called _custom-tool_, create new directory "_custom-tool_" inside 
_materialscloud-tools_ folder. We will first create the minimum set of files required
in this new tool as shown below.

```
mkdir custom-tool
cd custom-tool

# create configuration file
touch config.yaml

# create Dockerfile file
touch Dockerfile

# create user templates folder
mkdir user_templates
cd user_templates
touch ack.html                              # add acknowledgement text here
touch about.html                            # add information about this tool here
touch how_to_cite.html                      # add tool citation here
touch additional_content.html               # additional functionality if any otherwise empty file

```

The _config.yaml_ file contains the configuration details used in this new tool like window title, 
page title, list of html templates, etc. Update the _config.yaml_ file and add html templates 
for about the tool, tool citation text and acknowledgements. 

Below example shows the snippet of _config.yaml_ file. 

```
window_title: "Materials Cloud Tools: an example app"
page_title: "A simple tool example"

about_section_title: "About new tool"

templates:
  how_to_cite: "how_to_cite.html"
  about: "custom_about.html"

use_upload_structure_block: True

additional_accordion_entries:
  - header: "What is this?"
    template_page: what_is.html
  - header: "Acknowledgements"
    template_page: ack.html

```

Once the files are ready, we can write _Dockerfile_ extended from _tools-barebone_
to build and run the docker container for _custom-tool_. Below snippet shows the minimum required
_Dockerfile_ file for _custom-tool_. The _custom-tools_ specific commands with be added after this part.
 
```
FROM tools-barebone

MAINTAINER developers_name <developers_email>

COPY ./config.yaml /home/app/code/webservice/static/config.yaml
COPY ./user_templates/* /home/app/code/webservice/templates/user_templates/
COPY ./compute/ /home/app/code/webservice/compute/

# Set proper permissions
RUN chown -R app:app $HOME

#### Add custom-tools
```

The _custom-tool_ container can be build and run using below commands. It will start the web 
server at http://127.0.0.1:8091

```
# To build container
docker build -t custom-tools
  
# To launch container
docker run -p 8091:80 --rm --name=custom-tools-instance custom-tools  
```

## tools-example

Another example with additional REST API functionality using tools-barebone is available 
[here](https://github.com/materialscloud-org/tools-example).
