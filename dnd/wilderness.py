def _base_wilderness_damage_chance(days):
    return days * 5


wilderness_damage_chance_modifiers = {
    # TODO modifiers for footwear newness ... gah!
    "footwear": {
        "none": 12,
        "sandals, espadrilles, or moccasins": 8,
        "soft boots": 4,
        "hard boots": 0,
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


def wilderness_damage_chance(days, footwear, ability_scores, resistance=0):
    chance = _base_wilderness_damage_chance(days)
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
