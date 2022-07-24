import re
from pathlib import Path
from web import tx
from dnd import to_fewest_coins, to_copper_pieces, has_market
from dnd import characters
from dnd import towns
from dnd import game_date
from dnd import titlecase, ana, andlist, mod_to_text, idify, list_ingredients
from characters import final_abilities

__all__ = [
    "tx",
    "titlecase",
    "Path",
    "static_dir",
    "to_fewest_coins",
    "to_copper_pieces",
    "mod_to_text",
    "characters",
    "final_abilities",
    "ana",
    "andlist",
    "idify",
    "list_ingredients",
    "has_market",
    "towns",
    "game_date",
]


def static_dir():
    return Path(__file__).parent.parent / "static"
