from decimal import getcontext, Decimal
from math import ceil, floor
from references import u, Q
from towns import towns

# set up the Decimal environment
getcontext().prec = 6

D = Decimal

pi = Decimal(1) * u.pi


registry = dict()


density = {
    k: (Decimal(v.magnitude) * v.units).to(u.lb / u.cuft)
    for k, v in {
        "cast iron": 454.8 * u.lb / u.cuft,
        "wrought iron": 483 * u.lb / u.cuft,
        "steel": 489 * u.lb / u.cuft,
        "molasses": 88.1233091 * u.lb / u.cuft,
        "timber": 40 * u.lb / u.cuft,
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
    }.items()
}
def cylinder_volume(height, radius):
    # explicit to(u.cuft) call required to reduce representation from explicit pi to value thereof;
    # otherwise, printed value misleadingly shows "xxx ft ** 3 * pi" which looks like xxx ^ 3pi
    return (pi * height.to(u.ft) * radius.to(u.ft) * radius.to(u.ft)).to(u.cuft)


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
# TODO: Recipe subclasses for categories of goods, such as Weapon and Armor, which have special details (armor class, damage dice, break chance, etc)
# TODO saves_as field, which controls how item saves against damage (as wood, paper, leather, metal, glass, et -- even if the item not primarily made of that material)
# TODO container (as a separate field so that its weight can be ignored when doing ingredient math, but added in when calculating price)
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
        unit=None,
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
        self.container = container
        self.unit = unit
        if self.unit:
            self.unit = Decimal(unit.magnitude) * unit.units
        self._register()

    def _register(self):
        global registry
        if self.name in registry:
            raise ValueError(f"{self.name} is already a recipe")
        registry[self.name] = self

    def _ingredient_costs(self, towninfo):
        price_raws = {}
        for raw, q in self.raws.items():
            # unit employed in a recipe not always the base unit used in references.py
            # e.g. stone produced in oz, but usually recipes call for lbs
            newunit = u.cp / q.units
            final = towninfo["price"][raw].to(newunit) * q.magnitude
            price_raws[raw] = final
        price_recipes = {}
        for recipe, q in self.recipes.items():
            newunit = u.cp / q.units
            # TODO avoid costs of recursion
            # can I memoize while keeping while keeping this a method, or need to pull out into a function?
            final = registry[recipe].price(towninfo).to(newunit) * q.magnitude
            price_recipes[recipe] = final
        return price_raws, price_recipes

    def _denominator(self):
        return self.unit if self.unit else self.weight

    def price(self, towninfo):
        global registry
        ra, re = self._ingredient_costs(towninfo)
        # with necessary quantities of ingredients now priced in copper pieces, divide all units by themselves, making them dimensionless and summable (otherwise we may try adding cp / head and cp / pound, for instance)
        ra = {k: v / v.units for k, v in ra.items()}
        re = {k: v / v.units for k, v in re.items()}
        baseprice = sum(ra.values()) + sum(re.values())
        refs = towninfo["references"][self.governor]
        serviceprice = (baseprice / refs) * self.difficulty
        final = baseprice + serviceprice
        # convert dimensionless final back to cp / something
        return (final.magnitude * u.cp) / self._denominator()

    def chunked_price(self, towninfo):
        p = self.price(towninfo)
        result = {}
        justmoney = p * self._denominator()
        ingold = justmoney.to(u.gp)
        roundgold = floor(ingold.magnitude) * u.gp
        if roundgold.magnitude > 0:
            result["gp"] = roundgold
            # print(
            #    f"subtracting {roundgold} from {justmoney} makes {justmoney - roundgold}"
            # )
            justmoney = justmoney - roundgold
        insilver = justmoney.to(u.sp)
        roundsilver = floor(insilver.magnitude) * u.sp
        if roundsilver.magnitude > 0:
            result["sp"] = roundsilver
            # print(
            #    f"subtracting {roundsilver} from {justmoney} makes {justmoney - roundsilver}"
            # )
            justmoney = justmoney - roundsilver
        result["cp"] = justmoney
        result["denominator"] = self._denominator()
        return result

    def display_price(self, towninfo):
        p = self.chunked_price(towninfo)
        result = []
        for thing in ("gp", "sp", "cp"):
            if thing not in p:
                continue
            else:
                if thing == "cp":
                    val = round(p[thing])
                    result.append(f"{val:~}")
                else:
                    result.append(f"{p[thing]:~}")
        return ", ".join(result) + f" / {self._denominator():~}"


Recipe(
    "smelting fuel",
    "smelting",
    0.75 * u.lb,
    dict(coal=0.5 * u.lb, limestone=0.25 * u.lb),
    description="generic supplies required to smelt 1 lb metal",
)

Recipe(
    "iron ore",
    "iron",
    1 * u.lb,
    dict(iron=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="separated from waste rock and impurities",
)

Recipe(
    "pig iron",
    "ironmongery",
    1 * u.lb,
    {},
    {"iron ore": 1 * u.lb, "smelting fuel": 0.75 * u.lb},
    description="weak, brittle purified iron",
)

Recipe(
    "cast iron",
    "ironmongery",
    1 * u.lb,
    {},
    {
        "smelting fuel": 0.75 * u.lb,
        "manganese ore": 0.06 * u.lb,
        "nickel ore": 0.01 * u.lb,
        "pig iron": 0.93 * u.lb,
    },
    # description="volume of metal equalling 1x1x3.8 in.",
)

Recipe(
    "wrought iron",
    "ironmongery",
    1 * u.lb,
    {},
    {"pig iron": 1 * u.lb, "smelting fuel": 0.75 * u.lb},
    # description="ingot, 1x1x3.57 in.",
)

Recipe(
    "nickel ore",
    "nickel",
    1 * u.lb,
    dict(nickel=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="separated from waste rock and impurities",
)

Recipe(
    "manganese ore",
    "manganese",
    1 * u.lb,
    dict(manganese=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="separated from waste rock and impurities",
)

Recipe(
    "copper ore",
    "copper",
    1 * u.lb,
    dict(copper=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="separated from waste rock and impurities",
    # description="ingot, 2x1.065x1.45 in.",
)

Recipe(
    "tin ore",
    "tin",
    1 * u.lb,
    dict(tin=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="separated from waste rock and impurities",
)


Recipe(
    "gold ore",
    "gold",
    1 * u.lb,
    dict(gold=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="separated from waste rock and impurities",
    # description="ingot, 1x1x1.435 in.",
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
    "smelting",
    1 * u.lb,
    {},
    {
        "smelting fuel": 0.75 * u.lb,
        "tin ore": tin_in_lb_pewter,
        "copper ore": copper_in_lb_pewter,
    },
    # description="ingot, 1x1x3.65 in.",
)

Recipe(
    "steel",
    "ironmongery",
    1 * u.lb,
    {},
    {"pig iron": 1 * u.lb, "smelting fuel": 0.75 * u.lb},
    # description="ingot, 1x1x3.5 in.",
)

Recipe("iron filings", "ironmongery", 1 * u.lb, {}, {"wrought iron": 1 * u.lb})

# filings used following the methods described in Subterraneal Treasures
Recipe(
    "lead ore",
    "leadsmelting",
    1 * u.lb,
    {"lead": 1 * u.lb},
    {"iron filings": 0.25 * u.lb, "smelting fuel": 0.75 * u.lb},
    # description="ingot, 1.084x1.5x1.5 in.",
)

Recipe(
    "zinc ore",
    "smelting",
    1 * u.lb,
    {"zinc": 1 * u.lb},
    {"smelting fuel": 0.75 * u.lb},
)

Recipe(
    "silver ore",
    "smelting",
    1 * u.lb,
    {"silver": 1 * u.lb},
    {"smelting fuel": 0.75 * u.lb},
    # description="ingot, 1.5x1.5x1.175 in.",
)

copper_in_lb_bronze = Decimal(0.88) * u.lb
tin_in_lb_bronze = Decimal(0.12) * u.lb
volume_bronze_ingot = (tin_in_lb_bronze / density["tin"]) + (
    copper_in_lb_bronze / density["copper"]
)
density["bronze"] = 1 * u.lb / volume_bronze_ingot
Recipe(
    "bronze",
    "smelting",
    1 * u.lb,
    {},
    {
        "tin ore": tin_in_lb_bronze,
        "copper ore": copper_in_lb_bronze,
        "smelting fuel": 0.75 * u.lb,
    },
    # description="ingot, 1.125x1.675x1.675 in.",
)

copper_in_lb_brass = Decimal(0.55) * u.lb
zinc_in_lb_brass = Decimal(0.45) * u.lb
volume_brass_ingot = (zinc_in_lb_brass / density["zinc"]) + (
    copper_in_lb_brass / density["copper"]
)
density["brass"] = 1 * u.lb / volume_brass_ingot
Recipe(
    "brass",
    "smelting",
    1 * u.lb,
    {},
    {
        "zinc ore": zinc_in_lb_brass,
        "copper ore": copper_in_lb_brass,
        "smelting fuel": 0.75 * u.lb,
    },
    #    description="ingot, 1.77x2.05x0.95 in.",
)


copper_in_lb_bellmetal = Decimal(0.78) * u.lb
tin_in_lb_bellmetal = Decimal(0.22) * u.lb
volume_bellmetal_ingot = (tin_in_lb_bellmetal / density["tin"]) + (
    copper_in_lb_bellmetal / density["copper"]
)
density["bell metal"] = 1 * u.lb / volume_bellmetal_ingot
Recipe(
    "bell metal",
    "smelting",
    1 * u.lb,
    {},
    {
        "tin ore": tin_in_lb_bellmetal,
        "copper ore": copper_in_lb_bellmetal,
        "smelting fuel": 0.75 * u.lb,
    },
    #    description="ingot, 1.2x1.35x2 in.",
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
    "smelting",
    1 * u.lb,
    {},
    {
        "tin ore": tin_in_lb_sterlingsilver,
        "copper ore": copper_in_lb_sterlingsilver,
        "silver ore": silver_in_lb_sterlingsilver,
        "smelting fuel": 0.75 * u.lb,
    },
    #    description="ingot, 1.5x1.5x1.185 in.",
)

hilt_volume = (Decimal(2) * u.inch * Decimal(2) * u.inch * Decimal(5) * u.inch).to(
    "cuft"
)
hilt_weight = hilt_volume * density["timber"]
Recipe(
    "sword hilt",
    "carpentry",
    hilt_weight,
    {"timber": hilt_weight},
    unit=1 * u.item,
    description="wooden tube, carved from 2x2x5 in. block",
)

pommel_weight = Decimal(0.25) * u.lb
Recipe(
    "pommel",
    "metalsmithing",
    pommel_weight,
    {},
    {"steel": pommel_weight},
    unit=1 * u.item,
    description="metal knob which holds hilt and blade together",
)

# a 1-foot (unit) blade is 2 inches wide, 1/6 inch thick, 1 foot long
unit_blade_volume = (
    Decimal(2) * u.inch * Decimal(1) / Decimal(6) * u.inch * Decimal(1) * u.ft
).to(u.cuft)
unit_blade_weight = unit_blade_volume * density["steel"]
Recipe(
    "blade",
    "metalsmithing",
    unit_blade_weight,
    {},
    {"steel": unit_blade_weight},
    unit=1 * u.item,
    description="price for a one-foot steel blade",
)

dagger_length = Decimal(1) * u.ft
dagger_blade_needed = dagger_length / u.ft
dagger_weight = hilt_weight + pommel_weight + (dagger_blade_needed * unit_blade_weight)
Recipe(
    "dagger",
    "metalsmithing",
    dagger_weight,
    {},
    {
        "blade": dagger_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d4 damage, melee or thrown 2/3/4; {dagger_length}-foot blade",
    unit=1 * u.item,
    vendor="weaponsmith",
)

shortsword_length = Decimal(2) * u.ft
shortsword_blade_needed = shortsword_length / u.ft
shortsword_weight = (
    hilt_weight + pommel_weight + (shortsword_blade_needed * unit_blade_weight)
)
Recipe(
    "shortsword",
    "metalsmithing",
    shortsword_weight,
    {},
    {
        "blade": shortsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d6 damage; {shortsword_length}-foot blade",
    unit=1 * u.item,
    vendor="weaponsmith",
)

longsword_length = Decimal(3.5) * u.ft
longsword_blade_needed = longsword_length / u.ft
longsword_weight = (
    hilt_weight + pommel_weight + (longsword_blade_needed * unit_blade_weight)
)
Recipe(
    "longsword",
    "metalsmithing",
    longsword_weight,
    {},
    {
        "blade": longsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d8 damage; {longsword_length}-foot blade",
    unit=1 * u.item,
    vendor="weaponsmith",
)

greatsword_length = Decimal(4.5) * u.ft
greatsword_blade_needed = greatsword_length / u.ft
greatsword_weight = (
    hilt_weight + pommel_weight + (greatsword_blade_needed * unit_blade_weight)
)
Recipe(
    "greatsword",
    "metalsmithing",
    greatsword_weight,
    {},
    {
        "blade": greatsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d10 damage; {greatsword_length}-foot blade",
    unit=1 * u.item,
    vendor="weaponsmith",
)

Recipe(
    "flour",
    "flour",
    # TODO shouldn't this be made from husked cereals, which are derived from base recipe cereals? well no, it should be derived from wheat ... to which i have yet to give a prduction number based on cereals
    1 * u.lb,
    {"flour": 1 * u.lb},
    {},
    vendor="miller",
    description="ground from cereals",
)

Recipe(
    "bread",
    "bread",
    1 * u.lb,
    {"salt": 0.05 * u.lb},
    {"flour": 0.7 * u.lb},
    vendor="baker",
)

Recipe(
    "quicklime",
    "pottery",
    1 * u.lb,
    {"limestone": 1 * u.lb},
    {"smelting fuel": 0.75 * u.lb},
    vendor="potter",
    description="used in tanning and to make mortar",
)

Recipe(
    "animal feed",
    "cereals",
    1 * u.lb,
    {"cereals": 1 * u.lb},
    {},
    description="coarsely ground from cereals",
    vendor="stockyard",
)

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

muttonsheep_sale_weight = 130 * u.lb
Recipe(
    "mutton sheep",
    "sheep",
    muttonsheep_sale_weight,
    {},
    {"mature ewe": 1 * u.head, "animal feed": 120 * u.lb},
    # 120 lbs feed because four months of feeding at 1 lb grain/day
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
    "milk",  # TODO shouldn't I use 'milk' here instead of more general 'dairying'? but then when to use 'dairying' at all other than for milk and cheese, which have more specific references?
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
    "cheese",  # TODO "cheese, ewes' milk" the more specific reference made shit CRAZY expensive because there are so few .... stupid bloody logic
    cheese_sale_unit,
    {"salt": salt_in_cheese * cheese_sale_unit},
    {
        "ewes' milk": milk_in_cheese * cheese_sale_unit,
        "rennet": rennet_in_cheese * cheese_sale_unit,
    },
    description="local variety",
    vendor="dairy",
    # TODO Feta, rocquefort, manchego, pecorina romano are all sheep cheese
)

muttonsheep_carcass_weight = Decimal(0.55) * muttonsheep_sale_weight
muttonsheep_meat_weight = Decimal(0.75) * muttonsheep_carcass_weight
Recipe(
    "mutton",
    "meat",
    1 * u.lb,
    {},
    {"mutton sheep": (Decimal(1) * u.lb / muttonsheep_meat_weight) * u.head},
    vendor="butcher",
)

calf_sale_weight = Decimal(410) * u.lb
Recipe(
    "calf",
    "cattle",
    calf_sale_weight,
    {"cattle": 1 * u.head},
    {},
    vendor="stockyard",
    unit=1 * u.head,
    description="8 months old, suitable for rennet",
)

Recipe(
    "veal calf",
    "cattle",
    calf_sale_weight,
    {"cattle": 1 * u.head},
    {"animal feed": 121 * u.lb},
    # four months - half of life - being grain-finished at 1 lb/day
    vendor="stockyard",
    unit=1 * u.head,
    description="grain-finished, 8 months old, suitable for veal",
)

cow_sale_weight = Decimal(800) * u.lb
Recipe(
    "cow",
    "cattle",
    cow_sale_weight,
    {},
    {"calf": 1 * u.head, "animal feed": 243 * u.lb},
    # 243 = 8 additional months of feed at 1 lb/day to grain-finish
    unit=1 * u.head,
    vendor="stockyard",
    description="grain-finished, 16 months old; suitable for slaughtering",
)

cattle_carcass_fraction = Decimal(0.67)
cattle_meat_fraction = Decimal(0.67)
veal_per_calf = calf_sale_weight * cattle_carcass_fraction * cattle_meat_fraction
Recipe(
    "veal",
    "meat",
    1 * u.lb,
    {},
    {"veal calf": (Decimal(1) * u.lb / veal_per_calf) * u.head},
    vendor="butcher",
)

# TODO turn 1 cow into 2 sides of cow, then subdivide cow into different cuts of beef
beef_per_cow = cow_sale_weight * cattle_carcass_fraction * cattle_meat_fraction
Recipe(
    "beef",
    "meat",
    1 * u.lb,
    {},
    {"cow": (Decimal(1) * u.lb / veal_per_calf) * u.head},
    vendor="butcher",
)

abomasum_weight = Decimal(5) * u.lb  # this is a guess
Recipe(
    "abomasum",
    "meat",
    abomasum_weight,
    {},
    {"calf": (abomasum_weight / calf_sale_weight * cattle_carcass_fraction) * u.head},
    unit=1 * u.item,
    description="fourth compartment of calf stomach",
)

Recipe(
    "abomasum, cured",
    "meat",
    abomasum_weight,
    {"salt": 0.25 * u.lb},
    {"abomasum": 1 * u.item},
    # "vinegar": 1}, # TODO after beer
    unit=1 * u.item,
    vendor="butcher",
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
)

# http://www.personal.utulsa.edu/~marc-carlson/history/cattle.html
# this gives an average milk production of 3.5 gallons per day
cow_daily_milk_volume = Decimal(3.5) * u.gallon / u.day
# from some research, cows can give milk 300/365 days of the year (so 5/6 of the year)
# on the other hand, the production tapers off as this period goes on
# let's ad-hoc assign the effective number of days of milk production
cow_annual_milking_days = Decimal(250) * u.day
cow_annual_milk_volume = cow_daily_milk_volume * cow_annual_milking_days
Recipe(
    "cow milk",
    "milk",
    milk_weight * milk_sale_unit,
    {},
    {"cow": (milk_sale_unit / cow_annual_milk_volume) * u.head},
    unit=milk_sale_unit,
    vendor="dairy",
    description="customer supplies container",
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
    description="local variety",
    vendor="dairy",
)

cow_nonmeat_weight = cow_sale_weight - beef_per_cow
# suet is not all fats, just certain fats
suet_specificity = Decimal(2) * u.lb
Recipe(
    "suet",
    "meat",  # what's a better one? chandler? butchery?
    1 * u.lb,
    {},
    {"cow": (suet_specificity / cow_nonmeat_weight) * u.head},
    vendor="butcher",
    description="beef fat for cooking, or for manufacture of tallow",
)
