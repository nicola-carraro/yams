from enum import auto, Enum, IntEnum

from flask import g
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
import click


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

    # @property
    # def name(self):
    #      return self._name_.lower()

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
    PLAYING = auto()
    SCORING = auto()
    OVER = auto()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80),  nullable=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._username

    def __repr__(self):
        return '<User username: %s, id: %s>' % (self.username, self.id)

    @property
    def games(self):
        sel = db.select([players.c.game_id]).where(players.c.user_id == self.id)
        rs = db.session.execute(sel)
        rows = rs.fetchall()
        games = []
        for row in rows:
            games.append(Game.query.filter_by(id=row[0]).first())
        return games




class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    current_player = db.relationship('User',
        backref=db.backref('games_current', lazy=True))
    stage = db.Column(db.Enum(GameStage), nullable = False, default = GameStage.WAITING)

    @property
    def score_items(self):
        return ScoreItem

    @property
    def stages(self):
        return GameStage


    def __repr__(self):
        return '<Game id: %s, current_player_id: %s, stage: %s, players: %s>' % (self.id, self.current_player_id, self.stage, self.players)


    @property
    def players(self):
        result = None
        if self.id:
            sel = db.select([players.c.id]).where(players.c.game_id==self.id)
            rs = db.session.execute(sel)
            rows = rs.fetchall()
            player_ids = [row[0] for row in rows]
            result=[]
            for player_id in player_ids:
                user = db.session.query(User).filter_by(id=player_id).first()
                result.append(user)
        return result

    @players.setter
    def players(self, users):
        for user in users:
            sel = db.select([players]).where(db.and_(players.c.game_id == self.id, players.c.user_id == player.id))
            rs = db.session.execute(sel)
            rows = rs.fetchall()
            if len(rows) == 0:
                ins = db.insert(players).values(user_id = player.id, game_id = self.id)
                db.session().execute(ins)
            else:
                upd = db.update(players).values(user_id = player.id, game_id = self.id)
                db.session().execute(upd)
            db.session.commit()
        self._players=users

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

        score_entries = ScoreEntry.query.filter_by(game_id=self.id)
        for score_entry in score_entries:
            result[score_entry.user][score_entry.score_item] = score_entry.value
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

    # def _category_total(self, player, score_category):
    #     result = 0
    #     score_entries = ScoreEntry.query.filter_by(game_id == self.id and player_id == player.id)
    #     for score_entry in score_entries:
    #         if score_entry in score_category:
    #             result = result + score_entry.value
    #     return result
    #
    # def upper_total(self, player):
    #     self._category_total(player, UpperScoreItem)
    #
    # def middle_total(self, player):
    #     self._category_total(player, MiddleScoreItem)
    #
    # def lower_total(self, player):
    #     self._category_total(player, LowerScoreItem)
    #
    # def total(self, player):
    #     self._category_total(player, score_items())

    def bonus(self, player):
        if self.upper_total(player) < 60:
            return 0
        else:
            return 30 + 60 - self.upper_total(player)

class ScoreEntry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('score_entries', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('score_entries', lazy=True))
    score_item = db.Column(db.Enum(ScoreItem), nullable = False)
    value = db.Column(db.Integer, nullable=False)

class Die(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', backref=db.backref('dice', lazy=True))

    value = db.Column(db.Integer, nullable=False, default=6)

    def roll(self):
        self.value = randint(1,6)

players = db.Table('players',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
        db.Column('game_id', db.Integer, db.ForeignKey('game.id'), nullable=False))
