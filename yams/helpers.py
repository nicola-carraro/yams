MAX_PLAYERS = 5

STATES = ["waiting", "play", "mark", "over"]

SCORE_ENTRIES = ["name", "ones", "twoes", "threes", "fours", "fives", "sixes", "bonus", "upper_total", "max", "min", "middle_total", "poker", "full_house", "small_straight", "large_straight", "yams", "rigole", "lower_total", "global_total" ]


UPPER_VALUES = {"ones" : 1, "twoes" : 2, "threes" : 3, "fours" : 4, "fives" : 5, "sixes" : 6}

MIDDLE_ENTRIES = ["max", "min",]

LOWER_ENTRIES= ["poker", "full", "small_straight", "large_straight", "yams", "rigole"]

COMBINATION_ENTRIES = list(UPPER_VALUES.keys()) + MIDDLE_ENTRIES + LOWER_ENTRIES

TOTAL_ENTRIES = ["upper_total", "middle_total", "lower_total", "global_total"]

# Takes an iterable  of numbers, returns True  only if each number in the iterable is the successor of the previous one
def is_straight(sequence):
    for i in range(0, len(sequence) -1):
        if sequence[i] != (sequence[i + 1] - 1):
            return False
    return True
