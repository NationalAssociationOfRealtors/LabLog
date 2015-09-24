from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch import TransportError
from kombu import Connection
from lablog import config
from lablog import user_mapping
from lablog import influx
from lablog import celeryconfig
import influxdb
import gevent
import logging

def init_elasticsearch():
    es_connected = False
    while not es_connected:
        try:
            ES = Elasticsearch(
                hosts=config.ES_HOSTS,
                sniff_on_start=True,
                sniff_on_connection_fail=True,
                sniffer_timeout=60
            )
            es_connected = True
            logging.debug(ES)
        except TransportError as e:
            logging.info("Elasticsearch not connected")
            logging.error(e)
            gevent.sleep(1)
    return ES

def init_mongodb():
    mongo_connected = False
    while not mongo_connected:
        try:
            MONGO = MongoClient(config.MONGO_HOST, config.MONGO_PORT, use_greenlets=True, max_pool_size=10)
            mongo_connected = True
        except Exception as e:
            logging.info("MongoDB not connected")
            logging.error(e)
            gevent.sleep(1)

    return MONGO

def init_influxdb():
    influx_connected = False
    while not influx_connected:
        try:
            INFLUX = influxdb.InfluxDBClient(
                config.INFLUX_HOST,
                config.INFLUX_PORT,
                config.INFLUX_USER,
                config.INFLUX_PASSWORD,
                config.INFLUX_DATABASE,
            )
            influx_connected = True
        except Exception as e:
            logging.info("Influxdb not connected")
            logging.error(e)
            gevent.sleep(1)

    return INFLUX

def init_mq():
    return Connection(celeryconfig.BROKER_URL)

def create_index(ES):
    exists = ES.indices.exists(config.ES_INDEX)
    logging.info("Exists: {}".format(exists))
    if not exists:
        ES.indices.create(
            index=config.ES_INDEX,
            body = {
                "settings":user_mapping.SETTINGS,
                "mappings":{
                    "user":{
                        "_source":{"enabled":True},
                        "properties":user_mapping.USER
                    }
                }
            }
        )
    return

def create_shards(INFLUX):
    logging.info("Creating Influxdb database, retention policies and continuous queries")
    try:
        res = INFLUX.create_database(config.INFLUX_DATABASE)
    except Exception as e:
        logging.error(e)

    try:
        for policy in influx.POLICIES:
            INFLUX.create_retention_policy(
                policy['name'],
                policy['duration'],
                policy['replication'],
                database=config.INFLUX_DATABASE,
                default=policy['default']
            )
        for cq in influx.QUERIES:
            for measurement in influx.MEASUREMENTS:
                query = cq['query'].format(**{"database":config.INFLUX_DATABASE, "measurement":measurement})
                q = "CREATE CONTINUOUS QUERY \"{}\" ON {} BEGIN {} END".format(cq['name'].format(**{'measurement':measurement}), config.INFLUX_DATABASE, query)
                INFLUX.query(q)
    except Exception as e:
        logging.exception(e)
