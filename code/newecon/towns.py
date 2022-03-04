import copy, math
from collections import defaultdict
from decimal import Decimal, getcontext

import references
from references import world_references
from a_star_search import a_star_search

# set up the Decimal environment
getcontext().prec = 6

# todo don't forget that the TRADE distance is 1 more than the number of days away (so that places 1 day away do not export 100% of references)
towns = {
    # todo add location: Hex(q, r, s)
    # todo add whether a route is by land, sea, or river
    # todo add whether a route is one-way-only
    "Pearl Island": {
        "population": 3000,
        "references": {"olives": 1, "fish": 1, "dried fish": 1},
        "days to": {"Allrivers": 1.5, "Northshore": 2},
    },
    "Allrivers": {
        "population": 15000,
        "references": {"timber": 3, "markets": 1},
        "days to": {"Northshore": 2, "Gingol": 1.5, "Orii": 1, "Pearl Island": 1.5},
    },
    "Northshore": {
        "population": 5000,
        "references": {"timber": 1, "markets": 1},
        "days to": {"Allrivers": 2, "Ribossi": 1.5},
    },
    "Gingol": {
        "population": 10000,
        "references": {"cereals": 1, "markets": 1},
        "days to": {"Glimmergate": 2.5, "Allrivers": 1.5},
    },
    "Orii": {
        "population": 7000,
        "references": {"cereals": 1},
        "days to": {"Allrivers": 1, "Gingol": 3},
    },
    "Ribossi": {
        "population": 2000,
        "references": {"cattle": 1},
        "days to": {"Northshore": 1.5},
    },
    "Glimmergate": {
        "population": 22000,
        "references": {"sandstone": 1, "limestone": 1, "markets": 1, "smelting": 1},
        "days to": {"Gingol": 2.5},
    },
}



# decimalize all distances
for town, info in towns.items():
    info["days to"] = {k: Decimal(v) for k, v in info["days to"].items()}


# fill out towns with all-pairs distances
for source in towns:
    for target in towns:
        if source == target:
            pass
        elif target in towns[source]["days to"]:
            # distance from s to t is stipulated in original defn of towns, so reuse it
            # this assumes all distances between source and target are two-way traversable
            towns[target]["days to"][source] = towns[source]["days to"][target]
        else:
            distance, path = a_star_search(towns, source, target)
            towns[source]["days to"][target] = distance

total_assigned_refs = defaultdict(int)
for d in [info["references"] for t, info in towns.items()]:
    for k, v in d.items():
        total_assigned_refs[k] += v


def far_away():
    global towns
    towns["Far Away"] = {"references": {}, "days to": {}}
    # initialize distances
    for t in towns:
        if t != "Far Away":
            towns[t]["days to"]["Far Away"] = Decimal(100)
            towns["Far Away"]["days to"][t] = Decimal(100)

    # given G global total refs to commodity X,
    # and M total refs to X already assigned in `towns`,
    # assign all G - M remaining refs to Far Away
    for k, info in world_references.items():
        refs = info["references"]
        remaining_global_refs = max(0, refs - total_assigned_refs[k])
        towns["Far Away"]["references"][k] = remaining_global_refs


far_away()

# DETERMINING THE MONETARY VALUE OF A GOLD REFERENCE

# todo move to references.py - all except 'average refs per town' is fair game
for k, info in world_references.items():
    # calculations requiring both towns and world_references
    refs = info["references"]
    amount, unit = info["production"]
    # 'zero problem' - see below
    if refs == 0 or amount == 0:
        continue
    else:
        info["average references per town"] = refs / Decimal(len(towns.keys()))
        info["production per reference"] = (amount / refs, unit)

# todo more elegant way to do this with less chance of error by defining one side of ratio and inferring the other?
coin_exchange = {
    "gold": {
        "weight": (Decimal(0.4), "oz"),
        "silver": Decimal(8),
        "copper": Decimal(200),
    },
    "silver": {
        "weight": (Decimal(0.6), "oz"),
        "copper": Decimal(25),
        "gold": Decimal(1) / Decimal(8),
    },
    "copper": {
        "weight": (Decimal(0.8), "oz"),
        "silver": Decimal(1) / Decimal(25),
        "gold": Decimal(1) / Decimal(200),
    },
}

cp_per_gold_ore_ref = (
    # note assumption that gold production measured in oz!
    world_references["gold"]["production per reference"][0]
    * 10  # official gold content of 1 gold piece = 0.1 oz
    * coin_exchange["gold"]["copper"]
)

# EXPORTING

# export step will change `towns` reference counts in-place
# but performing the calculations for those exports will require access to the original references
original_towns = copy.deepcopy(towns)


def export_quantity(amount, distance):
    return Decimal(amount / (distance + 1))


for source in original_towns:
    for destination in towns:
        if source == destination:
            pass
        else:
            # given town T with N *original* references to commodity Q,
            # and another town R at distance D,
            # export N/(D+1) references of Q to R
            distance = towns[source]["days to"][destination]
            for thing, amount in original_towns[source]["references"].items():
                q = export_quantity(amount, distance)
                if thing in towns[destination]["references"]:
                    towns[destination]["references"][thing] += q
                else:
                    towns[destination]["references"][thing] = q


# DETERMINING EACH TOWN'S PRICE OF 1 PRODUCTION UNIT OF A COMMODITY

for t, tinfo in towns.items():
    tinfo["cp per unit"] = {}
    for commodity, numrefs in tinfo["references"].items():
        cinfo = world_references[commodity]
        refs = cinfo["references"]
        amount, unit = cinfo["production"]
        # 'zero problem' - see below
        if refs == 0 or amount == 0:
            continue
        else:
            # how does this town's num refs to commodity compare to average?
            availability_ratio = numrefs / cinfo["average references per town"]
            # thus, if average town has 1 reference to iron ore, and town T has 3, ratio is 3, and ore will cost 1/5 there
            price_per_ref = cp_per_gold_ore_ref / availability_ratio
            # todo do I need to put production unit into tinfo,
            # or OK to retrieve later from worldrefs[commodity]['production per unit'][1]?
            tinfo["cp per unit"][commodity] = (
                price_per_ref / cinfo["production per reference"][0]
            )


def main():
    p = towns["Pearl Island"]["cp per unit"]
    foo = []
    for commodity, info in world_references.items():
        refs = info["references"]
        amount, unit = info["production"]
        if commodity in p:
            foo.append((commodity, p[commodity], unit))
    foo.sort(key=lambda x: x[1])
    for commodity, price, unit in foo:
        print(f"{commodity} costs {price} CP / {unit}")


if __name__ == "__main__":
    main()

# todo: the zero problem
# some commodities have references, but 0 production (common, eg alchemy)
# some commodities have production, but 0 references (uncommon, about half a dozen, eg acid)
# both should be skipped until I figure out ways to "seed" both of these
