from towns import towns
import characters
from newdetails import is_leap_year


def test_no_town_visits_itself():
    assert not [t for t, info in towns.items() if t in info["hexes to"]]


def test_character_classes():
    assert "paladin" in characters.classes


def test_leapyear():
    assert is_leap_year(2004)
    assert is_leap_year(2000)
    assert not is_leap_year(1900)
    assert not is_leap_year(1901)
