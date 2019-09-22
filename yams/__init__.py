import os
from flask import Flask, render_template, request, session
from flask_login import LoginManager
from flask_session import Session
from .game import Game
from .db import test
from .ui import ui
import jsonpickle


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'yams.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    login_manager = LoginManager()

    from . import db
    db.init_app(app)

    @app.route('/')
    def index():
        return render_template("index.html", ui=ui(state))

    return app
