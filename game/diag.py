# diag.py
import game.logic.game_state as gs
import game.ui.screens.game_board as gb
import inspect

print("=== game_state файл ===")
print(gs.__file__)
src = inspect.getsource(gs.take_turn)
print("есть 'global_event' в take_turn:", "global_event" in src)

print()
print("=== game_board файл ===")
print(gb.__file__)
bsrc = inspect.getsource(gb.GameBoardScreen._roll_click)
print("кол-во вызовов _begin_round_if_needed:", bsrc.count("_begin_round_if_needed"))