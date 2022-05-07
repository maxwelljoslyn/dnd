import re
from pathlib import Path
from web import tx
from dnd import to_fewest_coins, to_copper_pieces, has_market
from dnd import characters
from dnd import towns
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
    "andlist",
    "has_market",
    "towns",
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


def andlist(l, separator):
    """Format a list for human-facing display, with the last item set off by 'and'.
    >>> andlist([1, 2, 3], ', ')
    '1, 2 and 3'
    """
    if not l:
        raise ValueError(f"argument list must have at least one item")
    elif len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return f"{l[0]} and {l[1]}"
    else:
        initials = separator.join([str(x) for x in l[:-1]])
        final = f" and {l[-1]}"
        return initials + final
