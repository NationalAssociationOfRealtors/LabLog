from flask import Flask, url_for
from flask.ext.script import Manager, Command, Option
from lablog import config
from lablog.app import App
from lablog import db
import humongolus
import logging

logging.basicConfig(level=logging.INFO)
app = App()
manager = Manager(app)
MONGO = db.init_mongodb()
humongolus.settings(logging, MONGO)

class RunWorker(Command):

    def run(self):
        logging.info("command!")

class InitApplication(Command):

    def run(self):
        app.configure_dbs()
        from lablog.triggers.node import CO2
        try:
            c = CO2()
            c.name = 'notify slack c02'#unique
            c.key = 'node.co2'
            c.save()
            logging.info(c.key)
            logging.info(c.name)
        except Exception as e:
            logging.exception(e)


manager.add_command('command', RunWorker())
manager.add_command('init_app', InitApplication())
#python manager.py command

if __name__ == "__main__":
    manager.run()
