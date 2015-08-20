from flask import Flask, url_for
from flask.ext.script import Manager, Command, Option
from lablog import config
from lablog.app import App
from lablog import db
import humongolus
import logging

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


manager.add_command('command', RunWorker())
manager.add_command('init_app', InitApplication())
#python manager.py command

if __name__ == "__main__":
    manager.run()
