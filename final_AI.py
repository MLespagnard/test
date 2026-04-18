""" Module for final AI implementation. """
import engine_gr_INFO_14 as engine

CLASS_PRIORITY = {
    "barbarian": 0,
    "healer": 1,
    "mage": 2,
    "rogue": 3
}

def get_alive_heroes(game, player_id):
    """Returns a list of alive heroes of a player.
    
    Parameters
    ----------
    game: data structure of the game that stores the all important game information.
    player_id: the player id of the AI
    
    Returns
    -------
    list of all alive heroes of the player.
    
    Version
    -------
    specification: Jan Peters (v1. 15/04/2026)
    implementation: Jan Peters (v1. 15/04/2026)
    """
    return {
        name: hero
        for name, hero in game['players'][player_id]['heroes'].items()
        if hero['hp'] > 0
    }


def get_enemy_heroes(game, player_id):
    """Returns a list of alive enemy heroes.
    
    Parameters
    ----------
    game: data structure of the game that stores the all important game information.
    player_id: the player id of the AI
    
    Returns
    -------
    list of all alive enemy heroes of the player.
    
    Version
    -------
    specification: Jan Peters (v1. 15/04/2026)
    implementation: Jan Peters (v1. 15/04/2026)
    """
    enemy_id = 2 if player_id == 1 else 1
    return {
        name: hero
        for name, hero in game['players'][enemy_id]['heroes'].items()
        if hero['hp'] > 0
    }


def get_occupied_cells(game):
    """Returns a list of occupied cells on the map.
    
    Parameters
    ----------
    game: data structure of the game that stores the all important game information.
    
    Returns
    -------
    list of all occupied cells on the map.
    
    Version
    -------
    specification: Jan Peters (v1. 15/04/2026)
    implementation: Jan Peters (v1. 15/04/2026)
    """
    occupied = set()
    for pid in [1, 2]:
        for hero in game['players'][pid]['heroes'].values():
            occupied.add(hero['loc'])
    for creature in game['creatures'].values():
        if creature['hp'] > 0:
            occupied.add(creature['loc'])
    return occupied


def choose_best_target(hero, enemies):
    """ Chooses the best target for the hero to attack. 
    The best target is the one with the lowest hp. 
    If there are multiple targets with the same hp, 
    the one with the lowest in alphabetical order is chosen.
    
    Parameters
    ----------
    hero: the hero which is being attacked by the AI (lowest hp, ...)
    enemies: a list of all alive enemy heroes of the player.
    
    Returns
    -------
    string: name of the best target for the hero to attack.
    
    Version
    -------
    specification: Jan Peters (v1. 15/04/2026)
    implementation: Jan Peters (v1. 15/04/2026)
    """
    candidates = []
    for enemy in enemies.values():
        candidates.append((
            enemy['hp'],
            engine.calculate_distance(
                hero['loc'][0], hero['loc'][1],
                enemy['loc'][0], enemy['loc'][1]
            ),
            CLASS_PRIORITY.get(enemy['type'], 999),
            enemy
        ))
    candidates.sort()
    return candidates[0][3] if candidates else None


def choose_attacking_style(hero, target):
    """ Chooses best possible attack for the hero.
    Either attack with the normal attack or with the special capability.
    Parameters
    ----------
    hero: the hero which is being attacked by the AI (lowest hp, ...)
    player_id: the player id of the AI
    game: data structure of the game that stores the all important game information.
    
    Returns
    -------
    string: attack command for the hero
    
    Version
    -------
    specification: Jan Peters (v1. 09/04/2026)
    implementation: Jan Peters (v1. 09/04/2026)
    """
    dist = engine.calculate_distance(
        hero['loc'][0], hero['loc'][1],
        target['loc'][0], target['loc'][1]
    )
    attack_order = None
    if dist < 2:
        # Special capability if cooldown is equal to 0
        if hero['cooldown'] == 0:
            if hero['type'] == "mage" and target['hp'] <= 5:
                r, c = target['loc']
                attack_order = f"{hero['name']}:fulgura:{r}-{c}"
            elif hero['type'] == "healer":
                attack_order = f"{hero['name']}:invigorate"
            elif hero['type'] == "rogue":
                attack_order = f"{hero['name']}:burst"
        # Normal attack if no special capability available or chosen
        if attack_order is None:
            r, c = target['loc']
            attack_order = f"{hero['name']}:*{r}-{c}"
    return attack_order


def move_hero(start, goal, occupied):
    """ Moves the hero towards the nearest enemy. (lowest hp, lowest in alphabetical order)
    
    Parameters
    ----------
    hero: the hero to move - when there was a hero created by the AI before.
    
    Returns
    -------
    position of the hero after movement
    
    Version
    -------
    specification: Jan Peters (v2. 15/04/2026)
    implementation: Jan Peters (v2. 15/04/2026)
    """
    sr, sc = start
    best_pos = start
    best_dist = engine.calculate_distance(sr, sc, goal[0], goal[1])
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if not (dr == 0 and dc == 0):
                nr, nc = sr + dr, sc + dc
                if (nr, nc) not in occupied:
                    dist = engine.calculate_distance(nr, nc, goal[0], goal[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_pos = (nr, nc)
    return best_pos


def get_ai_orders(game, player_id):
    """Return orders of AI.
    
    Parameters
    ----------
    game: game data structure (dict)
    player_id: player id of AI (int)

    Returns
    -------
    orders: orders of AI (str)
    
    Version
    -------
    implementation: Peters Jan (v1. 19/03/2026)
    """

    orders = []
    # determine enemy player
    if player_id == 1:
        enemy_id = 2
    else:
        enemy_id = 1
    # create first hero if none exist
    if len(game['players'][player_id]['heroes']) == 0:
        return "Hero1:barbarian"
    # build occupied cells
    occupied = set()
    for pid in [1, 2]:
        for hero in game['players'][pid]['heroes'].values():
            occupied.add(hero['loc'])
    for creature in game['creatures']:
        if creature['hp'] > 0:
            occupied.add(creature['loc'])

    if len(game['map']['spur']) > 0:
        spur_loc = game['map']['spur'][0]
    else:
        spur_loc = (1, 1) 
    for name, hero in game['players'][player_id]['heroes'].items():
        hero['name'] = name
        can_act = True
        hero['name'] = name
        can_act = True
        
        if hero['hp'] <= 0:
            can_act = False
        elif hero['effects']['stunned']:
            can_act = False
            
        if can_act:
            target = choose_best_target(hero, game['players'][enemy_id]['heroes'])
            
            attack_order = None
            if target is not None:
                attack_order = choose_attacking_style(hero, target)
            
            if attack_order is not None:
                orders.append(attack_order)
            else:
                new_pos = move_hero(hero['loc'], spur_loc, occupied)
                
                if new_pos != hero['loc']:
                    r, c = new_pos
                    orders.append(f"{name}:@{r}-{c}")
                    occupied.add(new_pos)

    return " ".join(orders)
# End of final_AI.py