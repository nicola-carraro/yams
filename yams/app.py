# -*- coding: utf-8 -*-

from ast import literal_eval
import os
from flask import Flask, render_template, request, session, redirect
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from db import db, init_app, Game, User, Die, ScoreItem, ScoreEntry, GameStage
from db import not_none

login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(app.instance_path, 'db.sqlite'),
    )

    app.jinja_env.filters['not_none'] = not_none

    init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

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

    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def index():


        if current_user.current_game != None:
            game = current_user.current_game

        else:
            game = Game(current_player=current_user, players=[current_user])
        #
        # print ('is current player: %s' % (current_user.id == game.current_player.id))
        # print('stage: %s' % game.stage)


        if request.method == 'POST':
            if 'roll' in request.form:
                game.roll_dice(literal_eval(request.form['roll']))
            elif 'hold' in request.form:
                game.hold()
            elif 'score' in request.form:
                game.enter_score(ScoreItem.get_item_by_name(request.form['score']))


        return render_template('index.html', game=game)

    @app.route('/new', methods=['GET'])
    @login_required
    def new():
        game = Game(current_player=current_user, players=[current_user])
        game.start()
        db.session.add(game)
        db.session.commit()
        return redirect('/')



    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            repeat_password = request.form.get('repeat_password')

            if not password == repeat_password:
                return render_template('/register.html', password_error='Les mots de passe ne correspondent pas')

            if not len(User.query.filter_by(username=username).all()) == 0:
                return render_template('/register.html', user_error='Ce nom d\'utilisateur est déjà pris')



            user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect('/login')

        else:
            logout_user()
            return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            error = 'Faux nom d\'utilisateur ou mot de passe'
            username = request.form.get('username')
            password = request.form.get('password')
            users = User.query.filter_by(username=username).all()

            if not len(users) == 1:
                return render_template('login.html', error=error)

            user = users[0]

            if not check_password_hash(user.password_hash, password):
                return render_template('login.html', error=error)

            login_user(user)


            return redirect('/')



        else:
            return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect('/login')

    return app
