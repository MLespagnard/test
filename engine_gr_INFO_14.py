import math
import time
import blessed
from remote_play import create_connection, get_remote_orders, notify_remote_orders, close_connection


def open_file(filename, mode='r'):
    """Opens a file and returns the content.
    
    Parameters
    filename: the name of the file to open (str)
    mode: the mode in which to open the file ('r' for read) (str)
    
    Returns
    content: The content of the file (dict)
    
    Version
    specification: Célia Gehlen (v.2 05/03/2026)
    Writer: Célia Gehlen (v.2 28/03/2026)
    """
    content = {'map': {}, 'spawn': {}, 'spur': [], 'creatures': []}
    sections = {'map:': 'map', 'spawn:': 'spawn', 'spur:': 'spur', 'creatures:': 'creatures'}

    with open(filename, mode, encoding='utf-8') as file:
        lines = file.readlines()

    current_section = None
    spawn_id = 1
    for line in lines:
        line = line.strip()
        if line:
            section = sections.get(line)
            if section:
                current_section = section
            elif current_section:
                if current_section == 'map':
                    content['map'] = {'height': int(line.split()[0]),
                                      'width': int(line.split()[1]), 
                                      'rounds': int(line.split()[2])}
                elif current_section == 'spawn':
                    r, c = map(int, line.split())
                    content['spawn'][spawn_id] = (r, c)
                    spawn_id += 1
                elif current_section == 'spur':
                    r, c = map(int, line.split())
                    content['spur'].append((r, c))
                elif current_section == 'creatures':
                    parts = line.split()
                    creature = {'name': parts[0],
                                'loc': (int(parts[1]), int(parts[2])),
                                'hp': int(parts[3]), 
                                'damage': int(parts[4]), 
                                'range': int(parts[5])}
                    content['creatures'].append(creature)
    return content


def get_information_player(game, player_id):
    """Shows information of the player, when a player_id is given.
    
    Parameters
    game: the main game dictionary (dict)
    player_id: the id of the player (1 or 2) (int)
    
    Returns
    player_info: A dictionary containing the player's information (dict)
    
    Version
    specification: Jan Peters
    Writer: Costermans David (V.1 19/03/2026)
    """
    player_info = {}
    if player_id == 1:
        player_info = game['players'][1]
    elif player_id == 2:
        player_info = game['players'][2]
    return player_info


def get_information_creature(game, name):
    """Shows information of the creature, when name is given.
    
    Parameters
    game: the main game dictionary (dict)
    name: the name of the creature (str)
    
    Returns
    creature_info: A dictionary containing the creature's information (dict)
    
    Version
    specification: Jan Peters (v2. 12/03/2026)
    Writer: Lespagnard Maximilien (v3. 30/03/2026)
    """
    for creature in game['creatures']:
        if creature['name'] == name:
            return creature
    return None

def get_information_heroes(game, name, player_id):
    """Shows information of the hero belonging to a player.
    
    Parameters
    game: the main game dictionary (dict)
    name: the name of the hero (str)
    player_id: the id of the player, who the hero belongs to (int)
    
    Returns
    hero_info: A dictionary containing the hero's information (dict)
    
    Version
    specification: Jan Peters (v1. 05/03/2026)
    Writer:David Costermans (V.1 19/03/2026)
    """
    hero_info = {}
    if player_id == 1:
        if name in game['players'][1]['heroes']:
            hero_info = game['players'][1]['heroes'][name]
    elif player_id == 2:
        if name in game['players'][2]['heroes']:
            hero_info = game['players'][2]['heroes'][name]
    return hero_info


def parse_orders(orders_str):
    """Parses a string of orders into a structured format.
    
    Parameters
    orders_str: the string containing orders separated by a single space (str)
    
    Returns
    parsed_orders: A list of distinct validated orders (list)
    
    Version
    specification: Costermans David
    Writer: Maximilien Lespagnard
    """
    parsed_orders = []
    if not orders_str or orders_str.strip() == "":
        return parsed_orders
    raw_orders = orders_str.split(' ')
    heroes_with_orders = []
    capacities = ["energise","stun","invigorate","immunize","fulgura","ovibus","reach","burst"]
    classes = ["barbarian", "healer", "mage", "rogue"]
    for order in raw_orders:
        if order != "":
            parts = order.split(':')
            if len(parts) >= 2:
                hero_name = parts[0]           
                # We verify our hero haven't received any order
                if hero_name not in heroes_with_orders:
                    action = parts[1]
                    order_added = False        
                    # movement order (:@r-c)
                    if action.startswith('@'):
                        coords = action[1:].split('-')
                        if len(coords) == 2 and coords[0].isdigit() and coords[1].isdigit():
                            parsed_orders.append({
                                "type": 'move',
                                "hero_name": hero_name,
                                "new_pos": {"r": int(coords[0]), "c": int(coords[1])}
                            })
                            order_added = True
                    # attack order (:*r-c)
                    elif action.startswith('*'):
                        coords = action[1:].split('-')
                        if len(coords) == 2 and coords[0].isdigit() and coords[1].isdigit():
                            parsed_orders.append({
                                "type": 'attack',
                                "hero_name": hero_name,
                                "target_pos": {"r": int(coords[0]), "c": int(coords[1])}
                            })
                            order_added = True
                    # creation order (:type)
                    elif action in classes:
                        parsed_orders.append({
                            "type": 'create',
                            "hero_name": hero_name,
                            "hero_class": action
                        })
                        order_added = True
                    # capacity order (:capacity or :capacity:r-c)
                    elif action in capacities:
                        #(ex: fulgura:10-10)
                        if len(parts) == 3:
                            coords = parts[2].split('-')
                            if len(coords) == 2 and coords[0].isdigit() and coords[1].isdigit():
                                parsed_orders.append({
                                    "type": 'capacity',
                                    "hero_name": hero_name,
                                    "capacity_name": action,
                                    "target_pos": {"r": int(coords[0]), "c": int(coords[1])}
                                })
                                order_added = True
                        # Capacité non ciblée (ex: burst)
                        elif len(parts) == 2:
                            parsed_orders.append({
                                "type": 'capacity',
                                "hero_name": hero_name,
                                "capacity_name": action
                            })
                            order_added = True
                    if order_added:
                        heroes_with_orders.append(hero_name)

    return parsed_orders


def calculate_distance(r1, c1, r2, c2):
    """Calculates the euclidian distance between two cells.
    
    Parameters
    
    r1, c1: row and column of the first cell (int)
    r2, c2: row and column of the second cell (int)
    
    Returns
    
    distance: The calculated Euclidian distance (float)
    
    Version
    
    specification: Costermans David
    Writer: Jan Peters (v2. 28/03/2026)
    """
    return math.sqrt((r2-r1)**2 + (c2-c1)**2)



def get_creature_orders(game):
    """Determines the automated orders for all creatures on the board.
    
    Parameters
    game: the main game dictionary (dict)
    
    Returns
    creature_orders: A string of orders generated by the creatures (str)
    
    Version
    specification: Costermans David
    Writer: Jan Peters (v3. 29/03/2026)
    """
    orders_str = ""
    for creature in game["creatures"]:
        cname = creature["name"]
        if not creature["hp"] > 0:
            pass
        cr,cc = creature["loc"]
        attack_range = creature["range"]
        best = None
        for pid in [1,2]:
            heroes_dict = game["players"][pid]["heroes"]
            for hname in heroes_dict:
                hero = heroes_dict[hname]
                if hero["hp"] <= 0:
                    pass
                hr,hc = hero["loc"]
                dist = calculate_distance(cr,cc,hr,hc)
                if dist > attack_range:
                    pass
                if hero["type"] == "barbarian":
                    cs = 1
                elif hero["type"] == "healer":
                    cs = 2
                elif hero["type"] == "mage":
                    cs = 3
                else:
                    cs = 4
                candidate = (dist, hero["hp"], cs, pid, hr, hc)
                if best is None or candidate < best:
                    best = candidate
        if best is not None:
            _, _, _, pid, hr, hc = best
            orders_str += f"{cname}:*{hr}-{hc}"
    return orders_str.strip()

def create_hero(game, player_id, hero_name, hero_class):
    """Creates a hero and places them on the player's spawn point.
    
    Parameters
    
    game: the main game dictionary (dict)
    player_id: the id of the player (int)
    hero_name: the unique name of the hero (str)
    hero_class: the class of the hero (str)
    
    Version
    specification: Lespagnard Maximilien
    Writer: Lespagnard Maximilien (v.3 29/03/2026)
    """
    spawn = game["map"]["spawn"][player_id]

    hp = 10
    max_hp = 10
    dmg = 2

    if hero_class == "barbarian":
        hp = 15
        max_hp = 15
    elif hero_class == "rogue":
        dmg = 3

    game["players"][player_id]["heroes"][hero_name] = {
        "type": hero_class,
        "level": 1,
        "hp": hp,
        "max_hp": max_hp,
        "damage": dmg,
        "loc": spawn,
        "powers": [],
        'cooldown': 0,
        'effects': {
            'stunned': False,
            'immune': False,
            'blocked': False,
            'extra_dmg': 0
        }
    }


def get_cells_in_range(hero_position):
    """Gives back all cells that are in range of selected hero.
    
    Parameters
    hero_position: the position of the selected hero (dict)

    Returns
    attackable_cells: a list of cells that are in range (dict)

    Version
    specification: Célia Gehlen (v.2 09/04/2026)
    Writer: Célia Gehlen (v.3 09/04/2026)
    """
    hero_r = hero_position['r']
    hero_c = hero_position['c']
    attackable_cells = []
    for r in range(hero_r - 1, hero_r + 2):
        for c in range(hero_c - 1, hero_c + 2):
            if (r, c) != (hero_r, hero_c):
                attackable_cells.append((r, c))

    return attackable_cells


def apply_special_capabilities_barbarian(game, parsed_orders, player_id):
    """Applies the effects of special capabilities invoked by heroes.
    
    Parameters
    
    game: the main game dictionary (dict)
    orders: the parsed orders containing special capability invocations (list/dict)
    
    Version
    
    specification: Célia Gehlen (v.2 19/03/2026)
    Writer: Célia Gehlen (v.3 01/04/2026)
    """
    current_player = player_id
    capacities = []

    for order in parsed_orders:
        if order['type'] == 'capacity':
            capacities.append(order['capacity_name'])

    if current_player == 1:
        opponent_player = 2
    else:
        opponent_player = 1

    for hero_info in game['players'][current_player]['heroes'].values():
        if hero_info['type'] == 'barbarian':
            hero_pos = {'r': hero_info['loc'][0], 'c': hero_info['loc'][1]}
            if 'energise' in capacities and 'stun' not in capacities:
                hero_info['powers'].append('extra_dmg')
                hero_info['powers'].append('energise')
                hero_info['effects']['extra_dmg'] += 2
                hero_info['cooldown'] = 1
            elif 'stun' in capacities  and 'energise' not in capacities:
                for opponent_hero_info in game['players'][opponent_player]['heroes'].values():
                    opponent_pos = (opponent_hero_info['loc'][0], opponent_hero_info['loc'][1])
                    if opponent_pos in get_cells_in_range(hero_pos):
                        opponent_hero_info['effects']['stunned'] = True
                for creature in game['creatures']:
                    creature_pos = (creature['loc'][0], creature['loc'][1])
                    if creature_pos in get_cells_in_range(hero_pos):
                        creature['effects']['stunned'] = True
                hero_info['powers'].append('stun')
                hero_info['cooldown'] = 1


def apply_special_capabilities_healer(game, parsed_orders, player_id):
    """Applies the effects of special capabilities invoked by the healer.
    
    Parameters
    
    game: the main game dictionary (dict)
    orders: the parsed orders containing special capability invocations (list/dict)
    
    Version
    
    specification:Célia Gehlen (v.2 19/03/2026)
    Writer: Célia Gehlen (v.3 01/04/2026)
    """
    capacities = []
    for order in parsed_orders:
        if order['type'] == 'capacity':
            capacities.append(order['capacity_name'])

    target_pos = None
    for order in parsed_orders:
        if order['type'] == 'capacity' and order['capacity_name'] in ['invigorate', 'immunize']:
            target_pos = order.get('target_pos')

    current_player = player_id

    for hero_info in game['players'][current_player]['heroes'].values():
        if hero_info['type'] == 'healer':
            hero_pos = {'r': hero_info['loc'][0], 'c': hero_info['loc'][1]}
            if 'invigorate' in capacities and 'immunize' not in capacities:
                for ally_hero_name, ally_hero_info in game['players'][current_player]['heroes'].items():
                    ally_pos = {'r': ally_hero_info['loc'][0], 'c': ally_hero_info['loc'][1]}
                    if ally_pos in get_cells_in_range(hero_pos):
                        if ally_hero_info['hp'] > 0:
                            ally_hero_info['hp'] = (ally_hero_info['hp'] + 3) if (ally_hero_info['hp'] + 3) <= ally_hero_info['max_hp'] else ally_hero_info['max_hp']
                            hero_info['powers'].append('heal')
                            hero_info['cooldown'] = 1
            elif 'immunize' in capacities and 'invigorate' not in capacities:
                for ally_hero_name, ally_hero_info in game['players'][current_player]['heroes'].items():
                    if target_pos and ally_hero_info['loc'] == (target_pos['r'], target_pos['c']):
                        ally_hero_info = game['players'][current_player]['heroes'][ally_hero_name]
                        if ally_hero_info['hp'] > 0:
                            ally_hero_info['effects']['immune'] = True
                            hero_info['powers'].append('immunize')
                            hero_info['cooldown'] = 1


def apply_special_capabilities_mage(game, parsed_orders, player_id):
    """Applies the effects of special capabilities invoked by the mage.
    
    Parameters
    
    game: the main game dictionary (dict)
    orders: the parsed orders containing special capability invocations (list/dict)
    
    Version
    
    specification: Célia Gehlen (v.2 19/03/2026)
    Writer: Célia Gehlen (v.3 01/04/2026)
    """
    capacities = []
    for order in parsed_orders:
        if order['type'] == 'capacity':
            capacities.append(order['capacity_name'])

    target_pos = None
    for order in parsed_orders:
        if order['type'] == 'capacity' and order['capacity_name'] in ['fulgura', 'ovibus']:
            target_pos = order.get('target_pos')

    creatures = game['creatures']
    current_player = player_id

    if current_player == 1:
        opponent_player = 2
    else:
        opponent_player = 1

    for hero_info in game['players'][current_player]['heroes'].values():
        if hero_info['type'] == 'mage':
            if 'fulgura' in capacities and 'ovibus' not in capacities:
                if target_pos:
                    for opponent_hero_info in game['players'][opponent_player]['heroes'].values():
                        if opponent_hero_info['hp'] > 0 and opponent_hero_info['loc'] == (target_pos['r'], target_pos['c']):
                            opponent_hero_info['hp'] = (opponent_hero_info['hp'] - 5) if (opponent_hero_info['hp'] - 5) >= 0 else 0
                    for creature in creatures:
                        if creature['hp'] > 0 and creature['loc'] == (target_pos['r'], target_pos['c']):
                            creature['hp'] = (creature['hp'] - 5) if (creature['hp'] - 5) >= 0 else 0
                            hero_info['cooldown'] = 1
            if 'ovibus' in capacities and 'fulgura' not in capacities:
                if target_pos:
                    for opponent_hero_info in game['players'][opponent_player]['heroes'].values():
                        if opponent_hero_info['loc'] == (target_pos['r'], target_pos['c']):
                            opponent_hero_info['effects']['blocked'] = True
                    for creature in creatures:
                        if creature['loc'] == (target_pos['r'], target_pos['c']):
                            creature['effects']['blocked'] = True
                    hero_info['cooldown'] = 1


def apply_special_capabilities_rogue(game, parsed_orders, player_id):
    """Applies the effects of special capabilities invoked by the rogue.
    
    Parameters
    
    game: the main game dictionary (dict)
    orders: the parsed orders containing special capability invocations (list/dict)
    
    Version
    
    specification:Célia Gehlen (v.2 19/03/2026)
    Writer: Célia Gehlen (v.3 01/04/2026)
    """
    capacities = []
    for order in parsed_orders:
        if order['type'] == 'capacity':
            capacities.append(order['capacity_name'])

    creatures = game['creatures']
    target_pos = None
    for order in parsed_orders:
        if order['type'] == 'capacity' and order['capacity_name'] in ['reach', 'burst']:
            target_pos = order.get('target_pos')

    current_player = player_id
    if current_player == 1:
        opponent_player = 2
    else:
        opponent_player = 1

    for hero_info in game['players'][current_player]['heroes'].values():
        if hero_info['type'] == 'rogue':
            hero_pos = {'r': hero_info['loc'][0], 'c': hero_info['loc'][1]}
            if 'reach' in capacities and 'burst' not in capacities:
                if target_pos not in [hero['loc'] for hero in game['players'][current_player]['heroes'].values()] and target_pos not in [(creature['loc'][0], creature['loc'][1]) for creature in creatures]:
                    hero_info['loc'] = (target_pos['r'], target_pos['c'])
                    hero_info['cooldown'] = 1
            if 'burst' in capacities and 'reach' not in capacities:
                for opponent_hero_info in game['players'][opponent_player]['heroes'].values():
                    if opponent_hero_info['loc'] in get_cells_in_range(hero_pos):
                        opponent_hero_info['hp'] = (opponent_hero_info['hp'] - 3) if (opponent_hero_info['hp'] - 3) >= 0 else 0
                for creature in creatures:
                    creature_pos = (creature['loc'][0], creature['loc'][1])
                    if creature_pos in get_cells_in_range(hero_pos):
                        creature['hp'] = (creature['hp'] - 3) if (creature['hp'] - 3) >= 0 else 0
                hero_info['cooldown'] = 1


def resolve_attacks(game, orders):
    """Resolves all attack orders before any movement occurs.
    
    Parameters
    game: the main game dictionary (dict)
    orders: the parsed orders containing attacks (list/dict)
    
    Version
    specification: Lespagnard Maximilien
    Writer: Jan Peters (v.2 29/03/2026)
    """

    for order in orders:
        if order["type"] == "attack":
            attacker_name = order["hero_name"]
            tr = order["target_pos"]["r"]
            tc = order["target_pos"]["c"]
            attacker = None
            is_creature = False
            for pid in [1, 2]:
                if attacker_name in game["players"][pid]["heroes"]:
                    attacker = game["players"][pid]["heroes"][attacker_name]
                    is_creature = False
            if attacker is None:
                for c in game["creatures"]:
                    if c["name"] == attacker_name:
                        attacker = c
                        is_creature = True

            if attacker is not None:
                if is_creature:
                    ar,ac = attacker["loc"]
                    dmg = attacker["damage"]
                else:
                    if attacker["hp"] > 0:
                        ar,ac = attacker["loc"]
                        dmg = attacker["damage"] + attacker["effects"]["extra_dmg"]
                    else:
                        dmg = None

                if dmg is not None:
                    dist = calculate_distance(ar, ac, tr, tc)
                    if dist > 0 and dist < 2:
                        # damage heroes
                        for pid in [1, 2]:
                            for hname, hero in game["players"][pid]["heroes"].items():
                                if hero["loc"] == (tr,tc):
                                    if not hero["effects"]["immune"]:
                                        hero["hp"] = hero["hp"] - dmg

                        # damage creatures
                        for cr in game["creatures"]:
                            if cr["loc"] == (tr,tc):
                                cr["hp"] -= dmg



def resolve_moves(game, orders):
    """Resolves all movement orders.
    
    Parameters
    
    game: the main game dictionary (dict)
    orders: the parsed orders containing movements (list/dict)
    
    Version
    specification: Costermans David
    Writer: Célia Gehlen (v5. 09/04/2026)
    """
    for move_order in orders:
        if move_order.get("type") == "move":
            pid = move_order["player_id"]
            hname = move_order["hero_name"]
            new_pos = move_order["new_pos"]
            new_loc = (new_pos["r"], new_pos["c"])

            hero = None
            if pid in [1, 2]:
                if hname in game["players"][pid]["heroes"]:
                    hero = game["players"][pid]["heroes"][hname]
            if hero is not None:
                occupied = (
                    [hero["loc"] for hero in game["players"][1]['heroes'].values()] +
                    [hero["loc"] for hero in game["players"][2]['heroes'].values()] +
                    [creature["loc"][0] for creature in game["creatures"]])
                if new_loc not in occupied:
                    hero["loc"] = new_loc


def level_up_and_clean(game):
    """Removes dead entities from the board and applies level ups.
    
    Parameters
    
    game: the main game dictionary (dict)
    
    Version
    
    specification: Jan Peters
    Writer: Costermans David(V.2 28/03/2026)
    """
    for pid in [1, 2]:
        to_delete = []
        for hname, hero in game["players"][pid]["heroes"].items():
            if hero["hp"] <= 0:
                to_delete.append(hname)
        for hname in to_delete:
            del game["players"][pid]["heroes"][hname]
    surviving_creatures = []
    for creature in game["creatures"]:
        if creature["hp"] > 0:
            surviving_creatures.append(creature)
    game["creatures"] = surviving_creatures


def check_game_over(game):
    """Checks if the game end conditions are met (victory or draw).
    
    Parameters
    
    game: the main game dictionary (dict)
    
    Returns
    
    is_over: True if the game is over, False otherwise (bool)
    
    Version
    specification: Jan Peters
    Writer: David Costermans(V.1 19/03/2026)
    """
    is_over = False
    objective = game['map']['consecutive_tours']
    if game['players'][1]['tours_on_spur'] >= objective:
        is_over = True
    elif game['players'][2]['tours_on_spur'] >= objective:
        is_over = True
    elif game['status']['idle_tours'] >= 40:
        is_over = True
    return is_over


def play_game(map_path, group_1, type_1, group_2, type_2):
    """Main function to play a game.
    
    Parameters
    map_path: path of map file (str)
    group_1: group of player 1 (int)
    type_1: type of player 1 ('human', 'AI', 'remote') (str)
    group_2: group of player 2 (int)
    type_2: type of player 2 ('human', 'AI', 'remote') (str)
    
    Returns
    No return
    
    Version
    specification: Costermans David
    Writer: Costermans David (v.3 30/03/2026)
    """
    from game_board import update_UI
    from final_AI import get_ai_orders

    term = blessed.Terminal()
    game_data = open_file(map_path)
    game = {}
    game['map'] = {}
    game['map']['width'] = game_data['map']['width']
    game['map']['height'] = game_data['map']['height']
    game['map']['consecutive_tours'] = game_data['map']['rounds']
    game['map']['spawn'] = game_data['spawn']
    game['map']['spur'] = game_data['spur']
    game['players'] = {}
    game['players'][1] = {}
    game['players'][1]['heroes'] = {}
    game['players'][1]['tours_on_spur'] = 0
    game['players'][1]['type'] = type_1
    game['players'][2] = {}
    game['players'][2]['heroes'] = {}
    game['players'][2]['tours_on_spur'] = 0
    game['players'][2]['type'] = type_2
    game['creatures'] = game_data['creatures']
    game['status'] = {}
    game['status']['round'] = 1
    game['status']['idle_tours'] = 0

    connection = None
    if type_1 == 'remote':
        connection = create_connection(group_2, group_1)
    if type_2 == 'remote':
        connection = create_connection(group_1, group_2)

    while check_game_over(game) is False:
        print("\n--- TOUR " + str(game['status']['round']) + " ---")
        orders_1_str = ""
        if type_1 == 'remote':
            orders_1_str = get_remote_orders(connection)
        if type_1 == 'AI':
            orders_1_str = get_ai_orders(game, 1)
        if type_1 == 'human':
            orders_1_str = input("Joueur 1 (Groupe " + str(group_1) + "), entrez vos ordres : ")
        if type_2 == 'remote':
            notify_remote_orders(connection, orders_1_str)
        orders_2_str = ""
        if type_2 == 'remote':
            orders_2_str = get_remote_orders(connection)
        if type_2 == 'AI':
            orders_2_str = get_ai_orders(game, 2)
        if type_2 == 'human':
            orders_2_str = input("Joueur 2 (Groupe " + str(group_2) + "), entrez vos ordres : ")

        if type_1 == 'remote':
            notify_remote_orders(connection, orders_2_str)

        creature_orders_str = get_creature_orders(game)

        orders_1 = parse_orders(orders_1_str)
        orders_2 = parse_orders(orders_2_str)
        creature_orders = parse_orders(creature_orders_str)

        for order in orders_1:
            order['player_id'] = 1
            if order['type'] == 'create':
                create_hero(game, 1, order['hero_name'], order['hero_class'])
        for order in orders_2:
            order['player_id'] = 2
            if order['type'] == 'create':
                create_hero(game, 2, order['hero_name'], order['hero_class'])

        all_parsed_orders = []
        for o in orders_1:
            all_parsed_orders.append(o)
        for o in orders_2:
            all_parsed_orders.append(o)
        for o in creature_orders:
            all_parsed_orders.append(o)

        apply_special_capabilities_barbarian(game, all_parsed_orders, 1)
        apply_special_capabilities_healer(game, all_parsed_orders, 1)
        apply_special_capabilities_mage(game, all_parsed_orders, 1)
        apply_special_capabilities_rogue(game, all_parsed_orders, 1)

        apply_special_capabilities_barbarian(game, all_parsed_orders, 2)
        apply_special_capabilities_healer(game, all_parsed_orders, 2)
        apply_special_capabilities_mage(game, all_parsed_orders, 2)
        apply_special_capabilities_rogue(game, all_parsed_orders, 2)

        level_up_and_clean(game)
        resolve_attacks(game, all_parsed_orders)
        resolve_moves(game, all_parsed_orders)
        level_up_and_clean(game)
        spur_cells = game['map']['spur']
        
        for pid in [1, 2]:
            player_on_spur = False
            
            for hero in game['players'][pid]['heroes'].values():
                if hero['hp'] > 0 and hero['loc'] in spur_cells:
                    player_on_spur = True
    
        
            if player_on_spur:
                game['players'][pid]['tours_on_spur'] += 1
            else:
                game['players'][pid]['tours_on_spur'] = 0
        game['status']['round'] = game['status']['round'] + 1
        update_UI(game, term)
        time.sleep(0.5)

    if connection is not None:
        close_connection(connection)
    print("\n===========================")
    print("   LA PARTIE EST TERMINÉE !  ")
    print("===========================")
    
if __name__ == "__main__":
    play_game("map.lon", 14, "AI", 0, "AI")