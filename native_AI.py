# AI native - 30 à 50 lines of code
import engine_gr_INFO_14 as engine
import random

def get_AI_orders(game, player_id):
    """  
    Naive AI returning a string of orders.
    - If no hero exists, create one.
    - Otherwise, randomly move or attack with each hero.
    
    Version
    -------
    specification: Jan Peters (v.1, 25/03/2026)
    implementation: Jan Peters (v.1, 25/03/2026)
    """

    player = game['players'][player_id]
    heroes = player['heroes']
    
    height = game['map']['height']
    width = game['map']['width']
    
    # --- No existing heroes -> create one ---
    if len(heroes) == 0:
     name = f"h{player_id}_{random.randint(1, 999)}"
     hero_class = random.choice(['barbarian', 'rogue', 'mage', 'healer'])
     return f"{name}:{hero_class}"
        
    
    # --- Randomly choose actions for existing heroes ---
    orders = []
    
    for hname in heroes.keys():
        action_type = random.random()    
        action_type = random.random()
        # randomly choose behavior
        if action_type < 0.40:
            r = random.randint(1, height)  
            c = random.randint(1, width)
            orders.append(f"{hname}:@{r}-{c}")
        
        elif action_type < 0.80:
            r = random.randint(1, height)
            c = random.randint(1, width)
            orders.append(f"{hname}:*{r}-{c}")
    
                
    return " ".join(orders)