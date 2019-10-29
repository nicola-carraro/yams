
from enum import auto, Enum, IntEnum
from db import db


class ScoreItem(IntEnum):
    def __new__(cls, value, field):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.field = field
        return obj

class UpperScoreItem(ScoreItem):
    ONES = (0, "As")
    TWOES = (1, "Deux")
    THREES = (2, "Trois")
    FOURS = (3, "Quatre")
    FIVES = (4, "Cinq")
    SIXES = (5, "Six")

class MiddleScoreItem(ScoreItem):
    MIN = (6, "Inférieur")
    MAX = (7, "Supérieur")

class LowerScoreItem(ScoreItem):
    POKER = (8, "Carré")
    FULL = (9, "Full")
    SMALL_STRAIGHT = (10, "Petite suite")
    LARGE_STRAIGHT = (11, "Grande suite")
    YAMS = (12, "Yam's")
    RIGOLE = (13, "Rigole")

def score_items():
    return list(UpperScoreItem) + list(MiddleScoreItem) + list(LowerScoreItem)


class GameStage(IntEnum):
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
        return '<User %r>' % self.username


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_player_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    current_player = db.relationship('User',
        backref=db.backref('games_current', lazy=True))
    stage = db.Column(db.Enum(GameStage), nullable = False, default = GameStage.WAITING)


    @property
    def players(self):
        player_ids = db.session().query(users_in_games).filter(users_in_games.c.game_id==self.id)
        players = []
        for player_id in player_ids:
            players.append(db.session.query(User).filter_by(id=player_id))
        return _self.players

    @players.setter
    def players(self, players):
        for player in players:
            sel = db.select([users_in_games]).where(db.and_(users_in_games.c.game_id == self.id, users_in_games.c.user_id == player.id))
            rs = db.session.execute(sel)
            rows = rs.fetchall()
            if len(rows) == 0:
                ins = db.insert(users_in_games).values(user_id = player.id, game_id = self.id)
                db.session().execute(ins)
            else:
                upd = db.update(users_in_games).values(user_id = player.id, game_id = self.id)
                db.session().execute(upd)
            db.session.commit()
        self._players=players


class ScoreEntry(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    game = db.relationship("Game", backref=db.backref("score_entries", lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship('User',
        backref=db.backref('score_entries', lazy=True))
    score_item = db.Column(db.Integer, nullable = False)
    value = db.Column(db.Integer, nullable=False)

class Die(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    game = db.relationship('Game', backref=db.backref('dice', lazy=True))

    value = db.Column(db.Integer, nullable=False, default=6)

    def roll(self):
        self.value = randint(1,6)

users_in_games = db.Table('users_in_games',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
        db.Column('game_id', db.Integer, db.ForeignKey('game.id'), nullable=False))
