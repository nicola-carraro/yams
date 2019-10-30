
from enum import auto, Enum, IntEnum
from db import db


class ScoreItem(IntEnum):
    def __new__(cls, value, field):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.field = field
        return obj

    @property
    def name(self):
         return self._name_.lower()

class UpperScoreItem(ScoreItem):

    ONE = (1, "As")
    TWO = (2, "Deux")
    THREE = (3, "Trois")
    FOUR = (4, "Quatre")
    FIVE = (5, "Cinq")
    SIX = (6, "Six")

class MiddleScoreItem(ScoreItem):
    MIN = (7, "Inférieur")
    MAX = (8, "Supérieur")

class LowerScoreItem(ScoreItem):

    POKER = (9, "Carré")
    FULL = (10, "Full")
    SMALL_STRAIGHT = (11, "Petite suite")
    LARGE_STRAIGHT = (12, "Grande suite")
    YAMS = (13, "Yam's")
    RIGOLE = (14, "Rigole")

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
        return '<User username: %s, id: %s>' % (self.username, self.id)

    @property
    def games(self):
        sel = db.select([users_in_games.c.game_id]).where(users_in_games.c.user_id == self.id)
        rs = db.session.execute(sel)
        rows = rs.fetchall()
        games = []
        for row in rows:
            games.append(Game.query.filter_by(id=row[0]).first())
        return games




class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_player_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    current_player = db.relationship('User',
        backref=db.backref('games_current', lazy=True))
    stage = db.Column(db.Enum(GameStage), nullable = False, default = GameStage.WAITING)


    def __repr__(self):
        return '<Game id: %s, current_player_id: %s, stage: %s, players: %s>' % (self.id, self.current_player_id, self.stage, self.players)


    @property
    def players(self):
        result = None
        if self.id:
            player_ids = db.session().query(users_in_games).filter(users_in_games.c.game_id==self.id)
            result = []
            for player_id in player_ids:
                result.append(db.session.query(User).filter_by(id=player_id))
        return result

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
