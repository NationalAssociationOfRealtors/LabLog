FROM ubuntu:14.04
RUN apt-get update && apt-get install -y python-dev python-pip build-essential git libldap2-dev libsasl2-dev libsmi2-dev libffi-dev
ADD . /app
ADD ./config /config
WORKDIR /app
RUN pip install -r requirements.txt
