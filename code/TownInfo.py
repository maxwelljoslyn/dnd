from decimal import *


class Town():
    """Stores data associated with a given town."""
    def __init__(self,coord,population,resources,services):
        self.coord = coord
        self.population = Decimal(population)
        self.resources = resources
        self.resources["labor"] = self.population / Decimal(1000)
        self.services = services
        self.services["laborer"] = self.resources["labor"]
        self.blackMarket = False

towns = {}
connections = {}

def addConnection(town_a,town_b):
    # check against not-yet-inserted
    if town_a not in connections:
        connections[town_a] = []
    connections[town_a].append(town_b)
    if town_b not in connections:
        connections[town_b] = []
    connections[town_b].append(town_a)

# the meat of this file: the actual data on each town,
# and setting up the connections between them
# note that the distance of the roads connecting towns
# is not determined by hand!
# the computer will do that for me,
# finding both the path of the road and the distance along it

# hill and mountain areas
# example industry: mining, clay, pottery, etc
towns["Guroff"]=Town((47,-63,16),
                     2382,
                     {"clay":1, "iron ore":2},
                     {"potter":1})
towns["Nender"] = Town((48,-66,18),
                       1000,
                       {"coal":1, "tin ore":1, "iron ore":1},
                       {"tinsmith":1})
towns["Pwodd"] = Town((49,-65,16),
                      1000,
                      {"gold ore":1, "silver ore":1},
                      {"goldsmith":1, "silversmith":1})

# Fulgarri has a mediterannean climate but is also a bit high in altitude
towns["Fulgarri"] = Town((47,-59,12),
                         1500,
                         {"copper ore":1, "lead ore":1},
                         {"coppersmith":1})
towns["Widder"] = Town((49,-63,14),
                       1162,
                       {"nickel ore":1, "manganese ore":2},
                       {"blacksmith":2})
towns["Yog"] = Town((45,-60,15),
                    1703,
                    {"limestone":2, "iron ore":1},
                    {"smelter":1, "blacksmith":2, "tailor":1})

# mostly plains and broad expanses
# as you go more towards DR you get more woodsy (the direction of jungly Drode)
# example industry: smelting, timber, carpentry, carving, farming, cereals; brewing, vineyards
towns["Veder Vek"] = Town((44,-62,18),
                          3252,
                          {"arable land":1, "hops":1},
                          {"hatter":1, "leatherworker":2, "baker":2, "farmer":2, "brewer":1, "tanner":1})
towns["Ekodo"] = Town((44,-64,20),
                      1686,
                      {"cereal":1, "timber":2},
                      {"cooper":1, "smelter":1, "carver":2, "miller":1, "farmer":1, "butcher":1})
towns["Kededal"] = Town((43,-60,17),
                        2109,
                        {"timber":1,"flax":1},
                        {"vintner":1, "spinner":2, "carpenter":1, "farmer":1})
towns["Gootonu"] = Town((43,-66,23),
                        8739,
                        {"cereal":1, "iron ore":1},
                        {"miller":2, "butcher":1, "tanner":2, "innkeeper":1})
# more southerly, warmer cities
# example: shipping, salt, sugarcane, shipwright, tobacco, shells
towns["Torkada"] = Town((42,-67,25),
                        916,
                        {"cod":1, "arable land":1},
                        {"baker":1, "dyer":1, "weaver":2, "sailor":1, "miller":1})
towns["Serdabach"] = Town((45,-68,23),
                          3913,
                          {"herring":1,"salt":1, "timber":1, "sugarcane":1, "cotton":1},
                          {"ropewalker":1, "shipwright":1, "lumpman":1,"smelter":1, "carpenter":2, "brewer":1, "embroiderer": 1})
towns["Berdorl"] = Town((43,-69,26),
                        2966,
                        {"sugarcane":1, "cotton":1, "zinc ore": 1},
                        {"hatter":1, "ropewalker":1, "carpenter":1 ,"blacksmith":1, "innkeeper":1})

# more central, slightly colder-climate port
# same as other ports, plus whales
towns["Ror Kadda"] = Town((41,-62,21),
                          1152,
                        {"cod":2,"flax":1},
                        {"ropewalker":1, "chandler":1, "shipwright":2,"carver":1})

# Drode is jungley, thought not as dense as true rainforest to the south
# Dreot has a bit of mild jungle in its lowlands, with open hills and river valleys
# thus Drode has timber, herbs, plants; Dreot has fish, coal, etc.
towns["Dreot"] = Town((47,-67,20),
                      1500,
                      {"timber":1},
                      {"tailor":1, "miller":1, "carpenter":1, "cooper":1, "fuller":1})
towns["Drode"] = Town((48,-68,20),
                      1500,
                      {"cereal":1, "timber":1, "tobacco":1},
                      {"cobbler":1,"alchemist":1, "glassblower":1})

# moving west
# this town should be very powerful since it has access to the sea AND the small inland sea
towns["Nam Gong"] = Town((40,-67,27),
                         5089,
                         {"cod":1, "herring":1, "tobacco":1},
                         {"shipwright":1,"fishmonger":1,"tobacconist":1})

towns["Gungoya"] = Town((41,-70,29),
                        1900,
                       {"timber":2, "lead ore":1},
                       {"cobbler":1, "hatter":1, "smelter":1})

towns["Chelong"] = Town((40,-71,31),
                        1157,
                          {"lead ore":1, "phosphorus rock":1, "sulfate":1},
                          {"glassblower":2, "bookbinder":1})

towns["Xin Qia"] = Town((38,-72,34),
                        2034,
                        {"lapis lazuli":1},
                        {"bowyer":1, "bookbinder":1, "cheesemonger":1})

towns["Jiu Qia"] = Town((38,-70,32),
                        1890,
                        {"cinnabar":1},
                        {"locksmith":1})

addConnection("Gungoya","Chelong")
addConnection("Chelong","Xin Qia")
addConnection("Xin Qia","Jiu Qia")
addConnection("Gungoya", "Berdorl")
addConnection("Nam Gong","Torkada")
addConnection("Dreot","Drode")
addConnection("Yog","Fulgarri")
addConnection("Ror Kadda","Veder Vek")
addConnection("Yog","Guroff")
addConnection("Pwodd","Widder")
addConnection("Widder","Guroff")
addConnection("Nender","Pwodd")
addConnection("Dreot","Nender")
addConnection("Dreot","Ekodo")
addConnection("Yog","Kededal")
addConnection("Kededal","Veder Vek")
addConnection("Gootonu","Serdabach")
addConnection("Torkada","Berdorl")
addConnection("Torkada", "Gootonu")
addConnection("Ekodo","Gootonu")
addConnection("Veder Vek","Ekodo")
