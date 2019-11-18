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

    @property
    def total_name(self):
         return '%s_total'% self._name_.lower()



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
    DISPLAYING_FINAL_SCORE = auto()
    OVER = auto()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80),  nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        return hash(self.id)



    @property
    def current_game(self):
        result = None
        for game in self.games:
            if game.is_current:
                result = game
        return result

    def get_entry_value(self, game, score_item):
        for score_entry in self.score_entries:
            if score_entry.game == game and score_entry.score_item == score_item:
                return score_entry.value

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

    def get_category_total(self, game, category):
        result = 0
        score_entries = filter(lambda score_entry: score_entry.game == game and score_entry.score_item.category == category, self.score_entries)
        return sum([score_entry.value for score_entry in score_entries if score_entry.value])

    def get_bonus(self, game):
        upper_total = self.get_category_total(game, ScoreItemCategory.UPPER)
        if upper_total < 60:
            return 0
        else:
            return 30 + 60 - upper_total


    @property
    def score(self):
        score_entries = filter(lambda score_entry: score_entry.game == self.current_game, self.score_entries)
        result = {}
        for score_entry in score_entries:
            result[score_entry.score_item.name] = score_entry.value

        result['bonus'] = self.get_bonus(self.current_game)
        result['total'] = result['bonus']

        for category in ScoreItemCategory:
            result[category.total_name] = self.get_category_total(self.current_game, category)
            result['total'] = result['total']  + result[category.total_name]

        result['name'] = self.username

        return result


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

        for player in self.players:
            for score_item in ScoreItem:
                score_entry = ScoreEntry(game=self, user=player, score_item=score_item)
                db.session.add(score_entry)
        db.session.commit()

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        return hash(self.id)

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
    def is_displaying_final_score(self):
        return self.stage == GameStage.DISPLAYING_FINAL_SCORE

    @property
    def is_over(self):
        return self.stage == GameStage.OVER

    @property
    def is_in_progress(self):
        return self.is_rolling or self.is_scoring

    @property
    def is_current(self):
        return self.is_rolling or self.is_scoring or self.is_displaying_final_score

    def is_game_end(self):
        for score_entry in self.score_entries:
            print('score entry: %s' % score_entry)
        for score_entry in self.score_entries:
            if score_entry.value == None:
                print('game is not over')
                return False
        print('game end')
        return True

    def dice_values(self):
        return [die.value for die in self.dice]

    def sorted_dice_values(self):
        return sorted(self.dice_values())

    def roll_dice(self, indexes=range(5)):

        print('rolling')

        for index in indexes:
            self.dice[index].roll();
        self.dice_rolls = self.dice_rolls + 1;
        if self.dice_rolls > 2:
            self.hold()
            self.dice_rolls = 0

        db.session.commit()

    def hold(self):
        print('stage: %s' % self.stage)
        print('holding')
        self.stage = GameStage.SCORING;
        db.session.commit()


    def __repr__(self):
        return '<Game id: %s, current_player_id: %s, stage: %s, players: %s>' % (self.id, self.current_player_id, self.stage, self.players)


    def start(self):
        print('starting')
        print('stage: %s' % self.stage)
        self.stage = GameStage.ROLLING
        self.roll_dice()



    def is_max(self):
        dice_value_sum = self.calculate_dice_value_sum()
        print('dice value sum: %s' % dice_value_sum)
        min = self.current_player.get_entry_value(self, ScoreItem.MIN)
        print('min: %s' % min)
        if min:
            if dice_value_sum < min:
                print('nomax')
                return False
        else:
            print('ismax')
            return True

    def is_min(self):
        dice_value_sum = self.calculate_dice_value_sum()
        print('dice value sum: %s' % dice_value_sum)
        max = self.current_player.get_entry_value(self, ScoreItem.MAX)
        print('max: %s' % max)
        if max:
            if dice_value_sum > max:
                print('nomin')
                return False
        else:
            print('ismin')
            return True

    def is_poker(self):
        dice_values = [die.value for die in self.dice]
        # If the first or the second value appear four times, we have a poker
        return (dice_values.count(dice_values[0]) >= 4) or (dice_values.count(dice_values[1]) >= 4)


    def is_full(self):
        # Sort the dice
        sorted_dice_values =self.sorted_dice_values()

        # Count frequency of first and last value
        firstcount = sorted_dice_values.count(sorted_dice_values[0])
        lastcount = sorted_dice_values.count(sorted_dice_values[-1])

        # We have a full if one value appears twice and the other appears three times
        return (firstcount == 2 and lastcount == 3) or (firstcount == 3 and lastcount == 2)



    def is_small_straight(self):

        unique_dice_values = list(dict.fromkeys(self.dice_values()))
        unique_sorted_dice_values = sorted(unique_dice_values)


        if len(unique_sorted_dice_values) == 4:
            return is_straight(unique_sorted_dice_values)

        elif len(unique_sorted_dice_values) == 5:
            return is_straight(unique_sorted_dice_values[0:4]) or is_straight(unique_sorted_dice_values[1:5])

        else:
            return False

    def is_large_straight(self):
        # Sort the dice
        sorted_dice_values = self.sorted_dice_values()


        # We have a small_straight if all the dice are a straight
        return is_straight(sorted_dice_values)


    def is_yams(self):
        # If the first value appears five times, we have a yams
        dice_values = self.dice_values()
        return dice_values.count(dice_values[0]) == 5


    def is_rigole(self):
        # Sort the dice
        sorted_dice_values = self.sorted_dice_values()

        # Count frequency of first and last value
        firstcount =  sorted_dice_values.count(sorted_dice_values[0])
        lastcount =  sorted_dice_values.count(sorted_dice_values[-1])

        # We have a rigole if one value appears once and the other appears four times, and the sum of the two values is 7
        if (firstcount == 4 and lastcount == 1) or (firstcount == 1 and lastcount == 4):
            return     sorted_dice_values [0] +     sorted_dice_values [-1] == 7
        else:
            return False


    def calculate_dice_value_sum(self, dice_values=[1, 2, 3, 4, 5, 6]):
        return sum([value for value in self.dice_values() if value in dice_values])

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
            result = 40 + self.calculate_dice_value_sum()

        elif entry == ScoreItem.FULL and self.is_full():
            result = 30 + self.calculate_dice_value_sum()

        elif entry == ScoreItem.SMALL_STRAIGHT and self.is_small_straight():
            result = 45

        elif entry == ScoreItem.LARGE_STRAIGHT and self.is_large_straight():
            result = 50

        elif entry == ScoreItem.YAMS and self.is_yams():
            result = 50 + self.calculate_dice_value_sum()

        elif entry == ScoreItem.RIGOLE and self.is_rigole():
            result = 50

        return result

    def enter_score(self, score_item):
        print('starting')
        print('stage: %s' % self.stage)
        #score_entry = ScoreEntry(game=self, user=self.current_player, score_item=score_item, value=self.calculate_score(score_item))
        score_entry = ScoreEntry.query.filter_by(game=self, user=self.current_player, score_item=score_item).first()
        print('score_entry to update: %s' % score_entry)
        score_entry.value=self.calculate_score(score_item)
        db.session.commit()
        if self.is_game_end():
            self.stage = GameStage.DISPLAYING_FINAL_SCORE
            print('game over')
        else:
            self.stage = GameStage.ROLLING
            self.dice_rolls = 0
            self.roll_dice()
        db.session.commit()



class ScoreEntry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('score_entries', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('score_entries', lazy=True))
    score_item = db.Column(db.Enum(ScoreItem), nullable = False)
    value = db.Column(db.Integer)

    def __repr__(self):
        return '<ScoreEntry id: %s, user: %s, score_item: %s, value: %s>' % (self.id, self.user, self.score_item, self.value)

class Die(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('dice', lazy=True))

    value = db.Column(db.Integer, nullable=False, default=6)

    def __init__(self, **kwargs):
        super(Die, self).__init__(**kwargs)



    def roll(self):
        self.value = randint(1,6)
