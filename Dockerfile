FROM materialscloud/tools-barebone:20200124152746970e15

MAINTAINER Kevin Maik Jablonka <kevin.jablonka@epfl.ch>

RUN pip3 install --upgrade numpy==1.17.2
COPY ./webservice/ webservice
COPY ./oximachine/compute/requirements.txt /home/app/code/webservice
RUN pip3  install -r /home/app/code/webservice/requirements.txt

COPY ./oximachine/compute /home/app/code/webservice/compute/
COPY ./oximachine/config.yaml /home/app/code/webservice/static/config.yaml
COPY ./oximachine/user_templates/* /home/app/code/webservice/templates/user_templates/

RUN chown -R app:app $HOME