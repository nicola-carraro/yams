
import os
from flask import Flask, render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from db import db, init_app
from template import die_img, buttons, title, icon, UPPER_VALUES, SCORE_ENTRIES
from user import User






def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(app.instance_path, 'db.sqlite'),
    )

    app.jinja_env.filters['die_img'] = die_img
    app.jinja_env.filters['title'] = title
    app.jinja_env.filters['icon'] = icon

    init_app(app)

    db.init_app(app)

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

    @app.route('/', methods=["GET", "POST"])
    def index():

        if request.method == "POST":
            print(request.form.get("roll"))


        game = {}

        game["scores"] = [{"name": 'caiuz', "ones": 1, "twoes": 2, "threes": 3, "fours": 4, "fives": 6, "sixes": 7, "bonus": 8, "upper_total": 9, "max": 10, "min": 11, "middle_total": 12, "poker": 13, "full_house": 14, "small_straight": 15, "large_straight": 16, "yams": 17,
        "rigole": 18, "lower_total": 19, "global_total": 20}]
        game["dice"] = [1, 2, 3, 4, 5]
        game["buttons"] = buttons("play")
        game["stage"] = "play"
        game["in_progress"] = True

        return render_template("index.html", game=game, UPPER_VALUES=UPPER_VALUES, SCORE_ENTRIES=SCORE_ENTRIES)

    @app.route('/register', methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            repeat_password = request.form.get("repeat_password")

            #TODO: Add check for password correctness

            user = User(username, generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect("/login")

        else:
            session["user_name"] = None
            return render_template("register.html")

    @app.route('/login')
    def login():
        session["user_name"] = None
        return render_template("login.html")

    @app.route('/logout')
    def logout():
        session["user_name"] = None
        return redirect("/login")

    return app
