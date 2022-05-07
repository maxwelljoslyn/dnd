# TODO I KNOW THAT, LIKE RACES AND CLASSES, THIS WILL BECOME A DEEPLY NESTED DATA STRUCTURE
# TODO decide on these weapons: mancatcher, sword cane, nunchucks
# TODO add greatclub as a lighter, cheaper, weaker, wood-only alternative to the goedendag?


weapons = {
    "shuriken": {
        "hands": 1,
        "damage": "1d2",
        "form": ["thrown"],
        "range": (4, 6, 8),
        "includes": ["throwing knife"],
    },
    "dart": {
        "hands": 1,
        "damage": "1d3",
        "form": ["melee", "thrown"],
        "range": (3, 4, 5),
        "includes": ["quoit", "plumbata"],
    },
    "chakram": {
        "hands": 1,
        "damage": "1d4",
        "form": ["melee", "thrown"],
        "range": (6, 9, 12),
    },
    "cestus": {
        "hands": 1,
        "damage": "+1",
        "includes": ["brass knuckles"],
        "form": ["melee"],
        "note": "improves damage of unarmed attack",
    },
    "trident": {
        "hands": 1,
        "damage": "1d4+1",
        "includes": ["sai"],
        "form": ["melee", "thrown"],
        "range": (3, 4, 5),
    },
    "battleaxe": {
        "hands": 2,
        "damage": "1d8+1",
        "form": ["melee"],
        "includes": ["pickaxe", "military pick"],
    },
    "bolas": {
        "hands": 1,
        "damage": "1d3",
        "form": ["thrown"],
        "range": (5, 10, 15),
        "note": "if successful hit also hits AC 20, defender saves vs explosion: failure leaves defender helpless, while success leaves defender entangled for 1d4+1 rounds",
    },
    "bow": {
        "hands": 2,
        "damage": "1d6",
        "form": ["missile"],
        "range": (15, 30, 45),
    },
    "broadsword": {
        "hands": 2,
        "damage": "1d10",
        "form": ["melee"],
    },
    "club": {
        "hands": 1,
        "damage": "1d6",
        "includes": ["tonfa", "truncheon", "shillelagh", "Chinese hard whip"],
        "form": ["melee"],
    },
    "dagger": {
        "hands": 1,
        "damage": "1d4",
        "includes": ["dirk"],
        "form": ["melee", "thrown"],
        "range": (2, 3, 4),
    },
    "flail": {
        "damage": "1d6+1",
        "hands": 1,
        "includes": [
            "ball and chain",
            "meteor hammer",
            "kusari-gama",
        ],
        "form": ["melee"],
    },
    "glaive": {
        "damage": "1d8",
        "hands": 2,
        "form": ["melee"],
        "includes": [
            "guisarme",
            "faulchard",
            "voulge",
            "bec de corbin",
            "ranseur",
            "corseque",
            "other stabbing/hooking/forking polearms",
        ],
    },
    "goedendag": {
        "hands": 2,
        "damage": "2d4",
        "form": ["melee"],
        "includes": ["maul"],
    },
    "greatsword": {
        "damage": "1d12",
        "hands": 2,
        "includes": ["claymore", "two-handed sword"],
        "form": ["melee"],
    },
    "halberd": {
        "form": ["melee"],
        "damage": "1d10",
        "hands": 2,
        "includes": [
            "poleaxe",
            "naginata",
            "lucerne hammer",
            "guandao",
            "yanyuedao",
            "other slashing/smashing/crushing/chopping polearms",
        ],
    },
    "handaxe": {
        "hands": 1,
        "damage": "1d6+1",
        "form": ["melee"],
        "includes": ["tomahawk"],
    },
    "javelin": {
        "hands": 1,
        "damage": "1d6",
        "form": ["thrown"],
        "range": (8, 14, 20),
    },
    "lance": {
        "damage": "1d6",
        "hands": 1,
        "form": ["melee"],
        "note": "can only be used with a special attachment, while mounted on a war-trained steed",
    },
    "longsword": {
        "damage": "1d8",
        "form": ["melee"],
        "includes": ["falchion", "bastard sword"],
    },
    "mace": {
        "damage": "1d6+1",
        "includes": ["morning star", "holy water sprinkler"],
        "form": ["melee"],
    },
    "pike": {
        "hands": 2,
        "form": ["melee"],
        "damage": "2d4",
        "note": "extreme length means -1 to hit unless setting against a charge or fighting in a pike square formation",
    },
    "quarterstaff": {
        "damage": "1d6",
        "hands": 2,
        "form": ["melee"],
    },
    "shortsword": {
        "form": ["melee"],
        "damage": "1d6",
        "hands": 1,
        "includes": [
            "dueling rapier",
            "smallsword",
            "cutlass",
            "hanger",
            "gladius",
            "arming sword",
            "estoc",
        ],
    },
    "sling staff": {
        "damage": "1d4",
        "hands": 2,
        "form": ["missile"],
        "range": (8, 14, 20),
    },
    "sling": {
        "damage": "1d4",
        "hands": 1,
        "form": ["missile"],
        "range": (6, 10, 14),
    },
    "spear": {
        "damage": "1d6",
        "hands": 2,
        "form": ["melee", "thrown"],
        "range": (4, 7, 10),
        "note": "only need 1 hand to throw",
    },
    "warhammer": {
        "hands": 1,
        "form": ["melee", "thrown"],
        "damage": "1d6",
        "range": (2, 3, 4),
    },
    "scimitar": {
        "form": ["melee"],
        "damage": "1d6",
        "includes": ["saber", "cutlass", "khopesh", "sickle sword", "hunting sword"],
        "hands": 1,
    },
    "spiked whip": {
        "damage": "1d4+1",
        "note": "exotic (character can only be proficient by spending 2 proficiency slots, by gaining a proficiency from a sage study, or by having a father with the 'explorer' background); deals bleeding wounds at multiples of 9 damage instead of 11",
        "hands": 1,
        "form": ["melee"],
    },
    "whip": {
        "damage": "1d4",
        "hands": 1,
        "form": ["melee"],
    },
}

armors = {
    "gambeson": {"AC bonus": 1},
    "leather": {"AC bonus": 2},
    "coat of plates": {"AC bonus": 3},
    "hauberk": {"AC bonus": 4},
    "haubergeon": {"AC bonus": 5},
    "cuirass": {"AC bonus": 6},
    "half-plate": {"AC bonus": 7},
    "full-plate": {"AC bonus": 8},
}


def main():
    import tradegoods

    done = []
    for r in tradegoods.registry:
        if r in weapons:
            done.append(r)
    undone = [w for w in weapons if w not in done]
    print("weapons implemented in equipment system", done, sep="\n")
    print("not yet implemented", undone, sep="\n")


if __name__ == "__main__":
    main()
