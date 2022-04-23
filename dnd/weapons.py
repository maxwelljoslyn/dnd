# TODO I KNOW THAT, LIKE RACES AND CLASSES, THIS WILL BECOME A DEEPLY NESTED DATA STRUCTURE
# TODO decide on these weapons: quoit/dart, mancatcher, sword cane, nunchucks
# TODO add greatclub as a lighter, cheaper, weaker, wood-only alternative to the goedendag?


weapons = {
    "shuriken": {
        "hands": 1,
        "damage": "1d2",
        "form": ["thrown"],
        "range": (4, 6, 8),
    },
    "dart": {
        "hands": 1,
        "damage": "1d3",
        "form": ["melee", "thrown"],
        "range": (3, 4, 5),
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
        "form": ["melee"],
    },
    "battleaxe": {
        "hands": 2,
        "damage": "2d4",
        "includes": ["pickaxe", "military pick"],
    },
    "bolas": {
        "hands": 1,
        "damage": "1d3",
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
        "includes": ["tonfa", "shillelagh"],
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
        "hands": 1,
        "includes": [
            "ball and chain",
            "meteor hammer",
            "kusari-gama",
        ],
        "form": ["melee"],
    },
    "glaive": {
        "hands": 2,
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
    },
    "greatsword": {
        "damage": "1d12",
        "includes": ["claymore", "two-handed sword"],
        "hands": 2,
    },
    "halberd": {
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
    "handaxe": {"hands": 1, "damage": "1d6+1"},
    "javelin": {"hands": 1},
    "lance": {
        "hands": 1,
        "note": "can only be used with a special attachment, while mounted on a war-trained steed",
    },
    "longbow": {"hands": 2},
    "longsword": {"damage": "1d8", "includes": ["falchion", "bastard sword"]},
    "mace": {"includes": ["morning star"]},
    "pike": {"hands": 2},
    "quarterstaff": {"damage": "1d6", "hands": 2},
    "scimitar": {
        "includes": ["saber", "cutlass", "khopesh", "sickle sword", "hunting sword"],
        "hands": 1,
    },
    "shortsword": {
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
    "sling staff": {"hands": 2},
    "sling": {"hands": 1},
    "spear": {
        "hands": 1,
        "form": ["melee", "thrown"],
        "range": (4, 7, 10),
    },
    "warhammer": {"hands": 1},
    "scimitar": {
        "includes": ["saber", "cutlass", "khopesh", "sickle sword", "hunting sword"],
        "hands": 1,
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
