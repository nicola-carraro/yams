"""Defines the database models and two enums used mainly in them.

This exports:
    - ScoreItem: an enumeration of the valid combinations that can be entered
    in the score.
    - Score_Item_Category: an enumeration of three categories, each associated
    with a group of score items.
    - Game_Stage: an enumeration of the stages of the game.
    - User: models a user of the application.
    - Game: models a game of yam's.
    - Player: relates users with the games they are playing.
    - Die: a die used within the game.
    - Score Entry: an entry in player's score.
"""

from enum import Enum, IntEnum, auto
from random import randint
from flask import g, session
from flask.cli import with_appcontext
from flask_login import current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from magic_repr import make_repr
from werkzeug.security import generate_password_hash
import click

# The connection with the database.
db = SQLAlchemy()


def _is_straight(sequence):
    # Takes an iterable  of numbers, returns True  only if each number in the
    # iterable is the successor of the previous one.
    for i in range(0, len(sequence) - 1):
        if sequence[i] != (sequence[i + 1] - 1):
            return False
    return True


def init_db():
    """Drop existing tables and create new ones"""
    db.drop_all()
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register the init_db_command with the app."""
    app.cli.add_command(init_db_command)


class ScoreItemCategory(Enum):
    """An enumaration of three categories of score items.

    Each category corresponds to a section of the score table with its own
    subtotal.
    """

    UPPER = auto()
    MIDDLE = auto()
    LOWER = auto()

    @property
    def subtotal_name(self):
        """Return a string representing this category's subtotal."""
        return '%s_subtotal' % self._name_.lower()


class ScoreItem(IntEnum):
    """An enumeration of the combination in the score.

    Each ScoreItem is associated with a name (string representation), and a
    ScoreItemCategory.
    """

    def __new__(cls, value, category):
        # Creates a score item with the given integer value and category.
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.category = category
        return obj

    @property
    def name(self):
        """Return the name of the score item."""
        return self._name_.lower()

    @classmethod
    def get_names(cls):
        """Return the list of names of all score items."""
        return [item.name for item in cls]

    @classmethod
    def get_item_by_name(cls, name):
        """Return the score item with the given name"""
        for item in cls:
            if item.name == name:
                return item
        return None

    @classmethod
    def get_items_by_category(cls, category):
        """Return a list of the score items in this category."""
        return [item for item in cls if item.category == category]

    @classmethod
    def upper_items(cls):
        """Return a list of the score items in the UPPER category."""
        return cls.get_items_by_category(ScoreItemCategory.UPPER)

    @classmethod
    def middle_items(cls):
        """Return a list of the score items in the MIDDLE category."""
        return cls.get_items_by_category(ScoreItemCategory.MIDDLE)

    @classmethod
    def lower_items(cls):
        """Return a list of the score items in the LOWER category."""
        return cls.get_items_by_category(ScoreItemCategory.LOWER)

    # Enumeration values:
    ONE = (1, ScoreItemCategory.UPPER)
    TWO = (2, ScoreItemCategory.UPPER)
    THREE = (3, ScoreItemCategory.UPPER)
    FOUR = (4, ScoreItemCategory.UPPER)
    FIVE = (5, ScoreItemCategory.UPPER)
    SIX = (6, ScoreItemCategory.UPPER)

    MIN = (7, ScoreItemCategory.MIDDLE)
    MAX = (8, ScoreItemCategory.MIDDLE)

    POKER = (9, ScoreItemCategory.LOWER)
    FULL = (10, ScoreItemCategory.LOWER)
    SMALL_STRAIGHT = (11, ScoreItemCategory.LOWER)
    LARGE_STRAIGHT = (12, ScoreItemCategory.LOWER)
    YAMS = (13, ScoreItemCategory.LOWER)
    RIGOLE = (14, ScoreItemCategory.LOWER)


class GameStage(Enum):
    """An enumeration of the stages of the game"""
    WAITING = auto()
    ROLLING = auto()
    SCORING = auto()
    DISPLAYING_FINAL_SCORE = auto()
    ARCHIVED = auto()


class User(db.Model):
    """Models a user of the application."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256),  nullable=False)

    def __init__(self, **kwargs):
        """Initalizes user object.

        Keyword arguments:
        id -- a unique integer identifying the user.
        username -- a unique string identifying the user.
        password_hash -- the hashed password for user.
        games -- the games the user is playing.
        players -- relationship between users and games.
        """
        super(User, self).__init__(**kwargs)

    def __eq__(self, other):
        """Return true if other is a user with the same id."""
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        """Return a hash for this object."""
        return hash(self.id)

    __repr__ = make_repr()

    def is_authenticated(self):
        """Return true."""
        return True

    def is_active(self):
        """Return true."""
        return True

    def is_anonymous(self):
        """Return false."""
        return False

    def get_id(self):
        """Return the user's username."""
        return self.username

    @property
    def has_current_game(self):
        """Return true if this user is playing a game."""
        for player in self.players:
            if not player.has_quit:
                return True

    @property
    def current_game(self):
        """Return the game this user is playing.

        Return None if the user is not playing any game.
        """

        for player in self.players:
            if not player.has_quit:
                return player.game
        return None

    @property
    def current_player(self):
        """ Return related to this user and their current game."""
        for player in self.players:
            if not player.has_quit:
                return player
        return None

    def change_password(self, password):
        """Update this user's password_hash based on password."""
        self.password_hash = generate_password_hash(password)


class Game(db.Model):
    """Models a game of Yam's.

    Each game is associated with a list of users that are playing it, a stage,
    five dice objects, a counter for the number of times the dice have been
    rolled in this round.
    """

    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.Enum(GameStage), nullable=False,
                      default=GameStage.WAITING)
    users = db.relationship('User', secondary='player', lazy='subquery',
                            backref=db.backref('games', lazy=True))
    dice_rolls = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, **kwargs):
        """Initializes user object and creates corresponding dice objects.

        Keyword arguments:
        id -- a unique integer identifying the user.
        stage -- the current stage of the game.
        users -- the users playing in this game.
        players -- relationship between game ans its users.
        dice -- five dice.
        dice_rolls -- number of times the dice have been rolled in this turn.
        score_entries -- the score entries associated with this game.
        """

        super(Game, self).__init__(**kwargs)
        self.number_of_dice = 5
        for i in range(self.number_of_dice):
            self.dice.append(Die(index=(i)))
        db.session.commit()

    def __eq__(self, other):
        """Return true if other is a game object with the same id."""
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        """Return a hash for this object."""
        return hash(self.id)

    __repr__ = make_repr()

    def add_player(self, user):
        """Add user to this game and create the corresponding player object."""
        player = Player(game=self, user=user, is_active=True, index=0)
        db.session.add(player)
        db.session.commit()

    @property
    def active_player(self):
        """Return the player that is currently active in this game."""
        for player in self.players:
            if player.is_active:
                return player

    def get_player(self, user):
        """Return the player object that corresponds to user in this game."""
        for player in self.players:
            if player.user == user:
                return player
        return None

    def get_die(self, index):
        """Return the die with this index."""
        for die in self.dice:
            if die.index == index:
                return die
        return None

    def get_die_value(self, index):
        """Return the face value of the die with this index."""
        return self.get_die(index).value

    def resigned_players_count(self):
        """Return the number of players that have resigned."""
        resigned_players = [player for player in self.players if
                            player.has_resigned]
        return count(resigned_players)

    @property
    def is_waiting(self):
        """Return true if the game has not started yet."""
        return self.stage == GameStage.WAITING

    @property
    def is_rolling(self):
        """Return true if the active player can roll the dice."""
        return self.stage == GameStage.ROLLING

    @property
    def is_playing(self):
        """Return true if the active player can roll the dice."""
        return self.is_rolling

    @property
    def is_scoring(self):
        """Return true if active player is in scoring stage."""
        return self.stage == GameStage.SCORING

    @property
    def is_displaying_final_score(self):
        """Return true if the game is over but not all players have quit."""
        return self.stage == GameStage.DISPLAYING_FINAL_SCORE

    @property
    def is_archived(self):
        """Return true if the game is over and all players have quit."""
        return self.stage == GameStage.ARCHIVED

    @property
    def is_in_progress(self):
        """Return true if the game has started and is not over."""
        return self.is_rolling or self.is_scoring

    def _is_game_end(self):
        # Return true if the game should end.

        # If the only player has resigned, the game is over
        if len(self.players) == 1:
            if self.players[0].has_resigned:
                return True

        # If there is more than one player, and all players but one have
        # resigned, the game is over.
        elif self.resigned_players_count() == len(self.players) - 1:
            return True

        # Otherwise, if not all score entries are taken, the game is not over.
        for score_entry in self.score_entries:
            if score_entry.is_available:
                return False

        # Otherwise, the game is over.
        return True

    def start(self):
        """Start the game."""
        self._next_round()

    def _next_round(self):
        # Reset dice roll counts and go into rolling stage."""
        self.dice_rolls = 0
        self.stage = GameStage.ROLLING
        db.session.commit()

    def _check_game_end(self):
        # Check if the game should end, and end it if necessary,
        # otherwise go to next round.
        if self._is_game_end():
            self.stage = GameStage.DISPLAYING_FINAL_SCORE
            db.session.commit()
        else:
            self._next_round()

    def _dice_values(self):
        # Return the list of face values of dice.
        return [die.value for die in self.dice]

    def _sorted_dice_values(self):
        # Return ordered list of face values of dice.
        return sorted(self._dice_values())

    def roll_dice(self, indexes=range(5)):
        """Roll the dice with given indexes.

        If this is the third dice roll in this round, go to scoring stage.
        """

        if len(indexes) == 0:
            return
        for index in indexes:
            self.get_die(index).roll()
        self.dice_rolls = self.dice_rolls + 1
        db.session.commit()

        if self.dice_rolls > 2:
            self.hold()

    def hold(self):
        """Got to rolling stage."""
        self.stage = GameStage.SCORING
        db.session.commit()

    def enter_score(self, score_item):
        """Update the active player's score entry for score item."""
        player = self.active_player
        score_entry = player.get_score_entry(score_item)
        score_entry.value = self._calculate_score(score_item)
        db.session.commit()
        self._check_game_end()

    def _is_max(self):
        # Return true if min is not taken or if the current value of dice are
        # more than the value of min.
        dice_value_sum = self._calculate_dice_value_sum()
        min = self.active_player.get_score_entry_value(ScoreItem.MIN)
        if min and dice_value_sum < min:
            return False
        else:
            return True

    def _is_min(self):
        # Return true if max is not taken or if the current value of dice are
        # less than the value of max.
        dice_value_sum = self._calculate_dice_value_sum()
        max = self.active_player.get_score_entry_value(ScoreItem.MAX)
        if max and dice_value_sum > max:
            return False
        else:
            return True

    def _is_poker(self):
        # Return true if the same dice value appears at least four times.
        dice_values = [die.value for die in self.dice]
        # If the first or the second value appear four times, we have a poker
        firstcount = dice_values.count(dice_values[0])
        lastcount = dice_values.count(dice_values[1])
        return (firstcount >= 4) or (lastcount >= 4)

    def _is_full(self):
        # Return true if one dice value appears two times, and another
        # three times.

        # Sort the dice
        sorted_dice_values = self._sorted_dice_values()

        # Count frequency of first and last value
        firstcount = sorted_dice_values.count(sorted_dice_values[0])
        lastcount = sorted_dice_values.count(sorted_dice_values[-1])

        # We have a full if one value appears twice and the other appears
        # three times.
        return (firstcount == 2 and lastcount == 3)\
            or (firstcount == 3 and lastcount == 2)

    def _is_small_straight(self):
        # Return true if four dice values are in sequence.

        unique_dice_values = list(dict.fromkeys(self._dice_values()))
        unique_sorted_dice_values = sorted(unique_dice_values)

        if len(unique_sorted_dice_values) == 4:
            return _is_straight(unique_sorted_dice_values)

        elif len(unique_sorted_dice_values) == 5:
            return _is_straight(unique_sorted_dice_values[0:4])\
                or _is_straight(unique_sorted_dice_values[1:5])

        else:
            return False

    def _is_large_straight(self):
        # Return true if five dice values are in sequence.

        # Sort the dice
        sorted_dice_values = self._sorted_dice_values()
        # We have a small_straight if all the dice are a straight
        return _is_straight(sorted_dice_values)

    def _is_yams(self):
        # Return true if all dice have the same values.

        # If the first value appears five times, we have a yams
        dice_values = self._dice_values()
        return dice_values.count(dice_values[0]) == 5

    def _is_rigole(self):
        # Return true if:
        #
        # Sort the dice
        sorted_dice_values = self._sorted_dice_values()

        # Count frequency of first and last value
        firstcount = sorted_dice_values.count(sorted_dice_values[0])
        lastcount = sorted_dice_values.count(sorted_dice_values[-1])

        # We have a rigole if one value appears once and the other appears
        # four times, and the sum of the two values is 7.
        if (firstcount == 4 and lastcount == 1)\
                or (firstcount == 1 and lastcount == 4):
            return ((sorted_dice_values[0] + sorted_dice_values[-1]) == 7)
        else:
            return False

    def _calculate_dice_value_sum(self, dice_values=[1, 2, 3, 4, 5, 6]):
        # Return the sum of the values for the dice with given values.
        return sum([value for value in self._dice_values()
                   if value in dice_values])

    def _calculate_score(self, entry):
        # Return the score value of the current dice for the given entry.

        result = 0

        # Upper combination: sum all dice with given values
        if entry == ScoreItem.ONE:
            result = self._calculate_dice_value_sum([1])

        elif entry == ScoreItem.TWO:
            result = self._calculate_dice_value_sum([2])

        elif entry == ScoreItem.THREE:
            result = self._calculate_dice_value_sum([3])

        elif entry == ScoreItem.FOUR:
            result = self._calculate_dice_value_sum([4])

        elif entry == ScoreItem.FIVE:
            result = self._calculate_dice_value_sum([5])

        elif entry == ScoreItem.SIX:
            result = self._calculate_dice_value_sum([6])

        elif entry == ScoreItem.MIN and self._is_min():
            result = self._calculate_dice_value_sum()

        elif entry == ScoreItem.MAX and self._is_max():
            result = self._calculate_dice_value_sum()

        # Poker: 40 points plus the values of the four dice that
        # form the poker.
        elif entry == ScoreItem.POKER and self._is_poker():
            pokervalue = None
            dice_values = self._dice_values()
            for value in dice_values:
                if dice_values.count(value) >= 4:
                    pokervalue = value
            result = 40 + (pokervalue * 4)

        # Full: 30 points plus the sum of all dice values.
        elif entry == ScoreItem.FULL and self._is_full():
            result = 30 + self._calculate_dice_value_sum()

        # Small straight: 45 points.
        elif entry == ScoreItem.SMALL_STRAIGHT and self._is_small_straight():
            result = 45

        # Large straight: 50 points.
        elif entry == ScoreItem.LARGE_STRAIGHT and self._is_large_straight():
            result = 50

        # Yams: 50 points plus the sum of the dice.
        elif entry == ScoreItem.YAMS and self._is_yams():
            result = 50 + self._calculate_dice_value_sum()

        # Rigole: 50 points.
        elif entry == ScoreItem.RIGOLE and self._is_rigole():
            result = 50

        return result


class Die(db.Model):
    """Models a die.

    A die is associated with a game, an index (unique within the game), and
    a face value.
    """

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('dice', lazy=True))
    index = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Integer, nullable=False, default=6)
    db.UniqueConstraint('game_id', 'index', name='uix_1')

    def __init__(self, **kwargs):
        """Initializes die object.

        Keyword arguments:
        id -- a unique integer identifying the die.
        game -- the game to which this die belongs.
        index -- orders the die within a game.
        value -- the face value of the die (defaults to 6).
        """
        super(Die, self).__init__(**kwargs)

    def __eq__(self, other):
        """Return true if other is a die with the same id."""
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        """Return a hash for this object."""
        return hash(self.id)

    __repr__ = make_repr()

    def roll(self):
        """Set die value to a random number between 1 and 6 (inclusive)."""
        self.value = randint(1, 6)


class Player(db.Model):
    """
    Represents a user in the context of a game.

    Each player is associated with a user, a game, and a list of score entries.
    """
    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User', backref=db.backref('players', lazy=True))
    game_id = db.Column('game_id', db.Integer, db.ForeignKey('game.id'),
                        nullable=False)
    game = db.relationship('Game', backref=db.backref('players', lazy=True))
    index = db.Column(db.Integer, nullable=False)
    is_active = db.Column('is_active', db.Boolean, nullable=False,
                          default=False)
    has_resigned = db.Column('has_resigned', db.Boolean, nullable=False,
                             default=False)
    has_quit = db.Column('has_quit', db.Boolean, nullable=False, default=False)
    db.UniqueConstraint('user_id', 'game_id', 'uix_1')
    db.UniqueConstraint('game_id', 'index', 'uix_2')

    def __init__(self, **kwargs):
        """Initializes player and creates corresponding score entries.
        Keyword arguments:
        id -- a unique integer identifying the player.
        game -- the game to which this player belongs.
        user -- the user to which this player belongs.
        score_entires -- the components of this player's score.
        index -- an integer identifying the user (unique within this game).
        is_active -- True if it is this player's turn.
        has_resigned -- True if this player has resigned.
        """
        super(Player, self).__init__(**kwargs)
        for score_item in ScoreItem:
            score_entry = ScoreEntry(player=self, score_item=score_item)
            db.session.add(score_entry)
        db.session.commit()

    def __eq__(self, other):
        """Return true if other is a player with the same id."""
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        """Return a hash for this object."""
        return hash(self.id)

    __repr__ = make_repr()

    def is_current_user(self):
        """Return true if the client is this player's user."""
        return self.user == current_user

    def get_score_entry(self, score_item):
        """Return the ScoreEntry associated with score_item and this player.

        score_item is a ScoreItem object.
        """

        result = None
        for score_entry in self.score_entries:
            if score_entry.score_item == score_item:
                result = score_entry
        return result

    def get_score_entry_value(self, score_item):
        """Return the value of this player's entry for score item.

        score_item is a ScoreItem object.
        """

        return self.get_score_entry(score_item).value

    def get_score_entry_by_name(self, name):
        """Return this player's score_entry with this name.

        score_item is the string representation of the ScoreItem object
        (as per the name() method of the Score Item class).
        """

        score_item = ScoreItem.get_item_by_name(name)
        return self.get_score_entry(score_item)

    def get_category_subtotal(self, category):
        """Return sum of the values for the score entries in this category."""
        category_items = ScoreItem.get_items_by_category(category)
        values = [score_entry.value for score_entry in self.score_entries
                  if score_entry.score_item in category_items]
        values = [value for value in values if value is not None]
        return sum(values)

    @property
    def total(self):
        """Return sum of the values of all score entries plus the bonus."""
        return self.upper_subtotal + self.bonus + self.middle_subtotal\
            + self.lower_subtotal

    @property
    def upper_subtotal(self):
        """Return sum of the values of upper score entries."""
        return self.get_category_subtotal(ScoreItemCategory.UPPER)

    @property
    def middle_subtotal(self):
        """Return sum of the values of middle score entries."""
        return self.get_category_subtotal(ScoreItemCategory.MIDDLE)

    @property
    def lower_subtotal(self):
        """Return sum of the values of lower score entries."""
        return self.get_category_subtotal(ScoreItemCategory.LOWER)

    @property
    def bonus(self):
        """Return the value of bonus.

        If the sum of the upper entries is less than 60, bonus is 0.
        If the sum of the upper entries is more than 60, bonus is 30 plus 1 for
        any point over 60 in upper values.
        """
        upper_subtotal = self.upper_subtotal
        if upper_subtotal < 60:
            return 0
        else:
            return 30 + upper_subtotal - 60

    def resign(self):
        """Resign from this game."""
        self.has_resigned = True
        db.session.commit()

    def quit(self):
        """Quit this game."""
        self.has_quit = True
        db.session.commit()


class ScoreEntry(db.Model):
    """Models a component of the score for a given player.

    A die is associated with a player (i.e. a user and a game), a score_item,
    and a value (number of points).
    """
    id = db.Column(db.Integer(), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'),
                          nullable=False)
    player = db.relationship('Player', backref=db.backref('score_entries',
                             lazy=True))
    score_item = db.Column(db.Enum(ScoreItem), nullable=False)
    value = db.Column(db.Integer)
    db.UniqueConstraint('player_id', 'score_item', name='uix_1')
    game = db.relationship('Game', secondary='player', lazy='subquery',
                           backref=db.backref('score_entries', lazy=True))
    user = db.relationship('User', secondary='player', lazy='subquery',
                           backref=db.backref('score_entries', lazy=True))

    def __init__(self, **kwargs):
        """Initializes score_entry.
        Keyword arguments:
        id -- a unique integer identifying the score_entry.
        score_item -- this entrie's score item.
        user -- the user to which this entry belongs.
        game -- the game to which this entry belongs.
        player -- the player object to which this entry belongs.
        value -- number of points for this entry (Null if the entry is still
                available).
        """
        super(ScoreEntry, self).__init__(**kwargs)

    def __eq__(self, other):
        """Return true if other is a score_entry with the same id."""
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        """A hash for this object."""
        return hash(self.id)

    __repr__ = make_repr()

    @property
    def is_available(self):
        """Return true if this entry is still available to the player."""
        return self.value is None
