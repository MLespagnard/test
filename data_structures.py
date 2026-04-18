game = {
    # Map  (Data from .lon file)
    'map': {
        'rows': 39,
        'cols': 40,
        'spur': [(20, 38), (20, 39), (21, 38), (21, 39)], 
        'spawn': {1: (20, 3), 2: (20, 38)},               
        'consecutive_tours': 25                           
    },

    # Players and its heroes 
    'players': {
        1: {
            'heroes': {
                'Albert': {
                    'type': 'barbarian', 
                    'level': 1, 
                    'hp': 15,         
                    'max_hp': 15,      
                    'damage': 2, 
                    'loc': (20, 3),   
                    'powers': [],       
                    'cooldown': 0,     
                    'effects': {       
                        'stunned': False, 
                        'immune': False, 
                        'extra_dmg': 0
                    }
                },
                'Jonathan': {
                    'type': 'healer', 'level': 1, 'hp': 10, 'max_hp': 10, 'damage': 2, 'loc': (20, 3), 
                    'powers': [], 'cooldown': 0, 
                    'effects': {'stunned': False, 'immune': False, 'extra_dmg': 0}
                },
                'Lucas': {
                    'type': 'mage', 'level': 1, 'hp': 10, 'max_hp': 10, 'damage': 2, 'loc': (20, 3), 
                    'powers': [], 'cooldown': 0, 
                    'effects': {'stunned': False, 'immune': False, 'extra_dmg': 0}
                },
                'Steve': {
                    'type': 'rogue', 'level': 1, 'hp': 10, 'max_hp': 10, 'damage': 3, 'loc': (20, 3), 
                    'powers': [], 'cooldown': 0, 
                    'effects': {'stunned': False, 'immune': False, 'extra_dmg': 0}
                }
            },
            'tours_on_spur': 0 
        },
        2: { 
            'heroes': {}, 
            'tours_on_spur': 0 
        }
    },

    'creatures': [
        {
            'name': 'bear', 
            'hp': 20, 
            'damage': 5, 
            'range': 3,       
            'loc': (10, 10), 
            'effects': {      
                'stunned': False, 
                'immune': False, 
                'extra_dmg': 0
            }
        },
        {
            'name': 'wolf', 'hp': 10, 'damage': 3, 'range': 2, 'loc': (15, 10), 
            'effects': {'stunned': False, 'immune': False, 'extra_dmg': 0}
        }
    ],
    'status': {
        'round': 1,   
        'idle_tours': 0    # Regle d'égalité (fin de la  partie après 40 tours d'inactivité)
    }
}