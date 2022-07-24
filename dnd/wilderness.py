road_types = {
    "high": {
        "miles per 10 hours": 15,
        "description": "Wide, smooth, and durable road suitable for frequent and heavy commercial traffic. Made of closely-fitted paving stones surfaced with asphalt. Drainage ditches keep road usable year-round.",
    },
    "cobbled": {
        "miles per 10 hours": 12,
        "description": "Hard but uneven road made of irregular cobblestones fitted with mortar. Minimal drainage. 4 in 6 chance per mile of dirt shoulder, allowing unimpeded passage of vehicle traffic from other direction (otherwise, passing or being passed when both sides are in vehicles requires extra time.)",
    },
    "rutted": {
        "miles per 10 hours": 8,
        "description": "Hardened dirt road with carved ruts laid with loose stone; suitable for carts but not wagons; if one cart must pass another, 1 in 12 chance that passing cart becomes entangled in vegetation",
    },
    "trail": {
        "miles per 10 hours": 6,
        "description": "Earthen footpath made by clearing vegetation, removing stones, and hacking the ground. Route skirts trees and large rocks. Maintained each year during the dry season.",
    },
    "path": {
        "miles per 10 hours": 4,
        "description": "Remnant of regular animal traffic. Constant protruding vegetation forces travelers to survey each twist and turn before making each movement. Often terminates abruptly, possibly picking up again nearby.",
    },
    "no road": {
        "miles per 10 hours": 2,
        "description": "Unimproved wilderland with minimal animal presence and no humanoid activity. Progress is impeded by deadfalls, mud, rocks, dense shrubbery, and other natural obstacles.",
    },
}


def base_wilderness_damage_chance(days):
    return sum((5 * n for n in range(0, days + 1)))


wilderness_damage_chance_modifiers = {
    "footwear": {
        # TODO modifiers for footwear newness ... gah!
        "barefoot": 12,
        "sandals, espadrilles, or moccasins": 8,
        "soft boots": 4,
        "hard boots": 0,
    },
    "sleeping environment": {
        "outdoors": 8,
        "indoors": 3,
    },
    "sleeping equipment": {
        "nothing": 10,
        "blankets": 7,
        "bedroll": 3,
        "bed": 0,
    },
    "constitution": {
        "above/below 10": "-1/+1 per point",
    },
    "dexterity": {
        "above/below 10": "-1/+1 per point",
    },
    "wisdom": {
        "above/below 10": "-1/+1 per point",
    },
}


def wilderness_damage_chance(days, ability_scores, **kwargs):
    footwear = kwargs.get("footwear", "barefoot")
    resistance = kwargs.get("resistance", 0)
    chance = base_wilderness_damage_chance(days)
    chance += wilderness_damage_chance_modifiers["footwear"][footwear]
    for abi, score in ability_scores.items():
        if abi not in wilderness_damage_chance_modifiers:
            pass
        else:
            # TODO TYPE LEVEL GUARANTEE of a non-negative score
            # 10 is average ability score for (playable race) humanoids
            diff = abs(score - 10)
            # higher scores subtract from chance
            if score > 10:
                chance -= diff
            else:
                chance += diff
    if resistance:
        # TODO rename resistance; that word already reserved for lessening of *damage itself*
        # an amount up to resistance is subtracted from base chance
        # resistance is depleted by the same amount
        # example: with 5 resistance and 3 base chance, base chance becomes 0 and remaining resistance is 3
        # example: with 10 resistance and 20 base chance, base chance becomes 10 and remaining resistance is 0
        amount_to_subtract = min(resistance, chance)
        chance -= amount_to_subtract
        resistance -= amount_to_subtract
    return max(0, chance), resistance


def wilderness_damage_dice(chance, d100_roll):
    die = (1, 4)
    dicepool = []
    while chance > 100:
        # above X * 100% chance, X damage rolls are certain
        dicepool.append(die)
        chance -= 100
    if d100_roll <= chance:
        dicepool.append(die)
    return dicepool
