from collections import OrderedDict
from .helpers import UPPER_VALUES, SCORE_ENTRIES, MIDDLE_ENTRIES, LOWER_ENTRIES

class Score:

    def __init__(self, name):
        self._score = OrderedDict()
        self._score["name"] = name
        for entry in SCORE_ENTRIES:
            self._score[entry] = name

    def get_score():
        return self._score.copy()

    def calculate_upper_total():
        return sum([self._score[entry] for entry in UPPER_VALUES])

    def calculate_middle_total():
        if self._score[min] < self._score[max]:
            return sum([self._score[entry] for entry in MIDDLE_ENTRIES])
        else:
            return 0

    def calculate_lower_total():
        return sum([self._score[entry] for entry in LOWER_ENTRIES])

    def calculate_global_total():
        return calculate_upper_total() + calculate_middle_total() + calculate_lower_total()

    def calculate_bonus():
        upper_total = calculate_upper_total()
        if upper_total < 60:
            return 0
        else:
            return 30 + 60 - upper_total

    def mark_score(combination, score):
        if not self._score[combination]:
            self._score[combination] = self._score[combination] + score
        else:
            raise ValueError("Combination already taken")

    def markfinal_score():
        self._score["upper_total"] = calculate_upper_total()
        self._score["middle_total"] = calculate_middle_total()
        self._score["lower_total"] = calculate_lower_total()
        self._score["global_total"] = calculate_global_total()
