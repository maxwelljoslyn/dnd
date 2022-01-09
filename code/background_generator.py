from random import *
from decimal import *
from details import *
from math import floor
from pathlib import Path
import mage_spells
from datetime import datetime
import dnd_globals
from characters import classes, races

# 2021-08-15 asssign NAMES to the family members o h thats a splendid idea!
# and draw up a rudimentary family tree!!!!

# 18h = area where 18 (or 3) are hardcoded as limits of PC ability score spectrum (no longer true once races are added)

getcontext().prec = 3
getcontext().rounding = ROUND_HALF_DOWN

def advantage_magnitude(abi_score):
    """Subtract a d20 roll from the score.
    This results in a value from -17 (worst) to +17 (best),
    which determines the nature of background characteristic granted by this ability score.

todo fixme: the range is assumed to be -17 to 17, but if racial (or other) ability score adjustments are used, the range will be 2-19 or even 1-20 (depending on the adjustments used).
furthermore it is probably hardcoded in many other places that -17/+17 are the edges."""
    roll = randint(1,20)
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
        return int(input("Enter "+prompt.capitalize()+":\n"))
    score = get_score()
    # todo extract this to rules or globals or races.py as racial maximums per stat, based on their modifiers
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
        "monk": 22
}

def starting_age(pClass):
    base = base_age[pClass]
    if pClass in ["fighter", "paladin", "ranger"]:
        base += randint(1,4)
    elif pClass in ["cleric", "druid"]:
        base += randint(2,4)
    elif pClass in ["mage", "illusionist"]:
        base += randint(1,6) + randint(1,6)
    else:
        base += randint(1,3)
    return base

def calc_height_weight(race, sex):
    source = randint(1,6) + randint(1,6) + randint(1,6) + randint(1,6)
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


def ideal_encumbrance(race, sex, strength):
    base = races[race]["base weight"][sex] / Decimal(3)
    return base + (5 * strength)

def calc_max_encumbrance(race, sex, strength, weight, enc_mult):
    proportion = weight / races[race]["base weight"][sex]
    ideal_max_encumbrance = ideal_encumbrance(race, sex, strength) * proportion
    actual_max = ideal_max_encumbrance * enc_mult
    return actual_max

# 2021-08-15
# todo redefine as function mapping weights to penalties
def encumbrance_penalty_cutoffs(max_enc):
    """Calculate the encumbrance levels at which character suffers reduced Action Points."""
    max_enc = Decimal(max_enc)
    nopenalty =   Decimal(0.4) * max_enc
    minus1penalty = Decimal(0.55) * max_enc
    minus2penalty = Decimal(0.7) * max_enc
    minus3penalty = Decimal(0.85) * max_enc
    # between the -3 penalty cutoff and max_enc, the penalty is -4
    return nopenalty, minus1penalty, minus2penalty, minus3penalty

def inches_to_feet_and_inches(arg):
    feet =  arg // 12
    inches = arg % 12
    return (feet, inches)


# 2021-08-15
# having e.g. Strength as a field on PC struc
# is bad. should be a map field within the PC struct
# with keys being bility enums (strings if you HAVE To but thats dumb) adn values being abi scores
# one use case for this: being able to get races['orc']['strength'] modifier and add that to new_pc['abilities']['strength'], with that code generic to all 6 abilities, rather than having to switch on a string 6 times to add to the corrent ability score field (pc.strength, pc.wisdom, etc.)
# AS USUAL, python inconsistency of data access between dict entries and object fields is an irritation ----- especially in light of fields being a dict under hte hood anyway, IIRC!
def function1(a_PC):
    abilities = [("Strength", a_PC.Strength),
                 ("Dexterity", a_PC.Dexterity),
                 ("Constitution", a_PC.Constitution),
                 ("Intelligence", a_PC.Intelligence),
                 ("Wisdom", a_PC.Wisdom),
                 ("Charisma", a_PC.Charisma)]
    filtered = [(a[0], a[1] - 10) for a in abilities if (a[1] - 10) >= 1]
    return dict(filtered)

def function2(above_tens):
    choices = []
    for name, points in above_tens.items():
        choices.extend([name] * points)
    chosen = choice(choices)
    return (chosen, above_tens[chosen])

def parent_profession(a_PC):
    above_average_scores = function1(a_PC)
    if above_average_scores == []:
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
            
class PC():
    def __init__(self):
        # todo: distinguish between values/variables used only in character generation, and values which characterize the resulting PC
        # e.g. money_mult
        # this will come into play when *returning a PC object* (whether it's a PC instance, or perhaps utlimately a ditionary) for use in the rest of the game code, storing in database, etc.
        # eventually there may be no diference (eg why not keep around the "added age" var from prison detail so you always know how long that was?) but at current time no reason to worry those cases

        self.seed = randint(0,1000000000)
        self.pClass = ""
        self.race = ""
        self.Strength = 0
        self.Dexterity = 0
        self.Constitution = 0
        self.Intelligence = 0
        self.Wisdom = 0
        self.Charisma = 0
        self.weight = 0 # pounds
        self.height = 0 # inches
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
        self.added_age = 0
        self.credit = 0
        # set this to false if getting the orphan result
        self.has_family = True
        self.base_hair = get_base_hair_color()
        self.eye_color = get_eye_color(self.base_hair)
        # certain classes and background results will set this to true
        self.literate = False
        self.father_prof = None
        self.mother_prof = None



# todo consider how this would need to be altered if data was provided through a web interface
def main():
    c = PC()
    seed(c.seed)
    testing = False
    if testing:
        c.pClass = "mage"
        c.Strength, c.Dexterity, c.Wisdom, c.Constitution, c.Intelligence, c.Charisma = 12,18,12,12,12,12
        c.sex = "male"
        c.name = "Foobar" + datetime.now().isoformat()
    else:
        c.pClass = input_charclass()
        c.race = input_race()
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
    characters_dir = dnd_globals.dnd_dir / Path("code/created-characters")
    # todo write to standard out if fail to open file
    output_file = characters_dir / Path(c.name + ".txt")
    with open(output_file, "w") as f:
        # todo: except file not found, f = stndaard out instaed
        f.write("[seed " + str(c.seed))
        f.write("]\n\n")

        abis = [("Strength",c.Strength),
                ("Dexterity",c.Dexterity),
                 ("Constitution",c.Constitution),
                 ("Intelligence",c.Intelligence),
                 ("Wisdom",c.Wisdom),
                 ("Charisma",c.Charisma)]
        f.write("Ability scores:\n")
        for name, stat in abis:
            dots = "." * (16 - len(name))
            f.write("{0}{1}{2}".format(name,dots,stat))
            f.write("\n")
        f.write("Background for " + c.name + f" the {c.race} {c.pClass}:")
        f.write("\n\n")
        f.write("Family:")
        f.write("\n")
        # this detail sets the has_family flag, so it has to come before interpersonal
        family_detail = detail_family(advantage_magnitude(c.Strength),c)
        f.write(family_detail)
        f.write("\n\n")

        f.write("Your father's profession: ")
        c.father_prof = parent_profession(c)
        f.write(str(c.father_prof))
        f.write("\n")
        f.write("Gained from your father: ")
        f.write(profession_effect(c,c.father_prof))
        f.write("\n\n")
        

        f.write("Feats of strength:")
        f.write("\n")
        feats_detail = detail_feats(advantage_magnitude(c.Strength),c)
        f.write(feats_detail)
        f.write("\n\n")

        f.write("Interpersonal relationships:")
        f.write("\n")
        interpersonal_detail = detail_interpersonal(advantage_magnitude(c.Wisdom),c)
        f.write(interpersonal_detail)
        f.write("\n\n")

        f.write("Tendencies:")
        f.write("\n")
        tendency_detail = detail_tendency(advantage_magnitude(c.Wisdom),c)
        f.write(tendency_detail)
        f.write("\n\n")

        f.write("Choices:")
        f.write("\n")
        choices_detail = detail_choices(advantage_magnitude(c.Intelligence),c)
        f.write(choices_detail)
        f.write("\n\n")

        f.write("Physical appearance:")
        f.write("\n")
        beauty_detail = detail_beauty(advantage_magnitude(c.Charisma),advantage_magnitude(c.Charisma),c)
        f.write(beauty_detail)
        f.write("\n\n")

        f.write("Bodily health:")
        f.write("\n")
        health_detail = detail_health(advantage_magnitude(c.Constitution),c)
        f.write(health_detail)
        f.write("\n\n")

        f.write("Agility and coordination:")
        f.write("\n")
        agility_detail = detail_agility(advantage_magnitude(c.Dexterity),c)
        f.write(agility_detail)
        f.write("\n\n")

        age = starting_age(c.pClass) + c.added_age
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

        # override any background result which would take literacy away
        if c.pClass in ["mage", "illusionist", "cleric", "druid"]:
            c.literate = True
        if c.literate:
            f.write("Literate: Yes\n")
        else:
            f.write("Literate: No\n")
        
        base_money = Decimal(20) + Decimal(randint(2,6) * 10)
        actual_money = base_money * c.money_mult
        f.write("Starting money: " + str(actual_money) + " gold pieces")
        f.write("\n")
        f.write("Credit: " + str(c.credit) + " gold pieces")
        f.write("\n")

        feet, inches = inches_to_feet_and_inches(c.height)
        f.write("Height: " + str(feet) + " ft. " + str(inches) + " in.")
        f.write("\n")

        # max encumbrance, incorporating changes to enc_mult made by detail calculation
        c.max_encumbrance = Decimal(calc_max_encumbrance(c.race, c.sex, c.Strength, c.weight, c.enc_mult))
        enc_nopenalty, enc_minus1, enc_minus2, enc_minus3 = encumbrance_penalty_cutoffs(c.max_encumbrance)
        # final weight MUST be calculated AFTER max encumbrance,
        # since if the character's weight is modified to be fat, max encumbrance SHOULD NOT increase
        if c.weight_mult == Decimal(1):
            # weight is normal; character has not grown fat
            f.write("Weight: " + str(c.weight) + " lbs")
            f.write("\n\n")
        else:
            # todo more robust check: this calc assumes adjusted weight is always > old_weight, but I could add a detail where weight_mult is BELOW 1 (result of starvation, prison, etc.)
            old_weight = c.weight
            adjusted_weight = c.weight * c.weight_mult
            diff = adjusted_weight - old_weight
            f.write("Weight: " + str(adjusted_weight) + " lbs; " + str(diff) + " lbs of this is fat. Counts against encumbrance! Can be worked off.")
            f.write("\n\n")

        f.write("Encumbrance Information:")
        f.write("\n")
        f.write("Carried weight <= " + str(enc_nopenalty) + " lbs: no AP penalty.")
        f.write("\n")
        f.write(str(enc_nopenalty) + " lbs < carried weight <= " + str(enc_minus1) + " lbs: -1 AP.")
        f.write("\n")
        f.write(str(enc_minus1) + " lbs < carried weight <= " + str(enc_minus2) + " lbs: -2 AP.")
        f.write("\n")
        f.write(str(enc_minus2) + " lbs < carried weight <= " + str(enc_minus3) + " lbs: -3 AP.")
        f.write("\n")
        f.write(str(enc_minus3) + " lbs < carried weight <= " + str(c.max_encumbrance) + " lbs: -4 AP.")
        f.write("\n")
        f.write("Above that, no movement is possible, regardless of remaining AP.")

        if c.pClass == "mage":
            f.write("\n\n")
            f.write("Pick one of these first-level spells:\n")
            for p in mage_spells.get_pickable_spells(c.Intelligence):
                f.write(p)
                f.write('\n')

if __name__ == "__main__":
    main()
