# LabLog,  Rosetta Home

This is the application that provides the backend services for CRTLabs infrastructure.

* LDAP/AD based login
* OAuth2 token flow for application authorization
* MQTT Server for sensor data pub/sub
* InfluxDB for time-series data
* NGINX for https/http proxy
* Websocket server for applications (OAuth2 enabled)
* REST API for application data
* Docker based deployment [Docker](https://docs.docker.com/) 

### Prerequisites:
* [Docker Toolbox] (https://www.docker.com/products/overview#/docker_toolbox)
* [Rosetta Home Back End Services](https://github.com/NationalAssociationOfRealtors/RosettaHomeServices)


### Configuration:
#### Nginx

* [Create self signed certificate and key](https://www.digitalocean.com/community/tutorials/how-to-create-an-ssl-certificate-on-nginx-for-ubuntu-14-04) and copy them to nginx/config directory

#### Environment Variables

* Copy the default.env file to .env and fill in the variables with your own information. 

#### User Accounts / Authentication

* LDAP based registration/authentication can be enabled or disabled in loglab/config.py

* If LDAP disabled, you need to create your users by navigating to the account registration page after the project is running.

```
https://<ip-address-of-virtual-machine>/auth/register
https://<ip-address-of-virtual-machine>/auth/login
```

### Launching Rosetta Home:


1. First start your [Rosetta Home Back End Services](https://github.com/NationalAssociationOfRealtors/RosettaHomeServices) 
2. Open Terminal and run the following commands, making sure to choose the correct configuration file depending on your operating system.

```
$ docker-compose -f docker-compose-macOS.yml up
```

### Creating your first location


To create your first location, navigate to the following location and fill out the form. If you do not have MLS information, you will need to make some changes to [property template](https://github.com/NationalAssociationOfRealtors/LabLog/blob/master/lablog/views/templates/locations/property.html) to remove MLS references so the pages can still be dislayed.

`https://<ip-address-of-virtual-machine>/location`


### Tips/Troubleshooting on macOS:

* To get the IP address of your docker vm machine:
 
`$ docker-machine ip default`

* Scheduler Fails to start: ERROR: Pidfile

`$ rm celerybeat.pid`

* ERROR: Couldn't connect to Docker daemon 

`$ eval "$(docker-machine env default)`


License
----

MIT
