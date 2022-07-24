from random import *
from decimal import Decimal, getcontext
import json
import copy

import click
from details import *
from math import floor
from pathlib import Path
import mage_spells
from datetime import datetime
import dnd_globals
import characters
from characters import (
    classes,
    races,
    con_max_hp_increase_adjustment,
    dex_initiative_ranged_attacks_mod,
    dex_ac_mod,
    str_attack_mod,
    str_damage_mod,
    wis_charm_illusion_save_mod,
    wis_bonus_cleric_druid_spells,
    cha_max_henchmen,
    default_literate,
    bodymass_hitdice,
    roll_dice,
    calc_height_weight,
    height_weight_roll,
    dice_to_text,
    mod_to_text,
)
import details
from jsonize import MyEncoder

template = {
    "background seed": 0,
    "name": "",
    "height": 0,  # 0 * u.inch, TODO use these once I've used pint Quantities for height/weight ranges in characters.races
    "weight": 0,  # 0 * u.lb,
    "sex": "",
    "race": "",
    "class": "",
    "level": 0,
    "birthday": "",
    "player username": "",
    "strength": 0,
    "dexterity": 0,
    "constitution": 0,
    "wisdom": 0,
    "intelligence": 0,
    "charisma": 0,
    "weapon proficiencies": [],
    "choosable weapons": [],
    "encumbrance modifier": Decimal(1),  # was enc_mult
    "money modifier": Decimal(
        1
    ),  # this one will get deleted once it's applied; was money_mult
    "added age": dict(),
    "XP": 0,
    "mass hit dice": "",
    "mass HP": 0,
    "class HP": 0,
    "maximum HP": 0,
    "current HP": 0,
    "spells known": dict(),
    "choosable spells": {},
    "chosen sage studies": [],
    "bonus sage studies": dict(),  # bard dabbling, or else originating from generated background; key: name, val: dice rolled for points at each level up
    "chosen sage fields": [],  # first field is chosen automatically based on sage study chosen at first level
    "sage points": dict(),
    "money": dict(),
    "credit": dict(),
    "hair color": "",
    "hair condition": "",
    "eye color": "",
    "inventory": dict(),
    "equipment slots": dict(),
    "literate": False,
    "has family": True,
    "background": dict(),
    "conditions": [],
}


# todo 2021-08-15 asssign NAMES to the family members o h thats a splendid idea!
# and draw up a rudimentary family tree!!!!

# todo display "years spent in training" in final output as component of age
# todo enhance that, also displaying "years spent prison" (at first, can assume 1 stretch of prison before training ... later, can break it up into multiple sentences, which will require something like PC.years list... or PC.lifetime ... ultimately these will all become "modifier" dicts hanging off the main PC, which will be read and converted into printed output)

getcontext().prec = 3
getcontext().rounding = ROUND_HALF_DOWN


def advantage_magnitude(abi_score):
    """Subtract a d20 roll from the score. This results in a value from -17 (worst: score of 3 minus rolled 20) to +17 (best: score of 18 minus rolled 1), which determines the nature of background characteristic granted by this ability score.
    TODO fixme: the range was originally assumed to be -17 to 17, but now that racial ability score adjustments are used, the range is 2-19. Furthermore it is probably hardcoded in many other places that -17/+17 are the edges."""
    roll = randint(1, 20)
    result = abi_score - roll
    return result


def input_sex():
    def get_sex():
        return input("Enter sex:\n").lower()

    sex = get_sex()
    males = {"m", "male", "man", "boy"}
    females = {"f", "female", "woman", "girl"}
    while sex not in males.union(females):
        print("Invalid sex.")
        sex = get_sex()
    if sex in males:
        return "male"
    else:
        return "female"


def input_ability_score(prompt, race="human"):
    def get_score():
        """This function requires exception handling beyond that of other BG input functions such as get_charclass() because recovering from failed integer cast requires exception handling."""
        while True:
            try:
                score = input("Enter " + prompt.capitalize() + ":\n")
                score = int(score)
            except ValueError:
                print("That doesn't look like a number.")
                continue
            else:
                return score

    # TODO extract this to rules or globals or races.py as racial maximums per stat, based on their modifiers
    score = get_score()
    if race == "human":
        minimum = 3
        maximum = 18
    else:
        minimum = 2
        maximum = 19
    while score < minimum:
        print(str(score) + " is too low.")
        score = get_score()
    while score > maximum:
        print(str(score) + " is too high.")
        score = get_score()
    return score


def input_charclass():
    def get_charclass():
        return input("Enter character class:\n").lower()

    pClass = get_charclass()
    while pClass not in classes:
        print("Invalid class.")
        pClass = get_charclass()
    return pClass


def input_race():
    def get_race():
        return input("Enter race:\n").lower()

    race = get_race()
    while race not in races:
        print("Invalid race.")
        race = get_race()
    return race


# todo put this in class_tables?
base_age = {
    "fighter": 15,
    "paladin": 19,
    "ranger": 17,
    "cleric": 20,
    "druid": 20,
    "mage": 22,
    "illusionist": 24,
    "thief": 17,
    "assassin": 19,
    "monk": 22,
}


def age_before_training():
    return 12


def years_in_training(PC):
    pass


def starting_age(pClass):
    # todo automatically incorporate aging effects - calculated and applied AFTER details have been determined AND char has been generated (because eg "+X years in prison" need to be added)
    base = base_age[pClass]
    if pClass in ["fighter", "paladin", "ranger"]:
        base += randint(1, 4)
    elif pClass in ["cleric", "druid"]:
        base += randint(2, 4)
    elif pClass in ["mage", "illusionist"]:
        base += randint(1, 6) + randint(1, 6)
    else:
        base += randint(1, 3)
    return base


def random_height_weight(race, sex):
    source = height_weight_roll()
    # bell curve for 4d6 has peak at 14:  ((6 * 4) + (1 * 4)) / 2 = 14
    # TODO instead of hardcoding 14, use code from race webpages to find average
    avg = 14
    height, weight = calc_height_weight(race, sex, source, avg)
    return height, weight


def inches_to_feet_and_inches(arg):
    feet = arg // 12
    inches = arg % 12
    return (feet, inches)


def abilities_above_ten(a_PC):
    return {
        ability: points - 10
        for ability, points in characters.ability_scores(a_PC).items()
        if (points - 10) >= 1
    }


def choose_father_ability(above_tens):
    choices = []
    for ability, points in above_tens.items():
        choices.extend([ability] * points)
    chosen = choice(choices)
    return (chosen, above_tens[chosen])


def parent_profession(a_PC):
    above_average_scores = abilities_above_ten(a_PC)
    if not above_average_scores:
        # no character scores above 10
        # (cannot happen for main PCs, given the "above 15" rule, but can happen for henchmen)
        return "peasant"
    else:
        chosen_ability, delta_10 = choose_father_ability(above_average_scores)
        mapping = {
            "strength": profession_strength,
            "dexterity": profession_dexterity,
            "constitution": profession_constitution,
            "wisdom": profession_wisdom,
            "intelligence": profession_intelligence,
            "charisma": profession_charisma,
        }
        return mapping[chosen_ability]()


@click.command()
@click.option(
    "--testing",
    default=False,
    help="If true, program uses testing data instead of interactive input.",
)
@click.option(
    "--charclass",
    help="If given, and --testing was also given, program creates a character with the given class.",
)
@click.option(
    "--race",
    help="If given, and --testing was also given, program creates a character with the given race.",
)
def create_character(testing, charclass, race):
    c = copy.deepcopy(template)
    c["background seed"] = randint(0, 1000000000)
    seed(c["background seed"])
    c["level"] = 1
    if testing:
        if charclass and race and charclass not in races[race]["permitted classes"]:
            raise ValueError(f"{charclass} not allowed for {race}")
        if charclass:
            c["class"] = charclass
        else:
            theclasses = races[race]["permitted classes"] if race else classes.keys()
            charclass = choice(list(theclasses))
        if race:
            c["race"] = race
        else:
            theraces = (
                [r for r in races if charclass in races[r]["permitted classes"]]
                if charclass
                else races.keys()
            )
            race = choice(list(theraces))
        c["class"] = charclass
        c["race"] = race
        # TODO incorporate racial ability modifiers (see input_ability_score for useful code)
        for abi, minimum in classes[c["class"]]["ability minimums"].items():
            c[abi] = randint(minimum, 18)
        for abi in characters.abilities.keys():
            if not c.get(abi):
                c[abi] = randint(3, 18)
        c["sex"] = choice(["male", "female"])
        c["name"] = "Foobar" + datetime.now().isoformat()
    else:
        c["class"] = input_charclass()
        c["race"] = input_race()
        for abi in characters.abilities.keys():
            c[abi] = input_ability_score(abi.capitalize(), c["race"])
        c["sex"] = input_sex()
        c["name"] = input("Enter character name:\n")

    c["height"], c["weight"] = random_height_weight(c["race"], c["sex"])

    # TODO this detail sets the has_family flag, so it has to come before relationships
    c["background"]["family composition"] = details.family_composition(
        advantage_magnitude(c["strength"]), c
    )
    c["background"]["father profession"] = parent_profession(c)
    c["background"]["father legacy"] = details.legacy(
        c, c["background"]["father profession"]
    )
    c["background"]["feats of strength"] = details.feats(
        advantage_magnitude(c["strength"]), c
    )
    c["background"]["relationships"] = details.relationships(
        advantage_magnitude(c["wisdom"]), c
    )
    c["background"]["tendencies"] = details.tendencies(
        advantage_magnitude(c["wisdom"]),
        c,
    )
    c["background"]["choices"] = details.choices(
        advantage_magnitude(c["intelligence"]), c
    )
    c["background"]["beauty"] = details.beauty(
        advantage_magnitude(c["charisma"]), advantage_magnitude(c["charisma"]), c
    )

    c["background"]["robustness"] = details.robustness(
        advantage_magnitude(c["constitution"]), c
    )
    c["background"]["agility and coordination"] = details.agility_coordination(
        advantage_magnitude(c["dexterity"]), c
    )

    # mass HD must be calculated before final weight so it doesn't incorporate weight modifiers
    # TODO if new character is a henchman, don't give max class HD for first level
    c["class HP"] = int(classes[c["class"]]["hit die"][1:])
    con_hp = con_max_hp_increase_adjustment(c["constitution"], c["class"])
    mass_hd = bodymass_hitdice(c["weight"])
    c["mass hit dice"] = dice_to_text(mass_hd)
    bodymass_hp = roll_dice(mass_hd)
    c["mass HP"] = bodymass_hp
    c["maximum HP"] = c["class HP"] + con_hp + bodymass_hp
    c["current HP"] = c["maximum HP"]

    age = starting_age(c["class"]) + sum(c["added age"].values())
    c["birthday"] = details.birthday(age)
    base_hair = details.get_base_hair_color()
    c["eye color"] = details.get_eye_color(base_hair)
    hcolor, hdesc, hcond = details.make_final_hair(
        base_hair, age, c["constitution"], c["sex"]
    )
    c["hair color"] = hcolor
    if hdesc and hcond:
        c["hair condition"] = ", ".join([hdesc, hcond])
    elif hdesc:
        c["hair condition"] = hdesc
    elif hcond:
        c["hair condition"] = hcond
    else:
        c["hair condition"] = ""

    if default_literate(c["class"]):
        # override any background result which would prevent literacy
        c["literate"] = True

    base_money = Decimal(20) + Decimal(randint(2, 6) * 10)
    c["money"] = dict(gp=int(base_money * c["money modifier"]))

    if c["class"] == "mage":
        c["choosable spells"][1] = mage_spells.get_pickable_spells(c["intelligence"])

    print(json.dumps(c, cls=MyEncoder, sort_keys=True, indent=2))


if __name__ == "__main__":
    create_character()
