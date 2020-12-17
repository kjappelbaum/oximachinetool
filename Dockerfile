FROM materialscloud/tools-barebone:1.1.0

LABEL maintainer="Kevin Maik Jablonka <kevin.jablonka@epfl.ch>"

ADD ./.docker_files/apache-site.conf /etc/apache2/sites-available/app.conf
RUN a2enmod wsgi && a2enmod xsendfile && \
    a2dissite 000-default && a2ensite app

COPY ./webservice/ webservice
RUN pip3 install --upgrade --no-cache-dir -r /home/app/code/webservice/requirements.txt

USER root
RUN /bin/bash -c 'echo -e "from oximachinerunner import OximachineRunner\nrunner=OximachineRunner(\"mof\")" | python3'

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN chown -R app:app $HOME
