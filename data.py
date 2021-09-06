import math


class Modifier():
    def __init__(self, **kwargs):
        pass

ability_scores = {
        "strength",
        "wisdom",
        "constitution",
        "dexterity",
        "intelligence",
        "charisma"
}

classes = {
        "assassin", "cleric", "druid", "fighter", "illusionist", "mage",
        "monk", "paladin", "ranger", "thief"
}

races = {
        "human", "elf", "halforc", "halfling", "gnome", "dwarf"
}

permitted_classes = {
        "human": classes,
        "elf": {"fighter", "thief", "assassin", "mage", "cleric", "druid", "ranger"},
        "halforc": {"thief", "assassin", "fighter", "cleric", "ranger"},
        "halfling": {"fighter", "thief", "assassin", "druid"},
        "gnome": {"fighter", "thief", "assassin", "illusionist", "druid", "ranger"},
        "dwarf": {"fighter", "thief", "assassin", "monk"}
}

racial_ability_bonuses = {
        "human": {},
        "elf":  dict(intelligence=1, constitution=-1),
        "halforc":  dict(strength=1, wisdom=-1),
        "halfling": dict(dexterity=1, strength=-1),
        "gnome": dict(wisdom=1, dexterity=-1),
        "dwarf": dict(constitution=1, charisma=-1)
}

def SaveMod(Modifier):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)



def elf_save_bonus(intelligence):
    """0-3 +0, 4-6 +1, 7-10 +2, etc."""
    value = min(5, math.floor(intelligence / 3.5))
    return SaveMod(effect="charm", value=value)


def gnome_save_bonus(wisdom):
    """0-3 +0, 4-6 +1, 7-10 +2, etc."""
    value = min(5, math.floor(wisdom / 3.5))
    return SaveMod(effect="illusion", value=value)


def dwarf_save_bonus(constitution):
    """0-3 +0, 4-6 +1, 7-10 +2, etc."""
    value = min(5, math.floor(constitution / 3.5))
    return [SaveMod(effect="magic", value=value),
            SaveMod(effect="poison", value=value)]
