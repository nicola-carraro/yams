#!/usr/lib/python3

import os
from flask import Flask, render_template, request, session
from helpers import SCORE_ENTRIES
from ui import ui
from flask_session import Session
from state import State
import jsonpickle




app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

@app.route('/')
def index():
    state = State()
    return render_template("index.html", ui=ui(state))

if __name__ == "__main__":

    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)
