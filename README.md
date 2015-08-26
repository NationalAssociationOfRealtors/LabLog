# LabLog

This is the application that provides the backend services for CRTLabs infrastructure.

* LDAP/AD based login
* OAuth2 token flow for application authorization
* MQTT Server for sensor data pub/sub
* InfluxDB for time-series data
* NGINX for https/http proxy
* Websocket server for applications (OAuth2 enabled)
* REST API for application data
* Docker based deployment [Docker](https://docs.docker.com/) ;)

## Installation

install [Docker](https://docs.docker.com/)

install docker-compose, not in a virtualenv, it needs sudo to talk to Docker (If you know how to give sudo access to a module installed in virtualenv, I would love to hear it)

    sudo pip install docker-compose

in order to startup NGINX you'll need to put your certs in config/nginx directory

you'll also want to copy the default.env file to .env and fill in the variables with your information.

LDAP based registration/authentication can be disabled in loglab/config.py

from within the base directory of LabLog run

    sudo docker-compose up

grab some coffee... it's going to download a few hundred MB of image files, but everything should be working when you get back...

assuming everything ran ok, you should be able to see some log files in syslog. Have fun!
