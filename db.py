from enum import Enum, IntEnum, auto
from random import randint
from flask import g, session
from flask.cli import with_appcontext
from flask_login import current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
import click



db = SQLAlchemy()

# Takes an iterable  of numbers, returns True  only if each number in the iterable is the successor of the previous one
def is_straight(sequence):
    for i in range(0, len(sequence) -1):
        if sequence[i] != (sequence[i + 1] - 1):
            return False
    return True

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
    ARCHIVED = auto()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256),  nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<User id:%s, username:%s>' % (self.id, self.username)

    @property
    def has_current_game(self):
        for player in self.players:
            if not player.has_quit:
                return True

    @property
    def current_game(self):
        for player in self.players:
            if not player.has_quit:
                return player.game
        return None

    @property
    def current_player(self):
        for player in self.players:
            if not player.has_quit:
                return player
        return None


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username



class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.Enum(GameStage), nullable = False, default = GameStage.WAITING)
    users = db.relationship('User', secondary='player', lazy='subquery',
        backref=db.backref('games', lazy=True))
    dice_rolls = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.number_of_dice = 5
        for i in range(self.number_of_dice):
            self.dice.append(Die(index=(i)))
        db.session.commit()

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.id == other.id)
        
    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Game id: %s, stage: %s, players: %s>' % (self.id, self.stage, self.players)

    @property
    def active_player(self):
        for player in self.players:
            if player.is_active:
                return player

    def get_player(self, user):
        for player in self.players:
            if player.user == user:
                return player

    def get_die(self, index):
        for die in self.dice:
            if die.index == index:
                return die

    def get_die_value(self, index):
        return self.get_die(index).value

    def resigned_players_count(self):
        resigned_players = [player for player in self.players if player.has_resigned]
        return count(resigned_players)

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
    def is_archived(self):
        return self.stage == GameStage.ARCHIVED

    @property
    def is_in_progress(self):
        return self.is_rolling or self.is_scoring

    @property
    def is_active(self):
        return not self.is_archived


    def is_game_end(self):
        #If the only player has resigned, the game is over
        if len(self.players) == 1:
            if self.players[0].has_resigned:
                return True

        #If there is more than one player, and all players but one have resigned, the game is over
        elif self.resigned_players_count() == len(self.players) - 1:
            return True

        #Otherwise, if not all score entries are taken, the game is not over
        for score_entry in self.score_entries:
            if not score_entry.is_taken:
                return False

        #Otherwise, the game is over
        return True

    def start(self):
        self.next_round()

    def next_round(self):
        self.stage = GameStage.ROLLING
        db.session.commit()


    def check_game_end(self):
        if self.is_game_end():
            self.stage = GameStage.DISPLAYING_FINAL_SCORE
            db.session.commit()

    def dice_values(self):
        return [die.value for die in self.dice]

    def sorted_dice_values(self):
        return sorted(self.dice_values())

    def roll_dice(self, indexes=range(5)):
        if len(indexes) == 0:
            return
        for index in indexes:
            self.get_die(index).roll();
        self.dice_rolls = self.dice_rolls + 1;
        if self.dice_rolls > 2:
            self.hold()
            self.dice_rolls = 0

        db.session.commit()

    def hold(self):
        self.stage = GameStage.SCORING;
        db.session.commit()



    def is_max(self):
        dice_value_sum = self.calculate_dice_value_sum()
        min = self.active_player.get_score_entry_value(ScoreItem.MIN)
        if min and dice_value_sum < min:
            return False
        else:
            return True

    def is_min(self):
        dice_value_sum = self.calculate_dice_value_sum()
        max = self.active_player.get_score_entry_value(ScoreItem.MAX)
        if max and dice_value_sum > max:
            return False
        else:
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
            pokervalue = None
            dice_values = self.dice_values()
            for value in dice_values:
                if dice_values.count(value) >= 4:
                    pokervalue = value
            result = 40 + (pokervalue * 4)

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
        player = self.active_player
        score_entry = player.get_score_entry(score_item)
        score_entry.value=self.calculate_score(score_item)
        db.session.commit()
        self.check_game_end()
        if not self.is_game_end():
            self.next_round()
        db.session.commit()

class Die(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('dice', lazy=True))
    index = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Integer, nullable=False, default=6)
    db.UniqueConstraint('game_id', 'index', name='uix_1')

    def __init__(self, **kwargs):
        super(Die, self).__init__(**kwargs)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Die id: %s, game: %s, value: %s>' % (self.id, self.game, self.value)

    def roll(self):
        self.value = randint(1,6)

class Player(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('players', lazy=True))
    game_id = db.Column('game_id', db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('players', lazy=True))
    index = db.Column(db.Integer, nullable=False)
    is_active = db.Column('is_active', db.Boolean, nullable=False, default=False)
    has_resigned = db.Column('has_resigned', db.Boolean, nullable=False, default=False)
    has_quit = db.Column('has_quit', db.Boolean, nullable=False, default=False)
    db.UniqueConstraint('user_id', 'game_id', 'uix_1')
    db.UniqueConstraint('game_id', 'index', 'uix_2')

    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        for score_item in ScoreItem:
            score_entry = ScoreEntry(player=self, score_item=score_item)
            db.session.add(score_entry)
        db.session.commit()

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Player id:%s, user:%s, game:%s, is_active:%s, has_resigned:%s, has_quit:%s>' % (self.id, self.user, self.game, self.is_active, self.has_resigned, self.has_quit)


    def is_current_user(self):
        return self.user == current_user

    def get_score_entry(self, score_item):
        result = None
        for score_entry in self.score_entries:
            if score_entry.score_item == score_item:
                result = score_entry
        return result

    def get_score_entry_value(self, score_item):
        return self.get_score_entry(score_item).value

    def get_score_entry_by_name(self, name):
        score_item = ScoreItem.get_item_by_name(name)
        return self.get_score_entry(score_item)

    def get_category_total(self, category):
        category_items = ScoreItem.get_items_by_category(category)
        values = [score_entry.value for score_entry in self.score_entries if score_entry.score_item in category_items]
        values = [value for value in values if value != None]
        return sum(values)

    @property
    def total(self):
        return self.upper_total + self.bonus + self.middle_total + self.lower_total

    @property
    def upper_total(self):
        return self.get_category_total(ScoreItemCategory.UPPER)

    @property
    def middle_total(self):
        return self.get_category_total(ScoreItemCategory.MIDDLE)

    @property
    def lower_total(self):
        return self.get_category_total(ScoreItemCategory.LOWER)

    @property
    def bonus(self):
        upper_total = self.upper_total
        if upper_total < 60:
            return 0
        else:
            return 30 + upper_total - 60

    def resign(self):
        self.has_resigned = True;
        db.session.commit()

    def quit(self):
        self.has_quit = True;
        db.session.commit()


class ScoreEntry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False )
    player = db.relationship('Player', backref=db.backref('score_entries', lazy=True))
    score_item = db.Column(db.Enum(ScoreItem), nullable = False)
    value = db.Column(db.Integer)
    db.UniqueConstraint('player_id', 'score_item', name='uix_1')
    game = db.relationship('Game', secondary='player', lazy='subquery',
        backref=db.backref('score_entries', lazy=True))
    user = db.relationship('User',
        secondary='player', lazy='subquery',
            backref=db.backref('score_entries', lazy=True))

    def __init__(self, **kwargs):
        super(ScoreEntry, self).__init__(**kwargs)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.id == other.id)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<ScoreEntry id: %s, user: %s, score_item: %s, value: %s>' % (self.id, self.user, self.score_item, self.value)

    @property
    def is_taken(self):
        return self.value != None
