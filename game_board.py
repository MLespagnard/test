import blessed

def update_UI(game, term):
    """All about the board .
    
    Parameters
    
    game: the main game dictionary (dict)
    
    Version
    
    specification: Jan
    Writer: Jan Peters (v.2 28/03/2026)
    """
    width = game['map']['width']
    height = game['map']['height']
    spawn = game['map']['spawn']
    spur = game['map']['spur']
    
    symbols = {
        'barbarian': 'B ',
        'healer': 'H ',
        'mage': 'M ',
        'rogue': 'R ',
        'bear': '🐻',
        'wolf': '🐺',
        'spawn': '🏛️ ',
        'spur': '⛰️ '
    }
    
    grid = {}
    for r in range(1, height + 1):
        for c in range(1, width + 1):
            grid[(r, c)] = {
                'heroes': [], 
                'creatures': [], 
                'spawn_player': 0, 
                'is_spur': False
            }

    for pid in [1, 2]:
        if pid in spawn:
            spawn_r = spawn[pid][0]
            spawn_c = spawn[pid][1]
            if (spawn_r, spawn_c) in grid:
                grid[(spawn_r, spawn_c)]['spawn_player'] = pid
                
    for coords in spur:
        spur_r = coords[0]
        spur_c = coords[1]
        if (spur_r, spur_c) in grid:
            grid[(spur_r, spur_c)]['is_spur'] = True
            
    for pid in [1, 2]:
        for hname in game['players'][pid]['heroes']:
            hero = game['players'][pid]['heroes'][hname]
            if hero['hp'] > 0:
                hr = hero['loc'][0]
                hc = hero['loc'][1]
                if (hr, hc) in grid:
                    grid[(hr, hc)]['heroes'].append([pid, hero])
                    
    for creature in game['creatures']:
        if creature['hp'] > 0:
            cr = creature['loc'][0]
            cc = creature['loc'][1]
            if (cr, cc) in grid:
                grid[(cr, cc)]['creatures'].append(creature)

    print(term.home + term.clear, end='')
    
    board_lines = []
    
    for r in range(1, height + 1):
        line_str = ""
        
        for c in range(1, width + 1):
            cell = grid[(r, c)]
            heroes_here = cell['heroes']
            creatures_here = cell['creatures']
            
            hero_count = len(heroes_here)
            if hero_count == 1:
                bg = term.on_black
            elif hero_count == 2:
                bg = term.on_green
            elif hero_count == 3:
                bg = term.on_white
            elif hero_count >= 4:
                bg = term.on_yellow
            else:
                bg = term.on_black

            display_str = '  '
            fg = term.normal
            
            if len(heroes_here) > 0:
                last_hero = heroes_here[-1]
                hero_pid = last_hero[0]
                the_hero = last_hero[1]
                
                if hero_pid == 1:
                    fg = term.blue
                else:
                    fg = term.red
                    
                hero_type = the_hero['type']
                if hero_type in symbols:
                    display_str = symbols[hero_type]
                else:
                    display_str = 'H '
                
            elif len(creatures_here) > 0:
                the_creature = creatures_here[0]
                cname = the_creature['name'].lower()
                
                if 'bear' in cname:
                    display_str = symbols['bear']
                elif 'wolf' in cname:
                    display_str = symbols['wolf']
                else:
                    display_str = '👾'
                    
            elif cell['spawn_player'] != 0:
                if cell['spawn_player'] == 1:
                    fg = term.blue
                else:
                    fg = term.red
                display_str = symbols['spawn']
                
            elif cell['is_spur'] == True:
                display_str = symbols['spur']
                
            else:
                fg = term.white
                if (r + c) % 2 == 0:
                    display_str = '░░'
                else:
                    display_str = '▒▒'
                    
            if len(display_str) == 1:
                display_str = display_str + ' '
                 
            line_str = line_str + bg + fg + display_str + term.normal
            
        board_lines.append(line_str)

    info_lines = []
    info_lines.append(term.bold + "=== STATISTIQUES ===" + term.normal)
    info_lines.append("")
    
    tours_team_1 = str(game['players'][1]['tours_on_spur'])
    total_tours = str(game['map']['consecutive_tours'])
    info_lines.append(term.blue + term.bold + "ÉQUIPE 1 (Bleu) - Éperon: " + tours_team_1 + " / " + total_tours + term.normal)
    
    for hname in game['players'][1]['heroes']:
        hero = game['players'][1]['heroes'][hname]
        if hero['hp'] <= 0:
            state = "Mort"
        else:
            state = str(hero['hp']) + "/" + str(hero['max_hp']) + " PV"
            
        h_symb = ""
        if hero['type'] in symbols:
            h_symb = symbols[hero['type']]
            
        hero_text = "  " + h_symb + hname + " : " + state + " | CD: " + str(hero['cooldown'])
        info_lines.append(term.blue + hero_text + term.normal)
        
    info_lines.append("")
    
    tours_team_2 = str(game['players'][2]['tours_on_spur'])
    info_lines.append(term.red + term.bold + "ÉQUIPE 2 (Rouge) - Éperon: " + tours_team_2 + " / " + total_tours + term.normal)
    
    for hname in game['players'][2]['heroes']:
        hero = game['players'][2]['heroes'][hname]
        if hero['hp'] <= 0:
            state = "Mort"
        else:
            state = str(hero['hp']) + "/" + str(hero['max_hp']) + " PV"
            
        h_symb = ""
        if hero['type'] in symbols:
            h_symb = symbols[hero['type']]
            
        hero_text = "  " + h_symb + hname + " : " + state + " | CD: " + str(hero['cooldown'])
        info_lines.append(term.red + hero_text + term.normal)
        
    info_lines.append("")
    
    info_lines.append(term.bold + "CRÉATURES" + term.normal)
    for creature in game['creatures']:
        if creature['hp'] > 0:
            cname_lower = creature['name'].lower()
            if 'bear' in cname_lower:
                c_symb = symbols['bear']
            elif 'wolf' in cname_lower:
                c_symb = symbols['wolf']
            else:
                c_symb = '👾'
                
            info_lines.append("  " + c_symb + " " + creature['name'] + " : " + str(creature['hp']) + " PV")

    current_round = str(game['status']['round'])
    print(term.bold + term.center("=== LEAGUE OF NAMUR - TOUR " + current_round + " ===") + term.normal)
    print()
    
    board_length = len(board_lines)
    info_length = len(info_lines)
    
    if board_length > info_length:
        max_lines = board_length
    else:
        max_lines = info_length
        
    for i in range(max_lines):
        if i < board_length:
            left_text = board_lines[i]
        else:
            left_text = " " * (width * 2) 
            
        if i < info_length:
            right_text = info_lines[i]
        else:
            right_text = "" 
            
        print(left_text + "    " + right_text)
        
    print()