from decimal import Decimal
from .TownInfo import towns


# this dictionary holds world production figures, with both amounts and units thereof,
# for each of the resources listed below.
# these are currently listed at 1/1000 of their full world size
worldProductionMatrix = {}

populationSum = 0
for t,d in towns.items():
    populationSum += d.population
worldProductionMatrix["labor"] = (populationSum,"head")
worldProductionMatrix["flax"] = (10000000,"lb")
worldProductionMatrix["timber"] = (2000000, "cuft")
worldProductionMatrix["arable land"] = (10000000, "acre")
worldProductionMatrix["clay"] = (10000000, "lb")
worldProductionMatrix["cereal"] = (10000000, "lb")
worldProductionMatrix["hops"] = (1000000, "lb")
worldProductionMatrix["sugarcane"] = (1000000, "lb")
worldProductionMatrix["cod"] = (500000, "lb")
worldProductionMatrix["herring"] = (500000, "lb")
worldProductionMatrix["tobacco"] = (1943618, "lb")
worldProductionMatrix["cotton"] = (10000000, "lb")

worldProductionMatrix["iron ore"] = (1000000000,"lb") 
worldProductionMatrix["manganese ore"] = (80000000, "lb")
worldProductionMatrix["nickel ore"] = (60000000, "lb")
worldProductionMatrix["zinc ore"] = (40000000,"lb")
worldProductionMatrix["copper ore"] = (20000000, "lb")
worldProductionMatrix["cobalt ore"] = (5000000, "lb")
worldProductionMatrix["lead ore"] = (2500000, "lb")
worldProductionMatrix["tin ore"] = (1250000, "lb")
worldProductionMatrix["silver ore"]= (625000, "lb")
worldProductionMatrix["cinnabar"] = (312500, "lb")
# cinnabar = ore from which mercury is refined
worldProductionMatrix["platinum ore"] = (156250, "lb")
worldProductionMatrix["gold ore"] = (78125, "lb")
worldProductionMatrix["mithril ore"] = (40000, "lb")
worldProductionMatrix["adamantine ore"] = (20000, "lb")
worldProductionMatrix["lapis lazuli"] = (50000, "lb")

stoneAndMinerals = ["chalk","coal","salt","talc","emery","granite",
                    "marble","slate","flint","obsidian","phosphorus rock",
                    "witherite","sulfate", "limestone"]

for sm in stoneAndMinerals:
    worldProductionMatrix[sm] = (1000000,"lb")
worldProductionMatrix["limestone"] = (2000000,"lb")


preciousGems = [("ruby",10),("emerald",10),("topaz",10),("sapphire",10),
                ("diamond",3)]

for pg in preciousGems:
    name = pg[0]
    worldProductionMatrix[name] = (1000 * pg[1], "lb")

ornamentalGems = ["agate","azurite","cat's eye","hawk's eye","hematite",
                    "malachite","lapis lazuli","mother-of-pearl","quartz",
                    "tiger eye","turquoise"]

for og in ornamentalGems:
    worldProductionMatrix[og] = (50000,"lb")
