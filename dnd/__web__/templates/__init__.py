import re
from pathlib import Path
from web import tx
from dnd import to_fewest_coins, to_copper_pieces
from dnd import characters
from characters import mod_to_text, final_abilities

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
]


def titlecase(s):
    def helper(s):
        # don't change all-caps items, which are probably abbreviations ... sigh, if only we had *structures* instead of strings... (text 'blah blah blah' (abbr 'CIA' :full 'Central Intelligence Agency') 'blah blah blah')
        return s if s.isupper() else s.capitalize()

    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: helper(mo.group(0)), s)


def static_dir():
    return Path(__file__).parent.parent / "static"


def ana(word):
    if not word:
        raise ValueError()
    elif word[0] in ("a", "e", "i", "o", "u"):
        return "an"
    else:
        return "a"
