FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y -qq git python-pip
RUN pip install shutit

WORKDIR /opt
RUN git clone https://github.com/ianmiell/shutit-library
WORKDIR /opt/shutit-library/wildfly
RUN shutit build --delivery dockerfile

CMD ["/bin/bash"] 
