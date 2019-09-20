from copy import deepcopy
from helpers import is_straight, COMBINATION_ENTRIES, UPPER_VALUES
from random import randint


class Dice:

    def __init__(self, dice = [6 for i in range(5)]):
        if len(dice) != 5:
            raise ValueError("dice argument does not contain five values")
        for die in dice:
            if die not in range (1, 7):
                raise ValueError("Invalid value for die: %i" % die)
        self._dice = dice

    def __str__(self):
        return str(self._dice)

    def get_die(self, index):
        return self._dice[index]


    # Roll the dice whose indexes are in the list
    def roll(self, indexes):
        if len(indexes) > len(self._dice):
            raise ValueError("Too many indexes")

        if len(indexes) != len(set(indexes)):
            raise ValueError("Duplicate index")

        for i in indexes:
            self._dice[i] = randint(1, 6)


    def roll_all(self):
        self.roll(range(0, 5))


    def is_poker(self):
        dice = self._dice
        # If the first or the second value appear four times, we have a poker
        return (dice.count(dice[0]) >= 4) or (dice.count(dice[1]) >= 4)


    def is_full(self):
        # Sort the dice
        sorteddice =  sorted(self._dice)

        # Count frequency of first and last value
        firstcount = sorteddice.count(sorteddice[0])
        lastcount = sorteddice.count(sorteddice[-1])

        # We have a full if one value appears twice and the other appears three times
        return (firstcount == 2 and lastcount == 3) or (firstcount == 3 and lastcount == 2)



    def is_small_straight(self):
        # Sort the dice
        sorteddice = sorted(self._dice)

        # The four dice with highest value
        highsequence = sorteddice[0: -1]

        # The last four dice
        lowsequence = sorteddice[1:]

        # We have a small_straight if lowest or the highest four dice are a straight
        return is_straight(highsequence) or is_straight(lowsequence)

    def is_large_straight(self):
        # Sort the dice
        sorteddice = sorted(self._dice)

        # We have a small_straight if all the dice are a straight
        return is_straight(sorteddice)


    def is_yams(self):
        # If the first value appears five times, we have a yams
        dice = self._dice
        return dice.count(dice[0]) == 5


    def is_rigole(self):
        # Sort the dice
        sorteddice = sorted(self._dice)

        # Count frequency of first and last value
        firstcount = sorteddice.count(sorteddice[0])
        lastcount = sorteddice.count(sorteddice[-1])

        # We have a full if one value appears once and the other appears four times, and the same of the two values is 7
        if (firstcount == 4 and lastcount == 1) or (firstcount == 1 and lastcount == 4):
            return sorteddice[0] + sorteddice[-1] == 7
        else:
            return False


    def calculate_score(self, entry):

        result = 0;

        if entry not in COMBINATION_ENTRIES:
            raise ValueError("Invalid entry")

        # Upper combination: sum all dice with given values
        elif entry in UPPER_VALUES:
            result = sum(filter(lambda x: x == UPPER_VALUES[entry], self._dice))

        elif entry == "min" or entry == "max":
            result = sum(self._dice)

        elif entry == "poker" and self.is_poker():
            result = 40 + sum(self._dice)

        elif entry == "full" and self.is_full():
            result = 30 + sum(self._dice)

        elif entry == "small_straight" and self.is_small_straight():
            result = 45

        elif entry == "large_straight" and self.is_large_straight():
            result = 50

        elif entry == "yams" and self.is_yams():
            result = 50 + sum(self._dice)

        elif entry == "rigole" and self.is_rigole():
            result = 50

        return result
