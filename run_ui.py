import blessed
from game_board import update_UI
import data_structures

term = blessed.Terminal()

with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    update_UI(data_structures, term)
    print(term.move_down(2))
    input("Press Enter to exit...")
