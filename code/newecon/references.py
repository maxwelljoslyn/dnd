from decimal import getcontext, Decimal
from collections import namedtuple
from pint import UnitRegistry

# "If you use Pint in multiple modules ... avoid creating multiple instances of the unit registry ... by instantiating the registry in a single place."
u = UnitRegistry()
u.load_definitions("units.txt")
Q_ = u.Quantity

# "[If] pickling and unpickling Quantities, [define] the registry as the application registry"
# set_application_registry(u)

getcontext().prec = 6

# todo - world_references[x]["category"] should be a list, so that "beans" has ['beans', 'food'], "horses, Brittany" has ['horses', 'animals'] etc
# todo regularize singular/plural naming in things like cantaloupes, almonds, etc.

# the primary use of these categories is to distribute e.g. production of generic "fruits" and "beans" among references to specific types of those things
# should I do so in the case of e.g. "horses" and "Brittany horses" or "wine" and "Chamblais wine" ? seems there is value in having both generic and specific in those cases.
categories = {
    "animals",
    "nuts",
    "beans",
    "wines",
    "timber",
    "fruits",
    "vegetables",
    "cereals",
    "oils",
    "horses",
    "metals",
    "smithing",
}

# todo sanity checks
# millet vs mullet
# cloves vs clover
# coral vs copal
# coral vs copal
# chestnut (wood) vs chestnuts (food)
# euphorbia (plant) vs euphoria (word)


world_references = {
    "acid": {"references": 0, "production": 3_957_453 * u.oz},
    "adamantite": {"references": 6, "production": 297_760 * u.oz},
    "alabaster": {"references": 8, "production": 1_092_766_558 * u.oz},
    "wood, African oak": {
        "references": 1,
        "category": "timber",
    },
    "agate": {
        "references": 11,
    },
    "alexandrite": {
        "references": 12,
    },
    "alfalfa": {
        "references": 14,
    },
    "almandine": {
        "references": 7,
    },
    "almonds": {
        "references": 35,
        "category": "nuts",
    },
    "aloe": {
        "references": 4,
    },
    "amber": {
        "references": 24,
    },
    "amber jewelry": {
        "references": 2,
    },
    "amethyst": {
        "references": 14,
    },
    "sherry, amontillado": {
        "references": 1,
    },
    "anchovies": {
        "references": 6,
    },
    "angora": {
        "references": 1,
    },
    "horn, antelope": {
        "references": 1,
    },
    "brandy, apple": {
        "references": 2,
    },
    "apricots": {
        "references": 31,
    },
    "aquamarine": {
        "references": 19,
    },
    "arak": {
        "references": 1,
    },
    "arbutus": {
        "references": 1,
    },
    "brandy, Armagnac": {
        "references": 2,
    },
    "armor": {
        "references": 45,
    },
    "arrack": {
        "references": 2,
    },
    "arrowroot": {
        "references": 3,
    },
    "artichokes": {
        "references": 1,
    },
    "artworks": {
        "references": 54,
    },
    "asafoetida": {
        "references": 6,
    },
    "asparagus": {
        "references": 5,
    },
    "aspen": {
        "references": 1,
        "category": "timber",
    },
    "asti spumante": {
        "references": 2,
    },
    "attar of roses": {
        "references": 8,
    },
    "avocados": {
        "references": 3,
    },
    "azulejos": {
        "references": 1,
    },
    "azurite": {
        "references": 5,
    },
    "bacon": {
        "references": 11,
    },
    "wine, Badocsony": {
        "references": 1,
    },
    "bamboo": {
        "references": 8,
    },
    "bananas": {
        "references": 47,
    },
    "banking": {
        "references": 37,
    },
    "barbel": {
        "references": 1,
    },
    "barges": {
        "references": 2,
    },
    "barrels": {
        "references": 15,
    },
    "ware, Barum": {
        "references": 1,
    },
    "baskets": {
        "references": 12,
    },
    "beads": {
        "references": 2,
    },
    "beans": {
        "references": 68,
    },
    "skins, bear": {
        "references": 8,
    },
    "beaujolais": {
        "references": 3,
    },
    "wood, beech": {
        "references": 7,
        "category": "timber",
    },
    "beef": {
        "references": 13,
    },
    "bells": {
        "references": 7,
    },
    "berries": {
        "references": 2,
    },
    "beryl": {
        "references": 4,
    },
    "betel nuts": {
        "references": 19,
        "category": "nuts",
    },
    "wood, birch": {
        "references": 2,
        "category": "timber",
    },
    "birdcages": {
        "references": 1,
    },
    "bread, black": {
        "references": 2,
    },
    "black coral": {
        "references": 5,
    },
    "blackcurrant liqueur": {
        "references": 1,
    },
    "marble, black": {
        "references": 2,
    },
    "wine, black": {
        "references": 1,
    },
    "blackberries": {
        "references": 1,
    },
    "blankets": {
        "references": 11,
    },
    "bloodstone": {
        "references": 5,
    },
    "quartz, blue": {
        "references": 6,
    },
    "boatbuilding": {
        "references": 31,
    },
    "bobbins": {
        "references": 1,
    },
    "bonecarving": {
        "references": 2,
    },
    "bonito": {
        "references": 4,
    },
    "borax": {
        "references": 8,
    },
    "acid, boric": {
        "references": 1,
    },
    "bottles": {
        "references": 3,
    },
    "boxes": {
        "references": 2,
    },
    "wood, boxwood": {
        "references": 2,
        "category": "timber",
    },
    "bracelets": {
        "references": 1,
    },
    "brandywine": {
        "references": 23,
    },
    "brass": {
        "references": 17,
    },
    "brasswares": {
        "references": 17,
    },
    "bread": {
        "references": 25,
    },
    "breadfruit": {
        "references": 1,
    },
    "bream": {
        "references": 2,
    },
    "horses, Brittany": {
        "references": 1,
    },
    "brocade": {
        "references": 6,
    },
    "bromine": {
        "references": 1,
    },
    "bronze": {
        "references": 18,
    },
    "brooms": {
        "references": 1,
    },
    "marble, brown": {
        "references": 1,
    },
    "brushes": {
        "references": 9,
    },
    "buckets": {
        "references": 1,
    },
    "buckles": {
        "references": 1,
    },
    "buffalo": {
        "references": 16,
    },
    "buttons": {
        "references": 6,
    },
    "cabbage": {
        "references": 9,
    },
    "cabinetmaking": {
        "references": 5,
    },
    "cairngorm": {
        "references": 2,
    },
    "cakes": {
        "references": 5,
    },
    "beans, Calabar": {
        "references": 1,
    },
    "calico cloth": {
        "references": 5,
    },
    "cambric": {
        "references": 2,
    },
    "camelhair": {
        "references": 4,
    },
    "cheese, Camembert": {
        "references": 1,
    },
    "cameos": {
        "references": 1,
    },
    "camphor": {
        "references": 6,
    },
    "canaries": {
        "references": 1,
    },
    "wine, canary sack": {
        "references": 1,
    },
    "cannon": {
        "references": 2,
    },
    "cantaloupes": {
        "references": 1,
    },
    "canvas": {
        "references": 9,
    },
    "carbon black": {
        "references": 1,
    },
    "carnations": {
        "references": 3,
    },
    "carnelian": {
        "references": 4,
    },
    "carobs": {
        "references": 2,
    },
    "wood, carobwood": {
        "references": 1,
        "category": "timber",
    },
    "carp": {
        "references": 3,
    },
    "carpentry": {
        "references": 17,
    },
    "carriages": {
        "references": 12,
    },
    "carroubes": {
        "references": 1,
    },
    "cashews": {
        "references": 4,
        "category": "nuts",
    },
    "cassavas": {
        "references": 18,
    },
    "cassia": {
        "references": 1,
    },
    "beans, castor": {
        "references": 27,
    },
    "castor oil": {
        "references": 4,
    },
    "casuarina": {
        "references": 1,
    },
    "catechu": {
        "references": 4,
    },
    "catfish": {
        "references": 1,
    },
    "catseye": {
        "references": 9,
    },
    "cauliflower": {
        "references": 1,
    },
    "wood, cedar": {
        "references": 6,
        "category": "timber",
    },
    "cellos": {
        "references": 3,
    },
    "wine, Chablis": {
        "references": 3,
    },
    "wine, Chabrieres": {
        "references": 1,
    },
    "chain": {
        "references": 2,
    },
    "chalcedony": {
        "references": 4,
    },
    "champagne": {
        "references": 9,
    },
    "charcoal": {
        "references": 15,
    },
    "cheese, cheddar": {
        "references": 1,
    },
    "cherries": {
        "references": 19,
    },
    "wood, chestnut": {
        "references": 15,
        "category": "timber",
    },
    "chestnuts": {
        "references": 35,
    },
    "wine, Chianti": {
        "references": 2,
    },
    "chickens": {
        "references": 18,
    },
    "chickpeas": {
        "references": 5,
    },  # bean
    "chicory": {
        "references": 10,
    },
    "china": {
        "references": 15,
    },
    "chocolate": {
        "references": 41,
    },
    "chrysoprase": {
        "references": 8,
    },
    "cinchona": {
        "references": 7,
    },
    "cinnamon leaf oil": {
        "references": 1,
    },
    "marble, Cipollina": {
        "references": 3,
    },
    "citrine": {
        "references": 13,
    },
    "citronella oil": {
        "references": 4,
    },
    "citrons": {
        "references": 5,
    },
    "citrus": {
        "references": 71,
    },
    "civet": {
        "references": 1,
    },
    "clementines": {
        "references": 1,
    },
    "clockmaking": {
        "references": 47,
    },
    "cloisonne": {
        "references": 1,
    },
    "clover": {
        "references": 6,
    },
    "cloverseed": {
        "references": 2,
    },
    "cob apples": {
        "references": 1,
    },
    "cobaltsmelting": {
        "references": 1,
    },
    "cochineal": {
        "references": 2,
    },
    "coconut oil": {
        "references": 1,
    },
    "coconuts": {
        "references": 57,
    },
    "cod": {
        "references": 20,
    },
    "cod liver oil": {
        "references": 2,
    },
    "coffins": {
        "references": 1,
    },
    "cognac": {
        "references": 4,
    },
    "coir": {
        "references": 7,
    },
    "colza": {
        "references": 3,
    },
    "combs": {
        "references": 1,
    },
    "common opal": {
        "references": 5,
    },
    "copal": {
        "references": 7,
    },
    "copra": {
        "references": 25,
    },
    "coral": {
        "references": 13,
    },
    "cork": {
        "references": 38,
    },
    "cormorants": {
        "references": 1,
    },
    "corsets": {
        "references": 1,
    },
    "corundum": {
        "references": 2,
    },
    "cottonseed": {
        "references": 4,
    },
    "crabs": {
        "references": 5,
    },
    "crayfish": {
        "references": 1,
    },
    "cream": {
        "references": 17,
    },
    "marble, crimson": {
        "references": 3,
    },
    "crockery": {
        "references": 2,
    },
    "cryptomeria": {
        "references": 1,
    },
    "crystal": {
        "references": 5,
    },
    "cucumbers": {
        "references": 5,
    },
    "currants": {
        "references": 13,
    },
    "curtains": {
        "references": 1,
    },
    "cuttlefish": {
        "references": 2,
    },
    "wood, cypress": {
        "references": 2,
        "category": "timber",
    },
    "daffodils": {
        "references": 3,
    },
    "dalbergia": {
        "references": 1,
    },
    "damascene": {
        "references": 1,
    },
    "damask": {
        "references": 5,
    },
    "darekh": {
        "references": 1,
    },
    "dates": {
        "references": 69,
    },
    "horn, deer and elk": {
        "references": 2,
    },
    "dhows": {
        "references": 3,
    },
    "diamondcutting": {
        "references": 5,
    },
    "dim sum": {
        "references": 2,
    },
    "dolls": {
        "references": 2,
    },
    "doors": {
        "references": 1,
    },
    "butter, Dorset": {
        "references": 1,
    },
    "horses, draft": {
        "references": 1,
    },
    "dresses": {
        "references": 1,
    },
    "drapery": {
        "references": 2,
    },
    "drugget goods": {
        "references": 1,
    },
    "dried peas": {
        "references": 1,
    },
    "ducks": {
        "references": 7,
    },
    "eau de Cologne": {
        "references": 1,
    },
    "ebony": {
        "references": 10,
    },
    "cheese, Edam": {
        "references": 3,
    },
    "edible birds' nests": {
        "references": 3,
    },
    "eels": {
        "references": 3,
    },
    "eggplants": {
        "references": 1,
    },
    "elaeocarpus": {
        "references": 1,
    },
    "elixir de Spa": {
        "references": 1,
    },
    "emerald": {
        "references": 25,
    },
    "enamelware": {
        "references": 21,
    },
    "engraving": {
        "references": 5,
    },
    "equisetifolia": {
        "references": 1,
    },
    "ermine": {
        "references": 3,
    },
    "espadrilles": {
        "references": 1,
    },
    "Esparto grass": {
        "references": 10,
    },
    "ware, Esparto": {
        "references": 1,
    },
    "wood, eucalyptus": {
        "references": 1,
    },
    "euphorbia": {
        "references": 1,
    },
    "cheese, ewes' milk": {
        "references": 1,
    },
    "faience": {
        "references": 11,
    },
    "fans": {
        "references": 3,
    },
    "felt": {
        "references": 15,
    },
    "felt boots": {
        "references": 1,
    },
    "felt caps": {
        "references": 8,
    },
    "fighting cocks": {
        "references": 1,
    },
    "figs": {
        "references": 59,
    },
    "figurines": {
        "references": 1,
    },
    "filbert nuts": {
        "references": 1,
        "category": "nuts",
    },
    "files": {
        "references": 1,
    },
    "wood, fir": {
        "references": 7,
    },
    "fire opal": {
        "references": 8,
    },
    "firecrackers": {
        "references": 8,
    },
    "fish fins": {
        "references": 1,
    },
    "fish hooks": {
        "references": 2,
    },
    "fish meal": {
        "references": 1,
    },
    "flags": {
        "references": 1,
    },
    "flannel": {
        "references": 4,
    },
    "flatfish": {
        "references": 1,
    },
    "flatware": {
        "references": 1,
    },
    "flounder": {
        "references": 1,
    },
    "flowers": {
        "references": 18,
    },
    "fodder": {
        "references": 54,
    },
    "fox furs": {
        "references": 6,
    },
    "frankincense": {
        "references": 3,
    },
    "freshwater fish": {
        "references": 52,
    },
    "friezes": {
        "references": 2,
    },
    "brandy, fruit": {
        "references": 1,
    },
    "fur clothing": {
        "references": 2,
    },
    "garlic": {
        "references": 2,
    },
    "garnet": {
        "references": 7,
    },
    "geese": {
        "references": 4,
    },
    "gemcarving": {
        "references": 2,
    },
    "gemcutting": {
        "references": 32,
    },
    "ghee": {
        "references": 5,
    },
    "gin": {
        "references": 4,
    },
    "gingerbread": {
        "references": 1,
    },
    "glazed fruit": {
        "references": 1,
    },
    "gloves": {
        "references": 35,
    },
    "glue": {
        "references": 2,
    },
    "goatskins": {
        "references": 7,
    },
    "gold filigree": {
        "references": 11,
    },
    "gold inlay": {
        "references": 1,
    },
    "gooseberries": {
        "references": 2,
    },
    "cheese, gorgonzola": {
        "references": 2,
    },
    "goshenite": {
        "references": 1,
    },
    "cheese, Gouda": {
        "references": 1,
    },
    "gowns": {
        "references": 2,
    },
    "gram": {
        "references": 23,
    },
    "Grand Chartreuse": {
        "references": 1,
    },
    "granite": {
        "references": 49,
    },
    "grapefruit": {
        "references": 6,
    },
    "greenstone": {
        "references": 5,
    },
    "marble, gray-pink": {
        "references": 1,
    },
    "grindstones": {
        "references": 4,
    },
    "grossular": {
        "references": 8,
    },
    "cheese, Gruyere": {
        "references": 2,
    },
    "guavas": {
        "references": 3,
    },
    "gudgeon": {
        "references": 1,
    },
    "lace, Guipure": {
        "references": 1,
    },
    "gum": {
        "references": 10,
    },
    "gum Arabic": {
        "references": 11,
    },
    "gum benzoin": {
        "references": 1,
    },
    "gum mastic": {
        "references": 4,
    },
    "gum tragacanth": {
        "references": 2,
    },
    "gutta-percha": {
        "references": 1,
    },
    "haddock": {
        "references": 4,
    },
    "hake": {
        "references": 1,
    },
    "handkerchiefs": {
        "references": 1,
    },
    "harari": {
        "references": 1,
    },
    "harpsichords": {
        "references": 3,
    },
    "tweed, Harris": {
        "references": 2,
    },
    "hats": {
        "references": 29,
    },
    "hawkseye": {
        "references": 1,
    },
    "hay": {
        "references": 50,
    },
    "hazelnuts": {
        "references": 2,
    },
    "healing earth": {
        "references": 1,
    },
    "heliodor": {
        "references": 4,
    },
    "hematite": {
        "references": 10,
    },
    "henna": {
        "references": 3,
    },
    "herring": {
        "references": 46,
    },
    "hessonite": {
        "references": 1,
    },
    "horn": {
        "references": 2,
    },
    "horncarving": {
        "references": 3,
    },
    "horn combs": {
        "references": 1,
    },
    "wood, hornbeam": {
        "references": 1,
        "category": "timber",
    },
    "hosiery": {
        "references": 42,
    },
    "hushhash": {
        "references": 5,
    },  # sour orange
    "hyacinths": {
        "references": 1,
    },
    "incense": {
        "references": 8,
    },
    "indigo": {
        "references": 17,
    },
    "iodine": {
        "references": 1,
    },
    "wood, iroko": {
        "references": 1,
        "category": "timber",
    },
    "iron flowers": {
        "references": 1,
    },
    "wood, ironwood": {
        "references": 4,
        "category": "timber",
    },
    "ivorycarving": {
        "references": 10,
    },
    "jade": {
        "references": 43,
    },
    "jadecarving": {
        "references": 5,
    },
    "jasper": {
        "references": 8,
    },
    "wood, jelutong": {
        # https://www.wood-database.com/jelutong/
        "references": 1,
        "category": "timber",
    },
    "jet": {
        "references": 4,
    },
    "jeweled daggers": {
        "references": 1,
    },
    "alchemy": {
        # alchemist
        "references": 321,
    },
    "alloys": {
        "references": 119,
    },
    "alum": {"references": 6, "production": 1_478_185 * u.oz},
    "anise": {"references": 3, "production": 196_332 * u.oz},
    "antimony": {"references": 43, "production": 3_359_461 * u.oz},
    "antimonysmelting": {"references": 2, "production": 180_736 * u.oz},
    "apples": {
        "references": 78,
    },
    "arsenic": {"references": 11, "production": 236_480 * u.oz},
    "artistic glassware": {"references": 0, "production": 3_607_423 * u.oz},
    "barley": {
        "references": 212,
    },
    "basalt": {"references": 2, "production": 222_700_425 * u.oz},
    "bear paws": {"references": 1, "production": 224_256 * u.oz},
    "bismuth": {"references": 4, "production": 312_508 * u.oz},
    "bitter salt": {"references": 14, "production": 75_768_877 * u.oz},
    "black powder": {"references": 5, "production": 254_061 * u.lb},
    "bookbinding": {
        "references": 101,
    },
    "boots and shoes": {
        "references": 105,
    },
    "brewing": {
        "references": 198,
        "production": 3_972_035_901 * u.floz,
    },  # category
    "bricks": {"references": 98, "production": 4_056_185_600 * u.oz},
    "bristles": {"references": 19, "production": 35_881_488 * u.oz},
    "brownstone": {"references": 1, "production": 203_389_393 * u.oz},
    "building stone": {
        "references": 74,
    },
    "butter": {"references": 84, "production": 435_499_008 * u.oz},
    "cacao": {"references": 48, "production": 20_142_080 * u.oz},
    "camels": {"references": 76, "production": 373_900 * u.head},
    "candles and wax": {
        "references": 95,
    },
    "cardamom": {"references": 7, "production": 2_508_800 * u.oz},
    "carpets": {"references": 110, "production": 519_502 * u.sqyd},
    "carts": {
        "references": 72,
    },
    "cattle": {"references": 486, "production": 12_588_600 * u.head},
    "caviar": {"references": 10, "production": 28_672 * u.oz},
    "cement": {"references": 131, "production": 6_218_604_800 * u.oz},
    "ceramics": {"references": 57, "production": 162_713_528 * u.oz},
    "cereals": {"references": 619, "production": 91_834_982_400 * u.oz},
    "chalk": {"references": 7, "production": 1_187_020_800 * u.oz},
    "chamomile": {"references": 1, "production": 5_017_600 * u.oz},
    "cheese": {"references": 84, "production": 682_264_576 * u.oz},
    "chromium": {"references": 43, "production": 135_618_560 * u.oz},
    "cider": {"references": 24, "production": 8_960_000 * u.floz},
    "cinnamon": {"references": 9, "production": 8_673_280 * u.oz},
    "cloth": {
        # weaver
        "references": 599,
    },
    "clothing": {
        "references": 93,
    },
    "cloves": {"references": 7, "production": 8_458_240 * u.oz},
    "coal": {"references": 875, "production": 23_935_364_096 * u.oz},
    "cobalt": {"references": 14, "production": 231_813 * u.oz},
    "coffee": {"references": 78, "production": 3_239_040 * u.lb},
    "confectionery": {"references": 21, "production": 620_827_648 * u.oz},
    "copper": {"references": 230, "production": 187_966_464 * u.oz},
    "coppersmelting": {"references": 47, "production": 36_544_466 * u.oz},
    "coppersmithing": {"references": 26, "production": 24_107_504 * u.oz},
    "coriander": {"references": 1, "production": 56_125 * u.oz},
    "cosmetics": {"references": 2, "production": 269_431 * u.oz},
    "cotton cloth": {
        "references": 227,
        "production": 339_151_777 * u.sqyd,
    },
    "cotton goods": {"references": 63, "production": 70_835_498 * u.sqyd},
    "cotton": {"references": 338, "production": 4_774_748_160 * u.oz},
    "cumin": {"references": 2, "production": 9_989_038 * u.oz},
    "dairying": {
        "references": 140,
    },
    "diamond": {"references": 65, "production": 3279 * u.oz},
    "distilling": {
        "references": 142,
        "production": 272_108_021 * u.oz,
    },
    "dogs": {"references": 4, "production": 10_127 * u.head},
    "dolomite": {"references": 2, "production": 378_216_586 * u.oz},
    "donkeys": {"references": 41, "production": 446_900 * u.head},
    "dried fish": {"references": 117, "production": 339_813_736 * u.oz},
    "dried fruit": {"references": 51, "production": 32_606_945 * u.oz},
    "dried meat": {"references": 9, "production": 177_049_600 * u.oz},
    "dyestuff": {"references": 71, "production": 11_495_703 * u.oz},
    "elephants": {"references": 10, "production": 50_637 * u.head},
    "embroidery": {"references": 46, "production": 788_234 * u.sqin},
    "emery": {"references": 5, "production": 89_035_630 * u.oz},
    "fish": {"references": 659, "production": 486_045_594 * u.oz},
    "flax": {"references": 101, "production": 498_175_000 * u.oz},
    "flint": {"references": 12, "production": 567_417_633 * u.oz},
    "flour": {"references": 232, "production": 12_384_870_400 * u.oz},
    "foodstuffs": {
        "references": 223,
    },
    "fowl": {"references": 59, "production": 140_660_000 * u.head},
    "freestone": {"references": 2, "production": 196_715_129 * u.oz},
    "fruit": {
        "references": 518,
        "production": 1_354_602_965 * u.oz,
    },  # category
    "furnishings": {
        "references": 160,
    },
    "furniture": {
        "references": 151,
    },
    "furs": {
        "references": 77,
    },
    "ginger": {"references": 7, "production": 55_603_395 * u.oz},
    "ginseng": {"references": 7, "production": 367_862 * u.oz},
    "glassware": {"references": 152, "production": 29_090_818 * u.oz},
    "goats": {"references": 129, "production": 6_294_340 * u.head},
    "gold": {"references": 237, "production": 311_529 * u.oz},
    "goldsmithing": {"references": 21, "production": 38_195 * u.oz},
    "grapes": {"references": 351, "production": 321_922_048 * u.oz},
    "griffs": {"references": 40, "production": 12_659 * u.head},
    "groundnuts": {
        "references": 89,
        "production": 1_104_588_800 * u.oz,
        "category": "nuts",
    },
    "guano": {"references": 2, "production": 74_547_200 * u.oz},
    "hemp goods": {
        # why in oz
        "references": 18,
        "production": 57_008_085 * u.oz,
    },
    "hemp": {
        "references": 95,
    },
    "hides": {"references": 349, "production": 251_023_360 * u.oz},
    "honey": {"references": 43, "production": 51_173_504 * u.oz},
    "hops": {"references": 23, "production": 6_104_412 * u.oz},
    "horses": {"references": 185, "production": 546_880 * u.head},
    "ink": {"references": 12, "production": 7_456_870 * u.oz},
    "iron": {"references": 512, "production": 20_176_558_080 * u.oz},
    "ironmongery": {
        "references": 74,
        "production": 991_353_858 * u.oz,
    },
    "ivory": {"references": 23, "production": 830_742 * u.oz},
    "kaolin": {"references": 43, "production": 1_082_152_960 * u.oz},
    "lace": {
        "references": 78,
    },
    "lamp oil": {
        "references": 84,
        "production": 30_638_272 * u.lb,
    },
    "lead": {"references": 214, "production": 109_691_904 * u.oz},
    "leadsmelting": {"references": 16, "production": 9_627_338 * u.oz},
    "leadsmithing": {"references": 4, "production": 1_553_947 * u.oz},
    "leathercraft": {
        # leatherworker
        "references": 165,
    },
    "leopards": {"references": 1, "production": 5064 * u.head},
    "licorice": {"references": 9, "production": 2_150_400 * u.oz},
    "limestone": {"references": 79, "production": 10_712_144_744 * u.oz},
    "linen goods": {"references": 24, "production": 771_181 * u.sqyd},
    "linen": {"references": 112, "production": 5_945_558 * u.sqyd},
    "lithographic stone": {
        "references": 2,
        "production": 232_312_699 * u.oz,
    },
    "livestock": {
        # stockyard
        "references": 484,
    },
    "lye": {"references": 2, "production": 10_054_464 * u.lb},
    "magnesite": {"references": 21, "production": 1_186_418_688 * u.oz},
    "maize": {
        "references": 275,
    },
    "malt": {"references": 8, "production": 68_919_962 * u.oz},
    "manganese": {"references": 106, "production": 273_824_768 * u.oz},
    "marble": {
        "references": 89,
    },
    "markets": {
        "references": 3159,
    },
    "masonry": {"references": 42, "production": 4_586_605_064 * u.oz},
    "meat": {
        "references": 98,
    },
    "medicinal plants": {
        # medicinal agents
        "references": 51,
        "production": 478_536 * u.oz,
    },
    "meerschaum": {"references": 1, "production": 37_315_619 * u.oz},
    "mercury": {"references": 38, "production": 307_292 * u.oz},
    "metalsmithing": {
        "references": 133,
    },
    "milk": {
        "references": 17,
        "production": 27_033_753_600 * u.oz,
    },  # why not floz
    "millet": {
        # dont confuse with mullet
        "references": 165,
    },
    "mineral water": {"references": 13, "production": 338_326 * u.floz},
    "mithril": {"references": 13, "production": 297_760 * u.oz},
    "molybdenum": {"references": 16, "production": 1_250_032 * u.oz},
    "mules": {"references": 33, "production": 126_200 * u.head},
    "mustard": {
        "references": 4,
        "production": 64_365_645 * u.oz,
    },  # mustard and sauces
    "nickel": {"references": 30, "production": 22_488_812 * u.oz},
    "nickelsmelting": {"references": 5, "production": 3_806_386 * u.oz},
    "niter": {"references": 2, "production": 470_938 * u.lb},
    "nutmeg": {"references": 2, "production": 5_304_320 * u.oz},
    "oats": {
        "references": 158,
    },
    "obsidian": {"references": 1, "production": 40_960_000 * u.oz},
    "oilseed": {"references": 29, "production": 6_573_916_160 * u.oz},
    "olive oil": {
        "references": 109,
    },
    "olives": {
        "references": 219,
    },
    "opium": {"references": 26, "production": 300_489 * u.oz},
    "ostrich feathers": {"references": 0, "production": 44_848 * u.oz},
    "paper": {"references": 255, "production": 42_824_340 * u.oz},
    "paprika": {"references": 2, "production": 25_017_969 * u.oz},
    "peat": {"references": 33, "production": 1_435_105_289 * u.oz},
    "pepper": {"references": 20, "production": 24_657_920 * u.oz},
    "perfume": {"references": 41, "production": 3_204_813 * u.oz},
    "perry": {"references": 3, "production": 1_120_000 * u.floz},
    "phosphorus": {"references": 7, "production": 128_000 * u.oz},
    "pig iron": {"references": 403, "production": 8_850_520_591 * u.oz},
    "pitch": {"references": 21, "production": 2_671_872 * u.lb},
    "plant oil": {
        "references": 0,
        "production": 2_176_348_160 * u.oz,
    },  # why in oz
    "platinum": {"references": 14, "production": 25_090 * u.oz},
    "poison": {"references": 9, "production": 861_728 * u.lb},
    "porcelain": {
        "references": 73,
        "production": 77_362_504 * u.oz,
    },
    "porphyry": {"references": 4, "production": 490_784_353 * u.oz},
    "potatoes": {
        "references": 201,
    },
    "pottery": {
        "references": 142,
    },
    "pulses": {"references": 11, "production": 94_639_360_000 * u.oz},
    "pumice": {"references": 2, "production": 35_614_252 * u.oz},
    "qat": {"references": 1, "production": 11_557 * u.oz},
    "quicklime": {"references": 16, "production": 5_368_832_000 * u.oz},
    "rabbits": {"references": 1, "production": 1_352_500 * u.head},
    "red sandstone": {"references": 0, "production": 271_616_994 * u.oz},
    "refined sugar": {
        "references": 191,
    },
    "reindeer": {"references": 191, "production": 121_529 * u.head},
    "rice": {
        "references": 444,
    },
    "rough fiber cloth": {
        "references": 26,
        "production": 2_754_662_400 * u.lb,
    },
    "rough fibers": {"references": 5, "production": 22_111_332 * u.sqyd},
    "rye": {
        "references": 108,
    },
    "saffron": {"references": 8, "production": 11_476 * u.oz},
    "sal ammoniac": {"references": 1, "production": 6_314_073 * u.oz},
    "salt": {"references": 230, "production": 771_592_192 * u.oz},
    "sandstone": {"references": 19, "production": 1_795_379_121 * u.oz},
    "sea ivory": {"references": 9, "production": 1_661_504 * u.oz},
    "sheep": {"references": 353, "production": 12_288_600 * u.head},
    "shipbuilding": {
        "references": 233,
    },
    "silk cloth": {"references": 130, "production": 3_170_451 * u.sqyd},
    "silk goods": {"references": 37, "production": 839_741 * u.oz},
    "silk": {"references": 234, "production": 50_727_216 * u.oz},
    "silver": {"references": 102, "production": 2_302_362 * u.oz},
    "silversmithing": {"references": 36, "production": 736_756 * u.oz},
    "slate": {"references": 49, "production": 2_342_860_800 * u.oz},
    "slaves": {"references": 51, "production": 810_190 * u.head},
    "smelting": {
        "references": 109,
    },
    "snuff": {
        "references": 115,
        "production": 8_124_928 * u.oz,
    },
    "soap": {"references": 124, "production": 273_056_205 * u.oz},
    "soda ash": {"references": 14, "production": 63_140_730 * u.oz},
    "sorghum": {
        "references": 76,
    },
    "spices": {
        "references": 45,
        "production": 225_498_837 * u.oz,
    },  # category
    "sugar": {"references": 0, "production": 3_266_959_360 * u.oz},
    "sugarbeets": {"references": 136, "production": 1_720_268_800 * u.oz},
    "sugarcane": {"references": 143, "production": 2_866_988_800 * u.oz},
    "sulfur": {"references": 62, "production": 66_368_512 * u.oz},
    "swine": {"references": 111, "production": 13_455_560 * u.head},
    "syenite": {"references": 1, "production": 116_222_510 * u.oz},
    "talc": {"references": 5, "production": 422_400_000 * u.oz},
    "tea": {"references": 153, "production": 155_115_520 * u.oz},
    "timber": {"references": 539, "production": 114_793_944_640 * u.oz},
    "tin": {"references": 87, "production": 8_951_327 * u.oz},
    "tinsmelting": {"references": 6, "production": 695_982 * u.oz},
    "tinsmithing": {"references": 14, "production": 456_709 * u.oz},
    "tobacco": {"references": 333, "production": 342_845_440 * u.oz},
    "tools": {
        "references": 378,
        "production": 817_026_800 * u.oz,
    },  # toolmaker
    "tortoise shell": {"references": 3, "production": 237_360 * u.oz},
    "trachyte": {"references": 1, "production": 136_568_417 * u.oz},
    "treenuts": {"references": 11, "production": 19_654_656 * u.oz},
    "tubers": {"references": 8, "production": 2_906_760_192 * u.oz},
    "tufa": {"references": 1, "production": 188_684_597 * u.oz},
    "tuff": {"references": 1, "production": 80_664_348 * u.oz},
    "tungsten": {"references": 41, "production": 2_670_864 * u.oz},
    "turmeric": {"references": 2, "production": 57_344_000 * u.oz},
    "vegetables": {"references": 375, "production": 2_456_882_176 * u.oz},
    "wagons": {
        # wainwright
        "references": 190,
    },
    "wax": {
        # cf candles and wax
        "references": 0,
        "production": 12_837_888 * u.oz,
    },
    "whale oil": {"references": 28, "production": 8_078_336 * u.floz},
    "wheat": {
        # category
        "references": 567,
    },
    "wine": {"references": 361, "production": 1_508_266_707 * u.floz},
    "witherite": {"references": 2, "production": 2_751_078 * u.oz},
    "wood alcohol": {"references": 6, "production": 287_275 * u.pint},
    "woodcraft": {
        "references": 124,
    },
    "wooden tools": {
        "references": 110,
    },
    "wool cloth": {"references": 111, "production": 13_791_196 * u.sqyd},
    "wool": {"references": 147, "production": 33_323_136 * u.lb},
    "woolens": {
        "references": 116,
        "production": 7_009_387 * u.sqyd,
    },
    "zinc": {"references": 129, "production": 231_232_512 * u.oz},
    "zincsmelting": {"references": 9, "production": 18_171_375 * u.oz},
}

for r, info in world_references.items():
    # decimalize reference counts and production totals
    info["references"] = Decimal(info["references"])
    if "production" in info:
        info["production"] = (
            Decimal(info["production"].magnitude) * info["production"].units
        )
    else:
        info["production"] = Decimal(0) * u.unit
    # set production per reference
    refs = info["references"]
    prod = info["production"]
    if refs == 0 or prod.magnitude == 0:
        # 'zero problem' - see towns.py
        continue
    else:
        # pull this into a function of commodity name
        info["production per reference"] = (prod.magnitude / refs) * prod.units



def main():
    for w, info in world_references.items():
        refs = info["references"]
        ppr = info.get("production per reference")
        prod = info["production"]
        name = w.title()
        if ppr:
            print(f"{name}: {refs} refs at {ppr}")
        elif refs and not prod:
            print(f"{name}: {refs} refs")
        else:
            print(f"{name}: world production {prod}")


if __name__ == "__main__":
    main()
