import web
from web import tx
import pendulum as p
from math import ceil


def game_date(db=None):
    if not db:
        db = tx.db
    query = db.select("date", what="date")[0]["date"]
    return p.from_format(query, "YYYY-MM-DD")


def week_of_year(d: p.Date):
    """Week of year defined such that January 1st through 7th are week 1, and some (all?) years have a 53rd week.
    This contrasts with Pendulum's builtin date.week_of_year(), which uses the ISO year, and so some early days in January are often part of week 53 of the previous year!"""
    return ceil(d.day_of_year / 7)


def titlecase(arg):
    """Capitalize all words in `ARG` that aren't short (and, of, in, the) or abbreviations (CIA, NBA, FBI)."""
    specials = {"and", "of", "the", "in"}
    result = arg.split(" ")
    for idx, each in enumerate(result):
        if each.isupper():
            # don't change what are probably abbreviations
            # if only we had *structures* instead of strings... (text 'blah blah blah' (abbr 'CIA' :full 'Central Intelligence Agency') 'blah blah blah')
            pass
        elif each in specials:
            result[idx] = each.capitalize() if idx == 0 else each.lower()
        else:
            result[idx] = each.capitalize()
    return " ".join(result)


def ana(word):
    if not word:
        raise ValueError()
    elif word[0] in ("a", "e", "i", "o", "u"):
        return "an"
    else:
        return "a"


def idify(s):
    """Make a string suitable for use as an HTML id."""
    s = s.lower()
    s = s.replace("'", "")
    s = s.replace('"', "")
    s = s.replace(" ", "-")
    return s


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


def mod_to_text(num):
    if num is None:
        return None
    else:
        return f"+{num}" if num >= 0 else f"{num}"

def list_ingredients(ings, linkify=False):
    if linkify:
        return [f"<a href='/tradegoods/{k}'>{k}</a>: {v}" for k, v in ings.items()]
    else:
        return [f"{k}: {v}" for k, v in ings.items()]

