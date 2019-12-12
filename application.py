# -*- coding: utf-8 -*-

from ast import literal_eval
import os
from flask import Flask, render_template, request, session, redirect
from flask_login import current_user, LoginManager, login_required,\
    login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from db import db, init_app, Game, User, Player, Die, ScoreItem, ScoreEntry,\
    GameStage

login_manager = LoginManager()
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    try:
        app.config.from_mapping(
            SECRET_KEY=os.environ['SECRET_KEY'],
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URL'],
            )
    except KeyError:
        pass

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

    #app.jinja_env.filters['not_none'] = not_none
    # app.jinja_env.filters['die_value'] = die_value
    # app.jinja_env.filters['score_value'] = score_value
    # #app.jinja_env.filters['is_score_entry_taken'] = is_score_entry_taken
    # app.jinja_env.filters['is_roll_button_disabled'] = is_roll_button_disabled
    # app.jinja_env.filters['is_score_button_disabled'] = is_score_button_disabled
    # app.jinja_env.filters['is_die_button_disabled'] = is_die_button_disabled
    # app.jinja_env.filters['is_hold_button_disabled'] = is_hold_button_disabled

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

        game = current_user.current_game

        if request.method == 'POST':
            if 'roll' in request.form:
                game.roll_dice(literal_eval(request.form['roll']))
            elif 'hold' in request.form:
                game.hold()
            elif 'score' in request.form:
                score_item_name = request.form['score']
                game.enter_score(ScoreItem.get_item_by_name(score_item_name))
            return redirect('/')

        else:
            return render_template('index.html', game=game)

    @app.route('/new', methods=['GET'])
    @login_required
    def new():
        if current_user.has_current_game:
            current_user.current_player.quit()
        game = Game()
        player = Player(game=game, user=current_user, is_active=True, index=0)
        db.session.add(player)
        db.session.commit()
        game.start()
        return redirect('/')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            repeat_password = request.form.get('repeat-password')
            user_error = 'Ce nom d\'utilisateur est déjà pris'
            password_error = 'Les mots de passe ne correspondent pas'
            user = None

            if not password == repeat_password:
                return render_template('/register.html',
                                       password_error=password_error)

            if not len(User.query.filter_by(username=username).all()) == 0:
                return render_template('/register.html',
                                       user_error=user_error)

            user = User(username=username,
                        password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/')

        else:
            logout_user()
            return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            error = 'Faux nom d\'utilisateur ou mot de passe'
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()

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

    @app.route('/resign', methods=['GET'])
    @login_required
    def resign():
        current_user.current_player.resign()
        if current_user.has_current_game:
            current_user.current_game.check_game_end()
        return redirect('/')

    @app.route('/pwdchange', methods=['GET', 'POST'])
    def change_password():
        if request.method == 'POST':
            old_password = request.form.get('old-password')
            new_password = request.form.get('new-password')
            repeat_password = request.form.get('repeat-password')
            password_hash = current_user.password_hash
            old_password_error = 'Ancient mot de passe incorrect'
            repeat_error = 'Les mots de passe ne correspondent pas'

            if not check_password_hash(password_hash, old_password):
                return render_template('pwdchange.html',
                                       old_password_error=old_password_error)
            elif not request.form.get('new-password') == repeat_password:
                return render_template('pwdchange.html',
                                       repeat_error=repeat_error)
            else:
                current_user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                return redirect('/')

        else:
            return render_template('pwdchange.html')

    @app.template_filter()
    def die_value(game, index=-1):
        if game == None:
            return 6;
        else:
            return game.get_die_value(index)

    @app.template_filter()
    def score_value(player, score_item_name):
        if score_item_name == 'name':
            return player.user.username
        if score_item_name == 'upper_total':
            return player.upper_total
        if score_item_name == 'middle_total':
            return player.middle_total
        if score_item_name == 'lower_total':
            return player.lower_total
        if score_item_name == 'total':
            return player.total
        if score_item_name == 'bonus':
            return player.bonus

        score_entry = player.get_score_entry_by_name(score_item_name)
        if score_entry.value == None:
            return ''
        else:
            return score_entry.value

    @app.template_filter()
    def is_play_button_disabled(game):
        if not is_current_user_playing(game):
            return True
        return False

    @app.template_filter()
    def is_roll_button_disabled(game):
        if not is_current_user_playing(game):
            return True
        return False

    @app.template_filter()
    def is_hold_button_disabled(game):
        print('has_current_user_rolled: %s' % has_current_user_rolled(game))
        if not has_current_user_rolled(game):
            return True
        return False

    @app.template_filter()
    def is_score_button_disabled(game, entry_name):
        if not is_current_player_active(game):
            return True
        if not game.is_scoring:
            return True
        if is_score_entry_taken(game, entry_name):
            return True
        return False

    @app.template_filter()
    def is_die_button_disabled(game):
        if not has_current_user_rolled(game):
            return True
        return False

    def is_score_entry_taken(game, entry_name=None):
        player = game.get_player(current_user_obj())
        score_entry = player.get_score_entry_by_name(entry_name)
        return score_entry.value != None

    # Unwraps current user from current_user proxy
    def current_user_obj():
        return current_user._get_current_object()

    def is_current_player_active(game):
        if game == None:
            return False
        player = game.get_player(current_user_obj())
        return player.is_active

    def is_current_user_playing(game):
        if not is_current_player_active(game):
            return False
        if game.is_playing:
            return True
        else:
            return False

    def has_current_user_rolled(game):
        return is_current_user_playing(game) and game.dice_rolls > 0


    return app
