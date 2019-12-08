from flask_login import current_user

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
    user = current_user._get_current_object()
    player = game.get_player(user)
    score_entry = player.get_score_entry_by_name(entry_name)
    return score_entry.value != None
