# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_charts import GoogleCharts
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from flask_seeder import FlaskSeeder
from flask_session import Session  # https://pythonhosted.org/Flask-Session

import identity, identity.web

# Logging
import logging
from logging.handlers import RotatingFileHandler
import time

#----------------------------------------------------------------------
def create_rotating_log(path):
    """
    Creates a rotating log
    """
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    
    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=20,
                                  backupCount=5)
    logger.addHandler(handler)
    
    for i in range(10):
        logger.info("This is test log line %s" % i)
        time.sleep(1.5)
        
db = SQLAlchemy()
login_manager = LoginManager()
charts = GoogleCharts()
seeder = FlaskSeeder()
session = Session()


def register_extensions(app):
    db.init_app(app)
    seeder.init_app(app, db)
    login_manager.init_app(app)
    charts.init_app(app)
    session.init_app(app)
    
    auth = identity.web.Auth(
        session=session,
        authority=app.config.get("AUTHORITY"),
        client_id=app.config["CLIENT_ID"],
        client_credential=app.config["CLIENT_SECRET"],
    )
    


def register_blueprints(app):
    for module_name in ('authentication', 'msal', 'home', 'api'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


from apps.authentication.oauth import github_blueprint

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['JSON_AS_ASCII'] = False
    create_rotating_log('./app.log')
    app.app_context().push()
    register_extensions(app)
    register_blueprints(app)
    app.register_blueprint(github_blueprint, url_prefix="/login")    
    configure_database(app)
    
    return app
