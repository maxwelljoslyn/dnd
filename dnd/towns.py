import copy
import math
from collections import defaultdict
from decimal import Decimal, getcontext
import warnings
import logging

import references
from a_star_search import a_star_search
from references import u, world_references
import web
import sqlyte
from models import town_model

# logging.basicConfig(level=logging.DEBUG, force=True)

# set up the Decimal environment
getcontext().prec = 6

SQMI_PER_HEX = Decimal(346) * u.sqmi


def infrastructure(population):
    return math.floor(population / SQMI_PER_HEX.magnitude)


def total_assigned_refs(towns):
    assigned = defaultdict(int)
    for d in [info["references"] for t, info in towns.items()]:
        for k, v in d.items():
            assigned[k] += v
    return assigned


def has_market(town):
    return "markets" in original_towns[town]["references"]


def export_quantity(amount, distance):
    return Decimal(amount / (distance + 1))


def far_away(towns):
    """Add dummy town representing all the economy activity not yet represented in `towns`, at a far enough distance that exporting will not have a significant effect on existing towns' references."""

    towns["Far Away"] = {"population": 5_000_000, "references": {}, "hexes to": {}}
    # initialize distances
    for t in towns:
        if t != "Far Away":
            towns[t]["hexes to"]["Far Away"] = Decimal(100)
            towns["Far Away"]["hexes to"][t] = Decimal(100)
    # given G global total refs to commodity X,
    # and M total refs to X already assigned in `towns`,
    # assign all G - M remaining refs to the "Far Away"
    totals = total_assigned_refs(towns)

    for k, info in world_references.items():
        refs = info["references"]
        remaining_global_refs = refs - totals[k]
        if remaining_global_refs < 0:
            warnings.warn(
                f"You have assigned {abs(remaining_global_refs)} more refs to {k} than listed in world_references!"
            )
        refs_for_faraway = max(0, remaining_global_refs)
        towns["Far Away"]["references"][k] = refs_for_faraway


def initialize_towns(towns):
    # decimalize all distances and populations
    for town, info in towns.items():
        info["population"] = Decimal(info["population"])
        info["hexes to"] = {k: Decimal(v) for k, v in info["hexes to"].items()}

    # fill out all-pairs shortest paths
    for source in towns:
        for target in towns:
            if source == target:
                pass
            elif target in towns[source]["hexes to"]:
                # distance from s to t is stipulated in original defn of towns, so reuse it
                # NOTE assumes all distances between source and target are two-way traversable
                towns[target]["hexes to"][source] = towns[source]["hexes to"][target]
            else:
                distance, path = a_star_search(towns, source, target)
                towns[source]["hexes to"][target] = distance

    far_away(towns)
    # export step changes `towns` reference counts in-place, but export calculations require access to original counts
    originals = copy.deepcopy(towns)
    return towns, originals


def export_references(towns, original_towns):
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
    return towns


def rarity_multiplier(commodity, local_refs):
    availability_ratio = world_references[commodity]["references"] / local_refs
    # 0.01 smoothing factor so prices don't swing wildly
    return Decimal(1) + (Decimal(0.01) * availability_ratio)


def determine_unit_prices(towns):
    # TODO don't give a price for every ref, but only the raw materials:
    # not all refs have production (e.g. markets)
    # some refs are categories which need distribution (e.g. fruit)
    # some refs are not raw materials and shouldn't be priced directly (e.g. woolens ... although 'hiring a woollens-maker' might be keyed off that reference, and priced according to the production thereof, no?)
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
    return towns


def infra_pop(towns):
    mylist = sorted(towns.keys())
    for town in mylist:
        info = towns[town]
        print(town)
        pop = info["population"]
        print(f"Pop: {pop}", f"Infra: {infrastructure(pop)}")


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

# DETERMINING THE MONETARY VALUE OF A GOLD REFERENCE

cp_per_gold_ore_ref = (
    world_references["gold"]["production per reference"].to("oz").magnitude
    # gold production measured in oz; official gold content of 1 gold piece = 0.1 oz
    * (u.oz / coin_exchange["gold"]["gold content"])
    * u.gp
).to(u.cp)


towns = {
    # todo add location: Hex(q, r, s)
    # todo add whether a route is by land, sea, or river
    # todo add whether a route is one-way-only
    # NOTE 'hexes to' takes into account elevation changes, so it is NOT hexes as the crow flies -- it is 'hex equivalent' distance
    "Sacra Mara": {
        "population": 8300,
        "references": {
            "timber": 1,
            "wine": 2,
            "grapes": 2,
            "wine, Sacramaran": 1,
            "champagne": 1,
            "limestone": 1,
            "wheat": 1,
        },
        "hexes to": {"Allrivers": 1},
    },
    "Castle Docemille": {
        "population": 5200,
        "references": {
            "smelting": 2,
            "wine, Lutewood": 1,
            "timber": 1,
            "mandarin oranges": 1,
            "figs": 2,
            "persimmons": 1,
            "pomegranates": 1,
            "carobs": 1,
            "pistachios": 1,
            "carobs": 1,
            "loquats": 1,
            "wheat": 4,
        },
        "hexes to": {"Fiora": 3},
    },
    "Fiora": {
        "population": 4781,
        "references": {"banking": 1},
        "hexes to": {"Allrivers": 1, "Castle Docemille": 3},
    },
    "Pearl Island": {
        "population": 5800,
        "references": {
            "eels": 1,
            "olives": 2,
            "olive oil": 2,
            "fish": 2,
            "timber": 1,
            "dried fish": 1,
        },
        "hexes to": {"Allrivers": 1.5, "Northshore": 2},
    },
    "Allrivers": {
        "population": 45000,
        "references": {
            "fish": 1,
            "dried fish": 1,
            "cabinetmaking": 1,
            "shipbuilding": 2,
            "timber": 4,
            "carpentry": 1,
            "grapes": 2,
            "markets": 2,
            "boatbuilding": 1,
            "woodcraft": 1,
            "wine": 2,
        },
        "hexes to": {
            "Sacra Mara": 1,
            "Fiora": 1,
            "Shipmoot": 1,
            "Lake Gingol": 1.5,
            "Orii": 1,
            "Pearl Island": 1.5,
            "Sugar Bay": 25,
            "Saint Marcus": 99,
        },
    },
    "Northshore": {
        "population": 5000,
        "references": {
            "markets": 1,
            "armor": 1,
        },
        "hexes to": {"Shipmoot": 1, "Ribossi": 1.5},
    },
    "Shipmoot": {
        "population": 3821,
        "references": {"shipbuilding": 1, "woodcraft": 1},
        "hexes to": {"Northshore": 1, "Allrivers": 1, "Castle Baccia": 1},
    },
    "Castle Baccia": {
        "population": 900,
        "references": {
            "wine": 1,
            "wine, Baccia": 1,
            "grapes": 3,
            "timber": 1,
        },
        "hexes to": {"Shipmoot": 1, "Ribossi": 1},
    },
    "Lake Gingol": {
        "population": 10000,
        "references": {
            "cereals": 3,
            "wheat": 1,
            "markets": 1,
            "slaves": 2,
            "boatbuilding": 1,
        },
        "hexes to": {"Glimmergate": 2.5, "Allrivers": 1.5},
    },
    "Orii": {
        "population": 7000,
        "references": {
            "markets": 1,
            "cereals": 2,
            "wheat": 2,
            "brewing": 4,
            "gnomish beer": 1,
            "millet": 1,
            "rye": 2,
            "alchemy": 2,
            "foodstuffs": 3,
            "fodder": 2,
            "bookbinding": 1,
            "paper": 1,
            "paper products": 1,
            "pearl": 1,
            "apricots": 1,
            "pears": 1,
            "pomegranates": 1,
            "cherries": 1,
            "peaches": 1,
        },
        "hexes to": {"Allrivers": 1, "Lake Gingol": 3},
    },
    "Ribossi": {
        "population": 2000,
        "references": {
            "timber": 2,
            "wine, asti spumante": 2,
        },
        "hexes to": {"Northshore": 1.5, "Parinea": 3},
    },
    "Sugar Bay": {
        "population": 1202,
        "references": {
            "refined sugar": 2,
            "sugarcane": 2,
            "rum": 2,
            "coconuts": 1,
        },
        "hexes to": {"Allrivers": 25},
    },
    "Glimmergate": {
        "population": 22000,
        "references": {
            "markets": 2,
            "iron": 2,
            "ironmongery": 1,
            "pig iron": 2,
            "metalsmithing": 1,
            "alloys": 2,
            "limestone": 1,
            "dolomite": 1,
            "silver": 1,
            "silversmithing": 1,
            "gold": 1,
            "goldsmithing": 1,
            "lead": 1,
            "leadsmithing": 1,
            "leadsmelting": 1,
            "nickel": 1,
            "nickelsmelting": 1,
            "pewter": 1,
        },
        "hexes to": {
            "Lake Gingol": 2.5,
            "Dwerglow": 1,
            "Giantsbane": 2,
        },
    },
    "Dwerglow": {
        "population": 7029,
        "references": {
            "emerald": 1,
            "alexandrite": 1,
            "chrysoprase": 1,
            "limestone": 1,
            "masonry": 1,
            "freestone": 1,
        },
        "hexes to": {"Glimmergate": 1, "Stoneshire": 2},
    },
    "Giantsbane": {
        "population": 4817,
        "references": {
            "common opal": 1,
            "azurite": 1,
            "quartz, blue": 1,
            "quartz": 1,
            "diamond": 1,
            "gemcarving": 1,
            "gemcutting": 2,
            "agate": 1,
            "cat's eye": 1,
            "amethyst": 1,
            "mercury": 1,
        },
        "hexes to": {"Grut": 4, "Langakuur": 2},
    },
    "Stoneshire": {
        "population": 4985,
        "references": {
            "bricks": 2,
            "ceramics": 3,
            "pottery": 2,
            "flint": 1,
            "enamelware": 1,
            "lacquerware": 1,
            "glassware": 1,
            "masonry": 1,
        },
        "hexes to": {"Dwerglow": 2, "Sheepshire": 1},
    },
    "Sheepshire": {
        "population": 2801,
        "references": {
            "sheep": 3,
            "mutton": 2,
            "meat": 1,
            "lamb": 1,
            "cheese, ewes' milk": 1,
            "wool": 3,
            "woolen cloth": 2,
            "woolen goods": 2,
            "worsted cloth": 1,
            "worsted goods": 1,
            "dogs": 1,
            "donkeys": 2,
            "goats": 3,
        },
        "hexes to": {"Dwerglow": 2, "Stoneshire": 1},
    },
    "Langakuur": {
        "population": 3393,
        "references": {
            "griffs": 3,
            "edible birds' nests": 1,
            "niter": 2,
        },
        "hexes to": {"Giantsbane": 2, "Uluban": 1, "Tloon": 4},
    },
    "Tloon": {
        "population": 17092,
        "references": {
            "alchemy": 2,
            "markets": 1,
            "weapons": 1,
            "armor": 1,
            "horncarving": 2,
            "geese": 1,
            "furs": 1,
        },
        "hexes to": {"Wasteguard": 1, "Langakuur": 4},
    },
    "Wasteguard": {
        "population": 0,
        "references": {},
        "hexes to": {"Tloon": 1, "Talamorga": 3},
    },
    "Talamorga": {
        "population": 40_000,
        "references": {
            "markets": 4,
            "bread, black": 2,
            "bread": 2,
            "beans": 4,
            "fodder": 2,
            "foodstuffs": 5,
            "peas": 2,
            "soybeans": 1,
            "potatoes": 3,
            "pulses": 2,
            "hay": 2,
            "artichokes": 1,
            "peppers": 1,
            "eggplants": 1,
            "brewing": 3,
            "rabbits": 1,
        },
        "hexes to": {"Wasteguard": 3},
    },
    "Grut": {
        "population": 0,
        "references": {
            "weapons": 2,
            "quartz": 1,
            "quartz, blue": 1,
            "fire opal": 1,
        },
        "hexes to": {"Giantsbane": 4},
    },
    "Uluban": {
        "population": 9800,
        "references": {
            "griffs": 1,
            "markets": 1,
            "horses": 2,
            "sulfur": 2,
            "leathercraft": 2,
            "blankets": 1,
        },
        "hexes to": {"Langakuur": 1, "Lower Uluban": 4},
    },
    "Lower Uluban": {
        "population": 1000,
        "references": {
            "horses": 3,
            "horses, draft": 1,
            "saddles": 1,
            "embroidery": 1,
            "ponies": 1,
            "cattle": 2,
            "goats": 1,
            "dogs": 1,
            "kumiss": 1,
            "leathercraft": 2,
            "meat": 2,
            "furs": 2,
            "horncarving": 1,
            "bonecarving": 1,
            "blankets": 1,
        },
        "hexes to": {"Uluban": 4},
    },
    "Parinea": {
        "population": 18000,
        "references": {
            "horses, draft": 1,
        },
        "hexes to": {"Ribossi": 3},
    },
    "Saint Marcus": {
        "population": 19100,
        "references": {
            "cochineal": 2,
            "tobacco": 3,
        },
        "hexes to": {"Allrivers": 99},
    },
}


towns, original_towns = initialize_towns(towns)
towns = export_references(towns, original_towns)
towns = determine_unit_prices(towns)


def dbify_towns(db, towns):
    with db.transaction as cur:
        for town, info in towns.items():
            logging.debug(f"inserting {town}")
            rowid = cur.insert("towns", name=town, population=info["population"])
            refs = []
            for ref, amount in info["references"].items():
                logging.debug(f" {town}: {ref}: {str(amount)}")
                refs.append(dict(town=rowid, name=ref, amount=str(amount)))
            cur.insert("town_references", *refs)
            travels = []
            for destination, distance in info["hexes to"].items():
                logging.debug(f" {town}: to {destination}: {distance}")
                travels.append(
                    dict(source=rowid, destination=destination, distance=distance)
                )
            cur.insert("travel_times", *travels)
            materials = []
            for thing, unit_price in info["price"].items():
                materials.append(dict(town=rowid, name=thing, price=str(unit_price)))
            cur.insert("material_costs", *materials)


def main():
    db = sqlyte.db("foo.db", sqlyte.Model("town_model", **town_model))
    dbify_towns(db, towns)


def sanity_check():
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


if __name__ == "__main__":
    main()

# todo: the zero problem
# some commodities have references, but 0 production (common, eg alchemy)
# some commodities have production, but 0 references (uncommon, about half a dozen, eg acid, sugar)
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
