from dnd import towns
from dnd.details import is_leap_year
from dnd.wilderness import wilderness_damage_chance


def test_no_town_visits_itself():
    assert not [t for t, info in towns.items() if t in info["hexes to"]]


def test_leapyear():
    assert is_leap_year(2004)
    assert is_leap_year(2000)
    assert not is_leap_year(1900)
    assert not is_leap_year(1901)


def test_wilderness_damage_chance():
    abis = {"constitution": 12, "dexterity": 10, "wisdom": 10}
    assert (15, 0) == wilderness_damage_chance(1, "none", abis)
    assert (3, 0) == wilderness_damage_chance(1, "hard boots", abis)
    assert (0, 7) == wilderness_damage_chance(1, "hard boots", abis, 10)
