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

## steps to use tools-barebone

1. As shown below from _tools-barebone_ template (left side) we will develop a new tool 
_custom-tool_ (right side) to add in Materials Cloud.

![tools-barebone => custom-tool](https://github.com/materialscloud-org/tools-barebone/blob/master/webservice/static/img/tool_templates.png)

2. create a parent directory which will contain both _tools-barebone_ and _custom-tool_. 
For this example we will call it as _materialscloud-tools_. 

```
mkdir materialscloud-tools
cd materialscloud-tools
```

### 3. _custom-tool_ app:

3.1 Inside _materialscloud-tools_ create the directory structure as shown below 
for the _custom-tool_.

```
mkdir custom-tool
cd custom-tool

# create configuration file
touch config.yaml

# create user templates folder
mkdir user_templates
touch ack.html                              # add acknowledgement text here
touch about.html                            # add information about this tool here
touch how_to_site.html                      # add tool citation here
select_content: "additional_content.html"   # additional functionality if any else empty file

```

3.2 In _config.yaml_ file, we can add values for the keys used in tools-barebone. One such 
example file is shown below. 

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


### 4. _tools-barebone_ app:

4.1 Next step is to clone the _tool-barebone_ repository in _materialscloud-tools_.

```
cd materialscloud-tools
git clone https://github.com/materialscloud-org/tools-barebone
```

4.2 Install the requirements in _tools-barebone_.

```
cd tools-barebone
pip install -e -r requirements.txt
```

4.3 Update the file _run-example.sh_ to add the path for the _custom-tool_ directory as shown below.

```
vim run-example.sh 

# inside run-example.sh file update below line 
TOOLS_EXAMPLE_DIR="../custom-tools"
```

4.4 With above changes, basic layout for _custom-tool_ is ready and it can be run locally as:

```
./run-example.sh   # launch the server at http://127.0.0.1:5000
```


4.5 To build and launch the docker container for custom tool:
 
```
./build-docker.sh
./run-docker.sh     # launch the server at http://127.0.0.1:8090
 ```


## tools-example

Another example with additional REST API functionality using tools-barebone is available 
[here](https://github.com/materialscloud-org/tools-example).
