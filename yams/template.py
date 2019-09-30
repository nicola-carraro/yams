from flask import url_for

BUTTONS = ["new", "roll", "hold"]

BUTTON_ACTIVATED = {}
BUTTON_ACTIVATED["waiting"] = {"new": True, "roll": False, "hold": False}
BUTTON_ACTIVATED["play"] = {"new": False, "roll": True, "hold": True}
BUTTON_ACTIVATED["mark"] = {"new": False, "roll": False, "hold": False}
BUTTON_ACTIVATED["done"] = {"new": True, "roll": False, "hold": False}

STATES = ["waiting", "play", "mark", "over"]

SCORE_ENTRIES = ["name", "ones", "twoes", "threes", "fours", "fives", "sixes", "bonus", "upper_total", "max", "min", "middle_total", "poker", "full_house", "small_straight", "large_straight", "yams", "rigole", "lower_total", "global_total" ]


UPPER_VALUES = {"ones" : 1, "twoes" : 2, "threes" : 3, "fours" : 4, "fives" : 5, "sixes" : 6}

MIDDLE_ENTRIES = ["max", "min",]

LOWER_ENTRIES= ["poker", "full", "small_straight", "large_straight", "yams", "rigole"]

COMBINATION_ENTRIES = list(UPPER_VALUES.keys()) + MIDDLE_ENTRIES + LOWER_ENTRIES

TOTAL_ENTRIES = ["upper_total", "middle_total", "lower_total", "global_total"]

ICONS = {"ones": "one", "twoes": "two", "threes": "three", "fours": "four", "fives": "five", "sixes": "six"}


TITLES = {"name" : "Nom", "bonus": "Bonus", "upper_total": "Total I", "max" : "Supérieure", "min": "Inférieure", "middle_total": "Total II", "poker": "Carré", "full_house": "Full", "small_straight": "Petite suite", "large_straight": "Grande suite", "yams": "Yams", "rigole": "Rigole", "lower_total": "Total III", "global_total": "Global"}

def die_img(die):
    return url_for('static', filename="img/die-%i.png" %die)

def buttons(stage):
    result = {}
    for button in BUTTONS:
        result[button] = BUTTON_ACTIVATED[stage][button]
    return result


def title(entry):
    return TITLES[entry]

def icon(entry):
    #icon name is entry name without final s (e.g. "one") for "ones")
    icon_name = ICONS[entry]

    return "fa-dice-%s" %icon_name
