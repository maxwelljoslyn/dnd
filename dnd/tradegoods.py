from decimal import Decimal, getcontext, localcontext, ROUND_UP
from math import ceil, floor
from collections import Counter
import logging
import json
import random
from mjtime import week_of_year
from pendulum import Date

# from functools import lru_cache

# logging.basicConfig(level=logging.DEBUG, force=True)

from references import Q, u, world_references, categories
from towns import towns
from characters import races
from jsonize import MyEncoder
import sqlyte
from models import tradegood_model
from rich.progress import Progress


# set up the Decimal environment
getcontext().prec = 4

D = Decimal

pi = Decimal(1) * u.pi

registry = dict()
vendors = set()
# the subset of vendors available at a settlement with no market references
limited_vendors = {
    "blacksmith",
    "brewer",
    "butcher",
    "costermonger",
    "greengrocer",
    "innkeeper",
    "stockyard",
    "tavern",
    "vintner",
}

chance_available_map = {
    1 * u.cp: 100,
    5 * u.cp: 99,
    10 * u.cp: 97,
    15 * u.cp: 95,
    20 * u.cp: 93,
    1 * u.sp: 90,
    2 * u.sp: 88,
    3 * u.sp: 86,
    4 * u.sp: 84,
    6 * u.sp: 82,
    1 * u.gp: 80,
    2 * u.gp: 77,
    3 * u.gp: 74,
    5 * u.gp: 71,
    8 * u.gp: 68,
    13 * u.gp: 65,
    21 * u.gp: 62,
    34 * u.gp: 59,
    55 * u.gp: 56,
    89 * u.gp: 53,
    144 * u.gp: 50,
    233 * u.gp: 47,
    377 * u.gp: 44,
    610 * u.gp: 41,
    987 * u.gp: 38,
    1597 * u.gp: 35,
    2584 * u.gp: 32,
    4181 * u.gp: 29,
    6765 * u.gp: 26,
    10946 * u.gp: 23,
    17711 * u.gp: 20,
    28657 * u.gp: 17,
    46368 * u.gp: 14,
}


def availability_chance(price):
    """How likely is it that a trade good which currently costs `price` will be available?"""
    price = to_copper_pieces(price)
    avail = [(k, v) for k, v in chance_available_map if k <= price]
    if avail:
        return min(avail, key=lambda each: each[1])[1]
    else:
        # so expensive it's not in chance_available_map? 5% chance
        return 5


def availability_seed(year, month, day):
    """Return a randomization seed string. Used when determining whether each good is available at its price for that week."""
    week = str(week_of_year(Date(year, month, day)))
    return str(year) + str(week)


def _maximum_available(chance):
    return max(1, floor(chance / 10))


def number_available(tradegood, year, month, day):
    seed = tradegood + availability_seed(year, month, day)
    random.seed(seed)
    # TODO implement price
    current_price = price(tradegood, year, month, day)
    if random.randint(1, 100) > availability_chance(current_price):
        return 0
    else:
        return random.randint(1, _maximum_available(availability_chance))


density = {
    k: (Decimal(v.magnitude) * v.units).to(u.lb / u.cuft)
    for k, v in {
        "snuff": 30 * u.lb / u.cuft,
        "cast iron": 454.8 * u.lb / u.cuft,
        "wrought iron": 483 * u.lb / u.cuft,
        "steel": 489 * u.lb / u.cuft,
        "molasses": 88.1233091 * u.lb / u.cuft,
        "timber": 40 * u.lb / u.cuft,
        "wood, oak": 704 * u.kg / u.cumt,
        "milk": 64.488 * u.lb / u.cuft,
        "tallow": 54.09 * u.lb / u.cuft,
        "tin": 456.3484 * u.lb / u.cuft,
        "copper": 559 * u.lb / u.cuft,
        "clay": 100 * u.lb / u.cuft,
        "silver": 655.4934 * u.lb / u.cuft,
        "lead": 709 * u.lb / u.cuft,
        "mercury": 844.900018 * u.lb / u.cuft,
        "horn": 81.1563 * u.lb / u.cuft,
        "gold": 1204.86 * u.lb / u.cuft,
        "vinegar": 63.05224 * u.lb / u.cuft,
        "zinc": 445 * u.lb / u.cuft,
        "quicklime": 209.1337 * u.lb / u.cuft,
        "water": 8.345404 * u.lb / u.gallon,
        "basalt": 2.9 * u.gram / u.cucm,
        "dolomite": 2.85 * u.gram / u.cucm,
        "granite": 2.65 * u.gram / u.cucm,
        "alabaster": 2.32 * u.gram / u.cucm,
        "limestone": 2.5 * u.gram / u.cucm,
        "crushed limestone": 90 * u.lb / u.cuft,
        "syenite": 2.7 * u.gram / u.cucm,
        "marble, green": 2.55 * u.gram / u.cucm,
        "marble, black": 2.55 * u.gram / u.cucm,
        "marble, brown": 2.55 * u.gram / u.cucm,
        "marble, crimson": 2.55 * u.gram / u.cucm,
        "marble, gray": 2.55 * u.gram / u.cucm,
        "marble, pink": 2.55 * u.gram / u.cucm,
        "marble, white": 2.55 * u.gram / u.cucm,
        "marble, yellow": 2.55 * u.gram / u.cucm,
        "marble": 2.55 * u.gram / u.cucm,
        "glass": 2.6 * u.gram / u.cucm,
        "sandstone": 2.5 * u.gram / u.cucm,
        "red sandstone": 2.5 * u.gram / u.cucm,
        "slate": 2.75 * u.gram / u.cucm,
        "tuff": 1.4 * u.gram / u.cucm,
        "tufa": 1.35 * u.gram / u.cucm,
        "porphyry": 1.4 * u.gram / u.cucm,
        "pitch": 72 * u.lb / u.cuft,
        "dry mortar": 150 * u.lb / u.cuft,
        # wet mortar has 0.75% the volume of dry mortar: airy voids between dry materials are filled with water as material mixes
        "wet mortar": 150 * u.lb / (D(0.75) * u.cuft),
        "wet concrete": 143 * u.lb / u.cuft,
        "dry concrete": 143 * u.lb / (D(1.5) * u.cuft),
        "flour": 4.75 * u.oz / u.cup,
        "butter": 0.95 * u.lb / u.pint,
        "salt": 2.17 * u.gram / u.cucm,
    }.items()
}
# ordinary clay items calculated with 1-sq-ft, 1-inch-thick slabs -- 1/12 of a cubic ft
clay_slab_volume = Decimal(1) / Decimal(12) * u.cuft
clay_slab_weight = Decimal(108) * u.oz
density["clay"] = (clay_slab_weight / clay_slab_volume).to(u.lb / u.cuft)

silvering_percentage = D(0.02)


def cylinder_volume(height, radius):
    # explicit to(u.cuft) call required to reduce representation from explicit pi to value thereof;
    # otherwise, printed value misleadingly shows "xxx ft ** 3 * pi" which looks like xxx ^ 3pi
    return (pi * height.to(u.ft) * radius.to(u.ft) * radius.to(u.ft)).to(u.cuft)


def ring_volume(bigheight, bigradius, smallheight, smallradius):
    """Return the difference in volumes of two cylinders, which gives the volume of a flat ring such as a washer."""
    big = cylinder_volume(bigheight, bigradius)
    small = cylinder_volume(smallheight, smallradius)
    if small > big:
        raise ValueError("small cylinder is bigger than large one")
    return big - small


def sphere_volume(radius):
    return (pi * Decimal(4) / Decimal(3) * (radius.to(u.ft) ** Decimal(3))).to(u.cuft)


def cone_volume(height, radius):
    """Volume of a cone."""
    return (pi * (radius.to(u.ft) ** 2) * (height.to(u.ft) / Decimal(3))).to(u.cuft)


def square_pyramid_volume(edge, height):
    """Volume of a right square pyramid."""
    return ((edge.to(u.ft) ** 2) * height.to(u.ft) / Decimal(3)).to(u.cuft)


def triangular_prism_volume(base, height, thickness):
    """The volume of a prism having two triangular faces and three quadrilateral ones.
    Like a truncated triangular pyramid: two 2D triangles with the area between them filled in."""
    return base.to(u.ft) * height.to(u.ft) / Decimal(2) * thickness.to(u.ft)


def truncated_cone_volume(big_radius, small_radius, height):
    return (
        Decimal(1)
        / Decimal(3)
        * pi
        * height.to(u.ft)
        * (
            (big_radius.to(u.ft) ** 2)
            + (big_radius.to(u.ft) * small_radius.to(u.ft))
            + (small_radius.to(u.ft) ** 2)
        )
    ).to(u.cuft)


class Cheapest:
    def __init__(self, *choices):
        self.choices = choices

    def choose(self, towninfo):
        prices = [(c, registry[c].price(towninfo)) for c in self.choices]
        name, price = min(prices, key=lambda x: x[1])
        return name


def to_copper_pieces(quantities):
    return sum([q.to(u.cp) for q in quantities])


def to_fewest_coins(money):
    # TODO write roundtrip test
    result = {}
    coppers = money.to(u.cp)
    ingold = coppers.to(u.gp)
    roundgold = floor(ingold.magnitude) * u.gp
    if roundgold.magnitude > 0:
        result["gp"] = roundgold
        # print(
        #    f"subtracting {roundgold} from {coppers} makes {coppers - roundgold}"
        # )
        coppers = coppers - roundgold
    insilver = coppers.to(u.sp)
    roundsilver = floor(insilver.magnitude) * u.sp
    if roundsilver.magnitude > 0:
        result["sp"] = roundsilver
        # print(
        #    f"subtracting {roundsilver} from {coppers} makes {coppers - roundsilver}"
        # )
        coppers = coppers - roundsilver
    result["cp"] = coppers
    return result


# molassesGallonWeight = densityMolasses * cuFtPerGallonLiquid

# TODO: Recipe subclasses for categories of goods, such as Weapon and Armor, which have special details (armor class, damage dice, break chance, etc)
# TODO saves_as field, which controls how item saves against damage (as wood, paper, leather, metal, glass, et -- even if the item not primarily made of that material)
# TODO length width height dimensions (all 3 optional)
# TODO description, with its reference to self.capacity and the height dimension (which I thought might also be a good field for Recipes) starting to look like sometimes it should b a function, or a method on the class, or sth... otherwise calculable from other Recipe fields
class Recipe:
    def __init__(
        self,
        name,
        # the reference upon which production of this recipe depends
        governor,
        weight,
        # raw material ingredients
        raws,
        # processed ingredients
        # necessary to distinguish raws and recipes rather than use one ingredients list b/c some raws and recipe share a name
        recipes=None,
        # name of shop where sold. differs from self.governor b/c that's not always a 'service' reference, unlike in v1 of my economy system
        # if None, recipe is not itself available for sale (replacing the old notion of "semigoods")
        vendor=None,
        unit=D(1) * u.item,
        difficulty=1,
        capacity=None,  # how much other stuff can it contain?
        container=None,  # what container does it come in?
        description="",
    ):
        self.name = name
        self.governor = governor
        self.weight = Decimal(weight.magnitude) * weight.units
        try:
            self.weight.to(u.lbs)
        except:
            raise ValueError(f"{self.name} failed to convert weight to weight units")
        self.raws = {k: Decimal(v.magnitude) * v.units for k, v in raws.items()}
        if recipes:
            self.recipes = {
                k: Decimal(v.magnitude) * v.units for k, v in recipes.items()
            }
        else:
            self.recipes = dict()
        self.vendor = vendor
        self.difficulty = D(difficulty)
        self.description = description
        self.capacity = capacity
        # container is a separate field so recipe X's container's weight is ignored when calculating weights of further recipes that make use of X, but the price of X can still incorporate the container's cost
        self.container = container
        self.unit = Decimal(unit.magnitude) * unit.units
        self._register()

    def _register(self):
        global registry
        if self.name in registry:
            raise ValueError(f"{self.name} is already a recipe")
        registry[self.name] = self
        if self.vendor:
            vendors.add(self.vendor)

    def to_json(self):
        val = {
            "name": self.name,
            "governor": self.governor,
            "weight": str(self.weight),
            "raws": [(name, str(amount)) for name, amount in self.raws.items()],
            "recipes": [(name, str(amount)) for name, amount in self.recipes.items()],
            "description": self.description,
            "difficulty": self.difficulty,
            "unit": str(self.unit),
            # can't just str() these attributes unconditionally: don't want to stringify a None
            "capacity": str(self.capacity) if self.capacity else None,
            "container": str(self.container) if self.container else None,
            "vendor": str(self.vendor) if self.vendor else None,
        }
        return json.dumps(val, cls=MyEncoder)

    def ingredient_costs(self, towninfo):
        price_raws = {}
        for raw, q in self.raws.items():
            if isinstance(raw, Cheapest):
                raw = raw.choose(towninfo)
            # unit employed in a recipe not always the base unit used in references.py
            # e.g. stone produced in oz, but usually recipes call for lbs
            newunit = u.cp / q.units
            final = towninfo["price"][raw].to(newunit) * q.magnitude
            price_raws[raw] = final
        price_recipes = {}
        for recipe, q in self.recipes.items():
            if isinstance(recipe, Cheapest):
                recipe = recipe.choose(towninfo)
            newunit = u.cp / q.units
            # TODO avoid costs of recursion
            # can I memoize while keeping while keeping this a method, or need to pull out into a function?
            final = registry[recipe].price(towninfo).to(newunit) * q.magnitude
            price_recipes[recipe] = final
        price_container = (
            registry[self.container].price(towninfo)
            if self.container
            else D(0) * u.cp / u.item
        )
        return price_raws, price_recipes, price_container

    def total_weight(self):
        if self.container:
            return self.weight + registry[self.container].weight
        else:
            return self.weight

    def service_cost(self, baseprice, towninfo):
        if self.governor:
            # ordinary case, for all non-"raw" recipes
            refs = towninfo["references"][self.governor]
            return baseprice / refs
        # else:
        #    return 0

    def price(self, towninfo):
        global registry
        ra, re, pc = self.ingredient_costs(towninfo)
        # necessary quantities of ingredients now priced in units of copper pieces per X
        # dividing by those units makes prices dimensionless and summable
        # otherwise we may try adding up, for instance, cp / head and cp / pound
        ra = {k: v / v.units for k, v in ra.items()}
        re = {k: v / v.units for k, v in re.items()}
        pc = pc / pc.units
        baseprice = sum(ra.values()) + sum(re.values()) + pc
        final = (baseprice + self.service_cost(baseprice, towninfo)) * self.difficulty
        # convert dimensionless final back to cp / X
        return (final.magnitude * u.cp) / self.unit

    def chunked_price(self, towninfo):
        p = self.price(towninfo)
        coppers = p * self.unit
        result = to_fewest_coins(coppers)
        result["cp"] = round(result["cp"])
        if result["cp"] == 25 * u.cp:
            # convert 1 silver's worth of cp into sp
            del result["cp"]
            if "sp" in result:
                result["sp"] += 1 * u.sp
            else:
                result["sp"] = 1 * u.sp
        if "sp" in result and result["sp"] == 8 * u.sp:
            # convert 1 gold's worth of sp into gp
            del result["sp"]
            if "gp" in result:
                result["gp"] += 1 * u.gp
            else:
                result["gp"] = 1 * u.gp
        if "cp" in result and result["cp"] == 0 * u.cp:
            del result["cp"]
        if not result.get("cp") and not result.get("sp") and not result.get("gp"):
            # set minimum price of 1 cp to avoid price of 0
            result["cp"] = 1 * u.cp
        return result

    def display_price(self, towninfo):
        p = self.chunked_price(towninfo)
        result = []
        for thing in ("gp", "sp", "cp"):
            if thing not in p:
                continue
            else:
                result.append(f"{p[thing]:~,}")
        # TODO format 'cup' unit as 'cup' instead of pint default abbrev 'cp'
        text = [", ".join(result)]
        if self.unit != D(1) * u.item:
            text.append(f"/ {self.unit:~,f}")
        if self.unit != self.total_weight():
            text.append(f"({self.total_weight():,f})")
        return " ".join(text)


smeltingfuel_sale_unit = D(0.75) * u.lb
Recipe(
    "smelting fuel",
    "smelting",
    smeltingfuel_sale_unit,
    dict(coal=0.5 * u.lb, limestone=0.25 * u.lb),
    description="generic supplies required to smelt 1 lb metal",
    unit=smeltingfuel_sale_unit,
    vendor="puddler",
)

Recipe(
    "raw iron",
    "iron",
    1 * u.lb,
    dict(iron=1 * u.lb),
    {"smelting fuel": smeltingfuel_sale_unit},
    unit=1 * u.lb,
    description="separated from waste rock and impurities",
)

Recipe(
    "pig iron",
    "pig iron",
    1 * u.lb,
    {},
    {"raw iron": 1 * u.lb, "smelting fuel": smeltingfuel_sale_unit},
    unit=1 * u.lb,
    description="weak, brittle purified iron",
)

Recipe(
    "cast iron",
    "ironmongery",
    1 * u.lb,
    {},
    {
        "smelting fuel": smeltingfuel_sale_unit,
        "raw manganese": 0.06 * u.lb,
        "raw nickel": 0.01 * u.lb,
        "pig iron": 0.93 * u.lb,
    },
    unit=1 * u.lb,
    description="for a volume of 1x1x3.8 in.",
)

Recipe(
    "wrought iron",
    "ironmongery",
    1 * u.lb,
    {"sulfur": 0.03 * u.lb},
    {
        "raw manganese": 0.03 * u.lb,
        "pig iron": 0.94 * u.lb,
        "smelting fuel": smeltingfuel_sale_unit,
    },
    vendor="puddler",
    unit=1 * u.lb,
    description="ingot, 1x1x3.57 in.",
)

Recipe(
    "raw nickel",
    "nickel",
    1 * u.lb,
    dict(nickel=1 * u.lb),
    {"smelting fuel": smeltingfuel_sale_unit},
    unit=1 * u.lb,
    vendor="puddler",
)

Recipe(
    "raw manganese",
    "manganese",
    1 * u.lb,
    dict(manganese=1 * u.lb),
    {"smelting fuel": smeltingfuel_sale_unit},
    unit=1 * u.lb,
    vendor="puddler",
)

Recipe(
    "raw copper",
    "copper",
    1 * u.lb,
    dict(copper=1 * u.lb),
    {"smelting fuel": smeltingfuel_sale_unit},
    unit=1 * u.lb,
    vendor="puddler",
    description="ingot, 2x1.065x1.45 in.",
)

Recipe(
    "raw tin",
    "tin",
    1 * u.lb,
    dict(tin=1 * u.lb),
    {"smelting fuel": smeltingfuel_sale_unit},
    vendor="puddler",
    unit=1 * u.lb,
    description="separated from waste rock and impurities",
)


Recipe(
    "raw gold",
    "gold",
    1 * u.lb,
    dict(gold=1 * u.lb),
    {"smelting fuel": smeltingfuel_sale_unit},
    description="ingot, 1x1x1.435 in.",
    unit=1 * u.lb,
    vendor="puddler",
)

# yes: 80mm x 80mm x 1/10,00 mm is the correct dimension for gold leaf!
# TODO add the materials for the 25-sheet book, made of kid skin
gold_leaf_area = D(80) * u.mm * D(80) * u.mm
gold_leaf_thickness = D(1) / D(10000) * u.mm
gold_leaf_volume = (gold_leaf_area * gold_leaf_thickness).to(u.cuft)
gold_leaf_weight = gold_leaf_volume * density["gold"]
gold_leaf_sale_unit = D(25) * u.leaf
Recipe(
    "gold leaf",
    "goldsmithing",
    gold_leaf_weight * gold_leaf_sale_unit.magnitude,
    {},
    {"raw gold": gold_leaf_weight * gold_leaf_sale_unit.magnitude},
    difficulty=5,
    unit=gold_leaf_sale_unit,
    vendor="goldsmith",
    description="each sheet is 80mm * 80mm * 1/10,000 mm",
)

tin_in_lb_pewter = Decimal(0.85) * u.lb
copper_in_lb_pewter = Decimal(0.15) * u.lb
# this volume calculation works because we're making a 1 lb ingot, so the number of pounds = the proportion
volume_pewter_ingot = (tin_in_lb_pewter / density["tin"]) + (
    copper_in_lb_pewter / density["copper"]
)
density["pewter"] = Decimal(1) * u.lb / volume_pewter_ingot
# resulting density = ~469 lbs. Sanity check: looks good for an alloy with this much copper

Recipe(
    "pewter",
    "pewter",
    1 * u.lb,
    {},
    {
        "smelting fuel": smeltingfuel_sale_unit,
        "raw tin": tin_in_lb_pewter,
        "raw copper": copper_in_lb_pewter,
    },
    unit=1 * u.lb,
    vendor="puddler",
    description="ingot, 1x1x3.65 in.",
)


Recipe(
    "steel",
    "ironmongery",
    1 * u.lb,
    {},
    {"pig iron": 1 * u.lb, "smelting fuel": smeltingfuel_sale_unit},
    vendor="puddler",
    unit=1 * u.lb,
    description="ingot, 1x1x3.5 in.",
)

Recipe(
    "iron filings",
    "ironmongery",
    1 * u.lb,
    {},
    {"wrought iron": 1 * u.lb},
    unit=1 * u.lb,
)

# filings used following the methods described in Subterraneal Treasures
Recipe(
    "raw lead",
    "leadsmelting",
    1 * u.lb,
    {"lead": 1 * u.lb},
    {"iron filings": 0.25 * u.lb, "smelting fuel": smeltingfuel_sale_unit},
    vendor="puddler",
    unit=1 * u.lb,
    description="ingot, 1.084x1.5x1.5 in.",
)

Recipe(
    "raw zinc",
    "smelting",
    1 * u.lb,
    {"zinc": 1 * u.lb},
    {"smelting fuel": smeltingfuel_sale_unit},
    unit=1 * u.lb,
    vendor="puddler",
)

Recipe(
    "raw silver",
    "smelting",
    1 * u.lb,
    {"silver": 1 * u.lb},
    {"smelting fuel": smeltingfuel_sale_unit},
    description="ingot, 1.5x1.5x1.175 in.",
    unit=1 * u.lb,
    vendor="puddler",
)

copper_in_lb_bronze = Decimal(0.88) * u.lb
tin_in_lb_bronze = Decimal(0.12) * u.lb
volume_bronze_ingot = (tin_in_lb_bronze / density["tin"]) + (
    copper_in_lb_bronze / density["copper"]
)
density["bronze"] = 1 * u.lb / volume_bronze_ingot
Recipe(
    "bronze",
    "bronze",
    1 * u.lb,
    {},
    {
        "raw tin": tin_in_lb_bronze,
        "raw copper": copper_in_lb_bronze,
        "smelting fuel": smeltingfuel_sale_unit,
    },
    vendor="puddler",
    unit=1 * u.lb,
    description="ingot, 1.125x1.675x1.675 in.",
)

copper_in_lb_brass = Decimal(0.55) * u.lb
zinc_in_lb_brass = Decimal(0.45) * u.lb
volume_brass_ingot = (zinc_in_lb_brass / density["zinc"]) + (
    copper_in_lb_brass / density["copper"]
)
density["brass"] = 1 * u.lb / volume_brass_ingot
Recipe(
    "brass",
    "brass",
    1 * u.lb,
    {},
    {
        "raw zinc": zinc_in_lb_brass,
        "raw copper": copper_in_lb_brass,
        "smelting fuel": smeltingfuel_sale_unit,
    },
    vendor="puddler",
    unit=1 * u.lb,
    description="ingot, 1.77x2.05x0.95 in.",
)


copper_in_lb_bellmetal = Decimal(0.78) * u.lb
tin_in_lb_bellmetal = Decimal(0.22) * u.lb
volume_bellmetal_ingot = (tin_in_lb_bellmetal / density["tin"]) + (
    copper_in_lb_bellmetal / density["copper"]
)
density["bell metal"] = 1 * u.lb / volume_bellmetal_ingot
Recipe(
    "bell metal",
    "alloys",
    1 * u.lb,
    {},
    {
        "raw tin": tin_in_lb_bellmetal,
        "raw copper": copper_in_lb_bellmetal,
        "smelting fuel": smeltingfuel_sale_unit,
    },
    vendor="puddler",
    unit=1 * u.lb,
    description="ingot, 1.2x1.35x2 in.",
)


copper_in_lb_sterlingsilver = Decimal(0.075) * u.lb
tin_in_lb_sterlingsilver = Decimal(0.01) * u.lb
silver_in_lb_sterlingsilver = Decimal(1) * u.lb - (
    tin_in_lb_sterlingsilver + copper_in_lb_sterlingsilver
)
volume_sterlingsilver_ingot = (
    (tin_in_lb_sterlingsilver / density["tin"])
    + (copper_in_lb_sterlingsilver / density["copper"])
    + (silver_in_lb_sterlingsilver / density["silver"])
)

density["sterling silver"] = 1 * u.lb / volume_sterlingsilver_ingot
Recipe(
    "sterling silver",
    "alloys",
    1 * u.lb,
    {},
    {
        "raw tin": tin_in_lb_sterlingsilver,
        "raw copper": copper_in_lb_sterlingsilver,
        "raw silver": silver_in_lb_sterlingsilver,
        "smelting fuel": smeltingfuel_sale_unit,
    },
    vendor="puddler",
    unit=1 * u.lb,
    description="ingot, 1.5x1.5x1.185 in.",
)

holysymbols = {
    "small pendant": {"height": D(1.5) * u.inch},
    "large pendant": {"height": D(4) * u.inch},
}


def holy_symbol_measurements(height, body_material, loop_material=None, thickness=None):
    """Measurements for a small crucifix `height` high, with all other measurements derived therefrom.
    All metal holy symbols will use the same amount of material as this crucifix, regardless of shape."""
    trunk_width = height / D(6)  # e.g. 1/4 inch for a 1.5-inch-high crucifix
    crossbar_length = D(2) / D(3) * height
    # area equals combined area of two pieces minus their overlap
    area = (height * trunk_width) + (crossbar_length * trunk_width) - (trunk_width ** 2)
    thickness = thickness if thickness else trunk_width / D(2)
    body_volume = area * thickness
    body_weight = density[body_material] * body_volume
    result = {
        "height": height,
        "width": crossbar_length,
        "area": area,
        "body weight": body_weight,
    }
    if loop_material:
        # include a loop for attaching a chain, rope, or similar
        loop_width = trunk_width / D(4)
        loop_volume = ring_volume(
            thickness, trunk_width, thickness, trunk_width - loop_width
        )
        result["loop weight"] = density[loop_material] * loop_volume
    return result


for name, info in holysymbols.items():
    h = info["height"]
    m = holy_symbol_measurements(h, "sterling silver", "steel")
    bw = m["body weight"]
    lw = m.get("loop weight", D(0) * u.lb)
    Recipe(
        f"silver holy symbol, {name}",
        "silversmithing",
        (bw + lw).to(u.lb),
        {},
        {"steel": lw.to(u.oz), "sterling silver": bw.to(u.oz)},
        vendor="goldsmith",
        description=f"sterling silver with steel loop for hanging; approx. {m['height']:~} tall and {m['width']:~} wide",
    )

    m = holy_symbol_measurements(h, "bronze", "bronze")
    bw = m["body weight"]
    lw = m.get("loop weight", D(0) * u.lb)
    Recipe(
        f"bronze holy symbol, {name}",
        "coppersmithing",  # TODO anything better?
        (bw + lw).to(u.lb),
        {},
        {"bronze": (bw + lw).to(u.lb)},
        vendor="redsmith",
        description=f"bronze, with loop for hanging; approx. {m['height']:~} tall and {m['width']:~} wide",
    )


for name, info in holysymbols.items():
    # a separate loop because I want all the gilded ones listed after the plain silver ones
    h = info["height"]
    m = holy_symbol_measurements(h, "sterling silver", "steel")
    bw = m["body weight"]
    lw = m.get("loop weight", D(0) * u.lb)
    area = m["area"]
    leaves = ceil(area / gold_leaf_area)
    # for each in (h, area, f"{(area / gold_leaf_area).to('dimensionless'):~P}", leaves):
    #    print(each)
    Recipe(
        f"gilt holy symbol, {name}",
        "silversmithing",
        (bw + lw + leaves * registry["gold leaf"].weight).to(u.lb),
        {},
        {
            "sterling silver": (lw + bw).to(u.oz),
            "gold leaf": leaves * u.leaf,
        },
        vendor="goldsmith",
        description=f"gilded sterling silver with loop for hanging; approx. {m['height']:~} tall and {m['width']:~} wide",
    )


hilt_volume = cylinder_volume(D(6) * u.inch, D(1.5) * u.inch)
hilt_weight = hilt_volume * density["timber"]
Recipe(
    "sword hilt",
    "woodcraft",
    hilt_weight,
    {"timber": hilt_weight},
    description="wooden tube",
)

big_hilt_volume = cylinder_volume(D(8) * u.inch, D(1.5) * u.inch)
big_hilt_weight = big_hilt_volume * density["timber"]
Recipe(
    "sword hilt, big",
    "woodcraft",
    big_hilt_weight,
    {"timber": big_hilt_weight},
    description="wooden tube",
)


pommel_weight = Decimal(0.25) * u.lb
Recipe(
    "pommel",
    "metalsmithing",
    pommel_weight,
    {},
    {"steel": pommel_weight},
    description="metal knob which holds hilt and blade together",
)

# a 1-foot (unit) blade is 2 inches wide, 1/6 inch thick, 1 foot long
unit_blade_volume = (
    Decimal(2) * u.inch * Decimal(1) / Decimal(6) * u.inch * Decimal(1) * u.ft
).to(u.cuft)
unit_blade_weight = unit_blade_volume * density["steel"]
Recipe(
    "blade",
    "metalsmithing",  # TODO weapons
    unit_blade_weight,
    {},
    {"steel": unit_blade_weight},
    description="price for a one-foot steel blade",
)

dagger_length = Decimal(1) * u.ft
dagger_blade_needed = dagger_length / u.ft
dagger_weight = hilt_weight + pommel_weight + (dagger_blade_needed * unit_blade_weight)
Recipe(
    "dagger",
    "weapons",
    dagger_weight,
    {},
    {
        "blade": dagger_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    vendor="weaponsmith",
    description=f"1d4 damage, melee or thrown 2/3/4; {dagger_length:~} blade",
)

silver_per_silver_dagger = (
    dagger_blade_needed * unit_blade_weight
) * silvering_percentage
Recipe(
    "dagger, silver",
    "weapons",
    dagger_weight,
    {},
    {
        "blade": dagger_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
        "raw silver": silver_per_silver_dagger,
    },
    vendor="weaponsmith",
    description=registry["dagger"].description,
)

shortsword_length = Decimal(2) * u.ft
shortsword_blade_needed = shortsword_length / u.ft
shortsword_weight = (
    hilt_weight + pommel_weight + (shortsword_blade_needed * unit_blade_weight)
)
Recipe(
    "shortsword",
    "swords",
    shortsword_weight,
    {},
    {
        "blade": shortsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    vendor="weaponsmith",
    description=f"1d6 damage; {shortsword_length} blade",
)

longsword_length = Decimal(3.5) * u.ft
longsword_blade_needed = longsword_length / u.ft
longsword_weight = (
    hilt_weight + pommel_weight + (longsword_blade_needed * unit_blade_weight)
)
Recipe(
    "longsword",
    "swords",
    longsword_weight,
    {},
    {
        "blade": longsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d8 damage; {longsword_length:~} blade",
    vendor="weaponsmith",
)

broadsword_length = Decimal(4.5) * u.ft
broadsword_blade_needed = broadsword_length / u.ft
broadsword_weight = (
    big_hilt_weight + pommel_weight + (broadsword_blade_needed * unit_blade_weight)
)
Recipe(
    "broadsword",
    "swords",
    broadsword_weight,
    {},
    {
        "blade": broadsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt, big": 1 * u.item,
    },
    vendor="weaponsmith",
    description=f"1d10 damage; {broadsword_length:~} blade",
)

greatsword_length = Decimal(5.5) * u.ft
greatsword_blade_needed = greatsword_length / u.ft
greatsword_weight = (
    big_hilt_weight + pommel_weight + (greatsword_blade_needed * unit_blade_weight)
)
Recipe(
    "greatsword",
    "swords",
    greatsword_weight,
    {},
    {
        "blade": greatsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt, big": 1 * u.item,
    },
    vendor="weaponsmith",
    description=f"1d12 damage, 2-handed; {greatsword_length:~} blade",
)

Recipe(
    "fresh fish",
    "fish",
    1 * u.lb,
    {"fish": 1 * u.lb},
    {},
    vendor="fishmonger",
    unit=1 * u.lb,
    description="local variety",
)


Recipe(
    "flour",
    "flour",
    # TODO shouldn't this be made from husked cereals, which are derived from base recipe cereals? well no, it should be derived from wheat ... to which i have yet to give a prduction number based on cereals
    1 * u.lb,
    {"wheat": 1 * u.lb},
    {},
    vendor="miller",
    unit=1 * u.lb,
    description="ground from cereals",
)

Recipe(
    "bread",
    "bread",
    1 * u.lb,
    {"salt": 0.05 * u.lb},
    {"flour": 0.7 * u.lb},
    unit=1 * u.lb,
    vendor="baker",
)

Recipe(
    "black bread",
    "bread, black",
    1 * u.lb,
    {"salt": 0.05 * u.lb},
    {"flour": 0.7 * u.lb},
    unit=1 * u.lb,
    vendor="baker",
    description="uses a recipe from Etain, a realm in the southwest",
)

Recipe(
    "quicklime",
    "quicklime",
    1 * u.lb,
    {"quicklime": 1 * u.lb},
    vendor="potter",  # potter b/c made in a kiln
    unit=1 * u.lb,
    description="used in tanning and to make mortar",
)

Recipe(
    "coal ash",
    "coal",
    1 * u.lb,
    {"coal": 10 * u.lb},
    {},
    unit=1 * u.lb,
    vendor="potter",  # potter b/c made in a kiln
)

masonry_unit = D(1) * u.cuft
drymortar_sale_weight = (density["dry mortar"] * masonry_unit).to(u.lb)
Recipe(
    "mortar, dry",
    "plaster",
    drymortar_sale_weight,
    {},
    {
        "quicklime": D(0.9) * u.lb,
        "coal ash": D(0.1) * u.lb,
    },
    vendor="mason",
    unit=drymortar_sale_weight,
    description="powdered, lime-based hydraulic mortar or plaster; sufficient for 1 cubic foot wet mortar",
)

wetmortar_sale_weight = (density["wet mortar"] * masonry_unit).to(u.lb)
Recipe(
    "masonry, mortar",
    "masonry",
    wetmortar_sale_weight,
    {},
    {
        "mortar, dry": drymortar_sale_weight,
    },
    unit=masonry_unit,
    vendor="mason",
)


# TODO baling string/wire/twine
Recipe(
    "straw",
    "straw goods",
    1 * u.lb,
    {"cereals": 2 * u.lb},
    {},
    unit=1 * u.lb,
)

Recipe(
    "dried hay",
    "hay",
    1 * u.lb,
    {"hay": 2 * u.lb},
    {},
    unit=1 * u.lb,
)


Recipe(
    "animal feed",
    "fodder",
    1 * u.lb,
    {},
    {"dried hay": 1 * u.lb},
    unit=1 * u.lb,
    description="composed primarily of hay",
    vendor="stockyard",
)


def fodder_while_growing(
    start_age, end_age, start_weight, end_weight, daily_food_per_bodyweight
):
    """Return the total amount of fodder needed to raise an animal from `start_age` to `end_age`."""
    months = (end_age - start_age).to(u.month)
    growth = (end_weight - start_weight).to(u.lb)
    result = D(0) * u.lb
    # TODO clean this up so I can use Decimals instead of having to lossily convert to Ints and back
    for i in range(1, int(months.magnitude) + 1):
        i = D(i) * u.month
        # age = start_age + i # used for debugging
        weight = start_weight + i * (growth / months)
        fodder = (daily_food_per_bodyweight * weight) * D(30)  # thirty days/month
        result += fodder
    return result


ewe_sale_age = D(8) * u.month
ewe_sale_weight = 90 * u.lb
Recipe(
    "mature ewe",
    "sheep",
    ewe_sale_weight,
    {"sheep": 1 * u.head},
    {},
    unit=1 * u.head,
    vendor="stockyard",
    description="eight months old, ready for milking or shearing",
)

sheep_carcass_fraction = Decimal(0.55)
sheep_meat_fraction = Decimal(0.75)
lamb_carcass_weight = sheep_carcass_fraction * ewe_sale_weight
lamb_meat_weight = sheep_meat_fraction * lamb_carcass_weight
Recipe(
    "lamb",
    "lamb",
    1 * u.lb,
    {},
    {"mature ewe": (Decimal(1) * u.lb / lamb_meat_weight) * u.head},
    vendor="butcher",
    unit=1 * u.lb,
    description="tender young lamb meat",
)

muttonsheep_sale_age = D(12) * u.month
muttonsheep_sale_weight = 130 * u.lb
muttonsheep_raising_fodder = fodder_while_growing(
    ewe_sale_age,
    muttonsheep_sale_age,
    ewe_sale_weight,
    muttonsheep_sale_weight,
    D(0.01) * u.lb / u.lb,
)

Recipe(
    "mutton sheep",
    "sheep",
    muttonsheep_sale_weight,
    {},
    {"mature ewe": 1 * u.head, "animal feed": muttonsheep_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description="grain-finished yearling, ready for slaughter",
)

milk_weight = density["milk"].to(u.lb / u.gallon)
# one mature ewe produces ~ 400 LBS (not gallons!) of milk annually (once a year during lambing)
sheep_annual_milk_weight = Decimal(400) * u.lb
# then we convert it to gallons
sheep_annual_milk_volume = (sheep_annual_milk_weight / milk_weight).to(u.gallon)
milk_sale_unit = 1 * u.gallon
Recipe(
    "ewes' milk",
    "milk",
    milk_weight * milk_sale_unit,
    {},
    {"mature ewe": (milk_sale_unit / sheep_annual_milk_volume) * u.head},
    unit=milk_sale_unit,
    vendor="dairy",
    description="customer supplies container",
)

salt_in_cheese = Decimal(0.25) * u.lb / u.lb  # a guess
milk_in_cheese = Decimal(3) * u.gallon / u.lb
rennet_in_cheese = Decimal(0.5) * u.teaspoon / u.gallon * milk_in_cheese
cheese_sale_unit = 1 * u.lb

Recipe(
    "ewes' milk cheese",
    "cheese, ewes' milk",
    cheese_sale_unit,
    {"salt": salt_in_cheese * cheese_sale_unit},
    {
        "ewes' milk": milk_in_cheese * cheese_sale_unit,
        "rennet": rennet_in_cheese * cheese_sale_unit,
    },
    description="halfling-made delicacy; includes feta, rocquefort, manchego, and pecorina romano",
    unit=cheese_sale_unit,
    vendor="dairy",
)

muttonsheep_carcass_weight = sheep_carcass_fraction * muttonsheep_sale_weight
muttonsheep_meat_weight = sheep_meat_fraction * muttonsheep_carcass_weight
Recipe(
    "mutton",
    "mutton",
    1 * u.lb,
    {},
    {"mutton sheep": (Decimal(1) * u.lb / muttonsheep_meat_weight) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

calf_sale_age = Decimal(8) * u.month
calf_sale_weight = Decimal(410) * u.lb
Recipe(
    "calf",
    "cattle",
    calf_sale_weight,
    {"cattle": 1 * u.head},
    {},
    vendor="stockyard",
    unit=1 * u.head,
    description=f"{calf_sale_age:} old, suitable for rennet",
)

# spends half of life being grain-finished
vealcalf_raising_fodder = fodder_while_growing(
    calf_sale_age / D(2),
    calf_sale_age,
    calf_sale_weight / D(2),
    calf_sale_weight,
    D(0.01) * u.lb / u.lb,
)
Recipe(
    "veal calf",
    "cattle",
    calf_sale_weight,
    {"cattle": 1 * u.head},
    {"animal feed": vealcalf_raising_fodder},
    vendor="stockyard",
    unit=1 * u.head,
    description=f"grain-finished, {calf_sale_age:} old, suitable for veal",
)

cow_sale_age = Decimal(16) * u.month
cow_sale_weight = Decimal(800) * u.lb
cow_raising_fodder = fodder_while_growing(
    calf_sale_age,
    cow_sale_age,
    calf_sale_weight,
    cow_sale_weight,
    D(0.01) * u.lb / u.lb,
)

Recipe(
    "cow, beef",
    "cattle",
    cow_sale_weight,
    {},
    {"calf": 1 * u.head, "animal feed": cow_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"grain-finished, {cow_sale_age:~} old; suitable for slaughtering",
)

dairycow_raising_fodder = fodder_while_growing(
    calf_sale_age,
    cow_sale_age,
    calf_sale_weight,
    cow_sale_weight,
    D(0.005) * u.lb / u.lb,  # less grain needed than grain-finished beef cow
)

cow_daily_milk_volume = Decimal(3) * u.gallon / u.day
# from some research, cows can give milk 300/365 days of the year (so 5/6 of the year)
# on the other hand, the production tapers off as this period goes on, so let's call it fewer days per year to make up for that
cow_annual_milking_days = Decimal(250) * u.day
cow_annual_milk_volume = cow_daily_milk_volume * cow_annual_milking_days


Recipe(
    "cow, dairy",
    "cattle",
    cow_sale_weight,
    {},
    {"calf": 1 * u.head, "animal feed": dairycow_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"{cow_sale_age:~} old; produces {cow_annual_milk_volume:~} milk annually, on average",
)

ox_sale_age = Decimal(30) * u.month
ox_sale_weight = Decimal(1200) * u.lb
ox_raising_fodder = fodder_while_growing(
    calf_sale_age,
    ox_sale_age,
    calf_sale_weight,
    ox_sale_weight,
    D(0.005) * u.lb / u.lb,
)
Recipe(
    "ox",
    "cattle",
    ox_sale_weight,
    {},
    {"calf": 1 * u.head, "animal feed": ox_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"female or gelded male; {ox_sale_age:~} old, bred for work",
)

cattle_carcass_fraction = Decimal(0.67)
cattle_meat_fraction = Decimal(0.67)
veal_per_calf = calf_sale_weight * cattle_carcass_fraction * cattle_meat_fraction
Recipe(
    "veal",
    "beef",
    1 * u.lb,
    {},
    {"veal calf": (Decimal(1) * u.lb / veal_per_calf) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

# TODO turn 1 cow into 2 sides of cow, then subdivide cow into different cuts of beef
# https://beef.unl.edu/beefwatch/2020/how-many-pounds-meat-can-we-expect-beef-animal
cow_carcass_weight = cow_sale_weight * cattle_carcass_fraction
beef_per_cow = cow_carcass_weight * cattle_meat_fraction
bone_per_cow = (cow_carcass_weight * (D(1) - cattle_meat_fraction)) / D(2)
# divide bone per cow in half b/c we assume half of nonmeat carcass weight is bone, and half is fat
fat_per_cow = bone_per_cow
Recipe(
    "beef",
    "beef",
    1 * u.lb,
    {},
    {"cow, beef": (Decimal(1) * u.lb / beef_per_cow) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

salt_for_beefjerky = (density["salt"] * (D(2) * u.teaspoon)).to(u.oz)
pepper_for_beefjerky = 2 * salt_for_beefjerky
Recipe(
    "beef jerky",
    "beef",
    1 * u.lb,
    {
        "salt": salt_for_beefjerky,
        "pepper, black": pepper_for_beefjerky,
    },
    {"beef": 1 * u.lb},
    vendor="grocer",
    description="salted and dry cured, with black pepper for flavor",
)


Recipe(
    "cattle bone",
    "meat",
    1 * u.lb,
    {},
    {"cow, beef": (Decimal(1) * u.lb / bone_per_cow) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

horn_per_cow = D(30) * u.lb
Recipe(
    "cattle horn",
    "meat",  # TODO horn reference makes it super expensive
    1 * u.lb,
    {},
    {"cow, beef": (Decimal(1) * u.lb / horn_per_cow) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

abomasum_weight = Decimal(5) * u.lb  # this is a guess
Recipe(
    "abomasum",
    "meat",
    abomasum_weight,
    {},
    {"calf": (abomasum_weight / calf_sale_weight * cattle_carcass_fraction) * u.head},
    description="fourth compartment of calf stomach; not for human consumption",
)

Recipe(
    "abomasum, cured",
    "meat",
    abomasum_weight,
    {"salt": 0.25 * u.lb},
    {"abomasum": 1 * u.item, "vinegar, in barrel": D(0.5) * u.pint},
    description=registry["abomasum"].description,
)

rennet_per_abomasum = Decimal(2) * u.pint / u.item
rennet_sale_unit = Decimal(1) * u.pint
Recipe(
    "rennet",
    "dairying",
    (density["water"] * rennet_sale_unit).to(u.lb),
    {},
    {"abomasum, cured": rennet_sale_unit / rennet_per_abomasum},
    unit=rennet_sale_unit,
    vendor="dairy",
    description="cow stomach enzyme for cheesemaking; not for human consumption",
)

Recipe(
    "cow milk",
    "milk",
    milk_weight * milk_sale_unit,
    {},
    {"cow, dairy": (milk_sale_unit / cow_annual_milk_volume) * u.head},
    unit=milk_sale_unit,
    vendor="dairy",
    description="customer supplies container",
)


milk_per_butter = D(3.25) * u.gallon / D(1) * u.lb
butter_sale_weight = D(0.5) * u.lb
Recipe(
    "butter",
    "butter",
    butter_sale_weight,
    # NOTE there *is* a butter production number ... ignoring it as usual
    {},
    {"cow milk": (milk_per_butter / butter_sale_weight).to(u.gallon)},
    unit=butter_sale_weight,
    vendor="dairy",
)


milk_per_serving = D(1) * u.pint
Recipe(
    "cow milk, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["milk"] * milk_per_serving).to(u.lb),
    {},
    {"cow milk": milk_per_serving},
    unit=milk_per_serving,
    vendor="tavern",
)

Recipe(
    "ewes' milk, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["milk"] * milk_per_serving).to(u.lb),
    {},
    {"ewes' milk": milk_per_serving},
    unit=milk_per_serving,
    vendor="tavern",
)

Recipe(
    "cheese",
    "cheese",
    cheese_sale_unit,
    {"salt": salt_in_cheese * cheese_sale_unit},
    {
        "cow milk": milk_in_cheese * cheese_sale_unit,
        "rennet": rennet_in_cheese * cheese_sale_unit,
    },
    unit=cheese_sale_unit,
    description="local variety",
    vendor="dairy",
)

Recipe(
    "suet",
    "meat",  # what's a better one? chandler? butchery?
    1 * u.lb,
    {},
    {"cow, beef": (1 * u.lb / fat_per_cow) * u.head},
    vendor="butcher",
    unit=1 * u.lb,
    description="beef fat for cooking, or for manufacture of tallow",
)

Recipe(
    "tallow",
    "candles and wax",
    1 * u.lb,
    {},
    {"suet": 1 * u.lb},
    unit=1 * u.lb,
    vendor="chandler",
)

timber_per_ash = Decimal(10) * u.lb / u.lb
Recipe(
    "wood ash",
    "timber",
    1 * u.lb,
    {"timber": timber_per_ash * u.lb},
    {},
    unit=1 * u.lb,
    vendor="chandler",
)

Recipe(
    "lye",
    "lye",  # TODO I used soap and wax at first ... "lye" ref makes it ~100x more exensive
    1 * u.lb,
    {},
    {"wood ash": 1 * u.lb},
    vendor="chandler",
    unit=1 * u.lb,
    description="made by leaching ash in water",
)

soap_weight = Decimal(1) * u.lb
# http://www.millennium-ark.net/News_Files/Soap/Lye_Fat_Table.html
# (above page copyright A L Durtschi)
# using the 5% excess fat column given here, the required lye content for soap is 0.133 times the tallow content
lye_per_soap_tallow = Decimal(0.133) * u.lb / u.lb
# add salt to get hard soap instead of soft
# http://www.motherearthnews.com/homesteading-and-livestock/how-to-make-soap-from-ashes-zmaz72jfzfre.aspx
# this article suggests 2.5 pints (3.22 lb) salt for 5 gallons (36.16 lb) of tallow
salt_per_soap_tallow = (Decimal(3.22) * u.lb) / (Decimal(36.16) * u.lb)
tallow_per_soap = (
    soap_weight / (lye_per_soap_tallow + salt_per_soap_tallow + Decimal(1)) / u.lb
)
soap_volume = Decimal(3) * u.inch * Decimal(2) * u.inch * Decimal(6) * u.inch
# my calculation for how many times it will wash one person:
# one bar of my soap is ~9 cubic inches and lasts about a month i.e. 30 washes
# the soap here is 36 cubic inches, thus it should last about 4 months or 120 washes
# but I'm going to cut that in half because Early Modern people got much dirtier than I ever do
Recipe(
    "hard soap",
    "soap",
    soap_weight,
    {"salt": salt_per_soap_tallow * soap_weight},
    {
        "lye": lye_per_soap_tallow * soap_weight,
        "tallow": tallow_per_soap * soap_weight,
    },
    vendor="chandler",
    unit=60 * u.use,
    description="will wash 1 person 60 times; 2x3x6 in.",
)

Recipe(
    "hard soap, rose scent",
    "soap",
    soap_weight,
    {
        "salt": salt_per_soap_tallow * soap_weight,
        "attar of roses": D(0.05) * soap_weight,
    },
    {
        "lye": lye_per_soap_tallow * soap_weight,
        "tallow": tallow_per_soap * soap_weight,
    },
    vendor="chandler",
    unit=registry["hard soap"].unit,
    description=registry["hard soap"].description,
)

# TODO should these be specified as being per head?
cowhide_area = Decimal(50) * u.sqft
cowhide_weight = Decimal(60) * u.lb
Recipe(
    "fleshy cowhide",
    "hides",
    cowhide_weight,
    {},
    {"cow, beef": 1 * u.head},
    unit=cowhide_area,
)

rawhide_area = cowhide_area
rawhide_weight = 15 * u.lb
Recipe(
    "rawhide",
    "hides",
    rawhide_weight,
    {},
    {"fleshy cowhide": rawhide_area},
    unit=rawhide_area,
    vendor="tanner",
    description="cleaned and dried cowskin",
)

# http://boar.org.uk/aaiwxw3MusprattL6Preparation.htm
# this says three to four cubic feet of "freshly burned fat lime" (aka quicklime) used for 100 average hides
# let's split the difference between 3 and 4 cuft of quicklime
quicklime_per_hide = (Decimal(3.5) * u.cuft * density["quicklime"]) / (
    Decimal(100) * rawhide_area
)
# tanned_hide_toughness = _weight.to(u.oz) / cowhide_area
Recipe(
    "leather",
    "hides",
    rawhide_weight,
    {},
    {"quicklime": quicklime_per_hide * rawhide_area, "rawhide": rawhide_area},
    unit=rawhide_area,
    vendor="tanner",
    description="soft cowhide",
)

# as with baked clay, while boiling is actually the last step for a piece of leather in a useful size and shape,  the trade good system processes the boiling before the shaping so that we don't clog up the registry with boiled and unboiled variants of all leather goods
Recipe(
    "boiled leather",
    "hides",
    rawhide_weight,
    {},
    {"leather": rawhide_area},
    unit=rawhide_area,
    vendor="tanner",
    description="leather hardened into rigid shape",
)


Recipe(
    "roasted malt",
    "malt",
    1 * u.lb,
    {"malt": 1 * u.lb},
    vendor="brewer",
    unit=1 * u.lb,
    description="germinated and dried; used for brewing",
)

gauge16wire_thickness = (Decimal(1) / Decimal(16)) * u.inch


def cask_measurements(height, radius):
    # a few considerations going into the design of the cask:
    # the heads (top and bottom) of the cask
    # the thickness of wood used for various parts
    # the wrought iron hoops reinforcing it (fat ones at the heads, thin ones around the body)
    volume = cylinder_volume(height, radius)
    cask_circumference = pi * radius * Decimal(2)
    head_thickness = Decimal(2) / Decimal(3) * u.inch
    head_volume = cylinder_volume(head_thickness, radius)
    head_weight = (density["timber"] * head_volume).to(u.lb)

    hoop_breadth = gauge16wire_thickness
    fat_hoop_width = Decimal(1.25) * u.inch
    fat_hoop_volume = cask_circumference * fat_hoop_width * hoop_breadth
    fat_hoop_weight = (density["wrought iron"] * fat_hoop_volume).to(u.lb)

    thin_hoop_width = Decimal(0.75) * u.inch
    thin_hoop_volume = cask_circumference * thin_hoop_width * hoop_breadth
    thin_hoop_weight = (density["wrought iron"] * thin_hoop_volume).to(u.lb)

    stave_thickness = Decimal(1) * u.inch
    staves_per_cask = Decimal(20)
    stave_width = cask_circumference / staves_per_cask
    stave_volume = height * stave_width * stave_thickness
    stave_weight = (density["timber"] * stave_volume).to(u.lb)

    return {
        "volume": volume,
        "circumference": cask_circumference,
        "head weight": head_weight,
        "num heads": Decimal(2),
        "fat hoop weight": fat_hoop_weight,
        "num fat hoops": Decimal(2),
        "thin hoop weight": thin_hoop_weight,
        "num thin hoops": Decimal(4),
        "stave weight": stave_weight,
        "num staves": staves_per_cask,
    }


casks = {
    "firkin": {"height": 2 * u.ft, "radius": 5 * u.inch},
    "rundlet": {"height": 3 * u.ft, "radius": 6 * u.inch},
    "barrel": {"height": 3 * u.ft, "radius": 8 * u.inch},
    "tierce": {"height": 4 * u.ft + 1 * u.inch, "radius": 8 * u.inch},
    "hogshead": {"height": 6 * u.ft + 1 * u.inch, "radius": 8 * u.inch},
    "puncheon": {"height": 8 * u.ft + 1 * u.inch, "radius": 8 * u.inch},
    "butt": {"height": 12 * u.ft + 1 * u.inch, "radius": 8 * u.inch},
    "tun": {"height": 15 * u.ft + 6 * u.inch, "radius": 10 * u.inch},
}

for name, info in casks.items():
    height = Decimal(info["height"].magnitude) * info["height"].units
    radius = Decimal(info["radius"].magnitude) * info["radius"].units
    m = cask_measurements(height, radius)
    total_head_weight = m["head weight"] * m["num heads"]
    total_stave_weight = m["stave weight"] * m["num staves"]
    total_fat_hoop_weight = m["fat hoop weight"] * m["num fat hoops"]
    total_thin_hoop_weight = m["thin hoop weight"] * m["num thin hoops"]
    Recipe(
        f"cask, {name}",
        "barrels",
        total_head_weight
        + total_stave_weight
        + total_fat_hoop_weight
        + total_thin_hoop_weight,
        {"timber": total_head_weight + total_stave_weight},
        {"wrought iron": total_fat_hoop_weight + total_thin_hoop_weight},
        vendor="cooper",
        capacity=m["volume"].to(u.gal),
        description=f"capacity {m['volume'].to(u.gal):~}, height {height:~}, radius {radius:~}",
    )

timber_per_pitch = (D(18) * u.cumt * density["timber"]).to(u.lb) / (
    D(500) * u.liter
).to(u.gallon)
pitch_container = "cask, firkin"
pitch_sale_volume = registry[pitch_container].capacity
pitch_sale_weight = density["pitch"].to(u.lb / u.gallon) * pitch_sale_volume
pitch_timber_weight = (timber_per_pitch * pitch_sale_volume).to(u.lb)
Recipe(
    "pitch",
    "pitch",
    pitch_sale_weight,
    {"timber": pitch_timber_weight},
    {},
    container=pitch_container,
    unit=pitch_sale_volume,
    vendor="potter",
    # TODO how much can it cover?
)


sugar_per_brewable = {
    "raw sugar": D(1) * u.lb / u.lb,
    "cereals": D(0.75) * u.lb / u.lb,
    "malt": D(0.8) * u.lb / u.lb,
    "roasted malt": D(0.8) * u.lb / u.lb,
    "grapes": D(0.25) * u.lb / u.lb,
    "mare milk": D(0.1) * u.lb / u.gallon,
}


def calculate_abv(sugar_sources, water_volume, desired_volume):
    # assumption: all the available sugar content of the sugar_sources is consumed by the yeast
    total_sugar = sum(
        [
            (sugar_per_brewable[name] * unit).to(u.lb)
            for name, unit in sugar_sources.items()
        ]
    )
    water_weight = water_volume.to(u.gallon) * density["water"]
    mash_weight = total_sugar + water_weight
    # specific gravity, with respect to water, is the relative density of some solution and water
    # the original gravity is the specific gravity of the mash
    # we are dissolving our sugar in water_volume gallons of water, and comparing the density of that to the density of water_volume gallons of water. because those two volumes are the same, we can ignore the volume component of density, and just make a ratio of the weights
    original_gravity = mash_weight / water_weight
    # distillation: boiling off and collecting the "spirit"
    # spirit is about 20% pure alcohol; leave off 1% to represent non-usable "head"
    distilled_volume = Decimal(0.19) * water_volume
    # final gravity: the specific density of the spirit
    # this value, 0.99, is an average one
    final_gravity = Decimal(0.99)
    base_abv = (original_gravity - final_gravity) * Decimal(129)
    # dilute the distilled spirit with water to reach the desired_volume, our final spirit product
    # the difference between distilled_volume and desired_volume is the volume of water added
    diluted_abv = base_abv * (distilled_volume / desired_volume)
    return diluted_abv


# based on the Clare household strong ale recipe from:
# https://www.cs.cmu.edu/~pwp/tofi/medieval_english_ale.html
# thanks, Paul Placeway AKA Tofi Kerthjalfadsson
cereal_for_ale = Decimal(1.5) * u.lb / u.gallon
malt_for_ale = Decimal(2.5) * u.lb / u.gallon
roasted_malt_for_ale = Decimal(0.5) * u.lb / u.gallon
ale_abv = calculate_abv(
    {
        "cereals": cereal_for_ale * 1 * u.gallon,
        "malt": malt_for_ale * 1 * u.gallon,
        "roasted malt": roasted_malt_for_ale * 1 * u.gallon,
    },
    1 * u.gallon,
    1 * u.gallon,
)

barrel_capacity = registry["cask, barrel"].capacity
Recipe(
    "ale, in barrel",
    "brewing",
    (density["water"] * barrel_capacity).to(u.lb),
    {
        "cereals": cereal_for_ale * barrel_capacity,
        "malt": malt_for_ale * barrel_capacity,
    },
    {
        "roasted malt": roasted_malt_for_ale * barrel_capacity,
    },
    unit=barrel_capacity,
    container="cask, barrel",
    vendor="brewer",
    description=f"{str(ale_abv.magnitude)}% alcohol",
)

# beer is following a recipe taken from http://brewery.org/library/PeriodRen.html
# "To brewe beer; 10 quarters malt. 2 quarters wheat, 2 quarters oats, 40 lbs hops. To make 60 barrels of single beer."
# a "quarter" equals 256 lbs of grain (b/c it's 64 gallons of dry volume and 1 gallon of grain ~= 4 lbs)
# a medieval barrel of beer was 36 gallons; 36 * 60 barrels = 2160 gal
# thus we have 2560 lbs malt, 512 lbs + 512 lbs = 1024 lbs cereal, 40 lbs hops = 2160 gallons.
# divide all amounts by 2160 to arrive at a 1-gallon recipe
original_gallons = Decimal(2160) * u.gallon
cereal_for_beer = Decimal(1024) * u.lb / original_gallons
malt_for_beer = Decimal(2560) * u.lb / original_gallons
hops_for_beer = Decimal(40) * u.lb / original_gallons
beer_abv = calculate_abv(
    {
        "cereals": cereal_for_beer * 1 * u.gallon,
        "malt": malt_for_beer * 1 * u.gallon,
    },
    1 * u.gallon,
    1 * u.gallon,
)

Recipe(
    "beer, in barrel",
    "brewing",
    (density["water"] * barrel_capacity).to(u.lb),
    {
        "cereals": cereal_for_beer * barrel_capacity,
        "malt": malt_for_beer * barrel_capacity,
        "hops": hops_for_beer * barrel_capacity,
    },
    {},
    unit=barrel_capacity,
    container="cask, barrel",
    vendor="brewer",
    description=f"{str(beer_abv.magnitude)}% alcohol",
)

Recipe(
    "gnomish beer, in barrel",
    "gnomish beer",
    (density["water"] * barrel_capacity).to(u.lb),
    {
        "cereals": cereal_for_beer * barrel_capacity,
        "malt": malt_for_beer * barrel_capacity,
        "hops": hops_for_beer * barrel_capacity,
    },
    {},
    unit=barrel_capacity,
    container="cask, barrel",
    vendor="brewer",
    description=f"{str(beer_abv.magnitude)}% alcohol; finest Amberite refreshment",
)


sugar_for_rum = D(10) * u.lb / u.gallon
rum_abv = calculate_abv(
    {"raw sugar": sugar_for_rum * 1 * u.gallon},
    1 * u.gallon,
    1 * u.gallon,
)

Recipe(
    "rum, in barrel",
    "rum",
    (density["water"] * barrel_capacity).to(u.lb),
    {},
    {
        "raw sugar": sugar_for_rum * barrel_capacity,
    },
    unit=barrel_capacity,
    container="cask, barrel",
    vendor="brewer",
    description=f"{str(rum_abv.magnitude)}% alcohol",
)


for member in categories["dried fruit"]["members"]:
    Recipe(
        member,
        member,
        1 * u.lb,
        {member: 1 * u.lb},
        {},
        vendor="grocer",
        unit=1 * u.lb,
    )

for member in categories["fruits"]["members"]:
    description = "sour orange" if member == "hushhash" else None
    Recipe(
        member,
        member,
        1 * u.lb,
        {member: 1 * u.lb},
        {},
        vendor="costermonger",
        unit=1 * u.lb,
        description=description,
    )

for member in categories["vegetables"]["members"]:
    Recipe(
        member,
        member,
        1 * u.lb,
        {member: 1 * u.lb},
        {},
        unit=1 * u.lb,
        vendor="greengrocer",
    )

for tuber in ("potatoes", "groundnuts", "sweet potatoes", "yams"):
    Recipe(
        tuber,
        tuber,
        1 * u.lb,
        {tuber: 1 * u.lb},
        {},
        unit=1 * u.lb,
        vendor="greengrocer",
    )

Recipe(
    "potato pulp",
    "potatoes",
    1 * u.lb,
    {"potatoes": 1 * u.lb},
    {},
    unit=1 * u.lb,
    description="intermediate stage of starch production",
)

potato_starch_fraction = D(0.25)
Recipe(
    "starch, potato",
    "starch",
    1 * u.lb,
    {},
    {"potato pulp": (1 / potato_starch_fraction) * u.lb},
    unit=1 * u.lb,
    vendor="grocer",
)

Recipe(
    "arrowroot pulp",
    "arrowroot",
    1 * u.lb,
    {"arrowroot": 1 * u.lb},
    {},
    unit=1 * u.lb,
    description="intermediate stage of starch production",
)

arrowroot_starch_fraction = D(0.2)
Recipe(
    "starch, arrowroot",
    "starch",
    1 * u.lb,
    {},
    {"arrowroot pulp": (1 / arrowroot_starch_fraction) * u.lb},
    unit=1 * u.lb,
    vendor="grocer",
)

grapes_for_wine = D(3.5) * u.lb / (D(750) * u.ml).to(u.gallon)
wine_abv = calculate_abv(
    {"grapes": grapes_for_wine * 1 * u.gallon},
    1 * u.gallon,
    1 * u.gallon,
)

wines = {
    "wine": "local variety of red or white",
    "champagne": "sparkling, bubbly white with biscuity flavor",
    "wine, Baccia": "the queen of Marasan viticulture; dry white wine made of late harvest grapes",
    "wine, asti spumante": "sweet, sparkling dessert wine from northwest Marasa; creamy texture and aromas of pear, honeysuckle, and peaches",
    "wine, Sacramaran": "central Marasan wine; light red with notes of apricot and currants",
    "wine, Lutewood": "southern Marasan 'orange' wine, aromatic and tart, made from skin-on white grapes",
    # "wine, Chablis": "dry white with 'flinty' notes",
    # "wine, Chianti": "very dry red",
    # "wine, Chabrieres": "dry, musty, delicate red",
    # "wine, Malaga": "dessert wine with hints of coffee and caramel",
    # "wine, Mees": "dry, fruity white",
    # "wine, Montona": "purplish red, light in flavor", # Croatian (formery Italian) territory https://en.wikipedia.org/wiki/Motovun note that they grow Malvasia/Malvazia wine here... might roll Montona into Malvasia
    # "wine, Tokay": {"references": 1},
    # "wine, Valtellina": {"references": 1},
    # TODO these fortified wines can't be made with the same ingredients and ABV as the others
    # "port": "fortified red with rich berry notes",
    # "wine, Marsala": "heavy-sweet red used in cookery",
    # "sherry, Amontillado": "hazel, caramel, and tobacco notes",
    # "wine, canary sack": "sweet fortified wine aged in oak, with strong flavor and bitter finish",
    # "wine, Madeira": "cinnamon-colored fortified red with a caramel, nutty flavor",
}

for w, description in wines.items():
    Recipe(
        f"{w}, in barrel",
        w,
        (density["water"] * barrel_capacity).to(u.lb),
        # NOTE raw material grapes, not recipe grapes (the latter is cleaned more thoroughly for eating)
        {
            "grapes": grapes_for_wine * barrel_capacity,
        },
        {},
        unit=barrel_capacity,
        container="cask, barrel",
        vendor="vintner",
        description=f"{str(wine_abv.magnitude)}% alcohol; {description}",
    )


ale_per_serving = (D(1) * u.cup).to(u.floz)
Recipe(
    "ale, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * ale_per_serving).to(u.lb),
    {},
    {"ale, in barrel": ale_per_serving},
    unit=ale_per_serving,
    vendor="tavern",
    description=registry["ale, in barrel"].description,
)


beer_per_serving = D(1) * u.pint
Recipe(
    "beer, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * beer_per_serving).to(u.lb),
    {},
    {"beer, in barrel": beer_per_serving},
    unit=beer_per_serving,
    vendor="tavern",
    description=registry["beer, in barrel"].description,
)

Recipe(
    "gnomish beer, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * beer_per_serving).to(u.lb),
    {},
    {"gnomish beer, in barrel": beer_per_serving},
    unit=beer_per_serving,
    vendor="tavern",
    description=registry["gnomish beer, in barrel"].description,
)

rum_per_serving = D(2) * u.floz
Recipe(
    "rum, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * rum_per_serving).to(u.lb),
    {},
    {"rum, in barrel": rum_per_serving},
    unit=rum_per_serving,
    vendor="tavern",
    description=registry["rum, in barrel"].description,
)


wine_per_serving = D(4) * u.floz
Recipe(
    "wine, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"wine, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="tavern",
    description=registry["wine, in barrel"].description,
)

Recipe(
    "wine, Baccia, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"wine, Baccia, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="tavern",
    description=registry["wine, Baccia, in barrel"].description,
)


Recipe(
    "champagne, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"champagne, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="tavern",
    description=registry["champagne, in barrel"].description,
)

Recipe(
    "wine, asti spumante, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"wine, asti spumante, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="tavern",
    description=registry["wine, asti spumante, in barrel"].description,
)

Recipe(
    "wine, Sacramaran, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"wine, Sacramaran, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="tavern",
    description=registry["wine, Sacramaran, in barrel"].description,
)

Recipe(
    "wine, Lutewood, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"wine, Lutewood, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="tavern",
    description=registry["wine, Lutewood, in barrel"].description,
)

# shall the price of greasy wool depend on the wool raw material? on the mature ewe recipe? or both?
# I've chosen both ...
greasy_wool_weight = Decimal(25) * u.lb
Recipe(
    "greasy wool",
    "wool",
    greasy_wool_weight,
    {"wool": greasy_wool_weight},
    {"mature ewe": 1 * u.head},
    unit=greasy_wool_weight,
)

scoured_wool_weight = D(15) * u.lb
Recipe(
    "scoured wool",
    "wool",
    scoured_wool_weight,
    {},
    {
        "greasy wool": scoured_wool_weight,
        # TODO "fuller's earth": 1,
    },
    unit=scoured_wool_weight,
)

# final step in cleaning wool is pounding by mills
Recipe(
    "clean wool",
    "wool",
    1 * u.lb,
    {},
    {"scoured wool": 1 * u.lb},
    unit=1 * u.lb,
    description="brownish-white color",
)

# some wool is additionally brushed for softness
Recipe(
    "brushed wool",
    "wool",
    1 * u.lb,
    {},
    {"clean wool": 1 * u.lb},
    unit=1 * u.lb,
    description="extra soft",
)


wool_yarn_linear_density = D(1) * u.lb / (Decimal(3000) * u.ft)
wool_yarn_sale_weight = Decimal(0.5) * u.lb
wool_yarn_sale_unit = wool_yarn_sale_weight / wool_yarn_linear_density
Recipe(
    "woolen yarn",
    "woolen goods",
    wool_yarn_sale_weight,
    {},
    {"clean wool": wool_yarn_sale_weight},
    unit=wool_yarn_sale_unit,
    vendor="spinner",
    description="useable as string, or in ropemaking and weaving",
)

Recipe(
    "brushed woolen yarn",
    "woolen goods",
    wool_yarn_sale_weight,
    {},
    {"brushed wool": wool_yarn_sale_weight},
    unit=wool_yarn_sale_unit,
    vendor="spinner",
    description="extra soft; useable as string, or in ropemaking and weaving",
)


Recipe(
    "worsted yarn",
    "worsted goods",
    wool_yarn_sale_weight,
    {},
    {"clean wool": wool_yarn_sale_weight},
    unit=wool_yarn_sale_unit,
    vendor="spinner",
    description="useable as string, or in ropemaking and weaving",
)

# TODO make a Pint unit for 'strands/threads per inch'
# warp threads per inch
ordinary_cloth_ends = D(32)
# weft per inch
ordinary_cloth_picks = D(32)
# X picks + Y ends per inch = X + Y inches of yarn per square inch of woven cloth
# given same yarn, more picks/ends = more yarn length used = more weight and cost per fabric square inch
# given heavier/lighter yarn, same picks/ends = same yarn length used but heavier/lighter fabric
yarn_per_ordinary_cloth = (
    ((ordinary_cloth_ends + ordinary_cloth_picks) * u.inch) / (D(1) * u.sqin)
).to(u.inch / u.sqft)
cloth_sale_unit = (D(1) * u.ell) * (D(6) * u.ft)
wool_ordinary_cloth_sale_weight = (
    (cloth_sale_unit * yarn_per_ordinary_cloth)
    / wool_yarn_sale_unit
    * wool_yarn_sale_weight
).to(u.lb)
# the WEAVE PATTERN influences neither weight nor ends/picks per inch, but does influence difficulty

Recipe(
    "woolen cloth",
    "woolen cloth",
    wool_ordinary_cloth_sale_weight,
    {},
    {"woolen yarn": yarn_per_ordinary_cloth * cloth_sale_unit},
    unit=cloth_sale_unit,
    vendor="weaver",
    description="plainweave",
)

Recipe(
    "flannel cloth",
    "woolen cloth",
    wool_ordinary_cloth_sale_weight,
    {},
    {"brushed woolen yarn": yarn_per_ordinary_cloth * cloth_sale_unit},
    unit=cloth_sale_unit,
    vendor="weaver",
    description="extra soft plainweave",
)

broadcloth_shrinking_factor = D(3)
Recipe(
    "broadcloth",
    "woolen cloth",
    wool_ordinary_cloth_sale_weight * D(2),
    {},
    {"woolen cloth": cloth_sale_unit * broadcloth_shrinking_factor},
    unit=cloth_sale_unit * D(2),
    vendor="weaver",
    description="stiff and tough plainweave woolen cloth, sold in double-wide bolts",
)

Recipe(
    "worsted cloth",
    "worsted cloth",
    wool_ordinary_cloth_sale_weight,
    {},
    {"worsted yarn": yarn_per_ordinary_cloth * cloth_sale_unit},
    unit=cloth_sale_unit,
    vendor="weaver",
    description="plainweave",
)

# Recipe(
#        'wool sweater',
#        'woolen goods',
#        )

Recipe(
    "worsted cloth, twill",
    "worsted cloth",
    wool_ordinary_cloth_sale_weight,
    {},
    {"worsted yarn": yarn_per_ordinary_cloth * cloth_sale_unit},
    unit=cloth_sale_unit,
    vendor="weaver",
    difficulty=1.1,
    description="twill weave",
)

Recipe(
    "worsted cloth, serge",
    "worsted cloth",
    wool_ordinary_cloth_sale_weight,
    {},
    {"worsted yarn": yarn_per_ordinary_cloth * cloth_sale_unit},
    unit=cloth_sale_unit,
    vendor="weaver",
    difficulty=1.2,
    description="diagonally-patterned twill weave",
)

Recipe(
    "carded cotton",
    "cotton",
    1 * u.lb,
    # roughly 60% of the weight of raw cotton is the boll, which is thrown away
    {"cotton": D(2.5) * u.lb},
    {},
    unit=1 * u.lb,
)

cotton_yarn_linear_density = D(1) * u.lb / (Decimal(4000) * u.ft)
cotton_yarn_sale_weight = Decimal(0.5) * u.lb
cotton_yarn_sale_unit = cotton_yarn_sale_weight / cotton_yarn_linear_density
Recipe(
    "cotton yarn",
    "cotton",
    cotton_yarn_sale_weight,
    {},
    {"carded cotton": cotton_yarn_sale_weight},
    unit=cotton_yarn_sale_unit,
    vendor="spinner",
    description="useable as string, or in ropemaking and weaving",
)

cotton_plainweave_sale_weight = (
    (cloth_sale_unit * yarn_per_ordinary_cloth)
    / cotton_yarn_sale_unit
    * cotton_yarn_sale_weight
).to(u.lb)
Recipe(
    "cotton cloth",
    "cotton cloth",
    cotton_plainweave_sale_weight,
    {},
    {"cotton yarn": yarn_per_ordinary_cloth * cloth_sale_unit},
    unit=cloth_sale_unit,
    vendor="weaver",
    description="plainweave",
)

Recipe(
    "retted flax",
    "flax",
    1 * u.lb,
    # this ratio is guesswork based on yield from 'scutching', which technically comes between retting and combing
    {"flax": 15 * u.lb},
    {},
    unit=1 * u.lb,
)

Recipe(
    "combed flax",
    "flax",
    1 * u.lb,
    {},
    {"retted flax": 1 * u.lb},
    difficulty=D(2),  # it's hard to work with flax fibers
    unit=1 * u.lb,
)

linen_yarn_linear_density = D(1) * u.lb / (Decimal(5000) * u.ft)
linen_yarn_sale_weight = Decimal(0.5) * u.lb
linen_yarn_sale_unit = linen_yarn_sale_weight / linen_yarn_linear_density
Recipe(
    "linen yarn",
    "flax",
    linen_yarn_sale_weight,
    {},
    {"combed flax": linen_yarn_sale_weight},
    unit=linen_yarn_sale_unit,
    vendor="spinner",
    description="useable as string, or in ropemaking and weaving",
)

linen_plainweave_sale_weight = (
    (cloth_sale_unit * yarn_per_ordinary_cloth)
    / linen_yarn_sale_unit
    * linen_yarn_sale_weight
).to(u.lb)
Recipe(
    "linen cloth",
    "linen cloth",
    linen_plainweave_sale_weight,
    {},
    {"linen yarn": yarn_per_ordinary_cloth * cloth_sale_unit},
    unit=cloth_sale_unit,
    vendor="weaver",
    description="plainweave",
)

pig_sale_weight = D(120) * u.lb
Recipe(
    "piglet",
    "swine",
    pig_sale_weight / 4,
    {"swine": 1 * u.head},
    vendor="stockyard",
    unit=1 * u.head,
)


Recipe(
    "pig",
    "swine",
    pig_sale_weight,
    {},
    {"piglet": 1 * u.head},
    vendor="stockyard",
    unit=1 * u.head,
)

# TODO refactor into two sides of pork, which are then divided into different cuts
pig_carcass_fraction = Decimal(0.75)
pig_meat_fraction = Decimal(0.75)
pork_per_pig = pig_sale_weight * pig_carcass_fraction * pig_meat_fraction
Recipe(
    "pork",
    "pork",
    1 * u.lb,
    {},
    {"pig": (Decimal(1) * u.lb / pork_per_pig) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

# cane can yield 50% of its mass in juice; approximately 20% of that juice is sugar
# brown (or "raw") sugar still contains some molasses
juice_from_sugarcane = Decimal(0.5) * u.lb / u.lb
sugar_from_juice = Decimal(0.2) * u.lb / u.lb
sugar_from_sugarcane = juice_from_sugarcane * sugar_from_juice
sugarcane_per_sugar = D(1) / sugar_from_sugarcane

Recipe(
    "raw sugar",
    "sugarcane",
    1 * u.lb,
    {"sugarcane": sugarcane_per_sugar * u.lb},
    {},
    vendor="grocer",
    unit=1 * u.lb,
    description="brown sugar with high molasses content",
)

Recipe(
    "refined sugar",
    "refined sugar",
    1 * u.lb,
    {},
    {"raw sugar": 1 * u.lb},
    vendor="grocer",
    unit=1 * u.lb,
    description="pale brown sugar with low molasses content",
)

molasses_from_juice = D(1) - sugar_from_juice
molasses_from_sugarcane = juice_from_sugarcane * molasses_from_juice
sugarcane_per_molasses = D(1) / molasses_from_sugarcane
# molasses_sale_volume = registry["cask, tierce"].capacity
molasses_sale_volume = D(1) * u.gallon
molasses_sale_weight = (
    density["molasses"].to(u.lb / u.gallon) * molasses_sale_volume
).to(u.lb)
Recipe(
    "molasses",
    "refined sugar",
    molasses_sale_weight,
    {"sugarcane": sugarcane_per_molasses * molasses_sale_weight},
    {},
    vendor="grocer",
    unit=molasses_sale_volume,
    description="black, gooey sugarcane extract",
)

Recipe(
    "raw tobacco",
    "tobacco",
    1 * u.lb,
    {"tobacco": 1 * u.lb},
    {},
    unit=1 * u.lb,
)

tobacco_sale_unit = D(14) * u.lb
Recipe(
    "cured tobacco",
    "tobacco",
    tobacco_sale_unit,
    {},
    {"raw tobacco": 5 * tobacco_sale_unit},
    unit=tobacco_sale_unit,
    vendor="tobacconist",
)

cigar_weight = D(0.75) * u.oz
Recipe(
    "cigar",
    "tobacco",
    cigar_weight,
    {},
    {"cured tobacco": cigar_weight},
    difficulty=2,  # aging, drying, and wrapping
    vendor="tobacconist",
)


snuff_sale_weight = D(1) * u.oz
snuff_per_use = D(0.2) * u.gram
uses_per_snuff_sale_unit = floor(snuff_sale_weight / snuff_per_use) * u.use
Recipe(
    "snuff",
    "snuff",
    snuff_sale_weight,
    {},
    {"cured tobacco": snuff_sale_weight},
    vendor="tobacconist",
    unit=uses_per_snuff_sale_unit,
    description=f"powdered snorting tobacco",
)

Recipe(
    "snuff, rose scent",
    "snuff",
    snuff_sale_weight,
    {
        "attar of roses": D(0.25) * snuff_sale_weight,
    },
    {
        "cured tobacco": snuff_sale_weight,
    },
    vendor="tobacconist",
    unit=uses_per_snuff_sale_unit,
    description=f"snuff scented with attar of roses",
)


smoking_pipe_length = D(6) * u.inch
horn_for_smoking_pipe = (
    D(2) * u.inch * D(2) * u.inch * smoking_pipe_length * density["horn"]
)
smoking_pipe_fraction_after_carving = D(0.75)  # 25% carved away
smoking_pipe_weight = (horn_for_smoking_pipe * smoking_pipe_fraction_after_carving).to(
    u.oz
)


Recipe(
    "smoking pipe, horn",
    "horncarving",
    smoking_pipe_weight,
    {},
    {
        "cattle horn": horn_for_smoking_pipe,
    },
    vendor="tobacconist",
    description=f"{smoking_pipe_length:~} long",
)


pony_sale_weight = D(600) * u.lb
pony_foal_age = D(1) * u.year
pony_foal_weight = pony_sale_weight / D(3)
pony_sale_age = D(2) * u.year
# raised on milk until weaned, then on both forage and feed
pony_raising_fodder = fodder_while_growing(
    pony_foal_age,
    pony_sale_age,
    pony_foal_weight,
    pony_sale_weight,
    D(0.015) * u.lb / u.lb,  # 1.5% of bodyweight in lbs of food per day
)
Recipe(
    "pony",
    "ponies",
    pony_sale_weight,
    # TODO use ponies as raw material, once ponies have a production number, and if they don't become a 'Raw'
    {"horses": 1 * u.head},
    {"animal feed": pony_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"{pony_sale_age} old, {pony_sale_weight:~}, {D(12) * u.hand:~} tall",
)


ridinghorse_sale_weight = D(1000) * u.lb
ridinghorse_foal_age = D(1) * u.year
ridinghorse_foal_weight = ridinghorse_sale_weight / D(3)
ridinghorse_sale_age = D(2.5) * u.year
# raised on milk until weaned, then on both forage and feed
ridinghorse_raising_fodder = fodder_while_growing(
    ridinghorse_foal_age,
    ridinghorse_sale_age,
    ridinghorse_foal_weight,
    ridinghorse_sale_weight,
    D(0.015) * u.lb / u.lb,
)
Recipe(
    "riding horse",
    "horses",
    ridinghorse_sale_weight,
    {"horses": 1 * u.head},
    {"animal feed": ridinghorse_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"{ridinghorse_sale_age} old, {ridinghorse_sale_weight:~}, {D(15) * u.hand:~} tall",
)

# assumes that a riding horse could instead be used for milking
mare_annual_milk_volume = (D(550) * u.liter).to(u.gallon)
Recipe(
    "mare milk",
    "milk",
    milk_weight * milk_sale_unit,
    {},
    {"riding horse": (D(1) / (mare_annual_milk_volume / milk_sale_unit)) * u.head},
    unit=milk_sale_unit,
    vendor="dairy",
    description="customer supplies container",
)


milk_for_kumiss = Decimal(3) * u.gallon / u.gallon
kumiss_abv = calculate_abv(
    {
        "mare milk": milk_for_kumiss * 1 * u.gallon,
    },
    1 * u.gallon,
    1 * u.gallon,
)

Recipe(
    "kumiss, in barrel",
    "kumiss",
    (density["milk"] * barrel_capacity).to(u.lb),
    {},
    {
        "mare milk": milk_for_kumiss * barrel_capacity,
    },
    unit=barrel_capacity,
    container="cask, barrel",
    vendor="brewer",
    description=f"{str(kumiss_abv.magnitude)}% alcohol; fermented mare milk, a favorite among the Ulub",
)


kumiss_per_serving = D(1) * u.pint
Recipe(
    "kumiss, by the glass",
    "foodstuffs",
    (density["milk"] * kumiss_per_serving).to(u.lb),
    {},
    {"kumiss, in barrel": kumiss_per_serving},
    unit=kumiss_per_serving,
    description=registry["kumiss, in barrel"].description,
    vendor="tavern",
)


drafthorse_sale_weight = D(1800) * u.lb
drafthorse_foal_age = D(1) * u.year
drafthorse_foal_weight = drafthorse_sale_weight / D(3)
drafthorse_sale_age = D(2.5) * u.year
# raised on milk until weaned, then on both forage and feed
drafthorse_raising_fodder = fodder_while_growing(
    drafthorse_foal_age,
    drafthorse_sale_age,
    drafthorse_foal_weight,
    drafthorse_sale_weight,
    D(0.015) * u.lb / u.lb,
)
Recipe(
    "draft horse",
    "horses, draft",  # TODO only one reference T_T
    drafthorse_sale_weight,
    {"horses": 1 * u.head},
    {"animal feed": drafthorse_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"{drafthorse_sale_age} old, {drafthorse_sale_weight:~}, {D(18) * u.hand:~} tall",
)

# TODO war horses avg weight 1400

donkey_sale_weight = D(650) * u.lb
donkey_foal_age = D(1) * u.year
donkey_foal_weight = donkey_sale_weight / D(2)
donkey_sale_age = D(2.5) * u.year
# raised on milk until weaned, then on both forage and feed
donkey_raising_fodder = fodder_while_growing(
    donkey_foal_age,
    donkey_sale_age,
    donkey_foal_weight,
    donkey_sale_weight,
    D(0.015) * u.lb / u.lb,
)

Recipe(
    "donkey",
    "donkeys",
    donkey_sale_weight,
    {"donkeys": 1 * u.head},
    {"animal feed": donkey_raising_fodder},
    vendor="stockyard",
    unit=1 * u.head,
    description=f"{donkey_sale_age} old jack (male), {donkey_sale_weight:~}; can carry 125 lbs",
)

# part eagle part lion - relatively light for its height
# compare with hippogriff, part eagle part horse - much heavier and nastier
griff_sale_weight = D(600) * u.lb
griff_sale_age = D(1) * u.year
griff_raising_fodder = fodder_while_growing(
    0 * u.year,
    griff_sale_age,
    0 * u.lb,
    griff_sale_weight,
    D(0.02) * u.lb / u.lb,
)

Recipe(
    "griffon",
    "griffs",
    griff_sale_weight,
    {"griffs": 1 * u.head},
    {"beef": griff_raising_fodder},
    vendor="stockyard",
    unit=1 * u.head,
    difficulty=2.5,
    description=f"{griff_sale_age} old, {griff_sale_weight:~}, {D(12) * u.hand} tall",
)

Recipe(
    "vinegar, in barrel",
    "vinegar",  # TODO vinegar ref makes it 10x more expensive :(
    registry["beer, in barrel"].weight,
    {},
    {"beer, in barrel": registry["beer, in barrel"].unit},
    vendor="brewer",
    unit=registry["beer, in barrel"].unit,
)


Recipe(
    "fired clay",
    "ceramics",
    clay_slab_weight,
    {"ceramics": Decimal(1.15) * clay_slab_weight},
    {},
    unit=clay_slab_weight,
    description="accounts for firing wet clay, so it does not have to be done separately for all clay goods",
)

# this is a huge fudge since it varies from stone to stone, but accurate enough for my purposes
AGGREGATE_DENSITY_FACTOR = D(1.6)


def aggregate_density(stone):
    d = density.get(stone)
    if not d:
        raise ValueError
    return density.get(f"crushed {stone}", d / AGGREGATE_DENSITY_FACTOR)


applicable_stones = [
    stone
    for stone in categories["building stones"]["members"]
    if (world_references[stone]["production"] != 0) and (stone in density)
]
for stone in applicable_stones:
    d = density[stone]
    theweight = (d * masonry_unit).to(u.lb)
    Recipe(
        f"masonry, {stone}",
        "masonry",
        theweight,
        {f"{stone}": theweight},
        unit=masonry_unit,
        vendor="mason",
    )

    ad = aggregate_density(stone)
    aggregate_sale_weight = (ad * masonry_unit).to(u.lb)
    Recipe(
        f"crushed {stone}",
        "masonry",
        aggregate_sale_weight,
        {
            f"{stone}": aggregate_sale_weight,
        },
        {},
        unit=masonry_unit,
    )

pan_thickness = D(1) / D(8) * u.inch
pan_handle_length = D(4) * u.inch
pan_handle_width = D(1) * u.inch
pan_handle_hole_radius = D(1) / D(8) * u.inch
pan_handle_volume = (
    pan_handle_length * pan_handle_width * pan_thickness
) - cylinder_volume(pan_thickness, pan_handle_hole_radius)
pan_body_radius = D(5) * u.inch
pan_body_height = D(2) * u.inch
# a cylinder, minus a smaller cylinder, leaving the shape of a straight-walled pan's body
pan_body_volume = cylinder_volume(pan_body_height, pan_body_radius) - cylinder_volume(
    pan_body_height - pan_thickness, pan_body_radius - pan_thickness
)
pan_weight = (density["cast iron"] * (pan_body_volume + pan_handle_volume)).to(u.lb)
Recipe(
    "cooking pan",
    "ironmongery",  # TODO "pans" is a reference... but if I do that it jumps from 2gp to 56gp!
    pan_weight,
    {},
    {"cast iron": pan_weight},
    vendor="blacksmith",
    description=f"cast iron; diameter {pan_body_radius * 2}; handle has hole for hanging",
)

clay_per_glass = D(0.7) * u.lb / u.lb
soda_per_glass = D(0.15) * u.lb / u.lb
quicklime_per_glass = D(0.1) * u.lb / u.lb
salt_per_glass = D(0.01) * u.lb / u.lb
dolomite_per_glass = D(0.04) * u.lb / u.lb  # source of magnesium
glass_pane_length = D(7) * u.inch
glass_pane_width = D(6) * u.inch
glass_pane_thickness = D(0.25) * u.inch
Recipe(
    "soda glass",
    "glassware",
    1 * u.lb,
    {
        "soda ash": soda_per_glass * u.lb,
        "dolomite": dolomite_per_glass * u.lb,
        "salt": salt_per_glass * u.lb,
    },
    {
        "fired clay": clay_per_glass * u.lb,
        "quicklime": quicklime_per_glass * u.lb,
    },
    vendor="glazier",
    unit=1 * u.lb,  # TODO use panes as unit
    description=f"{glass_pane_length} x {glass_pane_width} x {glass_pane_thickness} pane",
)


lead_per_glass = D(0.25) * u.lb / u.lb
Recipe(
    "lead glass",
    "glassware",
    1 * u.lb,
    {
        "soda ash": soda_per_glass * u.lb,
        "dolomite": dolomite_per_glass * u.lb,
        "salt": salt_per_glass * u.lb,
    },
    {
        "fired clay": clay_per_glass * u.lb,
        "raw lead": lead_per_glass * u.lb,
    },
    vendor="glazier",
    unit=1 * u.lb,  # TODO use panes as unit
    description=f"{glass_pane_length} x {glass_pane_width} x {glass_pane_thickness} pane",
)

wine_glass_weight = D(5) * u.oz
Recipe(
    "glass, wine",
    "glassware",
    wine_glass_weight,
    {},
    {"soda glass": wine_glass_weight},
    vendor="glassblower",
)

pint_glass_weight = D(6) * u.oz
Recipe(
    "glass, pint",
    "glassware",
    pint_glass_weight,
    {},
    {"soda glass": pint_glass_weight},
    vendor="glassblower",
)


# TODO add cork
wine_bottle_weight = D(1.4) * u.lb
wine_bottle_capacity = D(6) * wine_per_serving
Recipe(
    "bottle, wine",
    "glassware",
    wine_bottle_weight,
    {},
    {"soda glass": wine_bottle_weight},
    vendor="glassblower",
    capacity=wine_bottle_capacity,
)

for w in wines:
    Recipe(
        f"{w}, in bottle",
        "wine",  # generic because tapping and pouring into bottle doesn't depend on which type it is; same as how all "by the glass" recipes have "foodstuffs" governor
        (density["water"] * wine_bottle_capacity).to(u.lb),
        {},
        {
            f"{w}, in barrel": wine_bottle_capacity,
        },
        unit=wine_bottle_capacity,
        container="bottle, wine",
        vendor="vintner",
        description=registry[f"{w}, in barrel"].description,
    )

pint_bottle_weight = D(8) * u.oz
pint_bottle_capacity = beer_per_serving
Recipe(
    "bottle, pint",
    "glassware",
    pint_bottle_weight,
    {},
    {"soda glass": pint_bottle_weight},
    vendor="glassblower",
    capacity=pint_bottle_capacity,
)

for each in ("beer", "ale", "gnomish beer", "kumiss"):
    Recipe(
        f"{each}, in bottle",
        "brewing",  # generic because tapping and pouring into bottle doesn't depend on which type it is
        (density["water"] * pint_bottle_capacity).to(u.lb),
        {},
        {
            f"{each}, in barrel": pint_bottle_capacity,
        },
        unit=pint_bottle_capacity,
        container="bottle, pint",
        vendor="brewer",
        description=registry[f"{each}, in barrel"].description,
    )

dog_sale_weight = D(40) * u.lb
puppy_sale_weight = dog_sale_weight / D(4)
puppy_sale_age = D(3) * u.month
dog_sale_age = D(1) * u.year
puppy_raising_fodder = fodder_while_growing(
    D(0) * u.month,
    puppy_sale_age,
    D(0) * u.lb,
    puppy_sale_weight,
    D(0.03) * u.lb / u.lb,
)
dog_raising_fodder = fodder_while_growing(
    D(0) * u.month,
    dog_sale_age,
    D(0) * u.lb,
    dog_sale_weight,
    D(0.03) * u.lb / u.lb,
)

Recipe(
    "dog, puppy",
    "dogs",
    puppy_sale_weight,
    {"dogs": 1 * u.head},
    {"beef": puppy_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"{puppy_sale_age} old, {puppy_sale_weight:~}; totally untrained",
)

Recipe(
    "dog, working",
    "dogs",
    dog_sale_weight,
    {"dogs": 1 * u.head},
    {"beef": dog_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    description=f"{dog_sale_age} old, {dog_sale_weight:~}; includes herding and cart-pulling dogs",
)

Recipe(
    "dog, hunting/watch",
    "dogs",
    dog_sale_weight,
    {"dogs": 1 * u.head},
    {"beef": dog_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    difficulty=D(1.25),
    description=f"{dog_sale_age} old, {dog_sale_weight:~}; dog can track animals and alert owner to threats, but won't fight",
)

Recipe(
    "dog, guard",
    "dogs",
    dog_sale_weight,
    {"dogs": 1 * u.head},
    {"beef": dog_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    difficulty=D(1.5),
    description=f"{dog_sale_age} old, {dog_sale_weight:~}; as hunting dog, plus combat abilities",
)

Recipe(
    "dog, war",
    "dogs",
    dog_sale_weight,
    {"dogs": 1 * u.head},
    {"beef": dog_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
    difficulty=D(2),
    description=f"{dog_sale_age} old, {dog_sale_weight:~}; as guard dog, plus bonus HP and can wear armor",
)

slaves = {
    "porter/laborer": {
        "weight": D(150) * u.lb,
        "minimum age": D(16) * u.year,
        "difficulty": 1.1,
        "description": "large, strong male; Str and Con 11+, other abilities usually 8",
    },
    "courtesan": {
        "weight": D(110) * u.lb,
        "minimum age": D(14) * u.year,
        "description": "attractive  female; Cha 11+, other abilities usually 8",
        "difficulty": 1.2,
    },
    "entertainer": {
        "weight": D(130) * u.lb,
        "minimum age": D(14) * u.year,
        "description": "talented male; Dex and Cha 11+, other abilities usually 8",
        "difficulty": 1.4,
    },
    "house servant": {
        "weight": D(120) * u.lb,
        "minimum age": D(16) * u.year,
        "description": "male or female; all abilities usually 9",
    },
}

for slave, info in slaves.items():
    slave_raising_fodder = fodder_while_growing(
        D(0) * u.month,
        info["minimum age"].to(u.month),
        D(0) * u.lb,
        info["weight"],
        D(0.01) * u.lb / u.lb,
    )
    Recipe(
        f"slave, {slave}",
        "slaves",
        info["weight"],
        {"slaves": 1 * u.head},
        {"bread": slave_raising_fodder},
        unit=1 * u.head,
        vendor="slave trader",
        difficulty=info.get("difficulty", 1),
        description=f"{info['description']}; age {info['minimum age']} and up",
    )


building_member_width = D(6) * u.inch
building_member_thickness = D(6) * u.inch
for length in (2, 3, 3.47, 4, 5, 6, 8, 9, 14, 15):
    # lengths needed for standard housing size
    height = D(length) * u.foot
    volume = height * building_member_width * building_member_thickness
    weight = (density["timber"] * volume).to(u.lb)
    Recipe(
        f"building member, {length}-foot",
        "timber",  # TODO carpentry?
        weight,
        {
            "timber": weight,
        },
        {},
        description="hewn wooden member for timber framing",
    )
    if length == 14:
        # a wider member, used to form core of flooring on higher levels
        thickness = D(12) * u.inch
        volume = height * building_member_width * thickness
        weight = (density["timber"] * volume).to(u.lb)
        Recipe(
            f"building member, wide, {length}-foot",
            "timber",  # TODO carpentry?
            weight,
            {
                "timber": weight,
            },
            {},
            description="hewn wooden member for timber framing",
        )


# sunk one foot into sill and foundation
posts_per_story = 4
framing_first_story_posts = ["building member, 15-foot"] * posts_per_story
# between the posts
beams_per_story = 4
framing_first_story_beams = ["building member, 14-foot"] * beams_per_story
trusses_per_story = 8
framing_first_story_trusses = ["building member, 5-foot"] * trusses_per_story
framing_first_story_members = (
    framing_first_story_posts + framing_first_story_beams + framing_first_story_trusses
)
framing_first_story_weight = sum(
    [registry[m].weight for m in framing_first_story_members]
)
Recipe(
    "timber framing, first story",
    "carpentry",
    framing_first_story_weight,
    {},
    {k: v * u.item for k, v in Counter(framing_first_story_members).items()},
    description="per 60 feet of perimeter",
)

floorbeams_per_story = 4
framing_second_story_floorbeams = [
    "building member, wide, 14-foot"
] * floorbeams_per_story
framing_second_story_members = (
    framing_first_story_members + framing_second_story_floorbeams
)
framing_second_story_weight = sum(
    [registry[m].weight for m in framing_second_story_members]
)
Recipe(
    "timber framing, second story and higher",
    "carpentry",
    framing_second_story_weight,
    {},
    {k: v * u.item for k, v in Counter(framing_second_story_members).items()},
    description="per 60 feet of perimeter",
)

alabaster_for_cement = D(0.25) * u.lb / aggregate_density("alabaster")
Recipe(
    "cement",
    "masonry",
    1 * u.lb,
    {},
    {
        "quicklime": 0.25 * u.lb,
        "crushed alabaster": alabaster_for_cement,
        # the rest of the weight is sand/clay/shale -- no price available, too cheap to meter
    },
    vendor="mason",
    unit=1 * u.lb,
    description="powdered",
)

# One recipe from Wikipedia: "Typically, a batch of concrete can be made by using 1 part Portland cement, 2 parts dry sand, 3 parts dry stone, 1/2 part water. The parts are in terms of weight – not volume. For example, 1-cubic-foot (0.028 m3) of concrete would be made using 22 lb (10.0 kg) cement, 10 lb (4.5 kg) water, 41 lb (19 kg) dry sand, 70 lb (32 kg) dry stone (1/2" to 3/4" stone). This would make 1-cubic-foot (0.028 m3) of concrete and would weigh about 143 lb (65 kg). The sand should be mortar or brick sand (washed and filtered if possible) and the stone should be washed if possible. Organic materials (leaves, twigs, etc.) should be removed from the sand and stone to ensure the highest strength."
dryconcrete_sale_weight = (density["dry concrete"] * masonry_unit).to(u.lb)
Recipe(
    "concrete, dry",
    "masonry",
    dryconcrete_sale_weight,
    {},
    {
        "cement": 22 * u.lb,
        "crushed limestone": D(70) * u.lb / aggregate_density("limestone")
        # the rest of the weight is sand/clay/shale, and water
    },
    vendor="mason",
    unit=dryconcrete_sale_weight,
    description="powdered; sufficient for 1 cubic foot wet concrete",
)

wetconcrete_sale_weight = (density["wet concrete"] * masonry_unit).to(u.lb)
Recipe(
    "masonry, concrete",
    "masonry",
    wetconcrete_sale_weight,
    {},
    {
        "concrete, dry": dryconcrete_sale_weight,
    },
    unit=masonry_unit,
    vendor="mason",
)

# TODO make this more accurate by checking historical timber framing books
building_foundation_height = D(6) * u.inch
building_foundation_width = D(15) * u.foot
building_foundation_volume = (
    building_foundation_height * building_foundation_width * building_foundation_width
).to(u.cuft)
building_foundation_weight = (density["wet concrete"] * building_foundation_volume).to(
    u.lb
)
Recipe(
    "building foundation",
    "masonry",
    building_foundation_weight,
    {},
    {
        "masonry, concrete": building_foundation_volume,
    },
    description=f"{building_foundation_width:~} ft. square, {building_foundation_height:~} thick",
)

building_sill_height = building_member_thickness
building_sill_width = D(15) * u.foot
members_for_buildingsill = (building_sill_width / building_member_width).to(
    u.dimensionless
)
building_sill_volume = (
    building_sill_width * building_sill_width * building_sill_height
).to(u.cuft)
building_sill_weight = (density["timber"] * building_sill_volume).to(u.lb)
Recipe(
    "building sill",
    "carpentry",
    building_sill_weight,
    {},
    {
        "building member, 15-foot": members_for_buildingsill * u.item,
    },
    description="timber layer above foundation",
)

roofbeams_per_roof = 8
framing_roofbeams = ["building member, 14-foot"] * roofbeams_per_roof
framing_roof_oneside_members = (
    ["building member, 9-foot"] * 2
    + ["building member, 2-foot"] * 6
    + ["building member, 4-foot"] * 3
    + ["building member, 3-foot"] * 2
    + ["building member, 6-foot"] * 1
    + ["building member, 8-foot"] * 1
    # 3.47 foot = approx sqrt(12); these are trusses within the top triangle, perpendicular to the roofing tiles
    + ["building member, 3.47-foot"] * 2
)
framing_roof_members = framing_roofbeams + (2 * framing_roof_oneside_members)
framing_roof_weight = sum([registry[m].weight for m in framing_roof_members])
Recipe(
    "timber framing, roof",
    "carpentry",
    framing_roof_weight,
    {},
    {k: v * u.item for k, v in Counter(framing_roof_members).items()},
    description="per 60 feet of perimeter; additions may only require longer roofbeams",
)

shingle_length = D(1) * u.foot
shingle_width = D(1) * u.foot
shingle_thickness = D(0.25) * u.inch
shingle_volume = (shingle_length * shingle_width * shingle_thickness).to(u.cuft)
slate_shingle_weight = density["slate"] * shingle_volume
Recipe(
    "shingle, slate",
    "masonry",
    slate_shingle_weight,
    {},
    {"masonry, slate": shingle_volume},
    vendor="mason",
    description=f"{shingle_length:~} x {shingle_width:~} x {shingle_thickness:~}",
)

earthenware_shingle_weight = density["clay"] * shingle_volume
Recipe(
    "shingle, earthenware",
    "pottery",
    earthenware_shingle_weight,
    {},
    {"fired clay": earthenware_shingle_weight},
    vendor="potter",
    description=registry["shingle, slate"].description,
)


roofing_area = D(9) * u.foot * D(14) * u.foot
## if shingles are to cover 10 square feet, 12 square feet of shingles will be needed
shingle_overlap = D(0.20)
shingles_per_oneside_roof = (
    (roofing_area + (roofing_area * shingle_overlap)) / (shingle_length * shingle_width)
).to(u.dimensionless)
shingles_per_roof = D(2) * shingles_per_oneside_roof
for material in ("slate", "earthenware"):
    weight = (
        earthenware_shingle_weight
        if material == "earthenware"
        else slate_shingle_weight
    )
    governor = "pottery" if material == "earthenware" else "masonry"
    Recipe(
        f"roofing, {material}",
        governor,
        shingles_per_roof * weight,
        {},
        {f"shingle, {material}": shingles_per_roof * u.item},
        description="includes both sides of roof",
    )


infill_onewall_volume = D(14) * u.foot * D(13.5) * u.foot * D(0.5) * u.foot
infill_oneside_roof_volume = D(79.9422) * u.sqft * D(0.5) * u.foot
infill_volume_per_story = D(4) * infill_onewall_volume
infill_volume_per_roof = D(2) * infill_oneside_roof_volume


def total_infill_volume(stories):
    return infill_volume_per_roof + (stories * infill_volume_per_story)


def infill_ingredients(volume):
    return {
        "crushed limestone": D(0.7) * volume,
        "crushed sandstone": D(0.2) * volume,
        "masonry, mortar": D(0.1) * volume,
    }


onestory_house_components = {
    "building foundation": 1 * u.item,
    "building sill": 1 * u.item,
    "timber framing, first story": 1 * u.item,
    "timber framing, roof": 1 * u.item,
    "roofing, slate": 1 * u.item,
}

onestory_house_components.update(infill_ingredients(total_infill_volume(1)))

Recipe(
    "half-timbered house, one story",
    "carpentry",  # TODO anything better?
    sum(
        [
            registry[x].weight * amount.magnitude
            for x, amount in onestory_house_components.items()
        ]
    ),
    {},
    onestory_house_components,
    vendor="builder",
    description="15 x 15 ft perimeter, 14 x 14 ft usable internal area per floor; slate-roofed, with concrete foundation",
)

twostory_house_components = {
    "building foundation": 1 * u.item,
    "building sill": 1 * u.item,
    "timber framing, first story": 1 * u.item,
    "timber framing, second story and higher": 1 * u.item,
    "timber framing, roof": 1 * u.item,
    "roofing, slate": 1 * u.item,
}

twostory_house_components.update(infill_ingredients(total_infill_volume(2)))

Recipe(
    "half-timbered house, two stories",
    "carpentry",  # TODO anything better?
    sum(
        [
            registry[x].weight * amount.magnitude
            for x, amount in twostory_house_components.items()
        ]
    ),
    {},
    twostory_house_components,
    vendor="builder",
    description=registry["half-timbered house, one story"].description,
)

elucia_cabin_components = {
    "timber framing, first story": 2 * u.item,
    "timber framing, roof": 2 * u.item,
    "roofing, slate": 2 * u.item,
}

Recipe(
    "Elucia's wooden cabin",
    "carpentry",
    sum(
        [
            registry[x].weight * amount.magnitude
            for x, amount in elucia_cabin_components.items()
        ]
    ),
    {},
    elucia_cabin_components,
    vendor="builder",
    description="one-story half-timbered cabin, with slate roof",
)


goose_sale_weight = D(9.5) * u.lb
goose_sale_age = D(4) * u.month
goose_raising_fodder = fodder_while_growing(
    D(0) * u.month,
    goose_sale_age,
    D(2) * u.oz,
    goose_sale_weight,
    D(0.01) * u.lb / u.lb,
)

Recipe(
    "goose",
    "geese",
    goose_sale_weight,
    {"geese": 1 * u.head},
    {"animal feed": goose_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
)

goose_carcass_fraction = D(0.85)
goose_meat_fraction = D(0.75)
goose_carcass_weight = goose_carcass_fraction * goose_sale_weight
goose_meat_weight = goose_meat_fraction * goose_carcass_weight
Recipe(
    "goose meat",
    "meat",
    1 * u.lb,
    {},
    {"goose": (Decimal(1) * u.lb / goose_meat_weight) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

chicken_sale_age = D(4) * u.month
chicken_sale_weight = D(2.5) * u.lb
chicken_raising_fodder = fodder_while_growing(
    D(0) * u.month,
    chicken_sale_age,
    D(2) * u.oz,
    chicken_sale_weight,
    D(0.01) * u.lb / u.lb,
)

Recipe(
    "hen",
    "chickens",
    chicken_sale_weight,
    {"chickens": 1 * u.head},
    {"animal feed": chicken_raising_fodder},
    unit=1 * u.head,
    vendor="stockyard",
)

chicken_carcass_fraction = D(0.75)
chicken_meat_fraction = D(0.75)
chicken_carcass_weight = chicken_carcass_fraction * chicken_sale_weight
chicken_meat_weight = chicken_meat_fraction * chicken_carcass_weight
Recipe(
    "chicken meat",
    "meat",
    1 * u.lb,
    {},
    {"hen": (Decimal(1) * u.lb / chicken_meat_weight) * u.head},
    unit=1 * u.lb,
    vendor="butcher",
)

# one hen will produce approximately 300 eggs in the first year, and fewer in future years; so let's adjust that first-year figure to 250 for a more average number
chicken_annual_eggs = D(250)
Recipe(
    "egg, chicken",
    "poultry and eggs",
    Decimal(0.125) * u.lb,
    {},
    {"hen": D(1) * u.head / chicken_annual_eggs * D(12)},
    vendor="stockyard",
    unit=D(12) * u.item,
)

feather_weight = (D(0.00125) * u.gram).to(u.oz)
feathers_per_goose = D(1000)
Recipe(
    "feather, goose",
    "geese",
    feather_weight,
    {},
    {
        "goose": D(1) * u.head / feathers_per_goose,
    },
)

# arrowhead_volume = cone_volume(D(2) * u.inch, arrow_radius)
# arrowhead_weight = (density["wrought iron"] * arrowhead_volume).to(u.lb)
arrowhead_weight = D(15) * u.gram
Recipe(
    "arrowhead",
    "ironmongery",
    arrowhead_weight,
    {},
    {"steel": arrowhead_weight},
)


arrow_radius = D(0.125) * u.inch
arrow_length = D(28) * u.inch
arrow_volume = cylinder_volume(arrow_length, arrow_radius)
arrow_timber_weight = (density["timber"] * arrow_volume).to(u.oz)
arrow_feather_weight = D(3) * registry["feather, goose"].weight
total_arrow_weight = arrow_timber_weight + arrow_feather_weight + arrowhead_weight
Recipe(
    "arrow",
    "woodcraft",
    total_arrow_weight,
    {"timber": arrow_timber_weight},
    {
        "feather, goose": D(3) * u.item,
        "arrowhead": D(1) * u.item,
    },
    vendor="bowyer",
    description=f"{arrow_length}",
)

silver_arrow_silver_weight = arrowhead_weight * silvering_percentage
Recipe(
    "arrow, silver",
    "woodcraft",
    total_arrow_weight + silver_arrow_silver_weight,
    {"timber": arrow_timber_weight},
    {
        "feather, goose": D(3) * u.item,
        "arrowhead": D(1) * u.item,
        "raw silver": silver_arrow_silver_weight,
    },
    vendor="bowyer",
    description=f"{arrow_length}",
)


spearhead_length = D(5) * u.inch
spear_haft_radius = D(0.75) * u.inch
spearhead_volume = cone_volume(spearhead_length, spear_haft_radius)
spearhead_weight = (density["steel"] * spearhead_volume).to(u.lb)

Recipe(
    "spearhead",
    "weapons",
    spearhead_weight,
    {},
    {"steel": spearhead_weight},
)

spear_haft_length = D(4) * u.foot
spear_haft_volume = cylinder_volume(spear_haft_length, spear_haft_radius)
spear_haft_weight = (density["timber"] * spear_haft_volume).to(u.lb)
spear_weight = spear_haft_weight + spearhead_weight
Recipe(
    "spear",
    "weapons",
    spear_weight,
    {"timber": spear_haft_weight},
    {"spearhead": 1 * u.item},
    vendor="weaponsmith",
    description=f"1d6 damage, haft {spear_haft_length:~} long; 2-handed melee or 1-handed thrown 4/7/10",
)

dart_haft_length = D(6) * u.inch
dart_haft_radius = spear_haft_radius
dart_haft_volume = cylinder_volume(dart_haft_length, dart_haft_radius)
dart_haft_weight = (density["timber"] * dart_haft_volume).to(u.lb)
dart_weight = dart_haft_weight + spearhead_weight
Recipe(
    "dart",
    "weapons",
    dart_weight,
    {"timber": dart_haft_weight},
    {"spearhead": 1 * u.item},
    vendor="weaponsmith",
    description=f"1d3 damage; {dart_haft_length} haft; roughly a miniature spear; melee or thrown 3/4/5",
)

mace_flange_length = D(4) * u.inch
mace_flange_height = D(1) * u.inch
mace_flange_thickness = D(0.25) * u.inch
mace_flange_volume = triangular_prism_volume(
    mace_flange_length, mace_flange_height, mace_flange_thickness
)
mace_flange_weight = (density["steel"] * mace_flange_volume).to(u.lb)
Recipe(
    "mace flange",
    "weapons",
    mace_flange_weight,
    {},
    {"steel": mace_flange_weight},
)

mace_haft_length = D(2.5) * u.foot
mace_haft_radius = D(1) * u.inch
mace_haft_volume = cylinder_volume(mace_haft_length, mace_haft_radius)
mace_haft_weight = (density["timber"] * mace_haft_volume).to(u.lb)
mace_weight = mace_haft_weight + (6 * mace_flange_weight)
Recipe(
    "mace",
    "weapons",
    mace_weight,
    {"timber": mace_haft_weight},
    {"mace flange": 6 * u.item},
    vendor="weaponsmith",
    description=f"1d6+1 damage, one-handed; haft {mace_haft_length:~} long",
)


wire_sale_unit = D(100) * u.foot
wire_volume = cylinder_volume(wire_sale_unit, gauge16wire_thickness)
wire_sale_weight = (density["wrought iron"] * wire_volume).to(u.lb)
Recipe(
    "wire",
    "ironmongery",  # TODO should use wire but only 9 references so things get expensive
    wire_sale_weight,
    {},
    {"wrought iron": wire_sale_weight},
    # lots of hammering, then lots and lots of pulling
    difficulty=2,
    unit=wire_sale_unit,
    vendor="blacksmith",
    description=f"16-gauge ({gauge16wire_thickness:~} thick)",
)


def armor_size(race):
    # all armors are calculated relative to human proportions, then adjusted by the average for medium or small races
    # since humans included with other smaller-but-still-size-medium races, they get roughly a 15% discount on armor prices relative to what they should pay for their size
    def helper(race):
        return (
            races[race]["base height"]["male"] / races["human"]["base height"]["male"]
        )

    if race not in races:
        raise ValueError(f"{race} is not a valid race")
    medium_races = ("human", "halforc", "dwarf", "elf")
    small_races = ("gnome", "halfling")
    if race in medium_races:
        return sum([helper(r) for r in medium_races]) / len(medium_races)
    else:
        return sum([helper(r) for r in small_races]) / len(small_races)


body_proportions = {
    # these measurements are for a male human; scale up or down for other races
    "head": {"length": D(1) * u.ft, "girth": D(1) * u.ft},
    "torso": {"length": D(2) * u.ft, "girth": D(3) * u.ft},
    "forearm": {"length": D(1) * u.ft, "girth": D(1) * u.ft},
    "upper arm": {"length": D(1) * u.ft, "girth": D(1) * u.ft},
    "thigh": {"length": D(1.5) * u.ft, "girth": D(1.5) * u.ft},
    "calf": {"length": D(1.5) * u.ft, "girth": D(1) * u.ft},
    "foot": {"length": D(1) * u.ft, "girth": D(6) * u.inch},
    "hand": {"length": D(6) * u.inch, "girth": D(4) * u.inch},
}

quartersleeve_area = (
    D(0.5)
    * body_proportions["upper arm"]["length"]
    * body_proportions["upper arm"]["girth"]
)
halfsleeve_area = (
    body_proportions["upper arm"]["length"] * body_proportions["upper arm"]["girth"]
)
fullsleeve_area = (
    body_proportions["upper arm"]["length"] * body_proportions["upper arm"]["girth"]
) + (body_proportions["forearm"]["length"] * body_proportions["forearm"]["girth"])
forearm_area = (
    body_proportions["forearm"]["length"] * body_proportions["forearm"]["girth"]
)
thigh_area_around_one = (
    body_proportions["thigh"]["length"] * body_proportions["thigh"]["girth"]
)
thigh_area_around_both = (
    # NOTE torso girth because this is a continuous loop encompassing both thighs, as with a skirt or a fauld
    body_proportions["thigh"]["length"]
    * body_proportions["torso"]["girth"]
)
calf_area_around_one = (
    body_proportions["calf"]["length"] * body_proportions["calf"]["girth"]
)
calf_area_around_both = (
    # NOTE torso girth because this is a continuous loop encompassing both calves
    body_proportions["calf"]["length"]
    * body_proportions["torso"]["girth"]
)
torso_area = body_proportions["torso"]["length"] * body_proportions["torso"]["girth"]
hand_area = body_proportions["hand"]["length"] * body_proportions["hand"]["girth"]
foot_sole_area = (
    body_proportions["foot"]["length"] * D(0.5) * body_proportions["foot"]["girth"]
)

gambeson_layers = D(6)
gambeson_area = torso_area + (fullsleeve_area * 2)
gambeson_cloth = gambeson_area * gambeson_layers
# string is stitched around the perimeter of each layer, attaching it to the next
gambeson_string = gambeson_cloth / u.sqft * u.foot
gambeson_cloth_weight = (
    (gambeson_cloth / registry["cotton cloth"].unit) * registry["cotton cloth"].weight
).to(u.lb)
gambeson_string_weight = (
    (gambeson_string / registry["cotton yarn"].unit) * registry["cotton yarn"].weight
).to(u.lb)
gambeson_weight = gambeson_cloth_weight + gambeson_string_weight


def make_armor(name, base_weight, raws, recipes, description, vendor=None):
    for race in ("human", "gnome"):
        if race == "human":
            size = None
        else:
            size = "small"
        ratio = armor_size(race)
        Recipe(
            name if not size else name + f", {size}",
            "armor",
            base_weight * ratio,
            {k: v * ratio for k, v in raws.items()},
            {k: v * ratio for k, v in recipes.items()},
            vendor=vendor if vendor else None,
            description=description,
        )


make_armor(
    "gambeson",
    gambeson_weight,
    {},
    {
        "cotton cloth": gambeson_cloth,
        "cotton yarn": gambeson_string,
    },
    "AC +1; thickly-layered cloth armor with full sleeves, covering wearer to the waist",
    "armorer",
)

leatherarmor_layers = D(2)
leatherarmor_area = torso_area + (fullsleeve_area * 2)
leatherarmor_leather = leatherarmor_area * leatherarmor_layers
# 2 courses of string stitched around the perimeter of each layer, attaching it to the next
leatherarmor_string = 2 * leatherarmor_area / u.sqft * u.foot
leatherarmor_leather_weight = (
    (leatherarmor_leather / registry["boiled leather"].unit)
    * registry["boiled leather"].weight
).to(u.lb)
leatherarmor_string_weight = (
    (leatherarmor_string / registry["woolen yarn"].unit)
    * registry["woolen yarn"].weight
).to(u.lb)
leatherarmor_weight = leatherarmor_leather_weight + leatherarmor_string_weight

make_armor(
    "leather armor",
    leatherarmor_weight,
    {},
    {
        "boiled leather": leatherarmor_leather,
        "woolen yarn": leatherarmor_string,
    },
    "AC +2; stiffened cowhide armor with full sleeves, covering wearer to the waist",
    "armorer",
)


bodyarmor_plating_thickness = D(1.5) * u.mm
coatofplates_reinforced_area = D(0.8) * torso_area
coatofplates_plate_weight = (
    density["steel"] * coatofplates_reinforced_area * bodyarmor_plating_thickness
).to(u.lb)
coatofplates_weight = leatherarmor_weight + coatofplates_plate_weight

make_armor(
    "coat of plates",
    coatofplates_weight,
    {},
    {
        "boiled leather": leatherarmor_leather,
        "woolen yarn": leatherarmor_string,
        "steel": coatofplates_plate_weight,
    },
    "AC +3; as leather armor, but reinforced with metal plates between the leather layers",
    "armorer",
)


# this is a HUGE mail ring, way too big for realism, but if it's any smaller the damn mail armors come out heavier and more expensive than plate armor - so realism be damned
mailring_radius = Decimal(0.4) * u.inch
# this circumference == feet of wire per ring
mailring_circumference = (pi * mailring_radius * Decimal(2)).to(u.inch)
mailring_weight = (
    mailring_circumference / registry["wire"].unit * registry["wire"].weight
).to(u.oz)
# a strip is a single chain of mail rings
mailring_per_strip = D(1) * u.foot / mailring_radius
# I will ignore overlap of the rings
mailring_strip_area = D(1) * u.foot * (2 * mailring_radius)
mail_sale_unit = D(1) * u.sqft
mailring_per_mail = (mail_sale_unit / mailring_strip_area * mailring_per_strip).to(
    u.dimensionless
)
mail_sale_weight = (mailring_per_mail * mailring_weight).to(u.lb) / mail_sale_unit
wire_per_mail = mailring_per_mail * mailring_circumference / mail_sale_unit
# Recipe(
#    "mail",
#    "ironmongery",
#    mail_sale_weight,
#    {},
#    {"wire": mailring_per_mail * mailring_circumference},
#    unit=mail_sale_unit,
# )

# hauberkand haubergeon area ~= tube around the body from neck to knee, or to waist
hauberk_area = (
    body_proportions["torso"]["length"] + body_proportions["thigh"]["length"]
) * body_proportions["torso"]["girth"] + (halfsleeve_area * 2)

hauberk_weight = (hauberk_area * mail_sale_weight).to(u.lb)
make_armor(
    "hauberk",
    hauberk_weight,
    {},
    {
        "wire": wire_per_mail * hauberk_area,
        # "mail": hauberk_area,
    },
    "AC +5; chainmail with half sleeves, covering wearer to the knees",
    "armorer",
)

haubergeon_area = torso_area + (halfsleeve_area * 2)
haubergeon_weight = (haubergeon_area * mail_sale_weight).to(u.lb)
make_armor(
    "haubergeon",
    haubergeon_weight,
    {},
    {
        "wire": wire_per_mail * haubergeon_area,
        # "mail": haubergeon_area,
    },
    "AC +4; chainmail with half sleeves, covering wearer to the waist",
    "armorer",
)


plate_armor_description_tag = "part of half- and full-plate"

# TODO this is too simplistic a construction for the cuirass, which ought to be made of multiple plates riveted together; thus, current version uses too little metal and is too light
cuirass_area = torso_area
cuirass_strap_area = D(0.33) * u.sqft
# TODO make straps using a belt recipe function, since the straps would have included buckles
cuirass_strap_weight = (
    cuirass_strap_area / registry["leather"].unit * registry["leather"].weight
)
cuirass_plating_weight = (
    density["steel"] * cuirass_area * bodyarmor_plating_thickness
).to(u.lb)
cuirass_weight = cuirass_plating_weight + cuirass_strap_weight

make_armor(
    "cuirass",
    cuirass_weight,
    {},
    {
        "steel": cuirass_plating_weight,
        "leather": cuirass_strap_area,
    },
    description="; ".join(
        [
            "steel breastplate and backplate joined with leather straps",
            plate_armor_description_tag,
        ]
    ),
)

plate_armor_pieces = {
    "pauldron": dict(area=D(1) * u.sqft, description="steel armor for the shoulder"),
    "rerebrace": dict(
        area=halfsleeve_area, description="steel armor for the upper arm"
    ),
    "vambrace": dict(area=forearm_area, description="steel armor for the forearm"),
    "fauld": dict(
        area=thigh_area_around_both,
        description="steel armor skirt for the hips and groin, joined to the cuirass with leather straps",
    ),
    "chauss": dict(area=thigh_area_around_one, description="steel armor for the thigh"),
    "greave": dict(area=calf_area_around_one, description="steel armor for the calf"),
}

for name, info in plate_armor_pieces.items():
    area, description = info["area"], info["description"]
    weight = (density["steel"] * area * bodyarmor_plating_thickness).to(u.lb)
    ingredients = {"steel": weight}
    if name == "fauld":
        # TODO use belts; adjust number/size of belts away from same as cuirass
        # TODO pauldron needs rivets
        # TODO pauldron and fauld should be made in lamellar fashion
        # TODO this loop is an over abstraction - write individual recipes for each item
        strap_area, strap_weight = cuirass_strap_area, cuirass_strap_weight
        ingredients.update({"leather": strap_area})
        weight += strap_weight
    make_armor(
        name,
        weight,
        dict(),
        ingredients,
        "; ".join([description, plate_armor_description_tag]),
    )

# TODO OMGWTF fuck python! why is this variable still bound outside the plate_armor_pieces for loop?!?!?! WHY ON EARTH IS THAT NOT A BUG?!?!?!?!? lexical scoping, people, PLEASE! jesus christ
# print(description)

halfplate_components = {"cuirass": 1, "fauld": 1, "rerebrace": 2, "pauldron": 2}
fullplate_components = {
    "cuirass": 1,
    "fauld": 1,
    "rerebrace": 2,
    "pauldron": 2,
    "chauss": 2,
    "greave": 2,
    "vambrace": 2,
}

for size in ("medium", "small"):
    for name, components in [
        ("half-plate", halfplate_components),
        ("full-plate", fullplate_components),
    ]:
        if name == "half-plate":
            desc = "AC +6; steel armor covering the wearer from neck to thighs, with metal half-sleeves"
        else:
            desc = "AC +7; steel armor covering the wearer from neck to ankle, with full metal sleeves"
        if size == "small":
            components = {f"{k}, small": v for k, v in components.items()}
        weight = sum(
            [registry[piece].weight * count for piece, count in components.items()]
        )
        Recipe(
            name if size != "small" else f"{name}, small",
            "armor",
            weight,
            dict(),
            {k: v * u.item for k, v in components.items()},
            vendor="armorer",
            description=desc,
        )


glue_sale_weight = D(1) * u.lb
hide_collagen_yield = D(0.5) * u.dimensionless
bone_collagen_yield = D(0.3)
glue_bone_ratio = D(1) / D(2)
glue_hide_ratio = D(1) - glue_bone_ratio
quicklime_per_glue = D(0.1) * u.lb
hides_per_glue = (
    (glue_sale_weight / registry["rawhide"].weight)
    / hide_collagen_yield
    * registry["rawhide"].unit
) * glue_hide_ratio
bone_per_glue = (
    (glue_sale_weight / registry["cattle bone"].weight)
    / bone_collagen_yield
    * registry["cattle bone"].unit
) * glue_bone_ratio
glue_coverage = D(36) * u.sqft
Recipe(
    "hide glue",
    "glue",
    glue_sale_weight,
    {},
    {
        "quicklime": quicklime_per_glue,
        "rawhide": hides_per_glue,
        "cattle bone": bone_per_glue,
    },
    unit=glue_sale_weight,
    description=f"hard blob; heat 1:2 glue:water mixture to apply; covers {glue_coverage:~}",
    vendor="tanner",
)

gelatin_sale_weight = glue_sale_weight
gelatin_bone_ratio = D(4) / D(5)
gelatin_hide_ratio = D(1) - gelatin_bone_ratio
quicklime_per_gelatin = quicklime_per_glue
hides_per_gelatin = (
    (gelatin_sale_weight / registry["rawhide"].weight)
    / hide_collagen_yield
    * registry["rawhide"].unit
) * gelatin_hide_ratio
bone_per_gelatin = (
    (gelatin_sale_weight / registry["cattle bone"].weight)
    / bone_collagen_yield
    * registry["cattle bone"].unit
) * gelatin_bone_ratio
Recipe(
    "gelatin",
    "glue",
    gelatin_sale_weight,
    {},
    {
        "quicklime": quicklime_per_gelatin,
        "rawhide": hides_per_gelatin,
        "cattle bone": bone_per_gelatin,
    },
    unit=gelatin_sale_weight,
    description="hard blob; heat 1:3 gelatin:water mixture to use as binder",
    vendor="tanner",
)

bow_limb_length = D(2) * u.feet
bow_riser_length = D(2) * u.inch
bow_length = bow_riser_length + (2 * bow_limb_length)
# multiplier on bowstring length is for tying knots at ends of bow limbs
bowstring_length = D(1.1) * bow_length
bowstring_width = D(0.125) * u.inch
strands_per_bowstring = D(3)
hide_sqft_per_bowstring = (
    (bowstring_length * bowstring_width) * strands_per_bowstring
).to(u.sqft)
bowstring_weight = (
    (hide_sqft_per_bowstring / registry["rawhide"].unit) * registry["rawhide"].weight
).to(u.oz)
Recipe(
    "bowstring",
    "leathercraft",
    bowstring_weight,
    {},
    {"rawhide": hide_sqft_per_bowstring},
    vendor="bowyer",
)

bow_thickness = D(1) * u.inch
bow_limb_width = D(1.5) * u.inch
bow_limb_volume = bow_limb_length * bow_limb_width * bow_thickness
bow_limb_wood_fraction = D(0.7)
bow_limb_horn_fraction = D(1) - bow_limb_wood_fraction
bow_limb_wood = (density["timber"] * bow_limb_volume * bow_limb_wood_fraction).to(u.lb)
bow_limb_horn = (density["horn"] * bow_limb_volume * bow_limb_horn_fraction).to(u.lb)
bow_limb_hide = (bow_limb_width * bow_limb_length).to(u.sqft)
bow_layers = D(3)  # wood, horn, hide
bow_limb_glue = (
    (bow_limb_length * bow_limb_width * (bow_layers - 1)).to(u.sqft) / glue_coverage
) * registry["hide glue"].weight
bow_limb_weight = (
    bow_limb_wood
    + bow_limb_horn
    + (bow_limb_hide / registry["rawhide"].unit * registry["rawhide"].weight)
    + bow_limb_glue
).to(u.lb)
Recipe(
    "bow limb",
    "woodcraft",
    bow_limb_weight,
    {"timber": bow_limb_wood},
    {
        "cattle horn": bow_limb_horn,
        "rawhide": bow_limb_hide,
        "hide glue": bow_limb_glue,
    },
)

bow_riser_volume = cylinder_volume(bow_riser_length, D(0.125) * u.inch)
bow_riser_weight = (density["wrought iron"] * bow_riser_volume).to(u.lb)
Recipe(
    "bow riser",
    "ironmongery",
    bow_riser_weight,
    {},
    {"wrought iron": bow_riser_weight},
)

bow_weight = bow_riser_weight + bowstring_weight + (2 * bow_limb_weight)
Recipe(
    "bow",
    "weapons",
    bow_weight,
    {},
    {
        "bow riser": 1 * u.item,
        "bow limb": 2 * u.item,
        "bowstring": 1 * u.item,
    },
    vendor="bowyer",
    description=f"1d6 damage, {bow_length:~} long, range 15/30/45; comes with 1 bowstring",
)

# approximate as a metal cylinder plus four triangular spikes
shuriken_thickness = D(0.25) * u.inch
shuriken_body_radius = D(1) * u.inch
shuriken_body_volume = cylinder_volume(shuriken_thickness, shuriken_body_radius)
shuriken_spike_volume = triangular_prism_volume(
    D(1) * u.inch, D(1) * u.inch, shuriken_thickness
)
shuriken_total_volume = shuriken_body_volume + (4 * shuriken_spike_volume)
shuriken_weight = density["steel"] * shuriken_total_volume
Recipe(
    "shuriken",
    "weapons",
    shuriken_weight,
    {},
    {"steel": shuriken_weight},
    vendor="weaponsmith",
    description="1d2 damage, range 4/6/8; four-pointed throwing star, three inches wide",
)


# head modeled as a simple wedge
handaxe_head_length = D(6) * u.inch
handaxe_head_height = D(3) * u.inch
handaxe_head_width = D(1) * u.inch
handaxe_head_volume = triangular_prism_volume(
    handaxe_head_width, handaxe_head_length, handaxe_head_height
)
handaxe_head_weight = (density["steel"] * handaxe_head_volume).to(u.lb)

Recipe(
    "handaxe head",
    "weapons",
    handaxe_head_weight,
    {},
    {"steel": handaxe_head_weight},
)

handaxe_haft_length = mace_haft_length
handaxe_haft_radius = mace_haft_radius
assert 2 * handaxe_haft_radius > handaxe_head_width
handaxe_haft_volume = cylinder_volume(handaxe_haft_length, handaxe_haft_radius)
handaxe_haft_weight = (density["timber"] * handaxe_haft_volume).to(u.lb)
handaxe_weight = handaxe_haft_weight + handaxe_head_weight
Recipe(
    "handaxe",
    "weapons",
    handaxe_weight,
    {"timber": handaxe_haft_weight},
    {"handaxe head": 1 * u.item},
    vendor="weaponsmith",
    description=f"1d6+1 damage, haft {handaxe_haft_length:~} long",
)


battleaxe_head_length = D(1.25) * handaxe_head_length
battleaxe_head_width = handaxe_head_width
battleaxe_head_height = handaxe_head_height
battleaxe_head_volume = triangular_prism_volume(
    battleaxe_head_width, battleaxe_head_length, battleaxe_head_height
)
battleaxe_head_weight = (density["steel"] * battleaxe_head_volume).to(u.lb)

Recipe(
    "battleaxe head",
    "weapons",
    battleaxe_head_weight,
    {},
    {"steel": battleaxe_head_weight},
)

battleaxe_haft_length = D(3) * u.feet
battleaxe_haft_radius = mace_haft_radius
assert 2 * battleaxe_haft_radius > battleaxe_head_width
battleaxe_haft_volume = cylinder_volume(battleaxe_haft_length, battleaxe_haft_radius)
battleaxe_haft_weight = (density["timber"] * battleaxe_haft_volume).to(u.lb)
battleaxe_weight = battleaxe_haft_weight + 2 * battleaxe_head_weight
Recipe(
    "battleaxe",
    "weapons",
    battleaxe_weight,
    {"timber": battleaxe_haft_weight},
    {"battleaxe head": 1 * u.item},
    vendor="weaponsmith",
    description=f"1d8+1 damage, 2-handed; {battleaxe_haft_length:~} haft",
)

club_length = D(2) * u.feet
# multiplier accounts for carving away from a chunk of wood
club_volume = D(0.9) * cylinder_volume(club_length, D(1) * u.inch)
club_weight = (density["wood, oak"] * club_volume).to(u.lb)
Recipe(
    "club",
    "weapons",
    club_weight,
    {"wood, oak": club_weight},
    {},
    vendor="weaponsmith",
    description=f"1d6 damage; stout oaken cudgel, {club_length:~} long",
)

goedendag_head_length = D(4) * u.inch
goedendag_haft_radius = D(1) * u.inch
goedendag_head_volume = cone_volume(goedendag_head_length, goedendag_haft_radius)
goedendag_head_weight = (density["steel"] * goedendag_head_volume).to(u.lb)

Recipe(
    "goedendag head",
    "weapons",
    goedendag_head_weight,
    {},
    {"steel": goedendag_head_weight},
)

goedendag_haft_length = D(4) * u.feet
# more wood carved away from goedendag than club to keep weight manageable
goedendag_haft_volume = D(0.8) * cylinder_volume(
    goedendag_haft_length, goedendag_haft_radius
)
goedendag_haft_weight = (density["wood, oak"] * goedendag_haft_volume).to(u.lb)
goedendag_weight = goedendag_haft_weight + registry["goedendag head"].weight
Recipe(
    "goedendag",
    "weapons",
    goedendag_weight,
    {"wood, oak": goedendag_haft_weight},
    {"goedendag head": 1 * u.item},
    vendor="weaponsmith",
    description=f"2d4 damage, 2-handed; oaken bludgeon, {goedendag_haft_length:~} long, topped with large spearhead",
)

whip_handle_length = D(1) * u.feet
whip_handle_volume = cylinder_volume(whip_handle_length, D(0.75) * u.inch)
whip_handle_weight = (density["wood, oak"] * whip_handle_volume).to(u.lb)
whiplash_layers = D(2)
whiplash_length = D(4) * u.feet
whiplash_width = D(0.5) * u.inch
whiplash_area = whiplash_length * whiplash_width * whiplash_layers
whiplash_weight = (
    (whiplash_area / registry["rawhide"].unit) * registry["rawhide"].weight
).to(u.lb)
whip_weight = whip_handle_weight + whiplash_weight
Recipe(
    "whip",
    "weapons",
    whip_weight,
    {"wood, oak": whip_handle_weight},
    {"rawhide": whiplash_area},
    vendor="weaponsmith",
    description=f"1d4 damage; oak handle with {whiplash_length:} rawhide lash",
)

spikedwhip_barbs = (D(3) / u.foot) * whiplash_length
spikedwhip_barb_weight = D(0.125) * u.lb
spikedwhip_weight = whip_weight + (spikedwhip_barbs * spikedwhip_barb_weight).to(u.lb)
Recipe(
    "spiked whip",
    "weapons",
    spikedwhip_weight,
    {"wood, oak": whip_handle_weight},
    {
        "rawhide": whiplash_area,
        "steel": (spikedwhip_barbs * spikedwhip_barb_weight).to(u.lb),
    },
    vendor="weaponsmith",
    description=f"1d4+1 damage; whip with {spikedwhip_barbs.magnitude} steel barbs; exotic weapon; deals bleed on multiples of 9 damage instead of 11",
)

# TODO add pie tin
piecrust_flour = (density["flour"] * D(2) * u.cup).to(u.lb)
piecrust_salt = D(1) * u.teaspoon
piecrust_salt_weight = (density["salt"] * piecrust_salt).to(u.lb)
piecrust_eggs = D(1)
piecrust_vinegar = D(2) * u.teaspoon
piecrust_vinegar_weight = (density["vinegar"] * piecrust_vinegar).to(u.lb)
piecrust_butter = D(1.25) * u.cup
piecrust_butter_weight = (density["butter"] * piecrust_butter).to(u.lb)
piecrust_weight = (
    piecrust_flour
    + piecrust_salt_weight
    + (piecrust_eggs * registry["egg, chicken"].weight)
    + piecrust_vinegar_weight
    + piecrust_butter_weight
)
Recipe(
    "piecrust",
    "bread",  # TODO anything better?
    # "cakes" only thing I've found so far: no pie, tart, baking, pastry
    # there *is* "confectionery" ... not quite the same though
    piecrust_weight,
    {"salt": piecrust_salt_weight},
    {
        "flour": piecrust_flour,
        "egg, chicken": piecrust_eggs * u.item,
        "vinegar, in barrel": piecrust_vinegar,
        "butter": piecrust_butter_weight,
    },
    vendor="baker",
)

# insect's body is roughly 25% pigment by weight
cochineal_percent_dyestuff = D(0.25)
Recipe(
    "cochineal powder",
    "dyestuff",
    cochineal_percent_dyestuff * u.lb,
    {"cochineal": 1 * u.lb},
    {},
    unit=cochineal_percent_dyestuff * u.lb,
    description="ground cochineal insects harvested for dyeing",
)

# TODO needs container, like many other recipes
# TODO I made up all the numbers for these cochineal dyes - find a historical recipe
dye_sale_weight = 4 * u.oz
dye_sale_unit = 4 * u.floz
Recipe(
    "dye, crimson",
    "dyestuff",
    dye_sale_weight,
    {
        "alum": 1 * u.oz,
    },
    {
        "cochineal powder": 1 * u.gram,
    },
    unit=dye_sale_unit,
    vendor="dyer",
    description="cochineal-derived dye; usable on wool but not cotton",
)

Recipe(
    "dye, magenta",
    "dyestuff",
    dye_sale_weight,
    {},
    {
        "cochineal powder": 1 * u.gram,
    },
    unit=dye_sale_unit,
    vendor="dyer",
    description="cochineal-derived dye; usable on wool but not cotton",
)

# TODO how accurate is 20 lbs madder for 1 pound pigment
Recipe(
    "madder pigment",
    "dyestuff",
    1 * u.lb,
    {"madder": 20 * u.lb},
    {},
    unit=1 * u.lb,
    description="pigment ground from madder",
)

Recipe(
    "dye, pink",
    "dyestuff",
    dye_sale_weight,
    {"soda ash": 1 * u.oz, "alum": 1 * u.oz},
    {"madder pigment": 1 * u.gram},
    unit=dye_sale_unit,
    vendor="dyer",
    description="dusty pink dye",
)

# TODO how accurate is ratio of indigo plant to paste?
Recipe(
    "indigo paste",
    # https://thekindcraft.com/the-process-indigo-from-plant-to-paste/
    "dyestuff",
    1 * u.lb,
    {"indigo": 20 * u.lb},
    {"lye": 0.1 * u.lb},
    unit=1 * u.lb,
    description="potent dyestuff producing rich variations of blue and purple",
)

Recipe(
    "dye, indigo",
    "dyestuff",
    dye_sale_weight,
    {"soda ash": 1 * u.oz, "alum": 1 * u.oz},
    {"indigo paste": 1 * u.gram},
    unit=dye_sale_unit,
    vendor="dyer",
    description="deep purple dye",
)

# Jacoby D (2004). "Silk economics and cross-cultural artistic interaction: Byzantium, the Muslim world, and the Christian west". Dumbarton Oaks Papers. 58: 210, 197–240. doi:10.2307/3591386. JSTOR 3591386.
# David Jacoby remarks that "twelve thousand snails of Murex brandaris yield no more than 1.4 g of pure dye, enough to colour only the trim of a single garment."[15]
# so let's follow his lead; that seems a shit-ton of snails but Tyrian purple is famously labor intensive
# TODO how much does a murex weigh anyway
murex_weight = D(4) * u.oz
Recipe(
    "murex powder",
    # https://thekindcraft.com/the-process-indigo-from-plant-to-paste/
    "dyestuff",
    1 * u.gram,
    {"murex": 12_000 * murex_weight},
    {},
    unit=1 * u.gram,
    description="the only true royal purple dyestuff",
)

Recipe(
    "dye, royal purple",
    "dyestuff",
    dye_sale_weight,
    {},
    # no mordants because royal purple is colorfast
    {"murex powder": 1 * u.gram},
    unit=dye_sale_unit,
    vendor="dyer",
    description="gorgeous reddish-purple dye, fit for a king",
)

helmet_area = (
    D(0.75) * body_proportions["head"]["length"] * body_proportions["head"]["girth"]
)
helmet_weight = (
    helmet_area / registry["boiled leather"].unit * registry["boiled leather"].weight
).to(u.lb)
Recipe(
    "helmet, leather",
    "armor",
    helmet_weight,
    {},
    {"boiled leather": helmet_area},
    vendor="armorer",
    description="covers most of head; lessens chance of super criticals",
)

Recipe(
    "helmet, ogre jaw",
    "bonecarving",
    helmet_weight + D(2) * u.lb,
    {},
    {"helmet, leather": 1 * u.item},
    vendor="armorer",
    description="as leather helmet, with ogre jaw and tusks extending around lower half of face",
)

# a cylinder of cloth for the bourrelet, plus a percentage for the rest of the cloth including cornette
chaperon_area = (D(6) * u.inch * D(2) * u.feet) * D(1.8)
cotton_chaperon_weight = (
    chaperon_area / registry["cotton cloth"].unit * registry["cotton cloth"].weight
).to(u.lb)
Recipe(
    "chaperon, cotton",
    "hats",
    cotton_chaperon_weight,
    {},
    {"cotton cloth": chaperon_area},
    vendor="hatter",
    description="looped and draped bundle of cloth, wearable in many fashions",
)

wool_chaperon_weight = (
    chaperon_area / registry["woolen cloth"].unit * registry["woolen cloth"].weight
).to(u.lb)
Recipe(
    "chaperon, wool",
    "hats",
    wool_chaperon_weight,
    {},
    {"woolen cloth": chaperon_area},
    vendor="hatter",
    description=registry["chaperon, cotton"].description,
)

knitcap_layers = D(2)
knitcap_area = (
    D(0.5) * body_proportions["head"]["length"] * body_proportions["head"]["girth"]
) * knitcap_layers
knitcap_weight = (
    knitcap_area / registry["woolen cloth"].unit * registry["woolen cloth"].weight
).to(u.lb)
Recipe(
    "knit cap",
    "hats",
    knitcap_weight,
    {},
    {"woolen cloth": knitcap_area},
    vendor="hatter",
    description="thick woolen beanie-like hat",
)

# 4 foot chinstrap/string for hanging from neck, looped from one side to the other and back again for added security
strawhat_string = D(8) * u.feet
strawhat_string_weight = (strawhat_string / registry["cotton yarn"].unit) * registry[
    "cotton yarn"
].weight
# TODO total guess
strawhat_straw_weight = D(0.33) * u.lb
strawhat_weight = strawhat_straw_weight + strawhat_string_weight
Recipe(
    "straw hat",
    "straw hats",
    strawhat_weight,
    {},
    {
        "straw": strawhat_weight,
        "cotton yarn": strawhat_string,
    },
    vendor="hatter",
    description="wide-brimmed, with cotton strap to secure under chin or hang from neck",
)


hose_area = D(2) * (thigh_area_around_one + calf_area_around_one)
hose_weight = (
    hose_area / registry["cotton cloth"].unit * registry["cotton cloth"].weight
).to(u.lb)
Recipe(
    "hose",
    "hosiery",  # TODO hosiery
    hose_weight,
    {},
    {"cotton cloth": hose_area},
    vendor="tailor",
    description="unisex leggings covering groin, both legs, and both feet",
)


# TODO 4 leather or ceramic buttons
# TODO stitching
jerkin_area = torso_area
jerkin_weight = (
    jerkin_area / registry["leather"].unit * registry["leather"].weight
).to(u.lb)
Recipe(
    "jerkin",
    "clothing",  # NOT leathercraft
    jerkin_weight,
    {},
    {"leather": jerkin_area},
    vendor="tailor",
    description="sleeveless leather overshirt; commonly worn over a doublet or tunic",
)

# TODO stitching
tunic_area = torso_area + (2 * halfsleeve_area)
tunic_weight = (
    tunic_area / registry["cotton cloth"].unit * registry["cotton cloth"].weight
).to(u.lb)
Recipe(
    "tunic",
    "clothing",
    tunic_weight,
    {},
    {"cotton cloth": tunic_area},
    vendor="tailor",
    description="short-sleeved cotton shirt",
)

# TODO stitching
# on both sides of the body (the 2x factor), a sheet of cloth falling from neck to roughly the knees, but not wrapping all the way around (thus, half girth)
scapular_area = (
    D(2)
    * (body_proportions["torso"]["length"] + body_proportions["thigh"]["length"])
    * (D(0.5) * body_proportions["torso"]["girth"])
)
scapular_weight = (
    scapular_area / registry["cotton cloth"].unit * registry["cotton cloth"].weight
).to(u.lb)
Recipe(
    "scapular",
    "clothing",
    scapular_weight,
    {},
    {"cotton cloth": scapular_area},
    vendor="tailor",
    description="long cloth sheet with neck hole, draping down front and back of body; part of religious habit",
)

# TODO stitching
cassock_area = (
    (
        body_proportions["torso"]["length"]
        + body_proportions["thigh"]["length"]
        + body_proportions["thigh"]["length"]
    )
    * body_proportions["torso"]["girth"]
) + (2 * fullsleeve_area)
cassock_weight = (
    cassock_area / registry["cotton cloth"].unit * registry["cotton cloth"].weight
).to(u.lb)
Recipe(
    "cassock",
    "clothing",
    cassock_weight,
    {},
    {"cotton cloth": cassock_area},
    vendor="tailor",
    description="floor-length fitted robe with full sleeves; part of religious habit",
)

# TODO stitching
chemise_area = (
    (body_proportions["torso"]["length"] + body_proportions["thigh"]["length"])
    * body_proportions["torso"]["girth"]
) + (2 * fullsleeve_area)
chemise_weight = (
    chemise_area / registry["cotton cloth"].unit * registry["cotton cloth"].weight
).to(u.lb)
Recipe(
    "chemise",
    "clothing",
    chemise_weight,
    {},
    {"cotton cloth": chemise_area},
    vendor="tailor",
    description="unisex; thigh-length, long-sleeved, slightly baggy shirt worn as first or only layer",
)

bodice_area = (
    body_proportions["torso"]["length"] * body_proportions["torso"]["girth"]
) + (2 * quartersleeve_area)
bodice_weight = (
    bodice_area / registry["cotton cloth"].unit * registry["cotton cloth"].weight
).to(u.lb)
Recipe(
    "bodice",
    "clothing",
    bodice_weight,
    {},
    {"cotton cloth": bodice_area},
    vendor="tailor",
    description="female upper torso garment; not restrictive like a corset",
)

# given neck radius N, and desired height H, ruff uses a piece of cloth N+2 inches * 1.2H
# let's assume neck radius is 15 inches and ruff height is 3 inches
ruff_area = D(17) * u.inch * D(3.6) * u.inch
# TODO total guess
starch_per_ruff = D(0.1) * u.lb
ruff_weight = (
    ruff_area / registry["linen cloth"].unit * registry["linen cloth"].weight
).to(u.lb)
Recipe(
    "ruff",
    "clothing",
    ruff_weight,
    {},
    {"linen cloth": ruff_area, "starch, potato": starch_per_ruff},
    vendor="tailor",
    description="starched collar of folded linen",
)


leather_sole_weight = (
    foot_sole_area / registry["boiled leather"].unit * registry["boiled leather"].weight
).to(u.oz)
# 0.5 factor is for mid-calf height
lowboot_area = (
    body_proportions["foot"]["length"] * body_proportions["foot"]["girth"]
) + (D(0.5) * body_proportions["calf"]["length"] * body_proportions["calf"]["girth"])
lowboot_soft_weight = (
    lowboot_area / registry["leather"].unit * registry["leather"].weight
).to(u.oz) + leather_sole_weight
Recipe(
    "boot, soft",
    "boots and shoes",
    lowboot_soft_weight,
    {},
    {
        "leather": lowboot_area,
        "boiled leather": foot_sole_area,
    },
    vendor="cobbler",
    description="sold singly; unisex mid-calf boot",
)

highboot_area = (
    body_proportions["foot"]["length"] * body_proportions["foot"]["girth"]
) + (body_proportions["calf"]["length"] * body_proportions["calf"]["girth"])
highboot_soft_weight = (
    highboot_area / registry["leather"].unit * registry["leather"].weight
).to(u.oz) + leather_sole_weight
Recipe(
    "high boot, soft",
    "boots and shoes",
    highboot_soft_weight,
    {},
    {
        "leather": highboot_area,
        "boiled leather": foot_sole_area,
    },
    vendor="cobbler",
    description="sold singly; unisex knee-high boot",
)

lowboot_hard_weight = (
    lowboot_area / registry["boiled leather"].unit * registry["boiled leather"].weight
).to(u.oz) + leather_sole_weight
Recipe(
    "boot, hard",
    "boots and shoes",
    lowboot_hard_weight,
    {},
    {
        "boiled leather": lowboot_area + foot_sole_area,
    },
    vendor="cobbler",
    description=registry["boot, soft"].description + ", toughened for hard wearing",
)


highboot_hard_weight = (
    highboot_area / registry["boiled leather"].unit * registry["boiled leather"].weight
).to(u.oz) + leather_sole_weight
Recipe(
    "high boot, hard",
    "boots and shoes",
    highboot_hard_weight,
    {},
    {
        "boiled leather": highboot_area + foot_sole_area,
    },
    vendor="cobbler",
    description=registry["high boot, soft"].description
    + ", toughened for hard wearing",
)

blanket_length = 5 * u.ft
blanket_width = 3 * u.ft
blanket_area = blanket_length * blanket_width
blanket_weight = (
    blanket_area / registry["woolen cloth"].unit * registry["woolen cloth"].weight
).to(u.lb)
Recipe(
    "blanket",
    "blankets",
    blanket_weight,
    {},
    {"woolen cloth": blanket_area},
    vendor="weaver",
    description=f"made of cozy wool; {blanket_length} x {blanket_width}",
)

glove_area = hand_area
long_glove_area = hand_area + forearm_area
leatherglove_weight = (
    glove_area / registry["leather"].unit * registry["leather"].weight
).to(u.oz)
Recipe(
    "glove, leather",
    "gloves",
    leatherglove_weight,
    {},
    {"leather": glove_area},
    vendor="glover",
    description="sold singly",
)

long_leatherglove_weight = (
    long_glove_area / registry["leather"].unit * registry["leather"].weight
).to(u.oz)
Recipe(
    "long glove, leather",
    "gloves",
    long_leatherglove_weight,
    {},
    {"leather": long_glove_area},
    vendor="glover",
    description="sold singly; extends to the elbow",
)

stud_weight = D(2) * u.oz
Recipe(
    "steel stud",
    "ironmongery",
    stud_weight,
    {},
    {"steel": stud_weight},
)


cestus_area = long_glove_area
cestus_leather_weight = (
    cestus_area / registry["boiled leather"].unit * registry["boiled leather"].weight
).to(u.oz)
studs_for_cestus = 12
cestus_weight = (cestus_leather_weight + (studs_for_cestus * stud_weight)).to(u.lb)
Recipe(
    "cestus",
    "weapons",
    cestus_weight,
    {},
    {
        "boiled leather": cestus_area,
        "steel stud": studs_for_cestus * u.item,
    },
    vendor="weaponsmith",
    description="elbow-length stiffened leather glove with metal studs; adds +1 pummeling damage",
)


woolglove_weight = (
    glove_area / registry["woolen cloth"].unit * registry["woolen cloth"].weight
).to(u.oz)
Recipe(
    "glove, wool",
    "gloves",
    woolglove_weight,
    {},
    {"woolen cloth": glove_area},
    vendor="glover",
    description="sold singly",
)


long_woolglove_weight = (
    long_glove_area / registry["woolen cloth"].unit * registry["woolen cloth"].weight
).to(u.oz)
Recipe(
    "long glove, wool",
    "gloves",
    long_woolglove_weight,
    {},
    {"woolen cloth": long_glove_area},
    vendor="glover",
    description="sold singly; extends to the elbow",
)
# one industry website says it costs $75,000 to build a motel; my local motel costs $75/night
# let's use the same ratio to determine the price of one night at an inn
inn_construction_service_ratio = D(0.001)
Recipe(
    "private room",
    "foodstuffs",  # TODO this is terrible but nothing better...
    0 * u.lb,
    {},
    {"half-timbered house, one story": inn_construction_service_ratio * u.item},
    vendor="innkeeper",
    unit=1 * u.night,
    description="",
)

Recipe(
    "spot in common room",
    "foodstuffs",  # TODO this is terrible but nothing better...
    0 * u.lb,
    {},
    {
        "half-timbered house, one story": inn_construction_service_ratio
        / D(1.9)
        * u.item
    },
    vendor="innkeeper",
    unit=1 * u.night,
    description="",
)

tilled_land_sale_unit = D(1) * u.acre
cereal_crop_per_acre = D(1) * u.ton / u.acre
Recipe(
    "tilled land",
    "cereals",
    0 * u.lb,
    {"cereals": cereal_crop_per_acre * tilled_land_sale_unit},
    {},
    vendor="surveyor",
    unit=tilled_land_sale_unit,
    description="previously tilled and now lying fallow; 10% chance to be in same hex as market town, 30% chance in 1st ring of 6-mile hexes, and 60% chance in 2nd ring of surrounding 6-mile hexes",
)

Recipe(
    "dice, wood",
    "woodcarving",
    D(0.25) * u.oz,
    {"timber": D(0.25) * u.oz},
    {},
    unit=2 * u.item,
    difficulty=2,
    vendor="carver",
    description="pair of six-sided dice",
)

Recipe(
    "dice, bone",
    "bonecarving",
    D(0.25) * u.oz,
    {},
    {"cattle bone": D(0.25) * u.oz},
    unit=2 * u.item,
    difficulty=2,
    vendor="carver",
    description="pair of six-sided dice",
)

Recipe(
    "dice, ivory",
    "ivorycarving",
    D(0.25) * u.oz,
    {"ivory": D(0.25) * u.oz},
    {},
    unit=2 * u.item,
    difficulty=2,
    vendor="carver",
    description="pair of six-sided dice",
)

awl_timber_weight = awl_steel_weight = D(4) * u.oz
Recipe(
    "awl",
    "tools",
    awl_timber_weight + awl_steel_weight,
    {"timber": awl_timber_weight},
    {"steel": awl_steel_weight},
    vendor="blacksmith",
    description="wooden-handled metal tool for marking and piercing wood or leather",
)

mallet_weight = D(2) * u.lb
Recipe(
    "mallet",
    "wooden tools",
    mallet_weight,
    {"wood, oak": mallet_weight},
    {},
    vendor="carver",
    description="oaken hammer for gently pounding nails, chisels, and more",
)


Recipe(
    "needle, bone",
    "bonecarving",
    D(0.1) * u.oz,
    {},
    {"cattle bone": D(0.1) * u.oz},
    difficulty=2,
    vendor="carver",
    description="used for sewing cloth and leather; surgery requires a metal needle instead",
)


Recipe(
    "anvil",
    "tools",
    D(200) * u.lb,
    {},
    {"wrought iron": D(200) * u.lb},
    vendor="blacksmith",
)


Recipe(
    "stirring rod, glass",
    "tools",
    D(4) * u.oz,
    {},
    {"lead glass": D(4) * u.oz},
    vendor="glassblower",
    description="made of lead glass; used for medicine, alchemy, and more",
)


crystal_ball_weight = D(2) * u.lb
Recipe(
    "crystal ball",
    "tools",
    crystal_ball_weight,
    {},
    {
        "lead glass": crystal_ball_weight,
    },
    difficulty=3,
    vendor="glassblower",
    description="made of lead glass; used in alchemy and fortune-telling",
)

spoon_weight = fork_weight = D(1) * u.oz
knife_weight = D(2) * u.oz
Recipe(
    "fork, copper",
    "coppersmithing",
    fork_weight,
    {},
    {"raw copper": fork_weight},
    vendor="redsmith",
)
Recipe(
    "spoon, copper",
    "coppersmithing",
    spoon_weight,
    {},
    {"raw copper": spoon_weight},
    vendor="redsmith",
)
Recipe(
    "knife, copper",
    "coppersmithing",
    knife_weight,
    {},
    {"raw copper": knife_weight},
    vendor="redsmith",
)


def no_vendor():
    return {k: v for k, v in registry.items() if not v.vendor}


def list_all(town="Pearl Island"):
    t = towns[town]
    for name, recipe in registry.items():
        print(name)
        print(f"{recipe.display_price(t)}")
        if recipe.description:
            print(recipe.description)
        print()


def by_vendor(town="Pearl Island"):
    t = towns[town]
    for v in sorted(list(vendors)):
        l = len(v)
        print("-" * l)
        print(v.upper())
        print("-" * l)
        print()
        rs = {name: recipe for name, recipe in registry.items() if recipe.vendor == v}
        for name, recipe in rs.items():
            print(name)
            print(f"{recipe.display_price(t)}")
            if recipe.description:
                print(recipe.description)
            print()
        print()
    for name, recipe in no_vendor().items():
        print(name)
        print(f"{recipe.display_price(t)}")
        if recipe.description:
            print(recipe.description)
        print()


def dbify_tradegoods(db, registry):
    with Progress() as progress:
        with db.transaction as cur:
            numtowns = len(towns)
            numgoods = len(registry)

            recipes = []
            for good, recipe in registry.items():
                jr = recipe.to_json()
                recipes.append(dict(name=good, recipe=jr))
            cur.insert("tradegoods", *recipes)

            town_task = progress.add_task("[red]Generating prices...", total=numtowns)
            for t in towns:
                tradegood_task = progress.add_task(f"[blue]at {t}", total=numgoods)
                prices = []
                logging.debug(f"generating prices at {t}")
                for good, recipe in registry.items():
                    price = to_copper_pieces(recipe.chunked_price(towns[t]).values())
                    prices.append(dict(name=good, town=t, price=(str(price))))
                    progress.update(tradegood_task, advance=1)
                cur.insert("prices", *prices)
                logging.debug(f"inserted prices at {t}")
                progress.update(town_task, advance=1)


def main():
    db = sqlyte.db("foo.db", sqlyte.Model("tradegood_model", **tradegood_model))
    dbify_tradegoods(db, registry)


if __name__ == "__main__":
    main()

# TODO things which are raw materials - how to put them on pricing table w/o overcharging  for them by making them go through a recipe?
# for instance, 'grapes' are used as a raw material in wine production...
# ...  but for sale OF GRAPES THEMSELVES AS FOOD, what warrants making them more expensive by requiring a recipe?
# why not use the raw material price directly?
# this also applies to pig iron, iron (ore), gold, all the types of building stone, and more!
# it could also take down the price of cattle, sheep, etc no?
# currently, if I don't have a recipe I can't put them on the price table AS THEIR OWN ITEM
# TODO do I need a subclass of recipe, Raw, which doesn't require a governor and is sold as-is?
# TODO what is the dividing line between grapes (sold as a new Raw) and, say, cattle (which currently have to go through at least one recipe to be sold?)

# TODO one issue with Raw proposal is that it doesn't account for fact taht some 'Raws' are derived from others and prices will be wrong if we go straight to using Raw price
# for instance, 'dried fish' is a raw material, and very cheap; fresh fish is much more expensive
# so 'dried fish' shouldn't be a Raw, lest dried fish somehow cost much less per unit than fresh even though it's been processed, etc.


# https://en.wikipedia.org/wiki/Bone_char
# used in sugar production as a filtering agent


# def d(x): return Decimal(x)
# gallons olive oil produced per acre
# Decimal('105.6691999999999964643393469')
# 200 olive trees/acre * 4 lbs of oil annually/tree * 1 L oil/2 lbs * 0.264173... gal/L
# d(200) * d(4) / d(2) * d(0.264173)

# area of 2.2222222222 mile diameter hexagon, in sq mi
# Decimal('4.276583127718347711819777428')
# >>> import math as m
# >>> d(m.sqrt(d(3))) * d(2.2222) * d(2.2222) / d(2)

# earthenware ceramic goods
# glazed and unglazed

# candles: The wicks need to be mordanted with salts to make the wick bend into the flame, slowing down the burn time so that the wax is consumed as the candle burns and the flame is not extinguished in the melted wax.   A solution of 1 litre of water, 1/4 cup. coarse salt or other nonadditive salts, 1/2 cup of borax is used to prepare the wicks.  You can mordant your wicks in a skein or you can cut them to size and then mordant them individually.  Simmer the wicks for one hour in the solution.  Cool in the solution and then remove and allow to dry completely.

# TODO oil the hafts of weapons, or the whole bodies of wooden ones, so they stay durable
# TODO differentiate woods used for buildings, weapons, barrels, etc. (like the oak club)
# TODO turn attar of roses into a 'rose oil' recipe for use in e.g. snuff, perfume, rose soap
# fuller's teasel / card https://en.wikipedia.org/wiki/Dipsacus#Cultivation_and_uses
# TODO clothing: buttons, stitching
# boots: laces, stitching

# awl, needle, punch, short hammer, mallet, saw, vice or clamp, ruler, anvil, bellows, nails, (leather) apron, loupe, calipers, punty / blowpipe, tongs, fuller's earth, putty knife, adze / scraper, stirring rod, flask, vial, shears, loom, crystal ball, bowl, plate, cooking / work knife, cutting board, ladle, spoon fork eating knife, spinning wheel, mortar and pestle, alembic, trowel, shovel, towel, bathrobe, wine glass, pint glass, shot glass, last (foot, hand, head), oar, rowboat, coracle, remaining weapons, chair, cushion, embroidered cushion, bench, tattoo, quill, paper, parchment, ink, colored class, pamphlet, metal type, belt, backpack, coin pouch, scabbard, bit, bridle, saddlebags,

## a nitrate (niter is KNO3) + copper sulfate -> copper nitrate
## decomposition: copper nitrate Cu(NO3)2 + H2O -> copper oxide + 2 HNO3 (nitric acid)
## 2 KNO_3 + CuS + H_2O ⟶  CuO + 2 HNO_3 + S + 2 K
## I can skip the sulfur because I have elemental copper available
## 2 KNO_3 + Cu + H_2O ⟶  CuO + 2 HNO_3 + 2 K
# density["aqua fortis"] = D(1.5129) * u.gram / u.cucm
# niter_molar_weight = D(101.1) * u.gram
# copper_molar_weight = D(63.546) * u.gram
## cupricoxide_molar_weight = D(79.545) * u.gram
# aquafortis_molar_weight = D(63.012) * u.gram
# aquafortis_sale_unit = D(1) * u.pint
# aquafortis_sale_weight = (density["aqua fortis"] * aquafortis_sale_unit).to(u.lb)
# aquafortis_sale_concentration = D(0.68)
# aquafortis_just_acid_weight = aquafortis_sale_concentration * aquafortis_sale_weight
# aquafortis_sale_moles = aquafortis_just_acid_weight / aquafortis_molar_weight
# print(aquafortis_sale_moles)
## formula above produces 2 moles acid per 2 moles niter and 1 mole copper
# niter_for_aquafortis = (aquafortis_sale_moles * niter_molar_weight).to(u.lb)
# copper_for_aquafortis = ((aquafortis_sale_moles * copper_molar_weight) / D(2)).to(u.lb)
# Recipe(
#    "aqua fortis",
#    "alchemy",
#    aquafortis_sale_weight,
#    {"niter": niter_for_aquafortis},
#    {"raw copper": copper_for_aquafortis},
#    vendor="alchemist",
#    # difficulty b/c this method takes multiple days, especially the precipitation
#    # https://www.youtube.com/watch?v=hmB5x0LYfSE
#    difficulty=1.5,
#    unit=aquafortis_sale_unit,
#    # TODO add container
#    description=f"nitric acid, {aquafortis_sale_concentration*100:.2}% concentration by weight",
# )
#
## 2 KNO_3 + 2 S + 2 H_2O ⟶ 2 H_2SO_4 + 2 K + N_2
## niter + sulfur + water -> sulfuric acid + potassium + nitrogen gas
# density["oil of vitriol"] = D(1.8302) * u.gram / u.cucm
# oilvitriol_molar_weight = D(98.07) * u.gram
# sulfur_molar_weight = D(32.06) * u.gram
# oilvitriol_sale_unit = D(1) * u.pint
# oilvitriol_sale_weight = (density["oil of vitriol"] * oilvitriol_sale_unit).to(u.lb)
# oilvitriol_sale_concentration = D(0.65)
# print("ov weight", oilvitriol_sale_weight)
# print("ov concentration", oilvitriol_sale_concentration)
# oilvitriol_just_acid_weight = oilvitriol_sale_concentration * oilvitriol_sale_weight
# print("ov just acid weight", oilvitriol_just_acid_weight)
# oilvitriol_sale_moles = oilvitriol_just_acid_weight / oilvitriol_molar_weight
# print("ov moles", oilvitriol_sale_moles)
# niter_for_oilvitriol = (oilvitriol_sale_moles * niter_molar_weight).to(u.lb)
# sulfur_for_oilvitriol = (oilvitriol_sale_moles * sulfur_molar_weight).to(u.lb)
# Recipe(
#    "oil of vitriol",
#    "vitriol",
#    # TODO does vitriol ref refer to oil of vitriol, or to the vitriol minerals?! that determines whether to use vitriol or alchemy as the reference here
#    oilvitriol_sale_weight,
#    {
#        "sulfur": sulfur_for_oilvitriol,
#        "niter": niter_for_oilvitriol,
#    },
#    {},
#    vendor="alchemist",
#    unit=oilvitriol_sale_unit,
#    # TODO add container
#    description=f"sulfuric acid, {oilvitriol_sale_concentration*100:.2}% concentration by weight",
# )
#
## 3 NaCl + 2 H_2SO_4 + H_2O ⟶ 3 HCl + 3 NaOH + 2 S + 3 O_2
## table salt + sulfuric acid + water -> hydrochloric acid + sulfur + oxygen gas
# density["spirit of salt"] = D(1.169) * u.gram / u.cucm
# spiritsalt_molar_weight = D(36.46) * u.gram
# salt_molar_weight = D(58.44) * u.gram
# spiritsalt_sale_unit = D(1) * u.pint
# spiritsalt_sale_weight = (density["spirit of salt"] * spiritsalt_sale_unit).to(u.lb)
# spiritsalt_sale_concentration = D(0.34)
# spiritsalt_just_acid_weight = spiritsalt_sale_concentration * spiritsalt_sale_weight
# spiritsalt_sale_moles = spiritsalt_just_acid_weight / spiritsalt_molar_weight
# salt_for_spiritsalt = (spiritsalt_sale_moles * salt_molar_weight).to(u.lb)
## TODO this comes out wrong -- 19 pints of oil of vitriol? no way
# oilvitriol_for_spiritsalt = (
#    ((spiritsalt_sale_moles * oilvitriol_sale_moles) * D(2) / D(3))
#    * oilvitriol_sale_unit
# ).to(u.pint)
# Recipe(
#    "spirit of salt",
#    "alchemy",
#    spiritsalt_sale_weight,
#    {
#        "salt": salt_for_spiritsalt,
#    },
#    {"oil of vitriol": oilvitriol_for_spiritsalt},
#    vendor="alchemist",
#    unit=spiritsalt_sale_unit,
#    # TODO add container
#    description=f"hydrochloric acid, {spiritsalt_sale_concentration*100:.2}% concentration by weight",
# )

## TODO convert the 3:1 ratio to amounts in pints of spirit of salt and oil vitriol
# spiritsalt_for_aquaregia = 3  # moles
# oilvitriol_for_aquaregia = 1  # moles
# density["aqua regia"] = D(1.11) * u.gram / u.cucm
# aquaregia_sale_unit = D(1) * u.pint
# aquaregia_sale_weight = D(1) * u.pint
# Recipe(
#    "aqua regia",
#    "alchemy",
#    aquaregia_sale_weight,
#    {},
#    {
#        #        "oil of vitriol": oilvitriol_for_aquaregia,
#        #        "spirit of salt": spiritsalt_for_aquaregia,
#    },
#    vendor="alchemist",
#    unit=aquaregia_sale_unit,
#    # TODO add container
#    description="orange mixture of acids which dissolves noble metals; used in alchemy, glassmaking, and lithography",
# )
