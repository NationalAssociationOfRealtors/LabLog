FROM ubuntu:14.04
RUN apt-get -y update
RUN sudo apt-get -y install python-dev python-pip build-essential git
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
