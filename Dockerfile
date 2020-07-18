FROM materialscloud/tools-barebone:20200124152746970e15

LABEL maintainer="Kevin Maik Jablonka <kevin.jablonka@epfl.ch>"

ADD ./.docker_files/apache-site.conf /etc/apache2/sites-available/app.conf
RUN a2enmod wsgi && a2enmod xsendfile && \
    a2dissite 000-default && a2ensite app 
    
RUN pip3 install --upgrade numpy==1.18.4 pymatgen==2019.7.2 
COPY ./webservice/ webservice
COPY ./oximachine/compute/requirements.txt /home/app/code/webservice
RUN pip3  install --upgrade --no-cache-dir -r /home/app/code/webservice/requirements.txt

COPY ./oximachine/compute /home/app/code/webservice/compute/

RUN chown -R app:app $HOME 