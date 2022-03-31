from decimal import Decimal, getcontext
from math import ceil, floor
from collections import Counter

from references import Q, u, world_references, categories
from towns import towns

# set up the Decimal environment
getcontext().prec = 6

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
}

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
    }.items()
}
# ordinary clay items calculated with 1-sq-ft, 1-inch-thick slabs -- 1/12 of a cubic ft
clay_slab_volume = Decimal(1) / Decimal(12) * u.cuft
clay_slab_weight = Decimal(108) * u.oz
density["clay"] = (clay_slab_weight / clay_slab_volume).to(u.lb / u.cuft)


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
        # container is a separate field so recipe X's container's weight is ignored when calculating weights of further recipes that make use of X, but the price of X can still incorporate the container's cost
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
        if self.vendor:
            vendors.add(self.vendor)

    def ingredient_costs(self, towninfo):
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

    def denominator(self):
        return self.unit if self.unit else self.weight

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
        return (final.magnitude * u.cp) / self.denominator()

    def chunked_price(self, towninfo):
        p = self.price(towninfo)
        result = {}
        justmoney = p * self.denominator()
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
        result["denominator"] = self.denominator()
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
        return ", ".join(result) + f" / {self.denominator():~}"


Recipe(
    "smelting fuel",
    "smelting",
    0.75 * u.lb,
    dict(coal=0.5 * u.lb, limestone=0.25 * u.lb),
    description="generic supplies required to smelt 1 lb metal",
    vendor="puddler",
)

Recipe(
    "raw iron",
    "iron",
    1 * u.lb,
    dict(iron=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="separated from waste rock and impurities",
)

Recipe(
    "pig iron",
    "pig iron",
    1 * u.lb,
    {},
    {"raw iron": 1 * u.lb, "smelting fuel": 0.75 * u.lb},
    description="weak, brittle purified iron",
)

Recipe(
    "cast iron",
    "ironmongery",
    1 * u.lb,
    {},
    {
        "smelting fuel": 0.75 * u.lb,
        "raw manganese": 0.06 * u.lb,
        "raw nickel": 0.01 * u.lb,
        "pig iron": 0.93 * u.lb,
    },
    description="for a volume of 1x1x3.8 in.",
)

Recipe(
    "wrought iron",
    "ironmongery",
    1 * u.lb,
    {},
    {"pig iron": 1 * u.lb, "smelting fuel": 0.75 * u.lb},
    vendor="puddler",
    description="ingot, 1x1x3.57 in.",
)

Recipe(
    "raw nickel",
    "nickel",
    1 * u.lb,
    dict(nickel=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    vendor="puddler",
)

Recipe(
    "raw manganese",
    "manganese",
    1 * u.lb,
    dict(manganese=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    vendor="puddler",
)

Recipe(
    "raw copper",
    "copper",
    1 * u.lb,
    dict(copper=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    vendor="puddler",
    description="ingot, 2x1.065x1.45 in.",
)

Recipe(
    "raw tin",
    "tin",
    1 * u.lb,
    dict(tin=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    vendor="puddler",
    description="separated from waste rock and impurities",
)


Recipe(
    "raw gold",
    "gold",
    1 * u.lb,
    dict(gold=1 * u.lb),
    {"smelting fuel": 0.75 * u.lb},
    description="ingot, 1x1x1.435 in.",
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
        "smelting fuel": 0.75 * u.lb,
        "raw tin": tin_in_lb_pewter,
        "raw copper": copper_in_lb_pewter,
    },
    vendor="puddler",
    description="ingot, 1x1x3.65 in.",
)


Recipe(
    "steel",
    "ironmongery",
    1 * u.lb,
    {},
    {"pig iron": 1 * u.lb, "smelting fuel": 0.75 * u.lb},
    vendor="puddler",
    description="ingot, 1x1x3.5 in.",
)

Recipe("iron filings", "ironmongery", 1 * u.lb, {}, {"wrought iron": 1 * u.lb})

# filings used following the methods described in Subterraneal Treasures
Recipe(
    "raw lead",
    "leadsmelting",
    1 * u.lb,
    {"lead": 1 * u.lb},
    {"iron filings": 0.25 * u.lb, "smelting fuel": 0.75 * u.lb},
    vendor="puddler",
    description="ingot, 1.084x1.5x1.5 in.",
)

Recipe(
    "raw zinc",
    "smelting",
    1 * u.lb,
    {"zinc": 1 * u.lb},
    {"smelting fuel": 0.75 * u.lb},
    vendor="puddler",
)

Recipe(
    "raw silver",
    "smelting",
    1 * u.lb,
    {"silver": 1 * u.lb},
    {"smelting fuel": 0.75 * u.lb},
    description="ingot, 1.5x1.5x1.175 in.",
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
        "smelting fuel": 0.75 * u.lb,
    },
    vendor="puddler",
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
        "smelting fuel": 0.75 * u.lb,
    },
    vendor="puddler",
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
        "smelting fuel": 0.75 * u.lb,
    },
    vendor="puddler",
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
        "smelting fuel": 0.75 * u.lb,
    },
    vendor="puddler",
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
        unit=1 * u.item,
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
        unit=1 * u.item,
        vendor="blacksmith",
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
        unit=1 * u.item,
        vendor="goldsmith",
        description=f"gilded sterling silver with loop for hanging; approx. {m['height']:~} tall and {m['width']:~} wide",
    )


hilt_volume = (Decimal(3) * u.inch * Decimal(3) * u.inch * Decimal(6) * u.inch).to(
    "cuft"
)
hilt_weight = hilt_volume * density["timber"]
Recipe(
    "sword hilt",
    "woodcraft",
    hilt_weight,
    {"timber": hilt_weight},
    unit=1 * u.item,
    description="wooden tube",
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
    "metalsmithing",  # TODO weapons
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
    "weapons",
    dagger_weight,
    {},
    {
        "blade": dagger_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d4 damage, melee or thrown 2/3/4; {dagger_length} blade",
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
    "swords",
    shortsword_weight,
    {},
    {
        "blade": shortsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d6 damage; {shortsword_length} blade",
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
    "swords",
    longsword_weight,
    {},
    {
        "blade": longsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d8 damage; {longsword_length} blade",
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
    "swords",
    greatsword_weight,
    {},
    {
        "blade": greatsword_blade_needed * u.item,
        "pommel": 1 * u.item,
        "sword hilt": 1 * u.item,
    },
    description=f"1d10 damage; {greatsword_length} blade",
    unit=1 * u.item,
    vendor="weaponsmith",
)


Recipe(
    "fresh fish",
    "fish",
    1 * u.lb,
    {"fish": 1 * u.lb},
    {},
    vendor="fishmonger",
    description="local variety",
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
    "black bread",
    "bread, black",
    1 * u.lb,
    {"salt": 0.05 * u.lb},
    {"flour": 0.7 * u.lb},
    vendor="baker",
    description="southwestern millers' specialty",
)

Recipe(
    "quicklime",
    "quicklime",
    1 * u.lb,
    {"quicklime": 1 * u.lb},
    vendor="potter",  # potter b/c made in a kiln
    description="used in tanning and to make mortar",
)

Recipe(
    "coal ash",
    "coal",
    1 * u.lb,
    {"coal": 10 * u.lb},
    {},
    vendor="potter",  # potter b/c made in a kiln
)

Recipe(
    "mortar",
    "plaster",
    1 * u.lb,
    {},
    {
        "quicklime": D(0.9) * u.lb,
        "coal ash": D(0.1) * u.lb,
    },
    vendor="mason",
    description="lime-based hydraulic mortar or plaster",
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
    vendor="butcher",
)

Recipe(
    "cattle bone",
    "meat",
    1 * u.lb,
    {},
    {"cow, beef": (Decimal(1) * u.lb / bone_per_cow) * u.head},
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
    {"abomasum": 1 * u.item, "vinegar, in barrel": D(0.5) * u.pint},
    unit=1 * u.item,
    vendor="butcher",
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

milk_per_serving = D(1) * u.pint
Recipe(
    "cow milk, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["milk"] * milk_per_serving).to(u.lb),
    {},
    {"cow milk": milk_per_serving},
    unit=milk_per_serving,
    vendor="innkeeper",
)

Recipe(
    "ewes' milk, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["milk"] * milk_per_serving).to(u.lb),
    {},
    {"ewes' milk": milk_per_serving},
    unit=milk_per_serving,
    vendor="innkeeper",
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

Recipe(
    "suet",
    "meat",  # what's a better one? chandler? butchery?
    1 * u.lb,
    {},
    {"cow, beef": (1 * u.lb / fat_per_cow) * u.head},
    vendor="butcher",
    description="beef fat for cooking, or for manufacture of tallow",
)

Recipe("tallow", "candles and wax", 1 * u.lb, {}, {"suet": 1 * u.lb}, vendor="chandler")

timber_per_ash = Decimal(10) * u.lb / u.lb
Recipe(
    "wood ash",
    "timber",
    1 * u.lb,
    {"timber": timber_per_ash * u.lb},
    {},
    vendor="chandler",
)

Recipe(
    "lye",
    "lye",  # TODO I used soap and wax at first ... "lye" ref makes it ~100x more exensive
    1 * u.lb,
    {},
    {"wood ash": 1 * u.lb},
    vendor="chandler",
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
    description="will wash 1 person 60 times; 2x3x6 in.",
)

Recipe(
    "hard soap, rose scent",
    "soap",
    soap_weight,
    {
        "salt": salt_per_soap_tallow * soap_weight,
        "attar of roses": D(0.5) * u.ounce,
    },
    {
        "lye": lye_per_soap_tallow * soap_weight,
        "tallow": tallow_per_soap * soap_weight,
    },
    vendor="chandler",
    description="will wash 1 person 60 times; 2x3x6 in.",
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
    description=f"cleaned and dried cowskin, {rawhide_area:~}",
)

# http://boar.org.uk/aaiwxw3MusprattL6Preparation.htm
# this says three to four cubic feet of "freshly burned fat lime" (aka quicklime) used for 100 average hides
# let's split the difference between 3 and 4 cuft of quicklime
quicklime_per_hide = (Decimal(3.5) * u.cuft * density["quicklime"]) / (
    Decimal(100) * rawhide_area
)
# tanned_hide_toughness = _weight.to(u.oz) / cowhide_area
Recipe(
    "tanned cowhide",
    "hides",
    rawhide_weight,
    {},
    {"quicklime": quicklime_per_hide * rawhide_area, "rawhide": rawhide_area},
    unit=rawhide_area,
    vendor="tanner",
    description=f"typical leather, {rawhide_area:~}",
)

Recipe(
    "roasted malt",
    "malt",
    1 * u.lb,
    {"malt": 1 * u.lb},
    vendor="brewer",
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
        unit=1 * u.item,
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
}


def calculate_abv(sugar_sources, water_volume, desired_volume):
    # assumption: all the available sugar content of the sugar_sources is consumed by the yeast
    total_sugar = sum(
        [
            sugar_per_brewable[name] * weight.to(u.lb)
            for name, weight in sugar_sources.items()
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

for member in categories["fruits"]["members"]:
    description = "sour orange" if member == "hushhash" else None
    Recipe(
        member,
        member,
        1 * u.lb,
        {member: 1 * u.lb},
        {},
        vendor="costermonger",
        description=description,
    )

for member in categories["vegetables"]["members"]:
    Recipe(
        member,
        member,
        1 * u.lb,
        {member: 1 * u.lb},
        {},
        vendor="greengrocer",
    )

for tuber in ("potatoes", "groundnuts", "sweet potatoes", "yams"):
    Recipe(
        tuber,
        tuber,
        1 * u.lb,
        {tuber: 1 * u.lb},
        {},
        vendor="greengrocer",
    )


grapes_for_wine = D(3.5) * u.lb / (D(750) * u.ml).to(u.gallon)
wine_abv = calculate_abv(
    {"grapes": grapes_for_wine * 1 * u.gallon},
    1 * u.gallon,
    1 * u.gallon,
)

wines = {
    "wine": "local variety of red or white",
    "champagne": "sparkling, bubbly white, produced by northern elves",
    "wine, Baccia": "the queen of Marasan viticulture; dry white wine made of late harvest grapes",
    "wine, asti spumante": "sweet, sparkling dessert wine with creamy texture and aromas of pear, honeysuckle, and peaches",
    "wine, Sacramaran": "central Marasan wine; light red with notes of apricot and currants",
    "wine, Lutewood": "aromatic 'orange' wine with tart aftertaste, made from skin-on white grapes",
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
        vendor="brewer",
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
    vendor="innkeeper",
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
    vendor="innkeeper",
    description=registry["beer, in barrel"].description,
)

Recipe(
    "gnomish beer, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * beer_per_serving).to(u.lb),
    {},
    {"gnomish beer, in barrel": beer_per_serving},
    unit=beer_per_serving,
    vendor="innkeeper",
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
    vendor="innkeeper",
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
    vendor="innkeeper",
    description=registry["wine, in barrel"].description,
)

Recipe(
    "wine, Baccia, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"wine, Baccia, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="innkeeper",
    description=registry["wine, Baccia, in barrel"].description,
)


Recipe(
    "champagne, by the glass",
    "foodstuffs",  # TODO anything better?
    (density["water"] * wine_per_serving).to(u.lb),
    {},
    {"champagne, in barrel": wine_per_serving},
    unit=wine_per_serving,
    vendor="innkeeper",
    description=registry["champagne, in barrel"].description,
)
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
)

scoured_wool_weight = D(15) * u.lb
Recipe(
    "scoured wool",
    "wool",
    scoured_wool_weight,
    {},
    {
        "greasy wool": scoured_wool_weight,
        # "fuller's earth": 1,
    },
)

# final step in cleaning wool is pounding by mills
Recipe(
    "clean wool",
    "wool",
    1 * u.lb,
    {},
    {"scoured wool": 1 * u.lb},
    description="brownish-white color",
)

# some wool is additionally brushed for softness
Recipe(
    "brushed wool",
    "wool",
    1 * u.lb,
    {},
    {"clean wool": 1 * u.lb},
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
)
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
    wool_ordinary_cloth_sale_weight,
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
)
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
)

Recipe(
    "combed flax",
    "flax",
    1 * u.lb,
    {},
    {"retted flax": 1 * u.lb},
    difficulty=D(2),  # it's hard to work with flax fibers
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
)
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
    description="brown sugar with high molasses content",
)

Recipe(
    "refined sugar",
    "refined sugar",
    1 * u.lb,
    {},
    {"raw sugar": 1 * u.lb},
    vendor="grocer",
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
    description="black, gooey sugarcane extract",
)

Recipe("raw tobacco", "tobacco", 1 * u.lb, {"tobacco": 1 * u.lb}, {})

Recipe(
    "cured tobacco",
    "tobacco",
    1 * u.lb,
    {},
    {"raw tobacco": 5 * u.lb},
    vendor="tobacconist",
)

Recipe(
    "snuff",
    "tobacco",
    1 * u.lb,
    {},
    {"cured tobacco": 1 * u.lb},
    vendor="tobacconist",
    description="powdered tobacco, unscented",
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
    description=f"{donkey_sale_age} old jack (male), {donkey_sale_weight:~}",
)

griff_sale_weight = D(1100) * u.lb
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
    description=f"{griff_sale_age} old, {griff_sale_weight:~}",
)

Recipe(
    "vinegar, in barrel",
    "brewing",  # TODO vinegar ref
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
    description="accounts for firing wet clay, so it does not have to be done separately for all clay goods",
)

masonry_unit = D(1) * u.cuft
for stone in (
    "alabaster",
    "basalt",
    "brownstone",
    "dolomite",
    "granite",
    "limestone",
    "marble",
    "freestone",
    "porphyry",
    "sandstone",
    "red sandstone",
    "slate",
    "syenite",
    "trachyte",
    "tufa",
    "tuff",
):
    if world_references[stone]["production"] == 0:
        # TODO - but I think all of these have production except for granite, which will get some from building stone eventually
        pass
    elif stone not in density:
        # TODO add more figures to densty
        pass
    else:
        theweight = (density[stone] * masonry_unit).to(u.lb)
        Recipe(
            f"masonry, {stone}",
            "masonry",
            theweight,
            {f"{stone}": theweight},
            unit=masonry_unit,
            vendor="mason",
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
Recipe(
    "flat glass",
    "ceramics",
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
    description="6in x 7in x 0.25in sheet",
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


def main():
    by_vendor()
    print(f"Recipes: {len(registry)}")


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

# watchdog (barks to alert but won't fight)
# guard dog (as watchdog but also has combat training)
# war dog (as guard dog but can wear barding, has bonus HP, and has +1 to hit)
# working dog (including herd dog/sheepdog and draft dog which pulls dogcarts)


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
