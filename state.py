from dice import Dice
from copy import copy
from score import Score
import jsonpickle
from json import JSONEncoder




class State:


    def __init__(self):
        self._players = [None]
        self._dice = Dice()
        self._stage = "waiting"
        self._active_player = None
        self._rerolled = False




    def get_stage(self):
        return self._stage

    def get_players(self):
        return self._players.copy()

    def get_dice(self):
        return copy(self._dice)

    def get_active_player(self):
        if not self._active_player:
            return None
        return self._active_player.copy()

    def get_rerolled(self):
        return self._rerolled


    def is_game_over(self):
        for player in self._players:
            if not player.is_full_score():
                return False
        return True

    def new_game(self):
        self._players = [Player(), Player()]
        self._stage = "play"
        self.__active_player = 0
        self._dice.roll_all()



    def play(self, dice):
        self._dice.roll(dice)
        if self._rerolled:
            self.__stage() == "mark"
        self._rerolled = True


    def mark(self):
        mark_score(self, combination, self._dice.calculate_score(combination))
        if is_game_over():
            for player in self._players:
                self._stage = "over"
