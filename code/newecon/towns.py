import copy, math
from collections import defaultdict
from decimal import Decimal, getcontext

import references
from references import world_references, u
from a_star_search import a_star_search

# set up the Decimal environment
getcontext().prec = 6

SQMI_PER_HEX = Decimal(346) * u.sqmi


def infrastructure(population):
    return math.floor(population / SQMI_PER_HEX)


towns = {
    # todo add location: Hex(q, r, s)
    # todo add whether a route is by land, sea, or river
    # todo add whether a route is one-way-only
    "Sacra Mara": {
        "population": 8300,
        "references": {"timber": 1, "wine": 1, "limestone": 1},
        "hexes to": {"Allrivers": 1},
    },
    "Castle Docemille": {
        "population": 5200,
        "references": {"smelting": 2},
        "hexes to": {"Fiora": 3},
    },
    "Fiora": {
        "population": 4781,
        "references": {"banking": 1},
        "hexes to": {"Allrivers": 1, "Castle Docemille": 3},
    },
    "Pearl Island": {
        "population": 3000,
        "references": {"eels": 2, "olives": 1, "fish": 2, "timber": 1, "dried fish": 1},
        "hexes to": {"Allrivers": 1.5, "Northshore": 2},
    },
    "Allrivers": {
        "population": 15000,
        "references": {
            "fish": 1,
            "dried fish": 1,
            "cabinetmaking": 1,
            "shipbuilding": 2,
            "timber": 3,
            "carpentry": 1,
            "markets": 2,
            "boatbuilding": 1,
        },
        "hexes to": {
            "Sacra Mara": 1,
            "Fiora": 1,
            "Northshore": 2,
            "Lake Gingol": 1.5,
            "Orii": 1,
            "Pearl Island": 1.5,
            "Sugar Bay": 25,
        },
    },
    "Northshore": {
        "population": 5000,
        "references": {"markets": 1},
        "hexes to": {"Allrivers": 2, "Ribossi": 1.5},
    },
    "Lake Gingol": {
        "population": 10000,
        "references": {"cereals": 1, "markets": 1, "slaves": 1, "boatbuilding": 1},
        "hexes to": {"Glimmergate": 2.5, "Allrivers": 1.5},
    },
    "Orii": {
        "population": 7000,
        "references": {
            "cereals": 2,
            "wheat": 2,
            "millet": 1,
            "alchemy": 2,
            "bookbinding": 1,
        },
        "hexes to": {"Allrivers": 1, "Lake Gingol": 3},
    },
    "Ribossi": {
        "population": 2000,
        "references": {
            "cattle": 1,
            "timber": 2,
        },
        "hexes to": {"Northshore": 1.5},
    },
    "Sugar Bay": {
        "population": 1202,
        "references": {
            "refined sugar": 2,
            "sugarbeets": 1,
            "sugarcane": 1,
        },
        "hexes to": {"Allrivers": 25},
    },
    "Glimmergate": {
        "population": 22000,
        "references": {
            "iron": 2,
            "ironmongery": 1,
            "emerald": 1,
            "sandstone": 1,
            "limestone": 1,
            "markets": 1,
            "silver": 1,
            "silversmithing": 1,
            "gold": 1,
            "goldsmithing": 1,
            "lead": 1,
            "leadsmithing": 1,
            "metalsmithing": 1,
            "pig iron": 1,
        },
        "hexes to": {"Lake Gingol": 2.5},
    },
}

# decimalize all distances and populations
for town, info in towns.items():
    info["population"] = Decimal(info["population"])
    info["hexes to"] = {k: Decimal(v) for k, v in info["hexes to"].items()}


# fill out towns with all-pairs distances
for source in towns:
    for target in towns:
        if source == target:
            pass
        elif target in towns[source]["hexes to"]:
            # distance from s to t is stipulated in original defn of towns, so reuse it
            # this assumes all distances between source and target are two-way traversable
            towns[target]["hexes to"][source] = towns[source]["hexes to"][target]
        else:
            distance, path = a_star_search(towns, source, target)
            towns[source]["hexes to"][target] = distance


def far_away(towns):
    """Add dummy town representing all the economy activity not yet represented in `towns`, at a far enough distance that exporting will not have a significant effect on existing towns' references."""

    def total_assigned_refs(towns):
        assigned = defaultdict(int)
        for d in [info["references"] for t, info in towns.items()]:
            for k, v in d.items():
                assigned[k] += v
        return assigned

    towns["Far Away"] = {"population": 5_000_000, "references": {}, "hexes to": {}}
    # initialize distances
    for t in towns:
        if t != "Far Away":
            towns[t]["hexes to"]["Far Away"] = Decimal(100)
            towns["Far Away"]["hexes to"][t] = Decimal(100)
    # given G global total refs to commodity X,
    # and M total refs to X already assigned in `towns`,
    # assign all G - M remaining refs to the "Far Away"
    for k, info in world_references.items():
        refs = info["references"]
        remaining_global_refs = max(0, refs - total_assigned_refs(towns)[k])
        towns["Far Away"]["references"][k] = remaining_global_refs


far_away(towns)

# DETERMINING THE MONETARY VALUE OF A GOLD REFERENCE


coin_exchange = {
    "gold": {
        "weight": Decimal(0.4) * u.oz,
        "gold content": Decimal(0.1) * u.oz,
    },
    "silver": {
        "weight": Decimal(0.6) * u.oz,
        "silver content": Decimal(0.0923815) * u.oz,
    },
    "copper": {
        "weight": Decimal(0.8) * u.oz,
        "copper content": Decimal(0.603364) * u.oz,
    },
}

for coin, info in coin_exchange.items():
    info["nickel content"] = info["weight"] - info[f"{coin} content"]

cp_per_gold_ore_ref = (
    world_references["gold"]["production per reference"].to("oz").magnitude
    # gold production measured in oz; official gold content of 1 gold piece = 0.1 oz
    * Decimal(10)
    * u.gp
).to(u.cp)

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
            distance = towns[source]["hexes to"][destination]
            for thing, amount in original_towns[source]["references"].items():
                q = export_quantity(amount, distance)
                if thing in towns[destination]["references"]:
                    towns[destination]["references"][thing] += q
                else:
                    towns[destination]["references"][thing] = q


# DETERMINING EACH TOWN'S PRICE OF 1 PRODUCTION UNIT OF COMMODITIES
# todo don't give a price for every ref, but only the raw materials:
# not all refs have production (e.g. markets)
# some refs are categories which need distribution (e.g. fruit)
# some refs are not raw materials and shouldn't be priced directly (e.g. woolens ... although 'hiring a woollens-maker' might be keyed off that reference, and priced according to the production thereof, no?)


def rarity_multiplier(commodity, local_refs):
    availability_ratio = world_references[commodity]["references"] / local_refs
    # 0.01 smoothing factor so prices don't swing wildly
    return Decimal(1) + (Decimal(0.01) * availability_ratio)


for t, tinfo in towns.items():
    tinfo["price"] = {}
    for commodity, numrefs in tinfo["references"].items():
        winfo = world_references[commodity]
        world_refs = winfo["references"]
        world_prod = winfo["production"]
        if world_refs == 0 or world_prod.magnitude == 0:
            # 'zero problem' - see below
            continue
        else:

            multiplier = rarity_multiplier(commodity, numrefs)
            price_per_ref = multiplier * cp_per_gold_ore_ref
            tinfo["price"][commodity] = (
                price_per_ref / winfo["production per reference"]
            )


def main():
    for commodity in ("fish", "dried fish", "olives", "timber"):
        if (
            world_references[commodity]["references"] == 0
            or world_references[commodity]["production"].magnitude == 0
        ):
            # 'zero  problem'
            continue
        else:
            for t in towns:
                template = "At {}, {} costs {:~}"
                print(template.format(t, commodity, towns[t]["price"][commodity]))


def infra_pop():
    mylist = sorted(towns.keys())
    for town in mylist:
        info = towns[town]
        print(town)
        pop = info["population"]
        print(f"Pop: {pop}", f"Infra: {infrastructure(pop)}")

if __name__ == "__main__":
    main()

# todo: the zero problem
# some commodities have references, but 0 production (common, eg alchemy)
# some commodities have production, but 0 references (uncommon, about half a dozen, eg acid)
# both should be skipped until I figure out ways to "seed" both of these


# sisp 0.0739052 oz, 10 sp/gp
# cicp 0.301683 oz, 20 cp/sp -> 200 cp/gp
# sisp 0.0739052 oz, 10 sp/gp
# cicp 0.603365 oz, 20 cp/sp -> 200 cp/gp
# sisp 0.14781 oz, 10 sp/gp
# cicp 0.603365 oz, 20 cp/sp -> 200 cp/gp

# sisp 0.0923815 oz, 8 sp/gp
# cicp 0.301683 oz, 25 cp/sp -> 200 cp/gp
# sisp 0.
# cicp 0.603368 oz, 25 cp/sp -> 200 cp/gp
# sisp 0.184762 oz, 8 sp/gp
# cicp 0.603364 oz, 25 cp/sp -> 200 cp/gp
