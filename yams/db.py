from enum import Enum, IntEnum, auto
from random import randint
from flask import g, session
from flask.cli import with_appcontext
from flask_login import current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
import click
from helpers import is_straight



db = SQLAlchemy()

def init_db():
    db.drop_all()
    db.create_all()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db_command)

class ScoreItemCategory(Enum):
    UPPER = auto()
    MIDDLE = auto()
    LOWER = auto()


class ScoreItem(IntEnum):
    def __new__(cls, value, category):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.category = category
        return obj

    @property
    def name(self):
         return self._name_.lower()

    @classmethod
    def get_item_by_name(cls, name):
        for item in cls:
            if item.name == name:
                return item
        return None

    @classmethod
    def get_items_by_category(cls, category):
         return [item for item in cls if item.category == category]

    @classmethod
    def upper_items(cls):
        return cls.get_items_by_category(ScoreItemCategory.UPPER)

    @classmethod
    def middle_items(cls):
        return cls.get_items_by_category(ScoreItemCategory.MIDDLE)

    @classmethod
    def lower_items(cls):
        return cls.get_items_by_category(ScoreItemCategory.LOWER)

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
    WAITING = auto()
    ROLLING = auto()
    SCORING = auto()
    OVER = auto()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80),  nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


    @property
    def current_game(self):
        result = None
        for game in self.games:
            if game.is_in_progress:
                result = game
        return result


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def __repr__(self):
        return '<User username: %s, id: %s>' % (self.username, self.id)

    # @property
    # def games(self):
    #     sel = db.select([users_in_games.c.game_id]).where(users_in_games.c.user_id == self.id)
    #     rs = db.session.execute(sel)
    #     rows = rs.fetchall()
    #     games = []
    #     for row in rows:
    #         games.append(Game.query.filter_by(id=row[0]).first())
    #     return games


users_in_games = db.Table('users_in_games',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
        db.Column('game_id', db.Integer, db.ForeignKey('game.id'), nullable=False))

def __repr__(self):
    return '<User id: %s>' % (self.id, self.user, self.score_item, self.value)



class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    current_player = db.relationship('User',
        backref=db.backref('games_current', lazy=True))
    stage = db.Column(db.Enum(GameStage), nullable = False, default = GameStage.WAITING)
    players = db.relationship('User', secondary=users_in_games, lazy='subquery',
        backref=db.backref('games', lazy=True))
    dice_rolls = db.Column(db.Integer, nullable=False, default=0)



    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.number_of_dice = 5
        for i in range(self.number_of_dice):
            self.dice.append(Die())


    @property
    def is_waiting(self):
        return self.stage == GameStage.WAITING

    @property
    def is_rolling(self):
        return self.stage == GameStage.ROLLING

    @property
    def is_scoring(self):
        return self.stage == GameStage.SCORING

    @property
    def is_over(self):
        return self.stage == GameStage.OVER

    @property
    def is_in_progress(self):
        return self.is_rolling or self.is_scoring

    # @property
    # def score_items(self):
    #     return ScoreItem

    # @property
    # def stages(self):
    #     return GameStage

    def roll_dice(self, indexes):
        for index in indexes:
            self.dice[index].roll();
            self.dice_rolls = self.dice_rolls + 1;
            if self.dice_rolls > 2:
                self.hold()
        db.session.commit()

    def hold(self):
        self.stage = GameStage.SCORING;
        db.session.commit()


    def __repr__(self):
        return '<Game id: %s, current_player_id: %s, stage: %s, players: %s>' % (self.id, self.current_player_id, self.stage, self.players)



    #     self._players=players

    @property
    def score(self):
        result = {player : {} for player in self.players}
        for key in result:
            for score_item in ScoreItem:
                result[key][score_item.name] = None
            result[key]['upper_total'] = 0
            result[key]['middle_total'] = 0
            result[key]['lower_total'] = 0
            result[key]['total'] = 0
            result[key]['name'] = key.username


        for score_entry in self.score_entries:
            print('%s %s' % (score_entry.score_item, score_entry.value))
            result[score_entry.user][score_entry.score_item.name] = score_entry.value

            if score_entry.score_item in ScoreItem.upper_items():
                result[score_entry.user]['upper_total'] = result[score_entry.user]['upper_total'] + score_entry.value
            elif score_entry.score_item in ScoreItem.middle_items():
                result[score_entry.user]['middle_total'] = result[score_entry.user]['upper_total'] + score_entry.value
            elif score_entry.score_item in ScoreItem.lower_items():
                result[score_entry.user]['lower_total'] = result[score_entry.user]['lower_total'] + score_entry.value
            result[score_entry.user]['total'] = result[score_entry.user]['total'] + score_entry.value

        for player in self.players:
            if result[player]['upper_total'] < 60:
                result[player]['bonus'] = 0
            else:
                result[player]['bonus'] = 30 + 60 - result[player]['upper_total']

        return result


    def bonus(self, player):
        if self.upper_total(player) < 60:
            return 0
        else:
            return 30 + 60 - self.upper_total(player)

    def start(self):
        self.stage = GameStage.ROLLING
        for die in self.dice:
            die.roll()
        db.session.commit()

    def hold(self):
        self.stage = GameStage.SCORING
        db.session.commit()

    def is_max(self):
        dice_value_sum = sum([die.value for die in self.dice])
        min = self.score[current_player][ScoreItem.MIN]
        if min:
            if dice_value_sum > min:
                return True
        else:
            return False

    def is_min(self):
        dice_value_sum = sum([die.value for die in self.dice])
        max = self.score[current_player][ScoreItem.MAX]
        if max:
            if dice_value_sum < max:
                return True
        else:
            return False

    def is_poker(self):
        dice = self.dice
        # If the first or the second value appear four times, we have a poker
        return (dice.count(dice[0]) >= 4) or (dice.count(dice[1]) >= 4)


    def is_full(self):
        # Sort the dice
        sorted_dice_values = sorted([die.value for die in self.dice])

        # Count frequency of first and last value
        firstcount = sorted_dice_values.count(sorted_dice_values[0])
        lastcount = sorted_dice_values.count(sorted_dice_values[-1])

        # We have a full if one value appears twice and the other appears three times
        return (firstcount == 2 and lastcount == 3) or (firstcount == 3 and lastcount == 2)



    def is_small_straight(self):
        # Sort the dice
        sorted_dice_values = sorted([die.value for die in self.dice])


        # The four dice with highest value
        highsequence = sorted_dice_values[0: -1]

        # The last four dice
        lowsequence = sorted_dice_values[1:]

        # We have a small_straight if lowest or the highest four dice are a straight
        return is_straight(highsequence) or is_straight(lowsequence)

    def is_large_straight(self):
        # Sort the dice
        sorted_dice_values = sorted([die.value for die in self.dice])


        # We have a small_straight if all the dice are a straight
        return is_straight(sorted_dice_values)


    def is_yams(self):
        # If the first value appears five times, we have a yams
        dice = self.dice
        return dice.count(dice[0]) == 5


    def is_rigole(self):
        # Sort the dice
        sorted_dice_values = sorted([die.value for die in self.dice])

        # Count frequency of first and last value
        firstcount =  sorted_dice_values.count(sorted_dice_values[0])
        lastcount =  sorted_dice_values.count(sorted_dice_values[-1])

        # We have a rigole if one value appears once and the other appears four times, and the sum of the two values is 7
        if (firstcount == 4 and lastcount == 1) or (firstcount == 1 and lastcount == 4):
            return     sorted_dice_values [0] +     sorted_dice_values [-1] == 7
        else:
            return False


    def calculate_dice_value_sum(self, dice_value=[1, 2, 3, 4, 5, 6]):
        result = 0
        for die in self.dice:
            if die.value in dice_value:
                result = result + die.value
        return result

    def calculate_score(self, entry):

        result = 0;

        # Upper combination: sum all dice with given values
        if entry == ScoreItem.ONE:
            result = self.calculate_dice_value_sum([1])

        elif entry == ScoreItem.TWO:
            result = self.calculate_dice_value_sum([2])

        elif entry == ScoreItem.THREE:
            result = self.calculate_dice_value_sum([3])

        elif entry == ScoreItem.FOUR:
            result = self.calculate_dice_value_sum([4])

        elif entry == ScoreItem.FIVE:
            result = self.calculate_dice_value_sum([5])

        elif entry == ScoreItem.SIX:
            result = self.calculate_dice_value_sum([6])

        elif entry == ScoreItem.MIN and self.is_min():
            result = self.calculate_dice_value_sum()

        elif entry == ScoreItem.MAX and self.is_max():
            result = self.calculate_dice_value_sum()

        elif entry == ScoreItem.POKER and self.is_poker():
            result = 40 + sum(self.dice)

        elif entry == ScoreItem.FULL and self.is_full():
            result = 30 + sum(self.dice)

        elif entry == ScoreItem.SMALL_STRAIGHT and self.is_small_straight():
            result = 45

        elif entry == ScoreItem.LARGE_STRAIGHT and self.is_large_straight():
            result = 50

        elif entry == ScoreItem.YAMS and self.is_yams():
            result = 50 + sum(self.dice)

        elif entry == ScoreItem.RIGOLE and self.is_rigole():
            result = 50

        return result

    def enter_score(self, score_item):
        score_entry = ScoreEntry(game=self, user=self.current_player, score_item=score_item, value=self.calculate_score(score_item))
        db.session.add(score_entry)
        self.stage = GameStage.ROLLING
        db.session.commit()


class ScoreEntry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('score_entries', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('score_entries', lazy=True))
    score_item = db.Column(db.Enum(ScoreItem), nullable = False)
    value = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<ScoreEntry id: %s, user: %s, score_item: %s, value: %s>' % (self.id, self.user, self.score_item, self.value)

class Die(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('dice', lazy=True))

    value = db.Column(db.Integer, nullable=False, default=6)

    def __init__(self, **kwargs):
        super(Die, self).__init__(**kwargs)
        self.value=6


    def roll(self):
        self.value = randint(1,6)
