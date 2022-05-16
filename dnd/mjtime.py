import pendulum as p
from math import ceil


def week_of_year(d: p.Date):
    """Week of year defined such that January 1st through 7th are week 1, and some (all?) years have a 53rd week.
    This contrasts with Pendulum's builtin date.week_of_year(), which uses the ISO year, and so some early days in January are often part of week 53 of the previous year!"""
    return ceil(d.day_of_year / 7)
