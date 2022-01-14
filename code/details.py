from random import *
from decimal import *
from collections import namedtuple
from characters import martial_classes

getcontext().prec = 3


# todo move this function to globals / rules
def get_gender_words(sex):
    # todo account for neuter creatures
    if sex == "male":
        return ("he", "him", "his")
    else:
        return ("she", "her", "her")


# based on Strength
def detail_feats(magnitude, player):
    big_percent = choice([30, 40])
    small_percent = choice([10, 20])
    result = ""
    subj, obj, poss = get_gender_words(player.sex)
    if magnitude <= -17:
        result = "Weak lungs make it impossible to run."
    elif magnitude <= -14:
        result = "When stunned, must make save against crushing to end the stun and rejoin combat."
    elif magnitude <= -12:
        result = "Character is forever incapable of swimming, regardless of character class or skills."
    elif magnitude <= -11:
        result = (
            "Poor endurance. Character cannot run for more than 1 round at a time, no matter "
            + poss
            + " Constitution score."
        )
    elif magnitude <= -10:
        result = "One-handed melee weapons must be used two-handed (even daggers); two-handed melee weapons suffer the non-proficiency penalty (if already non-proficient with a given weapon,  add an additional -1 penalty.)"
    elif magnitude <= -9:
        result = "Encumbrance limits reduced by " + str(big_percent) + "%."
        player.enc_mult = player.enc_mult - Decimal(0.01 * big_percent)
    elif magnitude <= -8:
        result = "Too weak to draw or load any bow or crossbow."
    elif magnitude <= -7:
        result = "One-handed melee weapons must be used two-handed (except daggers); two-handed melee weapons have a -1 penalty to attack and damage."
    elif magnitude <= -6:
        result = "Encumbrance limits reduced by " + str(small_percent) + "%."
        player.enc_mult = player.enc_mult - Decimal(0.01 * small_percent)
    elif magnitude <= -5:
        result = "Too weak to draw a longbow or load a heavy crossbow."
    elif magnitude <= -4:
        result = "Poor cardiovascular health. Character can only hold breath for 1 round (normal: 3)."
    elif magnitude <= -2:
        result = (
            "Weak arms and legs. Treat character's Dexterity as half its actual value (round down) for the purpose of no-fault climbing. Danger climbing ability is reduced by "
            + str(randint(10, 15))
            + "%."
        )
    elif magnitude <= -1:
        result = "Throwing weapons deal 1 less damage (minimum 0.)"
    elif magnitude <= 1:
        result = "Throwing weapons deal 1 extra damage."
    elif magnitude <= 3:
        result = "Strong arms and legs. Treat character's Dexterity as 50% higher (round down) for no-fault climbing."
    elif magnitude == 4:
        result = "Strong hands and arms allow a 50% chance to spend 3 fewer AP when loading a crossbow."
    elif magnitude <= 6:
        result = "Character is capable of swimming."
    elif magnitude <= 8:
        result = "Encumbrance limits increased by " + str(small_percent) + "%."
        player.enc_mult = player.enc_mult + Decimal(0.01 * small_percent)
    elif magnitude <= 9:
        result = "Strong upper body. For slings, bows (not crossbows), and all thrown weapons, increase short range by 1 hex, and medium and long ranges by 2 hexes."
    elif magnitude <= 11:
        result = "Can hold breath for three times the normal duration (9 rounds instead of 3.)"
    elif magnitude <= 13:
        result = "Powerful muscles add +3 on rolls made to escape manacles, ropes, or other constraints."
    elif magnitude <= 15:
        result = (
            "Each day, the first time the character is stunned, after rejoining combat "
            + subj
            + " gains +2 to melee attack and damage for 10 rounds."
        )
    else:
        result = (
            "Each day, the first time the character is stunned, after rejoining combat "
            + subj
            + " gains hysterical strength. Roll 1d3+1: for 10 rounds, character gains that amount as a bonus to melee attack and damage."
        )
    return result


man_at_arms_weapons = ["dagger", "club", "quarterstaff", "sling"] * 3 + [
    "shortbow",
    "shortsword",
    "longsword",
    "mace",
    "bastard sword",
    "greatsword",
]
man_at_arms_armor = (
    ["no armor"] * 2
    + ["gambeson"] * 4
    + ["leather armor"] * 3
    + ["studded leather"] * 2
    + ["haubergeon"]
)


def man_at_arms_equipment():
    num_weapons = 1 if randint(1, 10) < 7 else 2
    weapons = sample(man_at_arms_weapons, num_weapons)
    armor = choice(man_at_arms_armor)
    equipment = namedtuple("equipment", ["weapons", "armor"])
    return equipment(weapons, armor)


def stringify_man_at_arms_equipment(equipment):
    return "has " + equipment.armor + "; carries " + ", ".join(equipment.weapons)


def man_at_arms_pay():
    return 4 + randint(1, 4) + randint(2, 5) + randint(2, 5) + randint(2, 5)


# based on Wisdom
def detail_interpersonal(magnitude, player):
    subj, obj, poss = get_gender_words(player.sex)
    result = ""
    if magnitude <= -17:
        result = "The character inadvertently revealed information to the enemy of the land where they are from, enabling that enemy to invade and seize wealth and property. A death sentence has been laid upon the character."
    elif magnitude == -16:
        result = (
            "Ill-considered opinions and bad intentions caused the character to be excommunicated from "
            + poss
            + " original religion. "
            + subj.capitalize()
            + " is marked as an apostate and all sites of organized worship will shun "
            + obj
            + "."
        )
    elif magnitude <= -14:
        crimes = [
            "murdered a peasant, and is being sought to receive lashes and time in the stocks.",
            "damaged property, and is being sought to pay restitution and receive time in the stocks.",
            "committed petty theft, and is being sought to receive lashes and pay restitution.",
            "murdered a merchant, and is being sought for prison time and a hefty fine.",
            "committed a serious theft, and is being sought to pay restitution and to have a hand chopped off.",
            "murdered a noble, and is being sought for execution.",
        ]
        roll = randint(1, 20)
        result_start = "Character has "
        if roll <= 3:
            result = result_start + crimes[0]
        elif roll <= 7:
            result = result_start + crimes[1]
        elif roll <= 11:
            result = result_start + crimes[2]
        elif roll <= 14:
            result = result_start + crimes[3]
        elif roll <= 18:
            result = result_start + crimes[4]
        else:  # 19 and 20
            result = result_start + crimes[5]
    elif magnitude == -13:
        result = "Character's strange proclivities and morals prevent the character from retaining hirelings for more than a month. Henchmen and followers received from leveling up are not affected."
    elif magnitude <= -11:
        result = (
            "Character is exiled from "
            + poss
            + " homeland, and will face a life sentence or execution if they return, although "
            + poss
            + " only 'crime' is that of having powerful enemies."
        )
    elif magnitude <= -9:
        enemy_family_member = ["wife"] * 9 + ["daughter"] * 10 + ["mother"] * 1
        sex_cutoff = 1
        if player.sex == "female":
            sex_cutoff = 11
        enemy_reasons = [
            (
                "foolishly slept with the enemy's "
                + choice(enemy_family_member)
                + ", making her pregnant."
            ),
            "stole a large sum of money from the enemy, and then lost it.",
            "destroyed a possession which the enemy held in great personal significance.",
        ]
        roll = randint(sex_cutoff, 20)
        result_start = "The character is pursued by a sworn enemy, who seeks revenge for the character having "
        if roll <= 10:
            result = result_start + enemy_reasons[0]
        elif roll <= 15:
            result = result_start + enemy_reasons[1]
        else:
            result = result_start + enemy_reasons[2]
    elif magnitude <= -8:
        if player.has_family:
            result = (
                "Character has been ostracized by "
                + poss
                + " family because of "
                + poss
                + " poor decisions. The character has no access to any family possessions or talents."
            )
        else:
            result = (
                "Character has been ostracized by "
                + poss
                + " mentor because of "
                + poss
                + " poor decisions. The character's training was incomplete, so "
                + subj
                + " has no weapon proficiencies."
            )
    elif magnitude <= -6:
        result = (
            "People in this area treat the character with profound dislike. Thus, "
            + subj
            + " has been banned from all town establishments save the market."
        )
    elif magnitude == -5:
        result = (
            "Word has spread that the character's word cannot be trusted. "
            + subj.capitalize()
            + " will be unable to obtain hirelings or make contracts in this town."
        )
    elif magnitude == -4:
        if player.has_family:
            result = "Family members strongly dislike the character, and will provide nothing more than a night's lodging, no more than once every every six months."
        else:
            result = "Character's occasional displays of foolishness means that hirelings and followers will take twice as long to earn morale increases for extended service. "
    elif magnitude <= -2:
        num = randint(3, 8)
        result = (
            "A group of "
            + str(num)
            + " local tough guys have been threatening and harassing the character whenever they can. These toughs certainly have class levels, but aren't too powerful."
        )
    elif magnitude == -1:
        result = (
            "The character's conduct has led to "
            + poss
            + " being banned from inns and taverns in this town."
        )
    elif magnitude == 0:
        if player.has_family:
            result = "Family members treat the character as hopeless and without prospects, but will provide lodging. Any brothers and sisters will work as hirelings, but will start with a morale of only 7."
        else:
            result = "Hirelings are made uneasy by character's small-mindedness. Base morale will be 1 point below normal, even if they are gained through this generator."
    elif magnitude == 1:
        sex = choice(["he", "she"])
        result = (
            "Character has made friends with a man-at-arms, who has a morale of 8. "
            + sex.capitalize()
            + " "
            + stringify_man_at_arms_equipment(man_at_arms_equipment())
            + ". "
            + sex.capitalize()
            + " may be hired now or later; cost is "
            + str(man_at_arms_pay())
            + " GP/month."
        )
    elif magnitude <= 3:
        if player.has_family:
            result = (
                "Family members treat the character and "
                + poss
                + " friends well, and look forward to news and visits. Brothers, sisters, and cousins will work as hirelings with a starting morale of 9."
            )
        else:
            lover = "daughter"
            if player.sex == "female":
                lover = "son"
            result = "The character is loved by the " + lover + " of an artisan."
    elif magnitude == 4:
        result = (
            "Character has made friends with two men-at-arms, who have a morale of 9. One, a "
            + choice(["man", "woman"])
            + ", "
            + stringify_man_at_arms_equipment(man_at_arms_equipment())
            + "; the other, a "
            + choice(["man", "woman"])
            + ", "
            + stringify_man_at_arms_equipment(man_at_arms_equipment())
            + ". Can be hired now or later; wages "
            + str(man_at_arms_pay())
            + " and "
            + str(man_at_arms_pay())
            + " GP/mo"
        )
    elif magnitude == 5:
        result = "Character is well-known and liked around these parts. Can easily obtain as many hirelings as needed (normally each one requires a reaction roll.) Limits based on town size still apply."
    elif magnitude == 6:
        if player.has_family:
            result = "Character is the family favorite and will receive regular gifts from home. The family will look forward to news and visits, and treat the character's friends well. All family members will work as hirelings, with starting morale of 10."
        else:
            result = (
                "Character has a particularly warm relationship with the mentor who taught "
                + obj
                + " class skills. The mentor will help find hirelings or procure items when the character is in town."
            )
    elif magnitude == 7:
        result = "Locals treat the character as a wise teacher, and will seek him or her out for advice. There is a 50% chance for the character to obtain a night's lodging for free each time he or she visits."
    elif magnitude == 8:
        result = "Character enjoys the favor of local farmers and peasants, and can count on a night's free lodging on each visit. Prices at nearest market are 10% lower for him or her."
    elif magnitude == 9:
        result = (
            "Character is so popular here that "
            + subj
            + " can count on free lodging indefinitely no matter how long the stay. This also applies to any area in which "
            + subj
            + " lives for at least 6 straight months."
        )
    elif magnitude <= 11:
        guild = choice(
            [
                "alchemist",
                "brewer",
                "blacksmith",
                "cooper",
                "carpenter",
                "carver",
                "shipwright",
                "chandler",
                "mason",
                "merchant",
                "weaver",
            ]
        )
        result = (
            "Character has made influential contacts in the local "
            + guild
            + " guild, and can count on a favor from them."
        )
    elif magnitude == 12:
        result = "Character has received the notice of the local government. The character may seek one favor."
    elif magnitude <= 14:
        num = randint(3, 5)
        descriptions = []
        for i in range(1, num + 1):
            enumerator = "the last, a" if i == num else "one "
            sex = choice(["man", "woman"])
            desc = (
                stringify_man_at_arms_equipment(man_at_arms_equipment())
                + ": wages "
                + str(man_at_arms_pay())
                + " GP/mo"
            )
            descriptions.append(enumerator + " " + sex + " " + desc)
        result = (
            "Character has made friends with "
            + str(num)
            + " men-at-arms, who have a morale of 10. Can be hired now or later. They are as follows:"
        )
        for d in descriptions:
            result = result + " " + d + "."
    elif magnitude <= 16:
        result = "Character has been made a member of the Illuminati. Tell nobody."
    else:
        result = "Events surrounding the character have caused people to believe that the character had a major part in a religious miracle. The character has received the goodwill of the highest religious figure in the land, and may seek one favor."
    return result


# based on Wisdom
def detail_tendency(magnitude, player):
    subj, obj, poss = get_gender_words(player.sex)
    result = ""
    if magnitude <= -17:
        num = randint(3, 5) * -1
        result = (
            "Character is deeply ignorant and superstitious. Saves against fear and mind-affecting spells suffer a "
            + str(num)
            + " penalty."
        )
    elif magnitude == -16:
        num = randint(2, 3) * -1
        result = (
            "Character is foolish, ignorant, and superstitious. Saves against fear and mind-affecting spells suffer a "
            + str(num)
            + " penalty."
        )
    elif magnitude <= -14:
        result = "Character is cowardly and lacks confidence. If stunned, a save must be made vs. crushing, or else the character will avoid all combat, including spellcasting, for 1d4 rounds."
    elif magnitude == -13:
        result = "Character has an awful temper. If character's weapon breaks or if he or she is hit by friendly fire, a save vs. magic must be made; otherwise, for 1d4+1 rounds, the character will be -3 to hit, +1 to damage, and unaffected by fear, morale, or attempts to communicate."
    elif magnitude <= -11:
        weight_gain = Decimal(1) + Decimal(randint(15, 25) * 0.01)
        result = "Gluttony and laziness has caused the character to gain fat."
        player.weight_mult *= weight_gain
    elif magnitude <= -9:
        result = (
            "Gullibility causes the character to frivolously spend and give away money. Whenever "
            + subj
            + " goes to market, if a Wisdom check is not successful, the character will lose 5d4 gold to the likes of confidence men, beggars, and snake-oil salesmen."
        )
    elif magnitude <= -7:
        result = (
            "Character's Wisdom is treated as 2 points lower when resisting seduction."
        )
    elif magnitude <= -5:
        result = "Character is overly cautious about combat. Must succeed at a Wisdom check before being able to make attacks (including discharging offensive spells) in a given combat. Check can be attempted on character's turn each round."
    elif magnitude <= -3:
        ungained = randint(2, 3) * 5
        result = (
            "Character has not quite completed "
            + poss
            + " training, and starts the game with negative experience equal to "
            + str(ungained)
            + "% of the number needed to attain 2nd level."
        )
    elif magnitude <= -1:
        result = "Should the character sample an addictive substance, the Wisdom check to determine addiction is made with a -3 penalty."
    elif magnitude == 0:
        result = (
            "A painful love affair has left the character emotionally toughened. "
            + poss.capitalize()
            + " Wisdom is treated as 2 points higher when resisting seduction."
        )
    elif magnitude == 1:
        result = "Character has a +3 bonus on Wisdom checks to avoid addiction."
    elif magnitude == 2:
        result = "Character is able to identify the exact time of day, to the half-hour, when out of doors."
    elif magnitude == 3:
        result = "Character has the ability to counsel others, which will give them a +2 bonus on their next check/save against addiction, overcaution in combat, or gullibility."
    elif magnitude <= 5:
        result = "The character's good will causes all hirelings and followers within five hexes to have +1 morale."
    elif magnitude == 6:
        xp = randint(6, 9) * 50
        result = (
            "If the character's class gives 10% bonus XP for high scores, but the character's scores are not high enough, or if "
            + poss
            + " class does not offer that bonus, the character receives 10% bonus XP. If they already qualify for 10% bonus XP, they instead begin adventuring with "
            + str(xp)
            + " XP."
        )
    elif magnitude == 7:
        result = "When the possibility arises, a successful save vs. poison will reveal to the character the location of a cursed item or location within 50 feet."
    elif magnitude <= 9:
        result = "Character can detect secret and concealed doors. Merely passing within 10 feet gives a 1/6 chance to notice it; actively searching an area gives a 2/6 chance."
    elif magnitude == 10:
        secret = choice(
            [
                "the location of hidden treasure",
                "the location of a shrine to a demon or obscure god",
                "the location of an area which is naturally magic",
            ]
        )
        result = "Character possesses secret knowledge: " + secret + "."
    elif magnitude <= 12:
        result = "One time per week, if an item worth less than 20 GP which could have been purchased at the last marketplace the character visited would now be useful, the character can retroactively purchase it."
    elif magnitude <= 15:
        result = "Once per day, the character may ignore the effects of being stunned."
    elif magnitude == 16:
        bonus = randint(1, 3)
        result = (
            "Character is very pious. All saves against fear and mind-affecting spells are made with a +"
            + str(bonus)
            + " bonus."
        )
    else:
        bonus = randint(2, 4)
        result = (
            "Character is very pious. All saves against fear and mind-affecting spells are made with a +"
            + str(bonus)
            + " bonus."
        )
    return result


def make_sibling():
    age_diff = randint(1, 6)
    sibling = (
        choice(["brother", "sister"])
        + " who is "
        + str(age_diff)
        + " years "
        + choice(["older", "younger"])
    )
    return sibling


def get_siblings(num):
    if num == 0:
        return "no siblings"
    else:
        acc = []
        while num > 0:
            acc.append(make_sibling())
            num = num - 1
        res = ", ".join(acc)
        return res


grandparents = [
    "paternal grandfather",
    "paternal grandmother",
    "maternal grandfather",
    "maternal grandmother",
]


def get_grandparents(num):
    if num == 0:
        return "no grandparents"
    if num == 4:
        return "all grandparents"
    else:
        res = ", ".join(sample(grandparents, num)) + ""
        return res


# based on Strength
def detail_family(magnitude, c):
    result = ""
    if magnitude <= -7:
        result = "Orphan. No known relatives."
        c.has_family = False
    elif magnitude <= -1:
        uncle = randint(0, 1)
        aunt = randint(0, 1)
        combined = uncle + aunt
        result_start = "Few living relations: "
        if uncle == 1 and aunt == 1:
            result = result_start + "character has an aunt and uncle."
        elif uncle == 1:
            result = result_start + "character has an uncle."
        elif aunt == 1:
            result = result_start + "character has an aunt."
        else:
            roll = randint(2, 4)
            result = result_start + "character has " + str(roll) + " cousins."
    elif magnitude == 0:
        relative = choice(
            ["grandparents"] * 3
            + ["aunt and uncle"] * 2
            + ["grandfather", "grandmother", "aunt", "uncle"]
        )
        mat_pat = choice(["on father's side", "on mother's side"])
        raised_by = relative + " " + mat_pat
        num_cousins = randint(1, 4) + randint(1, 4) - 2
        result = (
            "Character raised by "
            + (raised_by)
            + ". Number of first cousins: "
            + str(num_cousins)
            + "."
        )
    elif magnitude == 1:
        parent = choice(["father", "mother"])
        has_grandparent = choice([True, False])
        if has_grandparent:
            grandparent = (
                choice(["paternal", "maternal"])
                + " "
                + choice(["grandfather", "grandmother"])
            )
        else:
            grandparent = "no grandparents"
        has_sibling = choice([True, False])
        if has_sibling:
            sib = make_sibling()
        else:
            sib = "no siblings"
        result = (
            "Character raised by " + parent + ". Has " + grandparent + "; " + sib + "."
        )
    elif magnitude == 2:
        parents = choice(["mother and father", "mother and father", "mother", "father"])
        grands = get_grandparents(randint(0, 1))
        has_sib = choice([True, False])
        if has_sib:
            sib = make_sibling()
        else:
            sib = "no siblings"
        result = "Character raised by " + parents + ". Has " + grands + "; " + sib + "."
    elif magnitude <= 4:
        grands = get_grandparents(randint(0, 3))
        numsibs = randint(0, 2) + randint(0, 2)
        sibs = get_siblings(numsibs)
        result = (
            "Character raised by mother and father. Has " + grands + "; " + sibs + "."
        )
    elif magnitude <= 6:
        grands = get_grandparents(randint(0, 4))
        numsibs = randint(1, 2) + randint(0, 2)
        sibs = get_siblings(numsibs)
        result = (
            "Character raised by mother and father. Has " + grands + "; " + sibs + "."
        )
    elif magnitude <= 8:
        grands = get_grandparents(randint(1, 4))
        numsibs = randint(1, 2) + randint(0, 2)
        sibs = get_siblings(numsibs)
        result = "Character raised by mother and father. Has " + grands + "; "
    elif magnitude <= 12:
        grands = get_grandparents(randint(2, 4))
        numsibs = randint(1, 2) + randint(0, 3)
        sibs = get_siblings(numsibs)
        result = (
            "Character raised by mother and father. Has " + grands + "; " + sibs + "."
        )
    elif magnitude <= 14:
        grands = get_grandparents(randint(2, 4))
        numsibs = randint(1, 3) + randint(0, 3)
        sibs = get_siblings(numsibs)
        result = (
            "Character raised by mother and father. Has " + grands + "; " + sibs + "."
        )
    else:
        grands = get_grandparents(randint(2, 4))
        numsibs = randint(1, 3) + randint(1, 3)
        sibs = get_siblings(numsibs)
        result = (
            "Character raised by mother and father. Has " + grands + "; " + sibs + "."
        )
    return result


# based on Intelligence
def detail_choices(magnitude, player):
    subj, obj, poss = get_gender_words(player.sex)
    result = ""
    which_half = choice(["right", "left"])
    if magnitude <= -16:
        result = (
            "Character is missing lower half of "
            + which_half
            + " leg, and has a peg leg. One less AP than normal."
        )
    elif magnitude <= -14:
        result = "Character is missing left hand. Cannot use two-handed weapons. Can choose hook-hand as a weapon proficiency, but does not start with one to use."
    elif magnitude == -13:
        result = (
            "Character is missing "
            + which_half
            + " eye. Ranged weapons have additional attack penalty: -1 at close range, -3 at medium, -5 at long (total: -1/-5/-10)"
        )
    elif magnitude == -12:
        m = randint(1, 8) + randint(1, 8) + randint(1, 8) + randint(1, 8)
        result = "Character has spent " + str(m) + " miserable years in prison."
        player.added_age += m
    elif magnitude == -11:
        h = randint(1, 6) + randint(1, 6) + randint(1, 6)
        result = "Character has spent " + str(h) + " hard years in prison."
        player.added_age += h
    elif magnitude == -10:
        p = randint(1, 4) + randint(1, 4)
        result = "Character has spent " + str(p) + " years in prison."
        player.added_age += p
    elif magnitude == -9:
        num = randint(1, 3)
        result = (
            "Missing "
            + str(num)
            + " fingers on "
            + which_half
            + " hand. -2 on attack rolls when using that hand (including two-handed weapons.)"
        )
    elif magnitude == -8:
        num = randint(2, 3)
        result = (
            "Missing "
            + str(num)
            + " toes on "
            + which_half
            + " foot. -1 penalty on all Dexterity checks involving the feet."
        )
    elif magnitude == -7:
        months = randint(3, 9)
        if player.sex == "male":
            result = (
                "Character has fathered a child out of wedlock. The mother is "
                + str(months)
                + " months pregnant."
            )
        else:
            result = "Character is pregnant and " + str(months) + " months along."
    elif magnitude == -6:
        result = (
            "Character has been swindled of all money and possessions, leaving "
            + obj
            + " with only a shirt."
        )
        player.money_mult = Decimal(0)
    elif magnitude == -5:
        result = "Trust and generosity to family or others has left the character with little money."
        player.money_mult = player.money_mult * Decimal(0.3)
    elif magnitude == -4:
        num_cigs = randint(1, 4)
        grams_per_oz = Decimal(28.3495)
        # grams per cigar, converted to oz to measure pipe tobacco
        tobacco = num_cigs * Decimal(2.5) / grams_per_oz
        num_beers = randint(1, 4)
        is_cig = choice([True, False])
        consequence = "until the addiction is fed each day, the character's Wisdom will be treated as 50% normal, and other ability scores will be treated as 90% normal."
        if is_cig:
            result = (
                "Character is addicted to "
                + str(round(num_cigs))
                + " cigar(s) per day (or "
                + str(round(tobacco, 2))
                + " oz pipe tobacco); "
                + consequence
            )
        else:
            result = (
                "Character is addicted to "
                + str(num_beers)
                + " beer(s) per day; "
                + consequence
            )
    elif magnitude == -3:
        if player.sex == "male":
            p = "fathered"
        else:
            p = "mothered"
        kid_gender = choice(["son", "daughter"])
        result = "Character has " + p + " a bastard child, a " + kid_gender + "."
        # todo prompt player to name the kid - one reason to return a structured result ... then PROCESS that result, including has_family checks, to give the final string...!
        # todo use he/his she/her instead of "its (whereabouts)"
        # todo when family has become a data structure, choose a family member to care for the child
        if player.has_family:
            result += " Your family is caring for the child."
        else:
            result += " You gave the child up as a foundling, and its whereabouts are unknown."
    elif magnitude == -2:
        result = (
            "Gambling, waste, and foolishness has lost the character half "
            + poss
            + " money."
        )
        player.money_mult = player.money_mult * Decimal(0.5)
    elif magnitude == -1:
        years = randint(2, 5)
        result = (
            "A misspent youth cost the character "
            + str(years)
            + " extra years to finish training."
        )
        player.added_age += years
    elif magnitude == 0:
        scar = randint(3, 8)
        # todo choose where the scar is, or prompt player (or print a "fill in the blank" line!)
        result = (
            "Character has a "
            + str(scar)
            + "-inch scar on a normally-covered part of "
            + poss
            + " body, received as a child during a moment of pure stupidity."
        )
    elif magnitude <= 2:
        result = "Good luck has slightly increased the character's money."
        player.money_mult *= Decimal(2)
    elif magnitude <= 4:
        result = "Ability to play a musical instrument of the player's choosing."
    elif magnitude == 5:
        dir = choice(["north", "south", "east", "west"])
        result = (
            "Distinguished effort has earned a writ of passage, free of tolls, between this kingdom and the nearest one to the "
            + dir
            + "."
        )
    elif magnitude <= 7:
        result = (
            "Prudence and savings have significantly increased the character's money."
        )
        player.money_mult *= Decimal(3)
    elif magnitude <= 9:
        credit = (randint(1, 6) + randint(1, 6) + randint(1, 6)) * 50
        player.credit += credit
        result = "Character possesses credit with the local merchant guild."
    elif magnitude <= 11:
        num = randint(4, 6)
        result = "Prudence and savings have greatly increased the character's money."
        player.money_mult *= Decimal(num)
    elif magnitude <= 13:
        num = randint(6, 9)
        result = "Diligent effort has hugely increased the character's money."
        player.money_mult *= Decimal(num)
    elif magnitude == 14:
        result = "Character possesses a magic item."
    elif magnitude <= 16:
        num = randint(9, 12)
        result = "Smart and frugal behavior has grown the character's money to an incredible degree."
        player.money_mult *= Decimal(num)
    else:
        title = choice(["an academic degree", "former advisor to the nobility"])
        result = (
            "Character has gained a title or honor through work done during training: "
            + title
            + ". The character adds 2d4 points to one skill within "
            + poss
            + " 1st-level focus, representing the knowledge they cultivated to earn the title."
        )
    return result


# based on Charisma, requires two magnitude rolls
def detail_beauty(face_mag, body_mag, player):
    # to be added on to
    subj, obj, poss = get_gender_words(player.sex)

    def face_beauty():
        which_side = choice(["right", "left"])
        if face_mag <= -15:
            scar_length = randint(3, 7)
            scar_type = choice(["a blade", "an animal bite", "an animal's claws"])
            scar = (
                "has "
                + str(scar_length)
                + "-inch scar across the face, received from "
                + scar_type
            )
            choices = [
                scar,
                "is missing " + poss + " " + which_side + " ear",
                "is missing " + poss + " nose",
                "has a distinctly misshapen head",
            ]
            return choice(choices)
        elif face_mag <= -8:
            choices = [
                "has a lazy " + which_side + " eye",
                "has a whiny, irritating voice",
                "has a crackly, annoying voice",
                "suffers from halitosis if teeth are not brushed 3 times daily",
                "has an always-runny nose",
                "has a greasy, oily face",
            ]
            return choice(choices)
        elif face_mag <= -1:
            nose_problem = choice(["bulbous", "squashed", "piggish"])
            missing_teeth = randint(0, 1) + randint(1, 3)
            teeth_problem = choice(["buck", "crooked", str(missing_teeth) + " missing"])
            choices = [
                "has bushy eyebrows",
                "has a caveman-like protruding brow",
                "has distinctly large ears",
                "has a " + nose_problem + " nose",
                "has " + teeth_problem + " teeth",
                "has acne scars",
                "has eyes which are unnervingly close together",
            ]
            return choice(choices)
        elif face_mag <= 7:
            choices = [
                "has a beautiful aquiline nose",
                "has attractively straight teeth",
                "has a clean and healthy complexion",
            ]
            if player.sex == "male":
                choices = choices + ["has a strong chin"]
            else:
                choices = choices + ["has lovely full lips"]
            return choice(choices)
        elif face_mag <= 13:
            choices = [
                "perfectly-shaped, brilliantly white teeth",
                "marvelous high cheekbones",
            ]
            if player.sex == "male":
                choices = choices + ["a deep, compelling voice", "a strong jawline"]
            else:
                choices = choices + [
                    "a throaty, seductive voice",
                    "charmingly delicate features",
                ]
            return "has " + choice(choices)
        else:
            choices = [
                "has a rich, velvety voice",
                "has dazzling eyes",
                "has a flawless complexion",
            ]
            return choice(choices)

    def body_beauty():
        # redefine which_side so it can be different for face and body results
        which_side = choice(["right", "left"])
        if body_mag <= -16:
            burn_percent = randint(20, 80)
            return (
                "has nasty burn scars covering "
                + str(burn_percent)
                + "% of "
                + poss
                + " body"
            )
        elif body_mag <= -14:
            scar_length = randint(2, 6)
            scar_place = choice(
                [which_side + " cheek", "chin", "throat", "nose", "forehead"]
            )
            scar = (
                "has a "
                + str(scar_length)
                + "-inch scar across "
                + poss
                + " "
                + scar_place
            )
            choices = [
                scar,
                "gives off a nasty, unwashable odor",
                "has lumpy limbs",
                "has a misshapen torso",
                "is a hunchback",
            ]
            return choice(choices)
        elif body_mag <= -8:
            scar_length = randint(1, 3)
            scar_place = choice(
                [which_side + " arm", which_side + " hand", "scalp", "chin"]
            )
            scar = (
                "has a "
                + str(scar_length)
                + "-inch scar across "
                + poss
                + " "
                + scar_place
            )
            choices = [
                scar,
                "is bow-legged",
                "is knock-kneed",
                "moves with an awkward, loping gait",
                "has a sunken chest",
            ]
            return choice(choices)
        elif body_mag <= -1:
            choices = [
                "has a weak " + which_side + " leg and walks with a pronounced limp",
                "has a swayback",
                "has a overlong torso with stumpy legs",
            ]
            return choice(choices)
        elif body_mag == 0:
            foot_kind = choice(
                [
                    "very small feet (-5% footwear cost)",
                    "small feet",
                    "large feet",
                    "very large feet (+5% footwear cost)",
                ]
            )
            freckle_count = choice(["scattered", "many", "excessive"])
            choices = ["has " + foot_kind, "has " + freckle_count + " freckles"]
            return choice(choices)
        elif body_mag <= 7:
            choices = [
                "gives off a pleasant body odor",
                "has well-proportioned legs and arms",
                "has an elegant neck",
                "has healthy, glossy hair",
            ]
            return choice(choices)
        elif body_mag <= 13:
            if player.sex == "male":
                choices = [
                    "has large, muscular shoulders",
                    "has a broad, muscular back",
                    "has large, muscular arms",
                    "has large, muscular legs",
                    "has a six-pack",
                ]
            else:
                choices = [
                    "has a six-pack",
                    "has large, powerful thighs",
                    "has a narrow waist",
                    "has wide, curvy hips",
                ]
            return choice(choices)
        else:
            choices = [
                "has radiant skin",
                "has luxurious hair",
                "always has perfect posture",
            ]
            return choice(choices)

    # putting it all together
    face_result = "Character " + face_beauty()
    body_result = ", and also " + body_beauty()
    result = face_result + body_result + "."
    return result


# helper for health_detail
def get_health_condition(roll, sex):
    # the higher the number, the more severe the condition
    # the idea is to use these with a random roll in the specified range
    subj, obj, poss = get_gender_words(sex)
    if roll <= 2:
        return "Motion sickness: repeated waves of nausea and vomiting will occur with the rhythmic motion of any vehicle."
    elif roll <= 4:
        return "Flaring pain in joints: character finds outdoor travel difficult, and will suffer an extra point of damage each day when traveling."
    elif roll <= 6:
        return "Low tolerance for alcohol: character takes 1d3 damage for each 8 ounces consumed."
    elif roll <= 8:
        return "Skin chafes easily: while armored, character will suffer 1 damage per two hours spent walking or riding."
    elif roll <= 10:
        return "Weak stomach: character will suffer 1 point of damage per pound of food eaten which is raw or unprocessed."
    elif roll == 11:
        return "Muscle pulls: after each combat, character must save vs. explosion or suffer a -1 penalty to attacks for 3 days due to a pulled muscle. Multiple occurrences stack up to -3."
    elif roll == 12:
        colors = choice([["red", "orange", "green"], ["blue", "purple", "black"]])
        sentence_tail = ", ".join(colors)
        return (
            "Color confusion: character cannot distinguish between "
            + sentence_tail
            + "."
        )
    elif roll == 13:
        return "Total color blindness: character cannot distinguish between any colors of the spectrum. Everything appears to be in shades of gray. Ranged attack distance penalties are doubled."
    elif roll <= 15:
        return "Tone deafness: character cannot distinguish chords of sound, and thus receives neither positive nor negative effects of music."
    elif roll == 16:
        return "Chronic migraines: each day, the character has a 1 in 20 chance of being -4 to hit and -3 to saves and ability checks."
    elif roll <= 18:
        return (
            "Mild hemorrhaging: if character receives a bleeding wound, "
            + subj
            + " will bleed 1 extra HP per round. If bandages are used, character's wounds must be bound twice in order to stop the bleeding."
        )
    elif roll == 19:
        return "Shortened breath: character is unable to run for more than two rounds. If any strenuous activity (such as combat) continues for more than 10 rounds, the character must succeed at a save vs. poison or else be struck with a coughing spasm, incapacitating them for 1 round (counts as stunned) and causing 3d4 damage."
    elif roll == 20:
        return "Brittle bones: all falling damage dice for the character are increased by one step (e.g. d6 -> d8)."
    elif roll == 21:
        return "Cataracts: character cannot make out any detail further away than 60 feet, and cannot target attacks or spells beyond that range."
    elif roll == 22:
        return (
            "Mild hemorrhaging: if character receives a bleeding wound, "
            + subj
            + " will bleed 2 extra HP per round. If bandages are used, character's wounds must be bound three times in order to stop the bleeding."
        )
    elif roll == 23:
        return "Complete deafness: character cannot hear any sound at all, and will be unable to respond to or be affected by sound. Character can still sense vibration."
    elif roll == 24:
        return "Oversensitive skin: due to extreme discomfort, character cannot wear any kind of armor."
    elif roll == 25:
        return "Temporary demonic possession: while talking to strangers, character may suddenly lapse into abusive outbursts. 1 in 20 chance per round."
    elif roll <= 27:
        return "Weak heart: if reduced to -6 or fewer HP, character must make save vs. poison or suffer a heart attack and die."
    elif roll == 28:
        return (
            "Ghastly hemorrhaging: if character receives a bleeding wound, "
            + subj
            + " she will bleed 3 extra HP per round. If bandages are used, character's wounds must be bound four times in order to stop the bleeding."
        )
    elif roll == 29:
        return "Blindness: character cannot see at all, and is altogether unable to sense light. Chief among the consequences is that all attacks are treated as if attacking invisible creatures (-8 normally, -6 if someone spends 1 AP/turn helping to direct your strikes) and that all missile/thrown attacks which miss can cause friendly fire, in any direction."
    else:
        return "Crippled legs: while the character's legs appear whole and undamaged, they are in fact entirely without feeling or strength. The character cannot walk under their own power."


def detail_health(magnitude, player):
    subj, obj, poss = get_gender_words(player.sex)
    # get 4 health conditions, each with different possibilities of being mild or severe
    condition4 = get_health_condition(randint(24, 30), player.sex)
    condition3 = get_health_condition(randint(16, 24), player.sex)
    condition2 = get_health_condition(randint(8, 16), player.sex)
    condition1 = get_health_condition(randint(1, 8), player.sex)
    result = ""
    if magnitude <= -16:
        result = condition4
    elif magnitude <= -12:
        result = condition3
    elif magnitude <= -7:
        result = condition2
    elif magnitude <= -1:
        result = condition1
    elif magnitude == 0:
        num_days = randint(7, 14)
        result = (
            "Character is suffering from a severe cold at the start of the campaign. For the next "
            + str(num_days)
            + " days, character will be -1 to attack and damage."
        )
    elif magnitude == 1:
        result = "+1 save vs poison."
    elif magnitude == 2:
        result = "+1 save vs crushing."
    elif magnitude == 3:
        result = "+1 save vs explosion."
    elif magnitude == 4:
        result = "+1 save vs magic."
    elif magnitude == 5:
        source = choice(["snake or reptile", "insect"])
        result = (
            "Character is resistant against "
            + source
            + " poison/venom. Damage is reduced by 50%."
        )
    elif magnitude == 6:
        source = choice(["marine creature", "spider"])
        result = (
            "Character is resistant against "
            + source
            + " poison/venom. Damage is reduced by 50%."
        )
    elif magnitude <= 8:
        result = "Character heals 1 extra HP from a day's rest."
    elif magnitude == 9:
        result = "+2 save vs poison."
    elif magnitude == 10:
        result = "+2 save vs crushing."
    elif magnitude == 11:
        result = "+2 save vs explosion."
    elif magnitude == 12:
        result = "+2 save vs magic."
    elif magnitude <= 14:
        result = "Character heals 2 extra HP from a day's rest."
    elif magnitude <= 16:
        result = "+1 to all saves."
    else:
        result = "+2 to all saves."
    return result


# governed by Dex
def detail_agility(magnitude, player):
    subj, obj, poss = get_gender_words(player.sex)
    which_side = choice(["right", "left"])
    result = ""
    if magnitude <= -17:
        result = (
            "Fused bones in the character's "
            + which_side
            + " leg causes a severe, dragging limp. Normal AP is reduced by 2."
        )
    elif magnitude == -16:
        result = (
            "Character must save vs crushing before drawing a weapon; failure indicates "
            + subj
            + " cannot do it this round. No save is needed for subsequent attempts for the same weapon in the same combat."
        )
    elif magnitude == -15:
        result = (
            "Character's "
            + which_side
            + " hand is deformed and useless. Opposite hand is dominant."
        )
    elif magnitude == -14:
        result = (
            "Character's "
            + which_side
            + " foot is deformed, and "
            + subj
            + " has a permanent limp. Normal movement is reduced by 1."
        )
    elif magnitude == -13:
        result = (
            "Character suffers from severe vertigo. If "
            + subj
            + " gets within 5 feet of a drop that is at least 15 feet, "
            + subj
            + " will fall unconscious for five minutes. Once awakened, "
            + subj
            + " will be nauseated for 2d4 rounds."
        )
    elif magnitude == -12:
        result = (
            "Each time the character moves among delicate objects, including in a marketplace, "
            + subj
            + " must make a save vs. explosion to avoid accidentally breaking something."
        )
    elif magnitude == -11:
        result = (
            "Character is wholly unable to ride any mount of any kind, regardless of "
            + poss
            + " character class."
        )
    elif magnitude == -10:
        result = "Character is unable to use two-handed weapons or weapons which strike further away than five feet."
    elif magnitude == -9:
        result = "Character is incapable of loading or working any kind of bow, crossbow, or similar mechanical device."
    elif magnitude == -8:
        num = randint(1, 2)
        result = (
            "Character suffers a -"
            + str(num)
            + " penalty to hit with all ranged weapons."
        )
    elif magnitude == -7:
        result = (
            "Character requires triple normal time to mount or dismount from an animal."
        )
    elif magnitude == -6:
        result = "Character's armor class has a penalty of 2 when moving at a speed above normal."
    elif magnitude == -5:
        result = "Character requires 3 more AP than normal to load any bow."
    elif magnitude == -4:
        result = "If character causes friendly fire, it is 50% likely to be in ANY direction."
    elif magnitude == -3:
        result = "Character's clumsiness means that dropped weapons will break on 2 in 6 instead of 1 in 6."
    elif magnitude == -2:
        result = "Character requires 1 more AP than normal to draw any weapon."
    elif magnitude == -1:
        result = (
            "Character suffers from mild vertigo. If "
            + subj
            + " gets within 5 feet of a drop that is at least 15 feet, "
            + subj
            + " will become somewhat nauseated and suffer a -1 to hit. Nausea passes 1 round after moving away."
        )
    elif magnitude == 0:
        num = randint(1, 20)
        if num <= 18:
            how_hurt = "maimed"
        else:
            how_hurt = "killed"
        result = (
            "Through accidental clumsiness, the character caused a family member to be "
            + how_hurt
            + "."
        )
    elif magnitude == 1:
        result = "Character requires no AP to draw a weapon weighing 2 lbs or less."
    elif magnitude == 2:
        result = "Character requires no AP to draw a weapon weighing 3 lbs or less."
    elif magnitude == 3:
        result = "The character's penalty for attacks at long range is lessened by 1."
    elif magnitude == 4:
        result = (
            "Character automatically takes a defensive stance when surprised, improving "
            + poss
            + " AC by 1 until no longer surprised."
        )
    elif magnitude <= 6:
        result = (
            "Character is quick to find an opening in enemy defenses. "
            + subj.capitalize()
            + " has an extra +1 modifier to hit opponents from the flank or rear."
        )
    elif magnitude == 7:
        result = "Friendly fire committed by this character is ignored if the affected ally is within 20 feet."
    elif magnitude == 8:
        result = "Character has a talent for cheating at cards; base 20% chance plus more favorable of: 2% per point of Dex OR (if a thief) 1/2 of pickpocketing success target."
    elif magnitude == 9:
        result = "The character's penalty for attacks at both medium and long ranges is lessened by 1."
    elif magnitude == 10:
        result = "Character can climb poles and free-hanging ropes as if climbing an ordinary wall."
    elif magnitude == 11:
        if player.pClass == "thief":
            result = "Character notices traps as if one level higher."
        else:
            result = "Character has a 15% chance to notice traps."
    elif magnitude == 12:
        result = (
            "Character can catch and handle ordinary snakes if "
            + subj
            + " successfully saves vs. poison (with a +4 bonus.)"
        )
    elif magnitude == 13:
        num = randint(1, 2)
        if num == 1:
            result = (
                "Character gains "
                + obj
                + " a +1 bonus to hit with bolas, sling, and other weapons which are spun before throwing."
            )
        else:
            result = "Character is +1 to hit with any weapon or object which has a splash effect, including certain orb spells."
    elif magnitude == 14:
        result = "Character requires no AP to draw a weapon weighing 5 lbs or less."
    elif magnitude == 15:
        result = "Character requires no AP to draw any weapon."
    elif magnitude == 16:
        body_part = choice(["hip", "shoulder"])
        result = (
            "Character can dislocate "
            + poss
            + " "
            + which_side
            + " "
            + body_part
            + " at will, though doing so causes 1d4+1 damage."
        )
    else:
        # todo "with no penalties whatsoever - as if climbing an ordinary wall."
        result = "Character can climb poles and free-hanging ropes, and walk tightropes, as if climbing an ordinary wall."
    return result


def birthday(age, current_year=1650):
    birth_year = (current_year - age) + 1
    # the addition of 1 year here was supposed to correct so that even if the
    # characters' birthday had already passed this yar, they would still be the right age
    # but it's an off-by-one error making them too old if the birthday hasn't passed yet
    # the opposite error (making them too young) happens if we subtract 1
    # the solution, which I won't do yet, is to use not only the current day,
    # but also the current year
    leap_year = (birth_year % 4) == 0
    # todo this naive formula fails to take into account the quirk of leap years in a year divisible by 100
    if leap_year:
        feb_length = 29
    else:
        feb_length = 28
    end_january = 31
    end_february = feb_length + end_january
    end_march = 31 + end_february
    end_april = 30 + end_march
    end_may = 31 + end_april
    end_june = 30 + end_may
    end_july = 31 + end_june
    end_august = 31 + end_july
    end_september = 30 + end_august
    end_october = 31 + end_september
    end_november = 30 + end_october
    end_december = 31 + end_november
    month_ends = [
        end_january,
        end_february,
        end_march,
        end_april,
        end_may,
        end_june,
        end_july,
        end_august,
        end_september,
        end_october,
        end_november,
        end_december,
    ]
    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    # initialize the two-way correspondence between final ordinal day of year,
    # and name of the month whose last day is that day of the year
    month_relations = {}
    for x in range(0, len(month_names)):
        n = month_names[x]
        end = month_ends[x]
        month_relations[n] = end
        month_relations[end] = n

    # end_december is also the number of days in this year
    day_of_the_year = randint(1, end_december)

    birthday_month_day = ""
    for end in month_ends:
        if day_of_the_year <= end:
            m = month_relations[end]
            d = end - day_of_the_year + 1
            # the extra 1 added to d is so that days are number 1 to end, instead of 0 to (end-1)
            birthday_month_day = m + " " + str(d)
            break
        else:
            pass

    return birthday_month_day


hair_colors = ["black"] * 40 + ["brown"] * 30 + ["blonde"] * 20 + ["red"] * 10


def get_base_hair_color():
    return choice(hair_colors)


def adjust_hair_color_for_aging(base_hair_color, age, constitution):
    aging = randint(1, 100)  # lower is better
    hair = namedtuple("hair", ["color", "description"])
    base_case = hair(base_hair_color, "")
    if age <= 20:
        return base_case
    elif age <= 29:
        if aging > 7 * constitution:
            return hair(base_hair_color, "prematurely graying")
        else:
            return base_case
    elif age <= 39:
        if aging > 6 * constitution:
            return hair(base_hair_color, "graying")
        else:
            return base_case
    elif age <= 49:
        if aging > 5 * constitution:
            return hair("gray", "was once " + base_hair_color)
        else:
            return base_case
    elif age <= 59:
        if aging > 4 * constitution:
            return hair("gray", "was once " + base_hair_color)
        else:
            return hair(base_hair_color, "graying")
    else:
        # hair is always gray at age 60 and higher
        return hair("gray", "was once " + base_hair_color)


def hair_status_after_aging(age, constitution, sex):
    aging = randint(1, 100)  # lower is better

    if sex == "male":
        if age <= 20:
            return ""
        elif age <= 29:
            if aging > 7 * constitution:
                return "bald"
            if aging > 6 * constitution:
                return "thinning"
            else:
                return ""
        elif age <= 39:
            if aging > 6 * constitution:
                return "bald"
            elif aging > 5 * constitution:
                return "thinning"
            else:
                return ""
        elif age <= 49:
            if aging > 5 * constitution:
                return "bald"
            elif aging > 4 * constitution:
                return "thinning"
            else:
                return ""
        elif age <= 59:
            if aging > 3 * constitution:
                return "bald"
            elif aging > 2 * constitution:
                return "thinning"
            else:
                return ""
        else:
            if aging > 2 * constitution:
                return "bald"
            elif aging > constitution:
                return "thinning"
            else:
                return ""
    else:
        # sex is female
        hair_if_male = hair_status_after_aging(age - 10, constitution, "male")
        if hair_if_male == "bald":
            if aging > 10 * constitution:
                return "bald"
            else:
                return "wispy"
        else:
            return hair_if_male


def get_eye_color(base_hair_color):
    score = randint(1, 100)
    if base_hair_color == "black":
        if score < 40:
            return "brown"
        elif score < 80:
            return "black"
        else:
            return "green"

    elif base_hair_color == "red":
        if score < 50:
            return "green"
        else:
            return "blue"

    elif base_hair_color == "blonde":
        if score < 50:
            return "blue"
        elif score < 75:
            return "green"
        else:
            return "brown"

    else:
        # base_hair is brown
        if score < 15:
            return "blue"
        elif score < 35:
            return "green"
        elif score < 60:
            return "brown"
        else:
            return "black"


def make_final_hair(base_hair, age, con, sex):
    hair_data = namedtuple("hair", ["haircolor", "hairdesc", "haircond"])
    hair_color_adj = adjust_hair_color_for_aging(base_hair, age, con)
    hair_level_adj = hair_status_after_aging(age, con, sex)
    if hair_level_adj == "bald":
        return hair_data("bald", "was once " + base_hair, "")
    else:
        return hair_data(
            hair_color_adj.color, hair_color_adj.description, hair_level_adj
        )


def profession_strength():
    """Return a Strength-based profession."""
    roll = randint(1, 100)
    if roll <= 20:
        return "farmer"
    elif roll <= 40:
        return "fisherman"
    elif roll <= 55:
        return "sailor"
    elif roll <= 70:
        return "teamster"
    elif roll <= 75:
        return "guardsman"
    elif roll <= 80:
        return "mercenary"
    elif roll <= 85:
        return "outrider"
    elif roll <= 90:
        return "bounty hunter"
    elif roll <= 95:
        return "gladiator"
    else:
        return "weapon master"


artisans_food = [
    "brewer",
    "vintner",
    "baker",
    "chandler",
    "confectioner",
    "butcher",
    "tobacconist",
]

artisans_textiles = [
    "tailor",
    "draper",
    "fuller",
    "weaver",
    "furrier",
    "tanner",
    "leatherworker",
    "cobbler",
]

artisans_wood = [
    "cooper",
    "wainwright",
    "shipwright",
    "furniture maker",
    "instrument maker",
    "papermaker",
    "bookbinder",
]

artisans_minerals = ["potter", "glassmaker", "glazier", "sculptor"]

artisans_metals = [
    "smelter",
    "jeweller",
    "lapidary",
    "toolmaker",
    "diemaker",
    "engraver",
]

all_artisans = artisans_food
all_artisans.extend(artisans_textiles)
all_artisans.extend(artisans_wood)
all_artisans.extend(artisans_minerals)
all_artisans.extend(artisans_metals)


def profession_dexterity():
    """Return a Dexterity-based profession."""
    roll = randint(1, 100)
    if roll <= 90:
        selected = choice(all_artisans)
        return selected
    elif roll <= 94:
        return "juggler"
    elif roll <= 98:
        return "gambler"
    else:
        return "monk"


def profession_constitution():
    """Return a Constitution-based profession."""
    roll = randint(1, 100)
    if roll <= 5:
        return "laborer"
    if roll <= 10:
        return "rat catcher"
    elif roll <= 15:
        return "grave robber"
    elif roll <= 25:
        return "porter"
    elif roll <= 35:
        return "bricklayer"
    elif roll <= 45:
        return "drover"
    elif roll <= 55:
        return "miner"
    elif roll <= 60:
        return "hermit"
    elif roll <= 68:
        return "blacksmith"
    elif roll <= 76:
        return "armorer"
    elif roll <= 84:
        return "weaponsmith"
    elif roll <= 92:
        return "mine foreman"
    else:
        return "explorer"


def profession_intelligence():
    roll = randint(1, 100)
    if roll <= 10:
        return "trapper"
    elif roll <= 15:
        return "scribe"
    elif roll <= 20:
        return "alchemist's assistant"
    elif roll <= 25:
        return "boatman"
    elif roll <= 30:
        return "gamekeeper"
    elif roll <= 35:
        return "carpenter"
    elif roll <= 40:
        return "stonemason"
    elif roll <= 45:
        return "tinker"
    elif roll <= 49:
        return "bookkeeper"
    elif roll <= 51:
        return "tomb robber"
    elif roll <= 55:
        return "artillerist"
    elif roll <= 59:
        return "cartographer"
    elif roll <= 63:
        return "veterinarian"
    elif roll <= 67:
        return "hospitaler"
    elif roll <= 71:
        return "architect"
    elif roll <= 75:
        return "spy"
    elif roll <= 80:
        return "mage's apprentice"
    elif roll <= 85:
        return "lawyer"
    elif roll <= 90:
        return "alchemist"
    elif roll <= 97:
        return "spymaster"
    else:
        return "political advisor"


def profession_wisdom():
    roll = randint(1, 100)
    if roll <= 15:
        return "husbandman"
    elif roll <= 25:
        return "prospector"
    elif roll <= 30:
        return "herbalist"
    elif roll <= 39:
        return "tutor"
    elif roll <= 48:
        return "surgeon's apprentice"
    elif roll <= 57:
        return "librarian"
    elif roll <= 66:
        return "priest"
    elif roll <= 75:
        return "steward"
    elif roll <= 84:
        return "village healer"
    elif roll <= 88:
        return "priest"
    elif roll <= 92:
        return "mortician"
    elif roll <= 87:
        return "witch hunter"
    elif roll <= 91:
        return "professor"
    elif roll <= 96:
        return "ecclesiastical vicar"
    else:
        return "ecclesiastial rector"


# creative_artists = ["painter", "illustrator", "engraver", "sculptor"]
# performance_artists = ["mime", "jester", "clown", "monologist"]
# literary_artists = ["poet", "author"]


def profession_charisma():
    roll = randint(1, 1000)
    if roll <= 450:
        return choice(["dancer", "singer"])
    elif roll <= 550:
        return "landlord"
    elif roll <= 625:
        return "buccaneer"
    elif roll <= 700:
        return "innkeeper"
    elif roll <= 775:
        return "usurer"
    elif roll <= 800:
        return "fence"
    elif roll <= 875:
        return "hitman"
    elif roll <= 950:
        return "banker"
    elif roll <= 960:
        return "squire"
    elif roll <= 965:
        return "knight"
    elif roll <= 970:
        return "guildmaster " + choice(choice(all_artisans))
    elif roll <= 975:
        return "landless noble"
    elif roll <= 980:
        return "crusader"
    elif roll <= 985:
        return "marshal"
    elif roll <= 990:
        return "lesser noble"
    elif roll <= 994:
        return "middle noble"
    elif roll <= 998:
        return "greater noble"
    else:
        return "royalty"


fixed_results = {
    "farmer": "can raise crops; DR 1 vs ice/cold",
    "fisherman": "have Fishing skill",
    # fisherman and other "have X skill" results may also need to include "(amateur)"
    "sailor": "can handle rowboats and crew ships; +1 on checks/saves to keep balance",
    "teamster": "have Teamstering skill; party's pack animals have +1 morale",
    "guard": "only need 6 hrs of sleep per night; +1 awareness radius",
    "mercenary": "gain bonus weapon proficiency",
    "cavalier": "can ride a warhorse",
    "bounty hunter": "have Tracking skill (from Scouting study)",
    "gladiator": "+1 damage against all humanoids",
    "weapon master": "bonus weapon proficiency: any weapon; +1 damage with that kind of weapon",
    "baker": "DR 1 vs heat/fire",
    "chandler": "DR 1 vs heat/fire",
    "confectioner": "DR 1 vs heat/fire",
    "butcher": "+1 on attacks with dagger",
    "tobacconist": "+1 on checks/saves to stave off nausea (usually saves vs poison)",
    "tailor": "party's cloth goods have +2 on saves",
    "draper": "party's cloth goods have +2 on saves",
    "weaver": "party's cloth goods have +2 on saves",
    "furrier": "party's leather goods have +2 on saves",
    "tanner": "party's leather goods have +2 on saves",
    "leatherworker": "party's leather goods have +2 on saves",
    "cobbler": "party's leather goods have +2 on saves",
    "cooper": "party's wooden goods have +2 on saves",
    "wainwright": "party's wooden goods have +2 on saves",
    "shipwright": "party's wooden goods have +2 on saves",
    "furniture maker": "party's wooden goods have +2 on saves",
    "instrument maker": "pick an instrument: you can play that instrument. Crafting skill aplies only to this kind of instrument",
    "potter": "strong grip gives 5% bonus when climbing",
    "glassmaker": "DR 1 vs heat/fire",
    "glazier": "DR 1 vs heat/fire",
    "smelter": "DR 1 vs heat/fire",
    "jeweller": "appraise gems and jewelry within 25% of actual value",
    "lapidary": "appraise gems and jewelry within 25% of actual value",
    "toolmaker": "appraise metal goods within 25% of actual value",
    "diemaker": "appraise metal goods within 25% of actual value",
    "engraver": "appraise metal goods within 25% of actual value",
    "juggler": "while concentrating, can juggle 3 objects (0.25 to 1.5 lb each); +1 on attacks with thrown weapons",
    "gambler": "can palm an unattended or held item (weight <= 2 oz) into sleeve or pocket",
    "monk": "+1 natural AC",
    "rat catcher": "+1 save vs poison",
    "grave robber": "+1 attack vs undead",
    "drover": "reduce daily travel damage by 1 point",
    "alchemist's assistant": "+1 save vs explosion",
    "blacksmith": "party's metal goods have +2 on saves",
    "armorer": "party's armor has +1 on saves",
    "weaponsmith": "party's armor has +1 on saves",
    "mine foreman": "have Prospecting skill; know direction underground",
    "trapper": "have Hunting skill",
    "hermit": "have Foraging skill",
    "tinker": "have Tinkering skill",
    "carpenter": "design wooden structures; party's wooden goods have +2 on saves",
    "stonemason": "design stone structures; party's stone goods have +2 on saves",
    "boatman": "can handle rowboats and navigate rivers; +1 on checks/saves to keep balance",
    "gameaeeper": "+1 attack vs animals; have Hunting skill",
    "tomb robber": "possess a magic item",
    "artillerist": "gain weapon proficiency with one of: cannon, ballista, catapult, trebuchet",
    "veterinarian": "improve recovery of 3 resting animals by +2 HP/day",
    "hospitaler": "improve recovery of 2 resting people by +2 HP/day",
    "bookkeeper": "have Business Dealing skill",
    "spy": "have Passing Through skill",
    "husbandman": "have Herding skill",
    "prospector": "have Prospecting skill",
    "herbalist": "have Floriculture skill",
    "surgeon's apprentice": "have Binding Wounds skill",
    "priest": "can Turn Undead as if having 5 pts in Dweomercraft",
    "steward": "+1 morale for followers and hirelings",
    "village healer": "can cast a random 1st level druid or cleric spell",
    "mortician": "can embalm corpses; +1 on attacks vs undead",
    "witch hunter": "can Turn Undead as if having 10 pts in Dweomercraft; +1 save vs magic",
    "dancer": "perform war dance for up to 5 rounds/day; all sighted allies within 60 feet gain +1 attack and morale",
    "singer": "sing martial chants for up to 5 rounds/day; all non-deaf allies within 60 feet gain +1 attack and morale",
    "innkeeper": "begin game in possession of one-story house currently serving as an inn",
    "fence": "have black market connections in nearest market town",
    "hitman": "assassinate as a 1st level assassin",
    "landless noble": "hold noble title",
}


def profession_effect(c, prof):
    if not prof:
        return None
    ownership_roll = randint(1, 4)
    ownership = (
        "these lands belong to you personally"
        if ownership_roll == 4
        else "these lands can only belong to you if both your parents, and any siblings older than you, have died"
    )
    if prof == "usurer":
        c.credit += 200 * randint(1, 4)
        return "possess credit"
    elif prof == "banker":
        c.credit += 100 * randint(2, 4) * randint(2, 4)
        return "possess credit"
    elif prof == "cavalier" and c.pClass in martial_classes:
        return "gain bonus weapon proficiency: one of flail, warhammer, or pick"
    elif prof == "bounty hunter" and p.Class == "ranger":
        return "gain bonus weapon proficiency: any missile or throwing weapon"
    elif prof in all_artisans:
        result = (
            "create, identify, and repair "
            + prof
            + " products; "
            + fixed_results.get(prof, "")
        )
        if prof in ["bookbinder", "papermaker"]:
            c.literate = True
            result = result + "; literacy"
        return result
    elif prof == "laborer":
        c.enc_mult += Decimal(0.05)
        return "increase max encumbrance by 5%"
    elif prof == "porter":
        c.enc_mult += Decimal(0.1)
        return "increase max encumbrance by 10%"
    elif prof == "explorer":
        c.literate = True
        return "literacy; knowledge of a distant region; bonus weapon proficiency with unusual weapon from that region"
    elif prof == "scribe":
        c.literate = True
        return ("literacy; gain additional knowledge field",)
    elif prof == "alchemist":
        c.literate = True
        return "literacy; have Amateur status in Alchemy"
    elif prof == "cartographer":
        c.literate = True
        return "literacy; have Locate Self skill"
    elif prof == "architect":
        c.literate = True
        return "literacy; design structures; +1 attack and +10% damage if directing artillery fire"
    elif prof == "lawyer":
        c.literate = True
        return "literacy; have Solicitor skill"
    elif prof == "mage's apprentice":
        c.literate = True
        return "literacy; can cast a random 1st level mage or illusionist spell"
    elif prof == "political advisor":
        c.literate = True
        return "literacy; +10% reaction bonus on any group of three or more people; have Functionary skill"
    elif prof == "spymaster":
        c.literate = True
        return "literacy; have Amateur status in Guile study"
    elif "guildmaster" in prof:
        c.literate = True
        # cut out the "guildmaster" part to find out which guild it is
        x = len("guildmaster ")
        guild = prof[x:]
        result = "literacy; " + profession_effect(c, guild)
        return result
    elif prof == "tutor":
        c.literate = True
        return "literacy; gain additional knowledge field"
    elif prof == "librarian":
        c.literate = True
        return "literacy; gain additional knowledge specialty"
    elif prof == "professor":
        c.literate = True
        return "literacy; gain additional knowledge field and additional specialty within that field"
    elif prof == "ecclesiastical vicar":
        c.literate = True
        return "literacy; +10% reaction with clergymen"
    elif prof == "ecclesiastial rector":
        c.literate = True
        return "literacy; +10% reaction with clergymen; right of free passage throughout this region"
    elif prof == "landlord":
        acres = (
            randint(1, 8)
            + randint(1, 8)
            + randint(1, 8)
            + randint(1, 8)
            + randint(1, 8)
        )
        status = choice(["rented out", "held by family"])
        result = (
            "own "
            + str(acres)
            + " acres of personal land, which is currently "
            + status
        )
        return result
    elif prof == "buccaneer":
        GP = 2 * randint(250, 500)
        result = (
            "can handle boats and crew ships; begin game with 25-foot sloop, which requires "
            + GP
            + " GP in repairs to be usable"
        )
        return result
    elif prof == "squire":
        acres = (randint(1, 4) + randint(1, 4)) * 100
        result = (
            "begin game with " + str(acres) + "-acre estate (640 acres = 1 sq mile)"
        )
        return result
    elif prof == "knight":
        acres = (randint(1, 4) + randint(1, 4) + randint(1, 4)) * 100
        result = (
            "begin game with " + str(acres) + "-acre estate (640 acres = 1 sq mile)"
        )
        return result
    elif prof == "crusader":
        sqmi = randint(2, 4)
        result = (
            "+1 morale for followers and hirelings; family possesses foreign fief of "
            + str(sqmi)
            + " square miles"
        )
        return result
    elif prof == "marshal":
        sqmi = randint(3, 8)
        result = (
            "+1 morale for followers and hirelings; family possesses nearby fief of "
            + str(sqmi)
            + " square miles"
        )
        return result
    elif prof == "lesser noble":
        sqmi = randint(1, 6) + randint(1, 6) + randint(1, 6)
        result = (
            "noble title; +1 morale for followers and hirelings; family possesses fief of "
            + str(sqmi)
            + "square miles;"
            + ownership
        )
        return result
    elif prof == "middle noble":
        sqmi = 10 * (randint(1, 4) + randint(1, 4))
        result = (
            "noble title; +2 morale for followers and hirelings; family possesses fief of "
            + str(sqmi)
            + "square miles;"
            + ownership
        )
        return result
    elif prof == "greater noble":
        area = "one map hex (640 sq mi)"
        result = (
            "noble title; +2 morale for followers and hirelings; family possesses fief of "
            + area
            + ";"
            + ownership
        )
        return result
    elif prof == "royalty":
        r1 = randint(1, 4)
        r2 = 0 if r1 > 1 else randint(1, 4)
        r3 = 0 if r2 > 1 else randint(1, 4)
        r4 = 0 if r3 > 1 else randint(1, 4)
        area = r1 + r2 + r3 + r4
        result = (
            "royal title; +3 morale for followers and hirelings; family possesses fief of "
            + str(area)
            + " map hexes (640 sq mi each); "
            + ownership
        )
        return result
    else:
        return fixed_results.get(prof, "ask Maxwell")
