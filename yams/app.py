import os
from flask import Flask, render_template, request, session
from flask_login import LoginManager
from flask_session import Session
from game import Game
from db import db, test
from template import die_img, buttons, title, icon, UPPER_VALUES, SCORE_ENTRIES
from user import User
import jsonpickle



app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI = "sqlite:" + os.path.join(app.instance_path, 'yams.sqlite')
    )


#ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

login_manager = LoginManager()

db.init_app(app)

app.jinja_env.filters['die_img'] = die_img
app.jinja_env.filters['title'] = title
app.jinja_env.filters['icon'] = icon
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    game = {}
    game["scores"] = [{"name": "caiuz", "ones": 1, "twoes": 2, "threes": 3, "fours": 4, "fives": 6, "sixes": 7, "bonus": 8, "upper_total": 9, "max": 10, "min": 11, "middle_total": 12, "poker": 13, "full_house": 14, "small_straight": 15, "large_straight": 16, "yams": 17,
        "rigole": 18, "lower_total": 19, "global_total": 20}]
    game["dice"] = [1, 2, 3, 4, 5]
    game["buttons"] = buttons("play")
    return render_template("index.html", game=game, UPPER_VALUES=UPPER_VALUES, SCORE_ENTRIES=SCORE_ENTRIES)
