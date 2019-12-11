FROM tools-barebone

MAINTAINER Kevin Maik Jablonka <kevin.jablonka@epfl.ch>

RUN python3.6 -m pip install --upgrade numpy
COPY ./compute/requirements.txt /home/app/code/webservice
RUN python3.6 -m pip  install -r /home/app/code/webservice/requirements.txt

COPY ./config.yaml /home/app/code/webservice/static/config.yaml
COPY ./user_templates/* /home/app/code/webservice/templates/user_templates/
COPY ./compute/ /home/app/code/webservice/compute/


RUN chown -R app:app $HOME
CMD python3.6 webservice/run_app.py
