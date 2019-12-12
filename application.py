# -*- coding: utf-8 -*-

import os

from ast import literal_eval
from flask import Flask, render_template, request, session, redirect
from flask_login import current_user, LoginManager, login_required,\
    login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from db import db, init_app, Game, User, Player, Die, ScoreItem, ScoreEntry

login_manager = LoginManager()
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()


def create_app(test_config=None):
    """Create and configure the app"""
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
        # Load the instance config, if it exists, when not testing.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Routes:

    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        """Play the game.

        POST: perform one of three three actions: roll the dice,
        go into SCORING stage, and enter a score. Redirect to this route.
        GET: render index.html
        """

        game = current_user.current_game

        if request.method == 'POST':
            if 'roll' in request.form:
                game.roll_dice(literal_eval(request.form['roll']))
            elif 'hold' in request.form:
                game.hold()
            elif 'score' in request.form:
                row_name = request.form['score']
                game.enter_score(ScoreItem.get_item_by_name(row_name))
            return redirect('/')

        else:
            return render_template('index.html', game=game)

    @app.route('/new', methods=['GET'])
    @login_required
    def new():
        """Start a new game.

        Create a new Game object, quit current game if any, start the game,
        and redirect to / route.
        """
        game = Game()
        player = Player(game=game, user=current_user, is_active=True, index=0)

        if current_user.has_current_game:
            current_user.current_player.quit()
        db.session.add(player)
        db.session.commit()
        game.start()
        return redirect('/')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Register a user.

        POST: register new user and redirect to / route.
        GET: render register.html
        """

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
        """ Login a user.

        POST: login user and redirect to / route.
        GET: render login.html
        """

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
        """ Logout current user.

        POST: Logout current user and redirect to /login route.
        GET: render login.html
        """

        logout_user()
        return redirect('/login')

    @app.route('/resign', methods=['GET'])
    @login_required
    def resign():
        """Resign from current game redirect to / route."""
        current_user.current_player.resign()
        if current_user.has_current_game:
            current_user.current_game.check_game_end()
        return redirect('/')

    @app.route('/pwdchange', methods=['GET', 'POST'])
    def change_password():
        """Change current user's password.

        POST: change current user's password and redirect to / route.
        GET: render pwdchange.html
        """

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
                current_user.change_password(new_password)
                db.session.commit()
                return redirect('/')

        else:
            return render_template('pwdchange.html')

    # FILTERS:
    @app.template_filter()
    def die_value(game, index=-1):
        """Return the face value of the die with index i in game.

        Keyword argument:
        index -- the index of the die

        """

        if game is None:
            return 6
        else:
            return game.get_die_value(index)

    @app.template_filter()
    def score_value(player, row_name=None):
        """Return the appropriate content for a cell in the score table.

        Keyword argument:
        row_name -- the name of the row. It can be 'username', 'total'
            the name of a category total or the name of a score item.

        If row_name is username, return the username of player.
        If it is a total, return that total for player, if it is a score item,
        return the value of the corresponding entry for player (None if the
        entry is not taken).
        If an invalid row name is passed, raise a ValueError.
        """

        score_entry = player.get_score_entry_by_name(row_name)

        if row_name == 'username':
            return player.user.username
        if row_name == 'upper_total':
            return player.upper_total
        if row_name == 'middle_total':
            return player.middle_total
        if row_name == 'lower_total':
            return player.lower_total
        if row_name == 'total':
            return player.total
        if row_name == 'bonus':
            return player.bonus
        if score_entry is not None:
            # Return an empty string if the score entry is available
            if score_entry.is_available:
                return ''
            # Otherwise return the value of the score entry for player.
            else:
                return score_entry.value

        # If this line is reached, score_entry is None, i.e.,
        # the row name is invalid.
        raise ValueError('Invalid row name.')

    @app.template_filter()
    def is_roll_button_disabled(game):
        """Return true if the roll button should be disabled.

        The roll button should be disabled if the current user is not in a
        game, if it is not the current user's turn, or if the game is not
        in the PLAYING stage.
        """
        return not is_current_user_playing(game)

    @app.template_filter()
    def is_hold_button_disabled(game):
        """Return true if the hold button should be disabled.

        The hold button should be disabled if the current user is not in
        a game, if it is not the current user's turn, if the game is in
        the SCORING stage, or if the user has not yet rolled the dice
        in this round.
        """
        return not has_current_user_rolled(game)

    @app.template_filter()
    def is_score_button_disabled(game, entry_name):
        """Return true if the score buttons should be disabled.

        The score buttons should be disabled if the current user is not in a
        game, if it is not the current user's turn, if the game is in the
        ROLLING stage, or if the corresponding score entry is unavailable.
        """

        return not is_current_player_active(game)\
            or not game.is_scoring\
            or not is_score_entry_available(game, entry_name)

    @app.template_filter()
    def is_die_button_disabled(game):
        """Return true if the die buttons should be disabled.

        The die buttons should be disabled if the current user is not in a
        game, if it is not the current user's turn, if the game is not in the
        ROLLING stage, or if the user has not yet rolled the dice in this
        round.
        """

        return not has_current_user_rolled(game)

    # HELPER METHODS:
    def is_score_entry_available(game, entry_name=None):
        # Return true if the score entry with given name is available
        # for current user.

        player = game.get_player(current_user_obj())
        score_entry = player.get_score_entry_by_name(entry_name)
        return score_entry.is_available

    def current_user_obj():
        # Unwrap current user from current_user proxy
        # This is necessary to make == comparisons work

        return current_user._get_current_object()

    def is_current_player_active(game):
        # Return true if the current user is the active player in game.

        player = game.get_player(current_user_obj())
        return player is not None and player.is_active

    def is_current_user_playing(game):
        # Return true if it is the current user's turn and the game is in the
        # PLAYING stage.

        return is_current_player_active(game) and game.is_playing

    def has_current_user_rolled(game):
        # Return true if it is the current user's turn, the game is in the
        # PLAYING stage, and the user has rolled the dice at least once in this
        # round.

        return is_current_user_playing(game) and game.dice_rolls > 0

    return app
