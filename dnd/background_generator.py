import click
from random import *
from decimal import *
from decimal import Decimal
from details import *
from math import floor
from pathlib import Path
import mage_spells
from datetime import datetime
import dnd_globals
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
    dice_to_text,
    mod_to_text,
)

# todo 2021-08-15 asssign NAMES to the family members o h thats a splendid idea!
# and draw up a rudimentary family tree!!!!

# todo add XP field to PC; add "bonus_xp" field to PC; write XP field in final output; check char's scores against class bonus xp minimums to (1) add "+{PC.bonus_XP}% bonus XP gain" in final output if needed (2) reduce wordiness of "if character doesn't receive min xp due to abilities, they get it anyway; if they already receive bonus xp, they start game with free XP"

# todo display "years spent in training" in final output as component of age
# todo enhance that, also displaying "years spent prison" (at first, can assume 1 stretch of prison before training ... later, can break it up into multiple sentences, which will require something like PC.years list... or PC.lifetime ... ultimately these will all become "modifier" dicts hanging off the main PC, which will be read and converted into printed output)

getcontext().prec = 3
getcontext().rounding = ROUND_HALF_DOWN


def advantage_magnitude(abi_score):
    """Subtract a d20 roll from the score.
        This results in a value from -17 (worst) to +17 (best),
        which determines the nature of background characteristic granted by this ability score.

    todo fixme: the range is assumed to be -17 to 17, but if racial (or other) ability score adjustments are used, the range will be 2-19 or even 1-20 (depending on the adjustments used).
    furthermore it is probably hardcoded in many other places that -17/+17 are the edges."""
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

    # todo extract this to rules or globals or races.py as racial maximums per stat, based on their modifiers
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


def calc_height_weight(race, sex):
    source = randint(1, 6) + randint(1, 6) + randint(1, 6) + randint(1, 6)
    # bell curve for 4d6 has peak at 14:  ((6 * 4) + (1 * 4)) / 2 = 14
    avg = 14
    deviation = source - avg
    # low source, e.g. 4, means 4 - 14 = -10
    # high source, e.g. 18, means 18 - 14 = 4
    height_mod = 1 + (deviation * Decimal(0.01))
    weight_mod = 1 + (deviation * Decimal(0.025))

    height = height_mod * races[race]["base height"][sex]
    weight = weight_mod * races[race]["base weight"][sex]
    return (round(height), weight)


def calc_max_encumbrance(race, sex, strength, weight, enc_mult):
    # character's relative heaviness or lightness compared with average member of species
    personal_proportion = weight / races[race]["base weight"][sex]
    # character race's relative heaviness or lightness compared with humans
    # the heavier your species, the less 1 lb of stuff encumbers you, whether from the weight or the awkwardness of carrying a load
    racial_proportion = (
        races[race]["base weight"][sex] / races["human"]["base weight"][sex]
    )
    # the stronger, the more you can carry
    strength_factor = racial_proportion * (5 * strength)
    base_encumbrance = races[race]["base weight"][sex] / Decimal(3)
    ideal_max_encumbrance = (personal_proportion * base_encumbrance) + strength_factor
    # miscellaneous factors, such as those from background details
    actual_max = ideal_max_encumbrance * enc_mult
    return actual_max


# 2021-08-15
# todo redefine as function mapping weights to penalties
def encumbrance_penalty_cutoffs(max_enc):
    """Calculate the encumbrance levels at which character suffers reduced Action Points."""
    max_enc = Decimal(max_enc)
    nopenalty = Decimal(0.4) * max_enc
    minus1penalty = Decimal(0.55) * max_enc
    minus2penalty = Decimal(0.7) * max_enc
    minus3penalty = Decimal(0.85) * max_enc
    # between the -3 penalty cutoff and max_enc, the penalty is -4
    return nopenalty, minus1penalty, minus2penalty, minus3penalty


def inches_to_feet_and_inches(arg):
    feet = arg // 12
    inches = arg % 12
    return (feet, inches)


# 2021-08-15
# having e.g. Strength as a field on PC struc
# is bad. should be a map field within the PC struct
# with keys being bility enums (strings if you HAVE To but thats dumb) adn values being abi scores
# one use case for this: being able to get races['orc']['strength'] modifier and add that to new_pc['abilities']['strength'], with that code generic to all 6 abilities, rather than having to switch on a string 6 times to add to the corrent ability score field (pc.strength, pc.wisdom, etc.)
# AS USUAL, python inconsistency of data access between dict entries and object fields is an irritation ----- especially in light of fields being a dict under hte hood anyway, IIRC!
def function1(a_PC):
    abilities = [
        ("Strength", a_PC.Strength),
        ("Dexterity", a_PC.Dexterity),
        ("Constitution", a_PC.Constitution),
        ("Intelligence", a_PC.Intelligence),
        ("Wisdom", a_PC.Wisdom),
        ("Charisma", a_PC.Charisma),
    ]
    above_tens = [
        (ability, points - 10) for (ability, points) in abilities if (points - 10) >= 1
    ]
    return dict(above_tens)


def function2(above_tens):
    choices = []
    for ability, points in above_tens.items():
        choices.extend([ability] * points)
    chosen = choice(choices)
    return (chosen, above_tens[chosen])


def parent_profession(a_PC):
    above_average_scores = function1(a_PC)
    if not above_average_scores:
        # no character scores above 10
        # (cannot happen for main PCs, given the "above 15" rule, but can happen for henchmen)
        return None
    else:
        chosen_ability, delta_10 = function2(above_average_scores)
        # todo change to {'strength' : profession_strength, 'wisdom' : ...} dictionary, and select within that
        # in general, prefer map lookups to literal switches -- ie prefer data to imperative code
        if chosen_ability == "Strength":
            return profession_strength()
        elif chosen_ability == "Dexterity":
            return profession_dexterity()
        elif chosen_ability == "Constitution":
            return profession_constitution()
        elif chosen_ability == "Wisdom":
            return profession_wisdom()
        elif chosen_ability == "Intelligence":
            return profession_intelligence()
        else:
            return profession_charisma()


class PC:
    def __init__(self):
        # todo: distinguish between values/variables used only in character generation, and values which characterize the resulting PC
        # e.g. money_mult
        # this will come into play when *returning a PC object* (whether it's a PC instance, or perhaps utlimately a ditionary) for use in the rest of the game code, storing in database, etc.
        # eventually there may be no diference (eg why not keep around the "added age" var from prison detail so you always know how long that was?) but at current time no reason to worry those cases

        self.seed = randint(0, 1000000000)
        self.pClass = ""
        self.race = ""
        self.Strength = 0
        self.Dexterity = 0
        self.Constitution = 0
        self.Intelligence = 0
        self.Wisdom = 0
        self.Charisma = 0
        self.weight = 0  # pounds
        self.height = 0  # inches
        self.sex = ""
        # multiply this by final calculated "ideal" max enc. to determine final max enc
        self.enc_mult = Decimal(1.0)
        # this will be set later, don't change it
        self.max_encumbrance = Decimal(0)
        # mult this value times default starting money to determine actual starting money
        self.money_mult = Decimal(1)
        # used to calculate abnormal weight in the case of fatness
        # (see the main function for details on how we avoid incorporating the new
        # fat weight into encumbrance -- it's a question of function-call ordering.)
        self.weight_mult = Decimal(1)
        # add this to normal starting age to get actual starting age
        self.added_age = {}
        self.credit = 0
        # set this to false if getting the orphan result
        self.has_family = True
        self.base_hair = get_base_hair_color()
        self.eye_color = get_eye_color(self.base_hair)
        # certain classes and background results will set this to true
        self.literate = False
        self.father_prof = None
        self.mother_prof = None


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
def main(testing, charclass, race):
    # todo consider how this would need to be altered if data was provided through a web interface
    c = PC()
    seed(c.seed)
    if testing:
        if charclass:
            c.pClass = charclass
        else:
            c.pClass = choice(list(classes.keys()))
        if race:
            c.race = race
        else:
            c.race = choice(list(races.keys()))
            # another spot where having abilities as a map on the character would be useful
        # todo write a function generate random ability scores which *respect class minimums* (this naive approach does not) and which also applies racial modifiers
        c.Strength = randint(3, 19)
        c.Dexterity = randint(3, 19)
        c.Wisdom = randint(3, 19)
        c.Constitution = randint(3, 19)
        c.Intelligence = randint(3, 19)
        c.Charisma = randint(3, 19)
        c.sex = choice(["male", "female"])
        c.name = "Foobar" + datetime.now().isoformat()
    else:
        c.pClass = input_charclass()
        c.race = input_race()
        # todo uncapitalize these scores
        c.Strength = input_ability_score("Strength", c.race)
        c.Dexterity = input_ability_score("Dexterity", c.race)
        c.Constitution = input_ability_score("Constitution", c.race)
        c.Intelligence = input_ability_score("Intelligence", c.race)
        c.Wisdom = input_ability_score("Wisdom", c.race)
        c.Charisma = input_ability_score("Charisma", c.race)
        c.sex = input_sex()
        c.name = input("Enter character name:\n")

    # base height and weight
    # these must be calculated BEFORE any weight modifiers, i.e. fatness,
    # are accounted for in final printed weight,
    # so that e.g. fatness does not increase player's max encumbrance
    c.height, c.weight = calc_height_weight(c.race, c.sex)

    # Calculation of background details
    # some of these internally modify other aspects of the Player record
    characters_dir = dnd_globals.dnd_dir / Path("dnd/created-characters")
    # todo write to standard out if fail to open file
    output_file = characters_dir / Path(c.name + ".txt")
    with open(output_file, "w") as f:
        # todo: except file not found, f = stndaard out instaed
        f.write("[seed " + str(c.seed))
        f.write("]\n\n")

        abis = [
            ("Strength", c.Strength),
            ("Dexterity", c.Dexterity),
            ("Constitution", c.Constitution),
            ("Intelligence", c.Intelligence),
            ("Wisdom", c.Wisdom),
            ("Charisma", c.Charisma),
        ]
        f.write("Ability scores:\n")
        for name, stat in abis:
            dots = "." * (16 - len(name))
            f.write("{0}{1}{2}".format(name, dots, stat))
            if name == "Dexterity":
                deets = [
                    "initiative/ranged attack "
                    + mod_to_text(dex_initiative_ranged_attacks_mod(stat)),
                    "AC " + mod_to_text(dex_ac_mod(stat)),
                ]
                f.write(" (" + "; ".join(deets) + ")")
            if name == "Strength":
                deets = [
                    "melee attack " + mod_to_text(str_attack_mod(stat)),
                    "melee damage " + mod_to_text(str_damage_mod(stat)),
                ]
                f.write(" (" + "; ".join(deets) + ")")
            if name == "Wisdom":
                deets = [
                    mod_to_text(wis_charm_illusion_save_mod(stat))
                    + " save vs. Charm/Illusion"
                ]
                f.write(" (" + "; ".join(deets) + ")")
                if c.pClass in ("cleric", "druid"):
                    f.write(
                        " (bonus spells: "
                        + str(wis_bonus_cleric_druid_spells(stat))
                        + ")"
                    )
            if name == "Charisma":
                f.write(" (max henchmen " + str(cha_max_henchmen(stat)) + ")")
            f.write("\n")
        f.write("Background for " + c.name + f" the {c.sex} {c.race} {c.pClass}:")
        f.write("\n\n")
        f.write("Family:")
        f.write("\n")
        # this detail sets the has_family flag, so it has to come before interpersonal
        family_detail = detail_family(advantage_magnitude(c.Strength), c)
        f.write(family_detail)
        f.write("\n\n")

        # todo when rewriting to something like "your father is/was", use a more detailed family_detail result (a dictionary or something) to inform writing "father is" or "father was"
        f.write("Your father's profession: ")
        c.father_prof = parent_profession(c)
        if c.father_prof:
            f.write(str(c.father_prof))
            f.write("\n")
            f.write("Gained from your father: ")
            f.write(profession_effect(c, c.father_prof))
        else:
            f.write("peasant")
            f.write("\n")
        f.write("\n\n")

        f.write("Feats of strength:")
        f.write("\n")
        feats_detail = detail_feats(advantage_magnitude(c.Strength), c)
        f.write(feats_detail)
        f.write("\n\n")

        f.write("Interpersonal relationships:")
        f.write("\n")
        interpersonal_detail = detail_interpersonal(advantage_magnitude(c.Wisdom), c)
        f.write(interpersonal_detail)
        f.write("\n\n")

        f.write("Tendencies:")
        f.write("\n")
        tendency_detail = detail_tendency(advantage_magnitude(c.Wisdom), c)
        f.write(tendency_detail)
        f.write("\n\n")

        f.write("Choices:")
        f.write("\n")
        choices_detail = detail_choices(advantage_magnitude(c.Intelligence), c)
        f.write(choices_detail)
        f.write("\n\n")

        f.write("Physical appearance:")
        f.write("\n")
        beauty_detail = detail_beauty(
            advantage_magnitude(c.Charisma), advantage_magnitude(c.Charisma), c
        )
        f.write(beauty_detail)
        f.write("\n\n")

        f.write("Bodily health:")
        f.write("\n")
        health_detail = detail_health(advantage_magnitude(c.Constitution), c)
        f.write(health_detail)
        f.write("\n\n")

        f.write("Agility and coordination:")
        f.write("\n")
        agility_detail = detail_agility(advantage_magnitude(c.Dexterity), c)
        f.write(agility_detail)
        f.write("\n\n")

        # todo do henchmen get max hp at first? decide thereupon - if not, need a henchman flag in PC()
        # must be calculated before final weight, so bodymass doesn't incorporate "grown fat" or "starved" modifications
        class_hp = classes[c.pClass]["hit die"][1:]
        con_hp = con_max_hp_increase_adjustment(c.Constitution, c.pClass)
        bodymass_HD = dice_to_text(bodymass_hitdice(c.weight))
        f.write(f"HP: {bodymass_HD} + {class_hp} [from class] + {con_hp} [from Con]")
        f.write("\n")

        age = starting_age(c.pClass) + sum(c.added_age.values())
        f.write("Age: " + str(age))
        f.write("\n")
        f.write("Birthday: " + birthday(age))
        f.write("\n")
        hair_info = make_final_hair(c.base_hair, age, c.Constitution, c.sex)
        hair = hair_info.haircolor
        for attribute in [hair_info.hairdesc, hair_info.haircond]:
            if attribute == "":
                pass
            else:
                hair = hair + ", " + attribute
        f.write("Hair: " + hair)
        f.write("\n")
        f.write("Eyes: " + c.eye_color)
        f.write("\n")

        # overrides any background result which would take literacy away
        if default_literate(c.pClass):
            c.literate = True
        if c.literate:
            f.write("Literate: Yes\n")
        else:
            f.write("Literate: No\n")

        base_money = Decimal(20) + Decimal(randint(2, 6) * 10)
        actual_money = base_money * c.money_mult
        f.write("Starting money: " + str(actual_money) + " gold pieces")
        f.write("\n")
        f.write("Credit: " + str(c.credit) + " gold pieces")
        f.write("\n")

        feet, inches = inches_to_feet_and_inches(c.height)
        f.write("Height: " + str(feet) + " ft. " + str(inches) + " in.")
        f.write("\n")

        # max encumbrance, incorporating changes to enc_mult made by detail calculation
        c.max_encumbrance = Decimal(
            calc_max_encumbrance(c.race, c.sex, c.Strength, c.weight, c.enc_mult)
        )
        enc_nopenalty, enc_minus1, enc_minus2, enc_minus3 = encumbrance_penalty_cutoffs(
            c.max_encumbrance
        )
        # final weight MUST be calculated AFTER max encumbrance,
        # since if the character's weight is modified to be fat, max encumbrance SHOULD NOT increase
        if c.weight_mult == Decimal(1):
            # weight is normal; character has not grown fat
            f.write("Weight: " + str(c.weight) + " lbs")
            f.write("\n\n")
        else:
            # todo more robust check: this calc assumes adjusted weight is always > old_weight, but I could add a detail where weight_mult is BELOW 1 (result of starvation, prison, etc.)
            old_weight = c.weight
            c.weight = c.weight * c.weight_mult
            diff = c.weight - old_weight
            f.write(
                "Weight: "
                + str(c.weight)
                + " lbs. (including "
                + str(diff)
                + " lbs of fat: COUNTS AGAINST ENCUMBRANCE, but can be worked off.)"
            )
            f.write("\n\n")

        f.write("Encumbrance Information:")
        f.write("\n")
        f.write("Carried weight <= " + str(enc_nopenalty) + " lbs: no AP penalty.")
        f.write("\n")
        f.write(
            str(enc_nopenalty)
            + " lbs < carried weight <= "
            + str(enc_minus1)
            + " lbs: -1 AP."
        )
        f.write("\n")
        f.write(
            str(enc_minus1)
            + " lbs < carried weight <= "
            + str(enc_minus2)
            + " lbs: -2 AP."
        )
        f.write("\n")
        f.write(
            str(enc_minus2)
            + " lbs < carried weight <= "
            + str(enc_minus3)
            + " lbs: -3 AP."
        )
        f.write("\n")
        f.write(
            str(enc_minus3)
            + " lbs < carried weight <= "
            + str(c.max_encumbrance)
            + " lbs: -4 AP."
        )
        f.write("\n")
        f.write("Above that, no movement is possible, regardless of remaining AP.")

        sas = races[c.race]["special characteristics"]
        if sas:
            f.write("\n\nRacial bonuses:\n")
            for sa in sas:
                f.write(sa + "\n")

        if c.pClass == "mage":
            f.write("\n\n")
            f.write("Pick three of these first-level spells:\n")
            for p in mage_spells.get_pickable_spells(c.Intelligence):
                f.write(p)
                f.write("\n")


if __name__ == "__main__":
    main()
