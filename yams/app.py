
import os
from flask import Flask, render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from game import Game, User, Die, ScoreItem, ScoreEntry, GameStage
from db import db, init_app
from helpers import not_null


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(app.instance_path, 'db.sqlite'),
    )

    app.jinja_env.filters['not_null'] = not_null

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

    @app.route('/', methods=['GET', 'POST'])
    def index():

        if request.method == 'POST':
            #print(request.form.get('roll'))
            print(request.form.get('score-table'))

        else:
            user = User(username='Nicola', password_hash='password123')
            game = Game(current_player=user)

            game.stage =  GameStage.SCORING

            die_object=Die(game=game)
            score_entry = ScoreEntry(game=game, user=user, score_item=ScoreItem.ONE, value=4)
            db.session.add(user)
            db.session.add(game)
            db.session.add(die_object)
            db.session.add(score_entry)
            db.session.commit()
            game.players = [user]

        return render_template('index.html', game=game)




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
            user = User.query.filter_by(username=username).first()
            return redirect('/login')

        else:
            session['user_name'] = None
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

            session['user_name'] = username

            return redirect('/')



        else:
            session['user_name'] = None
            return render_template('login.html')

    @app.route('/logout')
    def logout():
        session['user_name'] = None
        return redirect('/login')

    return app
