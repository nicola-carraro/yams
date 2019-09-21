from .helpers import MAX_PLAYERS, SCORE_ENTRIES
from flask import session
from .state import State
from yattag import Doc


BUTTONS = ["new", "roll", "hold"]

BUTTON_ACTIVATED = {}
BUTTON_ACTIVATED["waiting"] = {"new": True, "roll": False, "hold": False}
BUTTON_ACTIVATED["play"] = {"new": False, "roll": True, "hold": True}
BUTTON_ACTIVATED["mark"] = {"new": False, "roll": False, "hold": False}
BUTTON_ACTIVATED["done"] = {"new": True, "roll": False, "hold": False}




def ui(state):
    result = {}
    result["buttons"] = buttons(state)
    result["dice"] = dice(state)
    result["score" ] =  score_table(state)

    return result


def buttons(state):
    stage = state.get_stage()
    result = {}
    for button in BUTTONS:
        result[button] = BUTTON_ACTIVATED[stage][button]
    return result

def dice(state):
    result = ""
    dice = state.get_dice()
    for i in range(5):
        die = dice.get_die(i)
        box_id = "single-dice-box-%i" %i
        box_klass = "single-dice-box %i-value-box" %die
        img_id = "dice-img-%i" %i
        img_klass = "dice-img %i-value-img" %die
        img_src = "./static/img/dice-%i.png" %die
        img_alt = "%i dice" %die
        doc, tag, text = Doc().tagtext()
        with tag("div", id=box_id, klass=box_klass):
            with tag("img", id=img_id, klass=img_klass, src=img_src, alt=img_alt):
                pass
        result = result + doc.getvalue()
    return result


def score_table(state):
    result = {}
    for entry in SCORE_ENTRIES:
        result[entry] = score_row(state, entry)
    return result


def score_row (state, entry):
    result = ""
    for player_index in range(MAX_PLAYERS):
        result = result + score_cell(state, entry, player_index)
    return result

def score_cell(state, entry, player_index):
    active = (player_index == state.get_active_player())
    id = "%s-cell-player-%i-" % (entry, player_index)
    klass = "score-cell player-%i-score-cell %s-score-cell" % (player_index, entry)
    if active:
        klass = klass + " active"

    doc, tag, text = Doc().tagtext()
    with tag("div", id=id, klass=klass):
        text = _score_cell_content(state, entry, player_index)
    return doc.getvalue()

def _score_cell_content(state, entry, player_index):
    players = state.get_players()
    if player_index >= len(players):
        return ""
    player = players[player_index]
    if not player:
        return ""
    return str(player[entry])
