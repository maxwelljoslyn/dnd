from decimal import getcontext, Decimal, DivisionByZero

getcontext().prec = 6

# done so far: everything in top 99 references (whether or not they have a production total)
# PLUS all other references which have extant production totals
world_references = {
    "acid": {"references": 0, "production": (3_957_453, "oz")},
    "adamantine": {"references": 6, "production": (297_760, "oz")},
    "alabaster": {"references": 8, "production": (1_092_766_558, "oz")},
    "alchemy": {
        "references": 321,
        "production": (0, "unit"),
    },  # alchemist
    "alloys": {
        "references": 119,
        "production": (0, "unit"),
    },
    "alum": {"references": 6, "production": (1_478_185, "oz")},
    "anise": {"references": 3, "production": (196_332, "oz")},
    "antimony": {"references": 43, "production": (3_359_461, "oz")},
    "antimonysmelting": {"references": 2, "production": (180_736, "oz")},
    "apples": {
        "references": 78,
        "production": (0, "unit"),
    },
    "arsenic": {"references": 11, "production": (236_480, "oz")},
    "artistic glassware": {"references": 0, "production": (3_607_423, "oz")},
    "barley": {
        "references": 212,
        "production": (0, "unit"),
    },
    "basalt": {"references": 2, "production": (222_700_425, "oz")},
    "bear paws": {"references": 1, "production": (224_256, "oz")},
    "bismuth": {"references": 4, "production": (312_508, "oz")},
    "bitter salt": {"references": 14, "production": (75_768_877, "oz")},
    "black powder": {"references": 5, "production": (254_061, "lb")},
    "bookbinding": {"references": 101, "production": (0, "unit")},
    "boots and shoes": {
        "references": 105,
        "production": (0, "unit"),
    },
    "brewing": {
        "references": 198,
        "production": (3_972_035_901, "fl oz"),
    },  # category
    "bricks": {"references": 98, "production": (4_056_185_600, "oz")},
    "bristles": {"references": 19, "production": (35_881_488, "oz")},
    "brownstone": {"references": 1, "production": (203_389_393, "oz")},
    "building stone": {
        "references": 74,
        "production": (0, "unit"),
    },
    "butter": {"references": 84, "production": (435_499_008, "oz")},
    "cacao": {"references": 48, "production": (20_142_080, "oz")},
    "camels": {"references": 76, "production": (373_900, "head")},
    "candles and wax": {"references": 95, "production": (0, "unit")},
    "cardamom": {"references": 7, "production": (2_508_800, "oz")},
    "carpets": {"references": 110, "production": (519_502, "sq yd")},
    "carts": {
        "references": 72,
        "production": (0, "unit"),
    },
    "cattle": {"references": 486, "production": (12_588_600, "head")},
    "caviar": {"references": 10, "production": (28_672, "oz")},
    "cement": {"references": 131, "production": (6_218_604_800, "oz")},
    "ceramics": {"references": 57, "production": (162_713_528, "oz")},
    "cereals": {"references": 619, "production": (91_834_982_400, "oz")},
    "chalk": {"references": 7, "production": (1_187_020_800, "oz")},
    "chamomile": {"references": 1, "production": (5_017_600, "oz")},
    "cheese": {"references": 84, "production": (682_264_576, "oz")},
    "chromium": {"references": 43, "production": (135_618_560, "oz")},
    "cider": {"references": 24, "production": (8_960_000, "fl oz")},
    "cinnamon": {"references": 9, "production": (8_673_280, "oz")},
    "cloth": {
        "references": 599,
        "production": (0, "unit"),
    },  # weaver (no production total)
    "clothing": {
        "references": 93,
        "production": (0, "unit"),
    },
    "cloves": {"references": 7, "production": (8_458_240, "oz")},
    "coal": {"references": 875, "production": (23_935_364_096, "oz")},
    "cobalt": {"references": 14, "production": (231_813, "oz")},
    "coffee": {"references": 78, "production": (3_239_040, "lb")},
    "confectionery": {"references": 21, "production": (620_827_648, "oz")},
    "copper": {"references": 230, "production": (187_966_464, "oz")},
    "coppersmelting": {"references": 47, "production": (36_544_466, "oz")},
    "coppersmithing": {"references": 26, "production": (24_107_504, "oz")},
    "coriander": {"references": 1, "production": (56_125, "oz")},
    "cosmetics": {"references": 2, "production": (269_431, "oz")},
    "cotton cloth": {
        "references": 227,
        "production": (339_151_777, "sq yd"),
    },
    "cotton goods": {"references": 63, "production": (70_835_498, "sq yd")},
    "cotton": {"references": 338, "production": (4_774_748_160, "oz")},
    "cumin": {"references": 2, "production": (9_989_038, "oz")},
    "dairying": {
        "references": 140,
        "production": (0, "unit"),
    },
    "diamonds": {"references": 65, "production": (464_790, "carat")},
    "distilling": {
        "references": 142,
        "production": (272_108_021, "oz"),
    },
    "dogs": {"references": 4, "production": (10_127, "head")},
    "dolomite": {"references": 2, "production": (378_216_586, "oz")},
    "donkeys": {"references": 41, "production": (446_900, "head")},
    "dried fish": {"references": 117, "production": (339_813_736, "oz")},
    "dried fruit": {"references": 51, "production": (32_606_945, "oz")},
    "dried meat": {"references": 9, "production": (177_049_600, "oz")},
    "dyestuff": {"references": 71, "production": (11_495_703, "oz")},
    "elephants": {"references": 10, "production": (50_637, "head")},
    "embroidery": {"references": 46, "production": (788_234, "sq in")},
    "emery": {"references": 5, "production": (89_035_630, "oz")},
    "fish": {"references": 659, "production": (486_045_594, "oz")},
    "flax": {"references": 101, "production": (498_175_000, "oz")},
    "flint": {"references": 12, "production": (567_417_633, "oz")},
    "flour": {"references": 232, "production": (12_384_870_400, "oz")},
    "foodstuffs": {
        "references": 223,
        "production": (0, "unit"),
    },
    "fowl": {"references": 59, "production": (140_660_000, "head")},
    "freestone": {"references": 2, "production": (196_715_129, "oz")},
    "fruit": {
        "references": 518,
        "production": (1_354_602_965, "oz"),
    },  # category
    "furnishings": {
        "references": 160,
        "production": (0, "unit"),
    },  # no production
    "furniture": {
        "references": 151,
        "production": (0, "unit"),
    },
    "furs": {"references": 77, "production": (0, "unit")},
    "ginger": {"references": 7, "production": (55_603_395, "oz")},
    "ginseng": {"references": 7, "production": (367_862, "oz")},
    "glassware": {"references": 152, "production": (29_090_818, "oz")},
    "goats": {"references": 129, "production": (6_294_340, "head")},
    "gold": {"references": 237, "production": (311_529, "oz")},
    "goldsmithing": {"references": 21, "production": (38_195, "oz")},
    "grapes": {"references": 351, "production": (321_922_048, "oz")},
    "griffs": {"references": 40, "production": (12_659, "head")},
    "groundnuts": {"references": 89, "production": (1_104_588_800, "oz")},
    "guano": {"references": 2, "production": (74_547_200, "oz")},
    "hemp goods": {"references": 18, "production": (57_008_085, "oz")},  # why in oz
    "hemp": {
        "references": 95,
        "production": (0, "unit"),
    },
    "hides": {"references": 349, "production": (251_023_360, "oz")},
    "honey": {"references": 43, "production": (51_173_504, "oz")},
    "hops": {"references": 23, "production": (6_104_412, "oz")},
    "horses": {"references": 185, "production": (546_880, "head")},
    "ink": {"references": 12, "production": (7_456_870, "oz")},
    "iron": {"references": 512, "production": (20_176_558_080, "oz")},
    "ironmongery": {
        "references": 74,
        "production": (991_353_858, "oz"),
    },
    "ivory": {"references": 23, "production": (830_742, "oz")},
    "kaolin": {"references": 43, "production": (1_082_152_960, "oz")},
    "lace": {"references": 78, "production": (0, "unit")},
    "lamp oil": {
        "references": 84,
        "production": (30_638_272, "lb"),
    },
    "lead": {"references": 214, "production": (109_691_904, "oz")},
    "leadsmelting": {"references": 16, "production": (9_627_338, "oz")},
    "leadsmithing": {"references": 4, "production": (1_553_947, "oz")},
    "leathercraft": {
        "references": 165,
        "production": (0, "unit"),
    },  # leatherworker
    "leopards": {"references": 1, "production": (5064, "head")},
    "licorice": {"references": 9, "production": (2_150_400, "oz")},
    "limestone": {"references": 79, "production": (10_712_144_744, "oz")},
    "linen goods": {"references": 24, "production": (771_181, "sq yd")},
    "linen": {"references": 112, "production": (5_945_558, "sq yd")},
    "lithographic stone": {"references": 2, "production": (232_312_699, "oz")},
    "livestock": {
        "references": 484,
        "production": (0, "unit"),
    },  # stockyard
    "lye": {"references": 2, "production": (10_054_464, "lb")},
    "magnesite": {"references": 21, "production": (1_186_418_688, "oz")},
    "maize": {
        "references": 275,
        "production": (0, "unit"),
    },
    "malt": {"references": 8, "production": (68_919_962, "oz")},
    "manganese": {"references": 106, "production": (273_824_768, "oz")},
    "marble": {
        "references": 89,
        "production": (0, "unit"),
    },
    "markets": {
        "references": 3159,
        "production": (0, "unit"),
    },
    "masonry": {"references": 42, "production": (4_586_605_064, "oz")},
    "meat": {
        "references": 98,
        "production": (0, "unit"),
    },
    "medicinal plants": {
        "references": 51,
        "production": (478_536, "oz"),
    },  # medicinal agents
    "meerschaum": {"references": 1, "production": (37_315_619, "oz")},
    "mercury": {"references": 38, "production": (307_292, "oz")},
    "metalsmithing": {
        "references": 133,
        "production": (0, "unit"),
    },
    "milk": {"references": 17, "production": (27_033_753_600, "oz")},  # why not fl oz
    "millet": {
        "references": 165,
        "production": (0, "unit"),
    },  # dont confuse with mullet
    "mineral water": {"references": 13, "production": (338_326, "fl oz")},
    "mithril": {"references": 13, "production": (297_760, "oz")},
    "molybdenum": {"references": 16, "production": (1_250_032, "oz")},
    "mules": {"references": 33, "production": (126_200, "head")},
    "mustard": {
        "references": 4,
        "production": (64_365_645, "oz"),
    },  # mustard and sauces
    "nickel": {"references": 30, "production": (22_488_812, "oz")},
    "nickelsmelting": {"references": 5, "production": (3_806_386, "oz")},
    "niter": {"references": 2, "production": (470_938, "lb")},
    "nutmeg": {"references": 2, "production": (5_304_320, "oz")},
    "oats": {
        "references": 158,
        "production": (0, "unit"),
    },
    "obsidian": {"references": 1, "production": (40_960_000, "oz")},
    "oilseed": {"references": 29, "production": (6_573_916_160, "oz")},
    "olive oil": {
        "references": 109,
        "production": (0, "unit"),
    },
    "olives": {
        "references": 219,
        "production": (0, "unit"),
    },
    "opium": {"references": 26, "production": (300_489, "oz")},
    "ostrich feathers": {"references": 0, "production": (44_848, "oz")},
    "paper": {"references": 255, "production": (42_824_340, "oz")},
    "paprika": {"references": 2, "production": (25_017_969, "oz")},
    "peat": {"references": 33, "production": (1_435_105_289, "oz")},
    "pepper": {"references": 20, "production": (24_657_920, "oz")},
    "perfume": {"references": 41, "production": (3_204_813, "oz")},
    "perry": {"references": 3, "production": (1_120_000, "fl oz")},
    "phosphorus": {"references": 7, "production": (128_000, "oz")},
    "pig iron": {"references": 403, "production": (8_850_520_591, "oz")},
    "pitch": {"references": 21, "production": (2_671_872, "lb")},
    "plant oil": {"references": 0, "production": (2_176_348_160, "oz")},  # why in oz
    "platinum": {"references": 14, "production": (25_090, "oz")},
    "poison": {"references": 9, "production": (861_728, "lb")},
    "porcelain": {
        "references": 73,
        "production": (77_362_504, "oz"),
    },
    "porphyry": {"references": 4, "production": (490_784_353, "oz")},
    "potatoes": {
        "references": 201,
        "production": (0, "unit"),
    },
    "pottery": {
        "references": 142,
        "production": (0, "unit"),
    },
    "pulses": {"references": 11, "production": (94_639_360_000, "oz")},
    "pumice": {"references": 2, "production": (35_614_252, "oz")},
    "qat": {"references": 1, "production": (11_557, "oz")},
    "quicklime": {"references": 16, "production": (5_368_832_000, "oz")},
    "rabbits": {"references": 1, "production": (1_352_500, "head")},
    "red sandstone": {"references": 0, "production": (271_616_994, "oz")},
    "refined sugar": {
        "references": 191,
        "production": (0, "unit"),
    },
    "reindeer": {"references": 191, "production": (121_529, "head")},
    "rice": {
        "references": 444,
        "production": (0, "unit"),
    },
    "rough fiber cloth": {"references": 26, "production": (2_754_662_400, "lb")},
    "rough fibers": {"references": 5, "production": (22_111_332, "sq yd")},
    "rye": {
        "references": 108,
        "production": (0, "unit"),
    },
    "saffron": {"references": 8, "production": (11_476, "oz")},
    "sal ammoniac": {"references": 1, "production": (6_314_073, "oz")},
    "salt": {"references": 230, "production": (771_592_192, "oz")},
    "sandstone": {"references": 19, "production": (1_795_379_121, "oz")},
    "sea ivory": {"references": 9, "production": (1_661_504, "oz")},
    "sheep": {"references": 353, "production": (12_288_600, "head")},
    "shipbuilding": {
        "references": 233,
        "production": (0, "unit"),
    },
    "silk cloth": {"references": 130, "production": (3_170_451, "sq yd")},
    "silk goods": {"references": 37, "production": (839_741, "oz")},
    "silk": {"references": 234, "production": (50_727_216, "oz")},
    "silver": {"references": 102, "production": (2_302_362, "oz")},
    "silversmithing": {"references": 36, "production": (736_756, "oz")},
    "slate": {"references": 49, "production": (2_342_860_800, "oz")},
    "slaves": {"references": 51, "production": (810_190, "head")},
    "smelting": {
        "references": 109,
        "production": (0, "unit"),
    },
    "snuff": {
        "references": 115,
        "production": (8_124_928, "oz"),
    },
    "soap": {"references": 124, "production": (273_056_205, "oz")},
    "soda ash": {"references": 14, "production": (63_140_730, "oz")},
    "sorghum": {"references": 76, "production": (0, "unit")},
    "spices": {"references": 45, "production": (225_498_837, "oz")},  # category
    "sugar": {"references": 0, "production": (3_266_959_360, "oz")},
    "sugarbeets": {"references": 136, "production": (1_720_268_800, "oz")},
    "sugarcane": {"references": 143, "production": (2_866_988_800, "oz")},
    "sulfur": {"references": 62, "production": (66_368_512, "oz")},
    "swine": {"references": 111, "production": (13_455_560, "head")},
    "syenite": {"references": 1, "production": (116_222_510, "oz")},
    "talc": {"references": 5, "production": (422_400_000, "oz")},
    "tea": {"references": 153, "production": (155_115_520, "oz")},
    "timber": {"references": 539, "production": (114_793_944_640, "oz")},
    "tin": {"references": 87, "production": (8_951_327, "oz")},
    "tinsmelting": {"references": 6, "production": (695_982, "oz")},
    "tinsmithing": {"references": 14, "production": (456_709, "oz")},
    "tobacco": {"references": 333, "production": (342_845_440, "oz")},
    "tools": {"references": 378, "production": (817_026_800, "oz")},  # toolmaker
    "tortoise shell": {"references": 3, "production": (237_360, "oz")},
    "trachyte": {"references": 1, "production": (136_568_417, "oz")},
    "treenuts": {"references": 11, "production": (19_654_656, "oz")},
    "tubers": {"references": 8, "production": (2_906_760_192, "oz")},
    "tufa": {"references": 1, "production": (188_684_597, "oz")},
    "tuff": {"references": 1, "production": (80_664_348, "oz")},
    "tungsten": {"references": 41, "production": (2_670_864, "oz")},
    "turmeric": {"references": 2, "production": (57_344_000, "oz")},
    "vegetables": {"references": 375, "production": (2_456_882_176, "oz")},
    "wagons": {
        "references": 190,
        "production": (0, "unit"),
    },  # wainwright
    "wax": {"references": 0, "production": (12_837_888, "oz")},  # cf candles and wax
    "whale oil": {"references": 28, "production": (8_078_336, "fl oz")},
    "wheat": {
        "references": 567,
        "production": (0, "unit"),
    },  # category
    "wine": {"references": 361, "production": (1_508_266_707, "fl oz")},
    "witherite": {"references": 2, "production": (2_751_078, "oz")},
    "wood alcohol": {"references": 6, "production": (287_275, "pint")},
    "woodcraft": {
        "references": 124,
        "production": (0, "unit"),
    },
    "wooden tools": {
        "references": 110,
        "production": (0, "unit"),
    },
    "wool cloth": {"references": 111, "production": (13_791_196, "sq yd")},
    "wool": {"references": 147, "production": (33_323_136, "lb")},
    "woolens": {
        "references": 116,
        "production": (7_009_387, "sq yd"),
    },
    "zinc": {"references": 129, "production": (231_232_512, "oz")},
    "zincsmelting": {"references": 9, "production": (18_171_375, "oz")},
}

# decimalize all production totals
for r, info in world_references.items():
    amount, unit = info["production"][0], info["production"][1]
    info["production"] = Decimal(amount), unit


def main():
    for w, info in world_references.items():
        refs = info["references"]
        amount, unit = info["production"][0], info["production"][1]
        name = w.title()
        if refs:
            per_refs = amount / refs
            print(f"{name}: {refs} refs at {per_refs} {unit} each")
        else:
            print(f"{name}: world production {amount} {unit}")


if __name__ == "__main__":
    main()
