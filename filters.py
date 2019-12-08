from flask_login import current_user

# Unwraps current user from current_user proxy
def current_user_obj():
    return current_user._get_current_object()

def is_current_player_active(game):
    if game == None:
        return False
    player = game.get_player(current_user_obj())
    return player.is_active

def is_current_user_playing(game):
    if not is_current_player_active(game):
        return True
    if game.is_playing:
        return True
    else:
        return False

def not_none(value):
    if value is None:
        return ''
    else:
        return value

def die_value(game, index=-1):
    if game == None:
        return 6;
    else:
        return game.get_die_value(index)

def score_value(player, score_item_name):
    if score_item_name == 'name':
        return player.user.username
    if score_item_name == 'upper_total':
        return player.upper_total
    if score_item_name == 'middle_total':
        return player.middle_total
    if score_item_name == 'lower_total':
        return player.lower_total
    if score_item_name == 'total':
        return player.total
    if score_item_name == 'bonus':
        return player.bonus

    score_entry = player.get_score_entry_by_name(score_item_name)
    if score_entry.value == None:
        return ''
    else:
        return score_entry.value

def is_score_entry_taken(game, entry_name=None):
    player = game.get_player(current_user_obj())
    score_entry = player.get_score_entry_by_name(entry_name)
    return score_entry.value != None

def is_play_button_disabled(game):
    if not is_current_user_playing(game):
        return True
    return False

def is_score_button_disabled(game):
    if not is_current_player_active(game):
        return True
    if not game.is_scoring:
        return True
    return False

def is_die_button_disabled(game):
    if not is_current_user_playing(game):
        return True
    if game.dice_rolls == 0:
        return True
    return False
