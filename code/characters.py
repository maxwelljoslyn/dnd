import math
import random
from class_tables import classes
from decimal import Decimal
from collections import Counter
from weapons import weapons


def inclusive_range(a, b):
    """A range that includes the argument b, unlike the builtin range(). In mathematical terms, inclusive_range is closed on both ends, while range() is open on one end.

    This library contains many calculations on numberic ranges which always closed on both ends. Calling a specific function to represent this helps avoid a common source of off-by-1 errors."""
    return range(a, b + 1)


def ir(a, b):
    """Alias for inclusive_range."""
    # todo how can I aoid the extra function call?
    # some languages have an alias mechanism
    return inclusive_range(a, b)


abilities = {
    "strength",
    "wisdom",
    "constitution",
    "dexterity",
    "intelligence",
    "charisma",
}

martial_classes = {"assassin", "fighter", "paladin", "ranger"}

races = {
    # there are half-elves, but they are played as humans (halfelf) or elves (halfhuman); ditto halfdwarves
    "human": {
        "ability modifiers": None,
        "permitted classes": set(classes.keys()),
        "base height": {"male": Decimal(70), "female": Decimal(66)},  # inches
        "base weight": {"male": Decimal(175), "female": Decimal(140)},  # pounds
        "special characteristics": None,
    },
    "elf": {
        "ability modifiers": dict(intelligence=1, constitution=-1),
        "permitted classes": {
            "fighter",
            "thief",
            "assassin",
            "mage",
            "illusionist",
            "cleric",
            "druid",
            "ranger",
        },
        "base height": {"male": Decimal(60), "female": Decimal(54)},  # inches
        "base weight": {"male": Decimal(120), "female": Decimal(85)},  # pounds
        "special characteristics": [
            "+1 on attacks with bows and with one-handed swords (i.e. shortsword and longsword)",
            "+1 on saves vs. Charm-school magic at 4/7/11/14/18 points of Intelligence",
        ],
    },
    "halforc": {
        "ability modifiers": dict(strength=1, charisma=-1),
        "permitted classes": {"thief", "assassin", "fighter", "cleric", "ranger"},
        "base height": {"male": Decimal(65), "female": Decimal(60)},  # inches
        "base weight": {"male": Decimal(150), "female": Decimal(120)},  # pounds
        "special characteristics": None,
    },
    "halfling": {
        "ability modifiers": dict(dexterity=1, strength=-1),
        "permitted classes": {"fighter", "thief", "druid"},
        "base height": {"male": Decimal(36), "female": Decimal(32)},  # inches
        "base weight": {"male": Decimal(75), "female": Decimal(55)},  # pounds
        "special characteristics": [
            "+3 on attacks with slings",
        ],
    },
    "gnome": {
        "ability modifiers": dict(wisdom=1, constitution=-1),
        "permitted classes": {
            "fighter",
            "thief",
            "assassin",
            "illusionist",
            "druid",
            "ranger",
        },
        "base height": {"male": Decimal(42), "female": Decimal(38)},  # inches
        "base weight": {"male": Decimal(95), "female": Decimal(75)},  # pounds
        "special characteristics": [
            "+1 on saves vs. Illusion-school magic at 4/7/11/14/18 points of Wisdom",
        ],
    },
    "dwarf": {
        "ability modifiers": dict(constitution=1, dexterity=-1),
        "permitted classes": {"fighter", "thief", "assassin", "monk"},
        "base height": {"male": Decimal(48), "female": Decimal(42)},  # inches
        "base weight": {"male": Decimal(140), "female": Decimal(120)},  # pounds
        "special characteristics": [
            "+1 on attacks against orcish or goblinoid defenders",
            "+3 AC against attacks from giants, ogres, and lizardmen",
            # todo how to associate this with dwarf_save_bonus function?
            # for background generator, simple way is to make a list `dwarf bonuses` and have bg print "your bonus: +N" ... but that's static, at-character-creation-time evaluation of the bonus, which would not suffice for LIVE/dynamic evaluation of bonus in situations such as "character's CON has been increased/reduced"
            # in other words, more sophistication needed for a RUNNING GAME ENVIRONMENT
            "+1 on saves vs. magic and poison at 4/7/11/14/18 points of Constitution",
        ],
    },
}


class SaveMod:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# todo convert these to
# { "type" racial "source" dwarf "effects" {"target" "constitution" "modifier" 1} }
# todo these do NOT vary with changes in the current val of an ability score?
def elf_save_bonus(intelligence):
    # todo change paraemeter to a character, and guard against passing a non-elf?
    # con: goes against defn of fun as ddeterming bonus gien intelligence
    # pro: fun is badly named and should be "elf ability baased save bonus" etc
    # the fact that I STIL don't have 'type - to insert _ in pytho mode' is such BS. emacs has had so much more attention paid to that kind of thing......
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
    return [SaveMod(effect="magic", value=value), SaveMod(effect="poison", value=value)]


def cha_max_henchmen(cha):
    """Maximum number of primary henchmen that a main PC can have at once. Primary henchmen are loyal to a main PC; secondary henchmen are loyal to primary henchmen (or, secondaries are the primaries of primaries.)"""
    # todo consider that rechecking this function as cha drops could affect whether henchmen ar eunder player's contro!
    # that's too granular for me.. this is MAX henchmen u can attract in your lifetime, not 'are  they lsitenin to u right now'
    if cha < 0:
        raise ValueError(f"cha {cha} less than 0 but ability scores can't go below 0")
    if cha == 0:
        return 0
    if cha <= 4:
        return 1
    elif cha in ir(5, 6):
        return 2
    elif cha in ir(7, 8):
        return 3
    elif cha in ir(9, 10):
        return 4
    elif cha in ir(11, 12):
        return 5
    elif cha in ir(13, 14):
        return 6
    elif cha in ir(15, 16):
        return 7
    elif cha in ir(17, 18):
        return 8
    else:
        return cha_max_henchmen(18) + 1


def str_attack_mod(s):
    """Modifier on attack rolls."""
    if s < 0:
        raise ValueError(f"s {s} less than 0 but ability scores can't go below 0")
    if s in ir(0, 2):
        return -3
    elif s in ir(3, 4):
        return -2
    elif s in ir(5, 8):
        return -1
    elif s in ir(9, 12):
        return 0
    elif s in ir(13, 16):
        return 1
    elif s in ir(17, 18):
        return 2
    elif s in ir(19, 20):
        return 3
    elif s in ir(21, 23):
        return 4
    else:
        return 5


def str_damage_mod(s):
    """Modifier on damage roll.s"""
    if s < 0:
        raise ValueError(f"s {s} less than 0 but ability scores can't go below 0")
    if s in ir(0, 2):
        return -3
    elif s in ir(3, 5):
        return -2
    elif s in ir(6, 8):
        return -1
    elif s in ir(9, 12):
        return 0
    elif s in ir(13, 15):
        return 1
    elif s in ir(16, 18):
        return 2
    elif s in ir(19, 20):
        return 3
    elif s in ir(21, 23):
        return 4
    else:
        return 5


def con_max_hp_increase_adjustment(con, char_class):
    """Amount of HP to add to each Hit Die rolled upon level up."""
    if con < 0:
        raise ValueError(f"con {con} less than 0 but ability scores can't go below 0")
    if con <= 4:
        return -2
    elif con in ir(5, 6):
        return -1
    elif con in ir(7, 13):
        return 0
    elif con in ir(14, 15):
        return 1
    elif con == 16:
        return 2
    elif con > 16 and char_class not in martial_classes:
        return 2
    else:
        if con in ir(17, 18):
            return 3
        else:
            return 4  # martial class with con 19+


# @depends("constitution")
# def con_resurrection_survival_chance(con):
#    3 40%
#    45%
#    50%
#    55%
#    60%
#    65%
#    70%
#    75%
#    80%
#    85%
#    90%
#    95%
#    96%
#    97%
#    98%
#    18+ 99%
#    pass


def con_system_shock_survival_chance(con):
    """Base percentage chance of surviving a system shock roll."""
    # todo does the code get cleaner if we dry up the repeated subexpressions below?
    if con < 0:
        raise ValueError(f"con {con} less than 0 but ability scores can't go below 0")
    base = 35
    if con <= 3:
        return base
    elif con <= 14:
        return base + ((con - 3) * 5)
    elif con <= 18:
        # at con 18, system shock rate is 98%
        return base + ((con - 3) * 5) + ((con - 14) * 2)
    else:
        return 99


def abi_mod_factory(f, attribute, pc):
    score = pc.getattr(attribute)
    if score < 0:
        raise ValueError(f"{attribute} {score} cannot be less than 0")
    return f(score)


def int_max_mage_spell_level(i):
    """Return highest level of spells that c can comprehend and cast
    this is crucial for cases of reduced intelligence; also, remember that if int dips below the minimum for mage/illusionist, they can no longer perform their functions!!!!"""
    # todo unlike some other aspects of character creation, this rule will be used and evaluated during the game
    if i < 0:
        raise ValueError(f"i {i} less than 0 but ability scores can't go below 0")
    # todo raise error if not a mage pc passed to this fun
    if i <= 8:
        return None
    if i in ir(9, 10):
        return 5
    if i in ir(11, 12):
        return 6
    if i in ir(13, 14):
        return 7
    if i in ir(15, 16):
        return 8
    else:
        return 9


def dex_ac_mod(d):
    if d < 0:
        raise ValueError(f"d {d} less than 0 but ability scores can't go below 0")
    if d <= 5:
        return -2
    elif d in ir(6, 7):
        return -1
    elif d in ir(8, 13):
        return 0
    elif d in ir(14, 15):
        return 1
    elif d in ir(16, 18):
        return 2
    else:
        return 3


def dex_initiative_ranged_attacks_mod(d):
    if d < 0:
        raise ValueError(f"d {d} less than 0 but ability scores can't go below 0")
    if d <= 2:
        return -3
    elif d in ir(3, 4):
        return -2
    elif d in ir(5, 6):
        return -1
    elif d in ir(7, 14):
        return 0
    elif d in ir(15, 16):
        return 1
    elif d in ir(17, 18):
        return 2
    else:
        return 3


def int_side_effects(i):
    # copied from https://wiki.alexissmolensk.com/index.php/Intelligence_(ability_stat)#Non-intelligent_.280_pts..29
    # for modification
    # this is meant to illuminate, for the player, the GAME  effects on the charcater (does this change my proficiencies? when do i need to make into checks to act normally?) for having a low Intelligence
    # thus playres shoudl still refer to the page linked aove for a fuller description and for inspiration o how to roleplay their low int
    if i == 3:
        return "Humanoids will be minimally communicative and animal-like in their display of emotions. They will form staunch bonds with others and will sacrifice themselves rather than let those others come to harm (though the sacrifice is not self-aware; death is a difficult concept to grasp). Fighting abilities will be instinctive; they are limited to bashing weapons. Weapons may not be hurled, not because the creature is physically incapable, but because it doesn't not occur. They are limited to daily living skills and are limited in sage abilities to adaptive or instinctive abilities [no defacto list exists at this time]. All efforts to problem solve or be alert, as well as recovering anything from memory, requires an intelligence check. "
    elif i == 4:
        return """Play is often extraordinarily aggressive or excessively idle, such as repeatedly throwing a ball against a wall for many hours at a time, mesmerized by the patterns it forms. Memories are long and grudges are common. They are not likely to judge the actions of others except when those actions directly infringe on their freedom.

Humanoids will be haltingly but moderately communicative and expressive with their emotions. They will form highly loyal bonds with fellows and may even fall in love, though they will not understand the social mores associated with relationships. They are not able to rebel against requests from trusted companions without an intelligence check. When a check succeeds, being conscious of their own limitations, they will be enormously proud of themselves.

Fighting abilities are instinctive; bashing and stabbing weapons are permissible. Weapons may be hurled. They are able to do tasks made of two-or-three steps, such as sharpening a weapon AND putting it away or eating from a plate, washing that plate and putting it away. Such things are limited to busywork; tasks that require figuring the place for something unfamiliar, sorting, locating something that can't be seen or is in an unfamiliar place, or any more complex problem requires a check. The creature can watch and be trusted to be aware in that specific direction, but being alert for something unexpected requires a check. Sage abilities must still fit into the descriptions above or are not available to the creature."""

    elif i == 5:
        return """When in simple, day-to-day situations, it is rare that any checks will need to be made. However, the alertness needed to think a player character's way through unusual environments (dungeons, dangerous and chaotic terrains, cities or streets where sensory overload is constant) will require occasional checks if there is no one else to keep the character focused. One such situation is battle.

Should surprise occur, creatures of primitive intelligence are apt not to rely upon their instincts but upon their responsibilities ~ and this may cause the creature to freeze, similar in manner to a deer but for entirely different reasons. Because of this, unless an intelligence check is made, the creature will be unable to take any action except to defend themselves for one more round than is usual. This hesistancy can be overcome, however, if a more intelligent creature, unaffected by this hesitancy, is there to shout "attack!" or similar order at the right moment, spurring lesser companions to action. Thus a chief in a primitive clan or tribe will usually have sufficient intelligence to thus lead their people.

Primitive intelligence allows the use of most hand-to-hand and hurled weapons, but discounts use of the bola, the bow, slings and like weapons that have multiple or moving parts. Common implements with moving parts require a check to use; complex implements, such an astrolabe or abacus, are beyond the creature's ken."""
    elif i in ir(6, 7):
        return "ALL ELSE IS AS NORMAL 8+ INT, save that they are, however, challenged to understand matters outside their immediate needs and positions. Even if they participate in religion, it is more mystery than belief. They are comfortable at festivals and sport; but discussions of current affairs and politics confuse them. They are apt to ignore the doings of the world. If someone should explain such things to them, it would be an intelligence check."
    else:
        return None


# todo why can't i use math.inf when it works fine at the interpreter? if cha in ir(-math.inf, 4):


def wis_charm_illusion_save_mod(w):
    if w < 0:
        raise ValueError(f"w {w} less than 0 but ability scores can't go below 0")
    if w <= 5:
        return -2
    elif w in ir(6, 8):
        return -1
    elif w in ir(9, 12):
        return 0
    elif w in ir(13, 15):
        return 1
    elif w in ir(16, 18):
        return 2
    else:
        # wis 19+
        return 3


def wis_bonus_cleric_spells(w):
    if w < 0:
        raise ValueError(f"w {w} less than 0 but ability scores can't go below 0")
    result = {}
    # higher and higher Wisdom *cumulatively* adds bonus spells
    # that's why we use multiple independent if statements to augment result
    if w < 13:
        return result
    else:
        if w in ir(14, 15):
            result[1] = 1  # one bonus 1st-level spell
        if w in ir(14, 15):
            result[2] = 1  # one bonus 2nd-level spell
        if w in ir(14, 15):
            result[3] = 1  # one bonus 3rd-level spell
        return result


def wis_max_cleric_spell_level(w):
    if w < 0:
        raise ValueError(f"w {w} less than 0 but ability scores can't go below 0")
    if w < 9:
        # cleric minimum wisdom is 9
        return None
    elif w in ir(10, 12):
        return 4
    elif w in ir(13, 14):
        return 5
    elif w in ir(15, 16):
        return 6
    else:
        # wis 17+; note that 7 is highest cleric spell level (highest mage spell level is 9)
        return 7


def wis_cleric_spell_success_percent(w):
    if w < 0:
        raise ValueError(f"w {w} less than 0 but ability scores can't go below 0")
    if w < 9:
        # cleric minimum wisdom is 9
        return None
    elif w == 9:
        return 80
    elif w == 10:
        return 90
    elif w == 11:
        return 95
    else:
        # no chance of failure
        return 100


def default_literate(klass):
    return klass in {"mage", "illusionist", "cleric", "druid"}


strength_based = [str_attack_mod, str_damage_mod]
constitution_based = [
    con_max_hp_increase_adjustment,
    con_system_shock_survival_chance,
    # con_resurrection_survival_chance,
]
dexterity_based = [
    dex_ac_mod,
    dex_initiative_ranged_attacks_mod,
]
wisdom_based = [
    wis_charm_illusion_save_mod,
    wis_bonus_cleric_spells,
    wis_max_cleric_spell_level,
    wis_cleric_spell_success_percent,
]
intelligence_based = [
    int_max_mage_spell_level,
    # int_side_effects,
]
charisma_based = [
    cha_max_henchmen,
]


def bodymass_hitdice(pounds):
    """Given POUNDS, return die or dice sizes of the bodymass hit die for a creature of that weight."""
    if pounds <= 10:
        return [(1, 2)]
    elif pounds <= 31:
        return [(1, 3)]
    elif pounds <= 71:
        return [(1, 4)]
    elif pounds <= 150:
        return [(1, 6)]
    elif pounds <= 290:
        return [(1, 8)]
    elif pounds <= 510:
        return [(1, 4), (1, 4)]
    elif pounds <= 830:
        return [(1, 10)]
    elif pounds <= 1275:
        return [(1, 4), (1, 6)]
    elif pounds <= 1800:
        return [(1, 12)]
    elif pounds <= 2500:
        return [(1, 6), (1, 6)]
    elif pounds <= 3500:
        return [(1, 4), (1, 4), (1, 4)]
    elif pounds <= 4800:
        return [(1, 6), (1, 8)]
    elif pounds <= 6500:
        return [(1, 4), (1, 4), (1, 6)]
    elif pounds <= 8700:
        return [(1, 8), (1, 8)]
    elif pounds <= 11500:
        return [(1, 4), (1, 6), (1, 6)]
    elif pounds <= 15000:
        return [(1, 8), (1, 10)]
    elif pounds <= 19000:
        return [(1, 10), (1, 10)]
    elif pounds <= 24000:
        return [(1, 10), (1, 12)]
    elif pounds <= 31000:
        return [(1, 12), (1, 12)]
    elif pounds <= 40000:
        return [(1, 8), (1, 8), (1, 10)]
    elif pounds <= 51000:
        return [(1, 8), (1, 10), (1, 10)]
    elif pounds <= 65000:
        return [(1, 10), (1, 10), (1, 10)]
    elif pounds <= 82000:
        return [(1, 8), (1, 8), (1, 8), (1, 8)]
    elif pounds <= 100000:
        return [(1, 12), (1, 12), (1, 12)]
    elif pounds <= 120000:
        return [(1, 8), (1, 10), (1, 10), (1, 10)]
    elif pounds <= 150000:
        return [(1, 10), (1, 10), (1, 10), (1, 12)]
    elif pounds <= 190000:
        return [(1, 10), (1, 12), (1, 12), (1, 12)]
    elif pounds <= 240000:
        return [(1, 10), (1, 10), (1, 10), (1, 10), (1, 10)]
    elif pounds <= 300000:
        return [(1, 8), (1, 8), (1, 8), (1, 10), (1, 10), (1, 10)]
    elif pounds <= 380000:
        return [(1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10)]
    elif pounds <= 480000:
        return [(1, 10), (1, 10), (1, 10), (1, 12), (1, 12), (1, 12)]
    else:
        return [(1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 12)]


def roll_die(sides, add=None, subtract=None, divide=None, multiply=None):
    return random.randint(1, sides)


def roll_bodymass_hitdice(dice):
    return sum([roll_die(high) for (low, high) in dice])


def die_to_text(num, sides):
    return f"{num}d{sides}"


def dice_to_text(dice):
    pool = Counter(dice)
    result = []
    for (_, sides), num in pool.items():
        result.append(die_to_text(num, sides))
    return "+".join(result)


def ability_scores(pc):
    # todo remove capitalization once same has been done in background_generator.PC
    return {abi: vars(pc)[abi.capitalize()] for abi in abilities}


def meets_ability_minimums(pc):
    scores = ability_scores(pc)
    for ability, minimum in classes[pc.pClass]["ability minimums"].items():
        # todo: one more reason to make ability scores a string -> value map -- checking pc's score becomes easier
        if scores[ability] < minimum:
            return False
    return True


def meets_bonus_xp_minimums(pc):
    scores = ability_scores(pc)
    for ability, minimum in classes[pc.pClass]["bonus xp minimums"].items():
        if scores[ability] < minimum:
            return False
    return True


def mod_to_text(num):
    return f"+{num}" if num >= 0 else f"{num}"

