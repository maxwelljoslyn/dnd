from decimal import *
from math import pi
from .ResourcePriceCalculator import allServiceNames

#set up the Decimal environment
getcontext().prec = 4

class Recipe:
    """This class holds the structure of a product's recipe, including which resources or other recipes are needed
    to make it, and how much of those amounts are needed, the service needed to create this recipe, and the difficulty
    of doing so."""
    def __init__(self, service, weight, subRaws, subRecipes=[], unit=None, difficulty=1, description=""):
        self.service = service
        self.difficulty = difficulty
        self.subRaws = subRaws
        self.subRecipes = subRecipes
        self.weight = (Decimal(weight[0]),weight[1])
        self.description = description
        # description of item, including dimensions, weight, properties
        # there may be some subclasses of Recipe specific to particular item types, such as Weapon and Armor,
        # since those have special details (AC, damage dice, break chance, etc)
        if unit is None:
            self.unit = self.weight
        else:
            self.unit = (Decimal(unit[0]),unit[1])

# keys in this dict are recipe names, used in printing
# values are Recipe objects
# when defining a Recipe, it is added to this dict
recipeStorage = {}

# semiGoods are those items whose prices need to be calculated to produce more complex items,
# but which themselves are not sold at market.
# the quintessential example is pig iron, which is brittle and mostly useless, but is the first step in making steel.
# if a key is stored in semiGoods, then it will not be printed by recipeRunner.main()
semiGoods = []

# measurements of this and that kind
densityCastIron = Decimal(454.8)
densityWroughtIron = 483 # lb/cu. ft
densitySteel = 489 # lbs/cu ft
# giving a density for generic timber until diversified, neither too soft nor too hard
densityTimber = 40 # lb/cu ft
densityMilk = Decimal(64.48808) # 1033 kg/cu meter, converted to lb/cu ft
cuFtPerGallonLiquid = 1 / Decimal(7.48052)
milkGallonWeight = densityMilk * cuFtPerGallonLiquid
densityMolasses = Decimal(88.1233091)
molassesGallonWeight = densityMolasses * cuFtPerGallonLiquid
densityTallow = Decimal(54.09)
densityTin = Decimal(456.3484)
densityCopper = 559
densityClay = 100
densitySilver = Decimal(655.4934)
densityLead = 709
percentageClayInGlass = Decimal(0.8)
densityMercury = Decimal(844.900018) # in liquid form
densityHorn = Decimal(81.1563)
densityGold = Decimal(1204.86)
densityVinegar = Decimal(63.05224)

weightWaterOneGal = Decimal(8.345404)
gallonsPerPint = Decimal(1)/Decimal(8)
waterWeightOnePint = weightWaterOneGal * gallonsPerPint

gramsPerOz = Decimal(28.3495)

cubicFootInPints = Decimal(59.8442)

teaspoonsPerPint = Decimal(96)

densityZinc = Decimal(445)

def cylinderCuFt(height,radius):
    height = Decimal(height)
    radius = Decimal(radius)
    val = Decimal(pi) * height * (radius ** 2)
    return val

def sphereCuFt(radius):
    val = Decimal(pi) * Decimal(4/3) * (Decimal(radius) ** 3)
    return val

def coneCuFt(height, radius):
    """Volume of a cone."""
    return Decimal(pi) * (radius ** 2) * (height / Decimal(3.0))

def squarePyramidCuFt(edge,height):
    """Volume of a right square pyramid."""
    return ((Decimal(edge) ** 2) * (height)) / Decimal(3)
def triangularPrismCuFt(base,height,thickness):
    """The volume of a prism having two triangular faces and three quadrilateral ones.
    Like two 2D triangles with the area between them filled in."""
    base = Decimal(base)
    height = Decimal(height)
    thickness = Decimal(thickness)
    val = ((base * height) / 2) * thickness
    return val

def truncatedConeCuFt(bigRadius, smallRadius, height):
    return Decimal(1)/Decimal(3) * Decimal(pi) * height * ((bigRadius ** 2) + (bigRadius * smallRadius) + (smallRadius ** 2))

def getUnitSize(name):
    """Convenience method to get size of unit."""
    return recipeStorage[name].unit[0]

def getWeight(name):
    """Convenience method to get weight in pounds."""
    return recipeStorage[name].weight[0]

bottleInnerRadius = Decimal(1.25)/Decimal(12)
bottleInnerCylinderHeight = Decimal(6)/Decimal(12)
bottleInnerConeHeight = Decimal(2)/Decimal(12)
bottleMouthInnerRadius = Decimal(0.25)/Decimal(12)
bottleInnerVolume = cylinderCuFt(bottleInnerCylinderHeight, bottleInnerRadius) + truncatedConeCuFt(bottleInnerRadius, bottleMouthInnerRadius, bottleInnerConeHeight)
# should be 0.01941 cuft, or about 15% more than a pint, which is ~0.0167101 cuft
bottleThickness = Decimal(0.125)/Decimal(12)
bottleOuterRadius = bottleInnerRadius + bottleThickness
bottleOuterCylinderHeight = bottleInnerCylinderHeight + bottleThickness
bottleMouthOuterRadius = bottleMouthInnerRadius + bottleThickness
bottleOuterConeHeight = bottleInnerConeHeight + bottleThickness
bottleOuterVolume = cylinderCuFt(bottleOuterCylinderHeight, bottleOuterRadius) + truncatedConeCuFt(bottleOuterRadius, bottleMouthOuterRadius, bottleOuterConeHeight)
bottleMaterialAmountCuft = bottleOuterVolume - bottleInnerVolume
# calculate it as if a clay bottle in order to find the weight of the material
bottleWeight = bottleMaterialAmountCuft * densityClay
bottleGlassWeightOfClay = bottleWeight * percentageClayInGlass
bottleGlassWeightQl = bottleWeight - bottleGlassWeightOfClay
bottleStopperCuFt = cylinderCuFt(Decimal(0.5)/Decimal(12),bottleMouthInnerRadius)
bottleTotalHeight = bottleOuterCylinderHeight + bottleOuterConeHeight
recipeStorage["bottle, glass"] = Recipe("glassblower",(bottleWeight,"lb"),
                                        [("timber",bottleStopperCuFt)],
                                        [("baked clay",bottleGlassWeightOfClay),("quicklime",bottleGlassWeightQl)],
                                        description="max cap. 1 pint 2 oz; " + str(bottleTotalHeight * 12) + " in. high plus 0.5 in stopper")



recipeStorage["pig iron"] = Recipe("smelter",(1, "lb"),
                                   [("iron ore",1),("coal",0.5),("limestone",0.25)])
semiGoods.append("pig iron")

recipeStorage["cast iron"] = Recipe("smelter",(1, "lb"),
                                    # first the components which go into cast iron
                                    [("manganese ore",0.06),
                                     ("nickel ore",0.01),
                                     ("coal",0.5),
                                     ("limestone",0.25)],
                                    [("pig iron",0.93)],
                                    description="ingot, 1x1x3.8 in.")
pewterTinProportion = Decimal(0.85)
pewterCopperProportion = Decimal(0.15)
# this volume calculation works because we're making a 1 lb ingot, so the number of pounds = the proportion
volumePewterIngot = (pewterTinProportion / densityTin) + (pewterCopperProportion / densityCopper)
densityPewter = 1 / volumePewterIngot # because it's a 1 lb ingot over whatever the volume turned out to be
# comes out to 469.3 lbs/cubic ft
# checked it for sanity and the density looks good for an alloy with this much copper.
recipeStorage["pewter"] = Recipe("smelter",(1,"lb"),
                                 [("tin ore",pewterTinProportion),("copper ore",pewterCopperProportion),
                                  ("coal",Decimal(0.5)),("limestone",Decimal(0.5))],
                                 [],
                                 description="ingot, 1x1x3.65 in.")

recipeStorage["iron filings"] = Recipe("blacksmith",(1,"lb"),
                                       [],
                                       [("wrought iron",1)])
semiGoods.append("iron filings")

# the filings are on the basis of the methods described in Subterraneal Treasures
recipeStorage["lead"] = Recipe("smelter",(1,"lb"),
                               [("lead ore",1),("coal",Decimal(0.5)), ("limestone",0.25)],
                               [("iron filings",Decimal(0.25))],
                               description="ingot, 1.084x1.5x1.5 in.")


recipeStorage["silver"] = Recipe("smelter",(1,"lb"),
                                 [("silver ore",1),("coal",Decimal(0.5)),("limestone",Decimal(0.5))],
                                 [],
                                 description="ingot, 1.5x1.5x1.175 in.")

recipeStorage["gold"] = Recipe("smelter", (1,"lb"),
                               [("gold ore",1), ("coal",Decimal(0.5)), ("limestone", Decimal(0.5))],
                               [],
                               description="ingot, 1x1x1.435 in.")

recipeStorage["copper"] = Recipe("smelter", (1,"lb"),
                                 [("copper ore",1), ("coal",Decimal(0.5)), ("limestone",Decimal(0.5))],
                                 [],
                                 description="ingot, 2x1.065x1.45 in.")

sterlingSilverProportionCopper = Decimal(0.075)
sterlingSilverProportionZinc = Decimal(0.01)
sterlingSilverProportionSilver = Decimal(1) - sterlingSilverProportionCopper - sterlingSilverProportionZinc
densitySterlingSilver = sterlingSilverProportionCopper * densityCopper + sterlingSilverProportionSilver * densitySilver + (sterlingSilverProportionZinc * densityZinc)
recipeStorage["sterling silver"] = Recipe("smelter", (1, "lb"),
                                          [("copper ore", sterlingSilverProportionCopper),
                                           ("silver ore", sterlingSilverProportionSilver),
                                           ("zinc ore", sterlingSilverProportionZinc),
                                           ("coal",Decimal(0.5)),
                                           ("limestone",Decimal(0.5))],
                                          [],
                                          description="ingot, 1.5x1.5x1.185 in.")

bronzeCopperProportion = Decimal(0.88)
bronzeTinProportion = Decimal(0.12)
volumeBronzeIngot = (bronzeTinProportion / densityTin) + (bronzeCopperProportion / densityCopper)
densityBronze = 1 / volumeBronzeIngot
# comes out to 544.4 lb/cuft
recipeStorage["bronze"] = Recipe("smelter",(1,"lb"),
                                 [("tin ore",bronzeTinProportion),("copper ore",bronzeCopperProportion),
                                  ("coal",Decimal(0.5)),("limestone",Decimal(0.5))],
                                 [],
                                 description="ingot, 1.125x1.675x1.675 in.")




brassCopperProp = Decimal(0.55)
brassZincProp = Decimal(1) - brassCopperProp
volumeBrassIngot = (brassCopperProp / densityCopper) + (brassZincProp / densityZinc)
densityBrass = 1 / volumeBrassIngot
recipeStorage["brass"] = Recipe("smelter",(1,"lb"),
                                [("zinc ore",brassZincProp),("copper ore",brassCopperProp),
                                 ("coal",Decimal(0.5)),("limestone",Decimal(0.5))],
                                [],
                                description="ingot, 1.77x2.05x0.95 in.")

bellmetalCopperProportion = Decimal(0.78)
bellmetalTinProportion = Decimal(0.22)
volumeBellmetalIngot = (bellmetalTinProportion / densityTin) + (bellmetalCopperProportion / densityCopper)
densityBellmetal = 1 / volumeBellmetalIngot
# comes out to 532.8 lb/cuft, almost the same as bronze but not quite
recipeStorage["bell metal"] = Recipe("smelter",(1,"lb"),
                                     [("tin ore",bellmetalTinProportion),("copper ore",bellmetalCopperProportion),
                                      ("coal",Decimal(0.5)),("limestone",Decimal(0.5))],
                                     [],
                                     description="ingot, 1.2x1.35x2 in.")

recipeStorage["wrought iron"] = Recipe("smelter",(1,"lb"),
                                       [("coal",Decimal(0.5)),("limestone",Decimal(0.25))],
                                       [("pig iron",1)],
                                       description="ingot, 1x1x3.57 in.")

recipeStorage["steel"] = Recipe("smelter",(1,"lb"),
                                [("coal",0.25),("limestone",0.25)],
                                # steel requires half as much coal as other iron stuff
                                # b/c howstuffworks says it only needs to get half as hot
                                       [("pig iron",1)],
                                description="ingot, 1x1x3.5 in.")

hiltCuFt = ((Decimal(1) / Decimal(6)) ** 2) * (Decimal(5) / Decimal(12))
hiltWeight = densityTimber * hiltCuFt
recipeStorage["blade hilt"] = Recipe("carpenter",(hiltWeight,"lb"),
                                     [("timber",hiltCuFt)],
                                     description="wood tube, carved from 2x2x5 in. block")
semiGoods.append("blade hilt")

recipeStorage["pommel"] = Recipe("blacksmith",(0.25,"lb"),
                                 [],
                                 [("steel",0.25)],
                                 description="metal knob which holds hilt and blade together")
semiGoods.append("pommel")


# a 1-foot (unit) blade is 2 inches wide, 1/6 inch thick, 1 foot long
unitBladeCuFt = Decimal(2/12) * Decimal(Decimal(1/6)/12) * 1
unitBladeWeight = unitBladeCuFt * densitySteel
recipeStorage["blade"] = Recipe("blacksmith",(unitBladeWeight,"lb"),
                                [],
                                [("steel",unitBladeWeight)],
                                description="price for a one-foot steel blade")
semiGoods.append("blade")

daggerWeight = getWeight("pommel") + getWeight("blade hilt") + getWeight("blade")
recipeStorage["dagger"] = Recipe("blacksmith",(daggerWeight,"lb"),
                                 [],
                                 [("blade",1),("pommel",1),("blade hilt",1)],
                                 description="1d4 damage, melee or thrown 2/3/4; 1-foot blade")

shortswordWeight = getWeight("pommel") + getWeight("blade hilt") + (Decimal(2) * getWeight("blade"))
recipeStorage["shortsword"] = Recipe("blacksmith",(shortswordWeight,"lb"),
                                     [],
                                     [("blade",2),("pommel",1),("blade hilt",1)],
                                     description="1d6 damage; 2-foot blade")

longswordWeight = getWeight("pommel") + getWeight("blade hilt") + (Decimal(3.5) * getWeight("blade"))
recipeStorage["longsword"] = Recipe("blacksmith",(longswordWeight,"lb"),
                                    [],
                                    [("blade",3.5),("pommel",1),("blade hilt",1)],
                                    description="1d8 damage; 3.5-foot blade")

greatswordWeight = getWeight("pommel") + getWeight("blade hilt") + (Decimal(4.5) * getWeight("blade"))
recipeStorage["greatsword"] = Recipe("blacksmith",(greatswordWeight,"lb"),
                                     [],
                                     [("blade",4.5),("pommel",1),("blade hilt",1)],
                                     description="1d10 damage; 4.5-foot blade")


# let's do some foods, plus feed, cattle/horse so we do cow prices and all the stuff coming from that

recipeStorage["husked cereal"] = Recipe("miller",(1,"lb"),
                                        [("cereal",1)],
                                        [])
semiGoods.append("husked cereal")

recipeStorage["flour"] = Recipe("miller",(1,"lb"),
                                [],
                                [("husked cereal",1)],
                                difficulty=2,
                                description="ground from cereals")

recipeStorage["feed, cattle/horse"] = Recipe("miller",(1,"lb"),
                                      [],
                                      [("husked cereal",1)],
                                      description="coarsely ground from cereals")

recipeStorage["bread"] = Recipe("baker",(1,"lb"),
                                      [("salt",0.05)],
                                      [("flour",0.7)])

recipeStorage["quicklime"] = Recipe("potter",(1,"lb"),
                                    [("limestone",1),("coal",0.5)],
                                    [],
                                    description="used in tanning and to make mortar")

recipeStorage["mortar"] = Recipe("potter",(1,"lb"),
                                 [],
                                 [("baked clay",0.75),("quicklime",0.25)],
                                 description="in powdered form")

recipeStorage["mature ewe"] = Recipe("farmer",(90,"lb"),
                                     [("arable land",Decimal(0.315))],
                                     [],
                                     unit = (1,"head"),
                                     description="eight months old, suitable for milking or shearing")

# a lamb which has been grain finished for slaughter
recipeStorage["mutton sheep"] = Recipe("farmer",(130,"lb"),
                                       [],
                                       [("mature ewe",1),("feed, cattle/horse",345)],
                                       unit=(1,"head"),
                                       description="one year old, suitable for slaughter")

# one mature ewe produces ~ 200 LBS (not gallons!) of milk, once a year during lambing
sheepAnnualMilkLbs = 200
# then we convert it to gallons
sheepAnnualMilkGallons = sheepAnnualMilkLbs / milkGallonWeight
recipeStorage["sheep milk"] = Recipe("farmer",(milkGallonWeight,"lb"),
                                     [],
                                     [("mature ewe",Decimal(1/sheepAnnualMilkGallons))],
                                     unit=(1,"gallon"))

# I take the dress percentage to be 55% of live weight, giving the hanging/carcass weight, and the useable meat to be 75% of the hanging weight
sheepCarcassWeight = getWeight("mutton sheep") * Decimal(0.55)
sheepMeatWeight = sheepCarcassWeight * Decimal(0.75)
# we divide the cost of a mutton sheep by this number to get a price for 1 lb mutton
recipeStorage["mutton"] = Recipe("butcher",(1,"lb"),
                                 [],
                                 [("mutton sheep",Decimal(1/sheepMeatWeight))])

# see ForageCalch.hs, as messy as it is, for how I arrived at this value.
# one day I'll stick those into here
calfSlaughterWeight = Decimal(410)

recipeStorage["calf"] = Recipe("farmer",(calfSlaughterWeight,"lb"),
                               [("arable land",Decimal(2.4045))],
                               [("feed, cattle/horse",123)],
                               unit=(1,"head"),
                               description="8 months old, weaned, suitable for veal and rennet")



cowCarcassFraction = Decimal(2)/Decimal(3)
cowMeatFraction = Decimal(2)/Decimal(3)
vealPerCalf = calfSlaughterWeight * cowCarcassFraction * cowMeatFraction
recipeStorage["veal"] = Recipe("butcher",(1,"lb"),
                               [],
                               [("calf",1/vealPerCalf)])

# this is a guess
abomasumWeight = Decimal(5)
recipeStorage["abomasum"] = Recipe("butcher",(abomasumWeight,"lb"),
                                        [],
                                        [("calf",abomasumWeight/(calfSlaughterWeight * cowCarcassFraction))],
                                        description="fourth compartment of calf stomach")

recipeStorage["abomasum, cured"] = Recipe("butcher",(abomasumWeight,"lb"),
                                        [("salt", Decimal(0.25))],
                                        [("abomasum", 1),
                                         ("vinegar", 1)])
# semiGoods.append("abomasum, cured")

# this is a guess
pintsRennetPerAbomasum = Decimal(2)
recipeStorage["rennet"] = Recipe("butcher",(waterWeightOnePint,"lb"),
                                 [],
                                 [("abomasum, cured", Decimal(1) / pintsRennetPerAbomasum)],
                                 unit=(1, "pint"))
# semiGoods.append("rennet")

teaspoonsRennetPerGallonMilk = Decimal(0.5)
pintsRennetPerGallonMilk = teaspoonsRennetPerGallonMilk / teaspoonsPerPint
gallonsMilkPerPoundCheese = Decimal(3)
# salt amount is a guess
recipeStorage["cheese"] = Recipe("cheesemonger",(1,"lb"),
                                 [("salt",Decimal(0.25))],
                                 [("cow milk", gallonsMilkPerPoundCheese),
                                  ("rennet", pintsRennetPerGallonMilk * gallonsMilkPerPoundCheese)])
                                  

                                 

cowSlaughterWeight = 800
recipeStorage["cow"] = Recipe("farmer",(cowSlaughterWeight,"lb"),
                              [("arable land",Decimal(5.28))],
                              [("feed, cattle/horse",246)],
                              unit=(1,"head"),
                              description="1 year and 4 months old, suitable for slaughtering")

# http://www.personal.utulsa.edu/~marc-carlson/history/cattle.html
# this gives an average milk production of 3.5 gallons per day
dailyMilkGallons = Decimal(3.5)
# from some research, cows can give milk 300/365 days of the year (so 5/6 of the year)
# on the other hand, the production tapers off as this period goes on
# let's be ad-hoc and say that that the effective number of days of milk production is 250
# thus yearly milk production is 3.5 gallons * 250 days
avgMilkingDays = 250
yearlyMilkGallons = dailyMilkGallons * avgMilkingDays
# then divide cow price by that, to get price of milk per gallon

recipeStorage["cow milk"] = Recipe("farmer",(milkGallonWeight,"lb"),
                                   [],
                                   [("cow",Decimal(1/yearlyMilkGallons))],
                                   unit=(1,"gallon"))

# take the carcass weight to be 2/3 of slaughter weight
# and the useable meat, in turn, to be 2/3 of carcass weight
# this approach treats all beef as generic: in reality, a given cow produces different amounts
# of each cut of beef. for now we'll treat them all as the same.
cowCarcassWeight = Decimal(cowSlaughterWeight*2) / Decimal(3)
cowMeatWeight = Decimal(cowCarcassWeight*2) / Decimal(3)
recipeStorage["beef"] = Recipe("butcher",(1,"lb"),
                               [],
                               [("cow",(1/cowMeatWeight))])

# above I said that 2/3 of the cow's carcass weight was meat
# let's assume that 2/3 of the other 1/3 of the carcass weight (i.e. 2/9) is fat, and the other 1/9 is innards, bones, horn, hoof, etc
cowFatWeight = Decimal(2/9) * cowCarcassWeight
# furthermore, since we are working toward a price for suet, which is not ALL fat but just certain portions,
# we'll divide the above weight in half below (or equivalently, treat it as requiring 2 lbs of cow per lb of suet)
recipeStorage["suet"] = Recipe("butcher",(1,"lb"),
                               [],
                               [("cow",(2/cowFatWeight))],
                               description="beef fat for cooking, or for manufacture of tallow")

recipeStorage["tallow"] = Recipe("chandler",(1,"lb"),
                                 [],
                                 [("suet",1)])

# 1% yield, number given from some research
poundsTimberPerPoundAshes = 100
ashesRequiredTimberCuFt = poundsTimberPerPoundAshes / densityTimber
recipeStorage["ashes"] = Recipe("chandler",(1,"lb"),
                                [("timber",ashesRequiredTimberCuFt)],
                                [])

# made by leaching ashes in water
recipeStorage["lye"] = Recipe("chandler",(1,"lb"),
                              [],
                              [("ashes",1)])

# http://www.millennium-ark.net/News_Files/Soap/Lye_Fat_Table.html
# (above page copyright AL Durtschi)
# using the 5% excess fat column given here, the required lye content for soap is 0.133 times the tallow content
lyeTallowRatio = Decimal(0.133)
# finally, we add a little bit of salt to get hard soap instead of soft
# http://www.motherearthnews.com/homesteading-and-livestock/how-to-make-soap-from-ashes-zmaz72jfzfre.aspx
# this article suggests 2.5 pints (3.22 lb) salt for 5 gallons (36.16 lb) of tallow
saltTallowRatio = Decimal(3.22) / Decimal(36.16)
# let's put it all together:
# to find the amount of tallow needed for 1 pound of soap, we solve for x in this equation: 1 = x + (x*lye-to-tallow ratio) + (x*salt-to-tallow ratio)
tallowForOneLbSoap = 1 / (1 + saltTallowRatio + lyeTallowRatio)
# finally, using the density of tallow as a proxy, we find the weight of a bar of soap
barSoapInCuFt = Decimal(3/12) * Decimal(2/12) * Decimal(6/12)
weightOneBarSoap = densityTallow * barSoapInCuFt
# my calculation for how many times it will wash one person:
# one bar of my soap is ~9 cubic inches and lasts about a month i.e. 30 washes
# the soap here is 36 cubic inches, thus it should last about 4 months or 120 washes
# but I'm going to cut that in half because adventurers get much dirtier than I ever would
recipeStorage["soap, hard"] = Recipe("chandler",(weightOneBarSoap,"lb"),
                                     [("salt",saltTallowRatio * weightOneBarSoap)],
                                     [("lye",lyeTallowRatio * weightOneBarSoap),
                                      ("tallow",tallowForOneLbSoap * weightOneBarSoap)],
                                     description="will wash 1 person 60 times; 3x2x6 in.")


# a raw cowhide is about 50 square feet
# this includes the irregularly-shaped edge portions,
# so a nice big single square piece would only be about 40 square feet at most.
recipeStorage["fleshy cowhide"] = Recipe("butcher",(60,"lb"),
                                         [],
                                         [("cow",1)],
                                         unit=(50,"sq ft"))
semiGoods.append("fleshy cowhide")

recipeStorage["rawhide"] = Recipe("tanner",(15,"lb"),
                                  [],
                                  [("fleshy cowhide",1)],
                                  unit=recipeStorage["fleshy cowhide"].unit,
                                  description="cleaned and dried cowskin")

densityQuicklime = Decimal(209.1337)
# this site:
# http://boar.org.uk/aaiwxw3MusprattL6Preparation.htm
# says that three to four cubic feet measure of "freshly burned fat lime" (aka quicklime)
# is used for 100 average hides
# let's split the difference between 3 and 4 cuft of quicklime, and call it 3.5
tannedCowhidePoundsQuicklime = Decimal(3.5) * densityQuicklime / Decimal(100)
weightCowhideInOz = getWeight("rawhide") * 16
cowhideWeightInOzPerSqFt = weightCowhideInOz / Decimal(getUnitSize("rawhide"))
recipeStorage["tanned cowhide"] = Recipe("tanner",(getWeight("rawhide"),"lb"),
                                         [],
                                         [("quicklime",tannedCowhidePoundsQuicklime),("rawhide",1)],
                                         unit=recipeStorage["fleshy cowhide"].unit,
                                         description= str(cowhideWeightInOzPerSqFt) + " oz/sq. ft)")

recipeStorage["holy symbol, plain, wooden"] = Recipe("carpenter",(1,"lb"),
                                                     [("timber",0.02)],
                                                     [])

recipeStorage["holy symbol, plain, iron"] = Recipe("blacksmith",(1,"lb"),
                                                   [],
                                                   [("wrought iron",1)])

# first step in making red and yellow (ochre) dyes
# high difficulty because multiple steps in the process
# here: https://en.wikipedia.org/wiki/Ochre#Modern_history
# wiki says that clay would be about 90% junk and 10% ochre
recipeStorage["separated ochre clay"] = Recipe("potter",(1,"lb"),
                                               [],
                                               [("baked clay",10)])
semiGoods.append("separated ochre clay")

# primary componenent of paints and of dyes
recipeStorage["pigment, red/yellow"] = Recipe("dyer",(1,"lb"),
                                              [],
                                              [("separated ochre clay",1)])
semiGoods.append("pigment, red/yellow")

# component of blue dye
recipeStorage["lapis lazuli, ground"] = Recipe("potter",(1,"lb"),
                                               [("lapis lazuli",1)])
semiGoods.append("lapis lazuli, ground")

recipeStorage["lapis lazuli, cleaned"] = Recipe("potter",(1,"lb"),
                                                [],
                                                [("lapis lazuli, ground",1),("ashes",0.2),("tallow",0.2)])
semiGoods.append("lapis lazuli, cleaned")

recipeStorage["pigment, ultramarine"] = Recipe("dyer",(1,"lb"),
                                               [],
                                               [("lapis lazuli, cleaned",1)])
semiGoods.append("pigment, ultramarine")

recipeStorage["malted grain"] = Recipe("brewer",(1,"lb"),
                                       [("cereal",1)],
                                       description="germinated and dried; used in brewing")

recipeStorage["roasted malt"] = Recipe("brewer",(1,"lb"),
                                       [],
                                       [("malted grain",1)])

# for volume considerations,I've approximated a 30-gallon barrel as a cylinder with radius = 0.67 ft and height = 2 and 11/12 ft.
# were it a right cylinder, this would give a volume of 4.12 cubic feet, or approx. 30.8 US gallons.
# the actual barrel is not a perfect cyllinder, but has sloping sides,
# thus it holds a bit less than 4.12 cubic feet, so I feel OK rounding off to 30 gallons.
# then there's a few more considerations going into the design of the barrel:
# the heads (top and bottom) of the barrel
# the thickness of wood used for all the wood
# and the wrought-iron hoops, of which I use 6 (two fat at the heads, four thin around the body)

# let's say the actual radius of the top/bot of the barrel is 6.5 inches
# and let's say the thickness of the heads is 2/3 inch and the staves are 1.125 inch thick
# let's say the fat hoops are 1.25 inch wide, and the thin ones are 1 inch. hoop breadth is 16 gauge (1/16 of an inch)

gauge16WireThicknessInches = Decimal(0.05082)

barrelHeadThickness = Decimal(2/3) / Decimal(12)
barrelHeadRadius = Decimal(6.5)/Decimal(12)
barrelHeadCircleArea = Decimal(pi) * (barrelHeadRadius ** 2)
barrelCuFt = barrelHeadCircleArea * barrelHeadThickness
barrelHeadWeight = densityTimber * barrelCuFt

recipeStorage["barrel head"] = Recipe("cooper",(barrelHeadWeight,"lb"),
                                      [("timber",barrelCuFt)],
                                      [])
semiGoods.append("barrel head")

barrelHeadCircumference = barrelHeadRadius * 2 * Decimal(pi)
fatHoopCuFt = barrelHeadCircumference * (Decimal(1.25) / Decimal(12)) * (gauge16WireThicknessInches / Decimal(12))
fatHoopWeight = densityWroughtIron * fatHoopCuFt

recipeStorage["barrel hoop, fat"] = Recipe("blacksmith",(fatHoopWeight, "lb"),
                                           [],
                                           [("wrought iron",fatHoopWeight)])
semiGoods.append("barrel hoop, fat")

# the thin hoops are actually 1/3 and 2/3 the distance to the middle of the barrel,
# so with the sloping of the barrel, we'd use a measure less than the barrel's max circumference
# to get their length.
# but I'll just go ahead and approximate them as being the same as its radius. no need for total accuracy.
barrelBodyCircumference = Decimal(2) / Decimal(3)
thinHoopCuFt = barrelBodyCircumference * (Decimal(1) / Decimal(12)) * (gauge16WireThicknessInches / Decimal(12))
thinHoopWeight = densityWroughtIron * thinHoopCuFt

recipeStorage["barrel hoop, thin"] = Recipe("blacksmith",(thinHoopWeight, "lb"),
                                            [],
                                            [("wrought iron",thinHoopWeight)])
semiGoods.append("barrel hoop, thin")

# these are quite rough measurements. so it goes.
numStaves = 12
staveWidth = barrelBodyCircumference / Decimal(numStaves)
staveThickness = (Decimal(1.125)/Decimal(12))
staveHeight = Decimal(35) / Decimal(12) # 2 and 11/12 feet high, i.e. 35 inches
staveCuFt = staveWidth * staveHeight * staveThickness
staveWeight = staveCuFt * densityTimber
recipeStorage["barrel stave"] = Recipe("cooper",(staveWeight,"lb"),
                                       [("timber",staveCuFt)],
                                       [])
semiGoods.append("barrel stave")

# bringing it all together
barrelWeight = (numStaves * staveWeight) + (4 * thinHoopWeight) + (2 * fatHoopWeight) + (2 * barrelHeadWeight)
recipeStorage["barrel"] = Recipe("cooper",(barrelWeight, "lb"),
                                 [],
                                 [("barrel stave",numStaves),("barrel hoop, fat",2),("barrel hoop, thin",4),
                                  ("barrel head",2)],
                                 description="30-gallon barrel; 0.67-ft widest radius; 2 ft 11 in. tall")


def calculateABV(sugarPounds, cerealPounds, maltPounds, waterGals, desiredVolumeGals):
    sugarOfCereal = sugarPounds * Decimal(0.75)
    sugarOfMalt = maltPounds * Decimal(0.8)
    totalSugar = sugarPounds + sugarOfCereal + sugarOfMalt
    waterWeight = waterGals * weightWaterOneGal
    mashWeight = totalSugar + waterWeight
    # specific gravity, with respect to water, is the relative density of some solution and water
    # the original gravity is the specific gravity of the mash
    # we are dissolving our sugar in waterGals gallons of water, and comparing the density of that to the density of waterGals gallons of water. because those two volumes are the same, we can ignore the volume component of density, and just make a ratio of the weights
    originalGravity = mashWeight / waterWeight
    # then we boil off the alcohol to collect it: this is distillation
    # note that this distilled spirit is NOT pure alcohol!
    # it would be ~ 20%, but I've left off 1% to represent the non-usable "head" of the spirit
    distilledVolumeGals = Decimal(0.19) * waterGals
    # final gravity: the specific density of the spirit
    # this value, 0.99, is an average one
    finalGravity = Decimal(0.99)
    baseABV = (originalGravity - finalGravity) * 129
    # now we dilute the distilled spirit with water to reach the desiredVolumeGals, our final spirit product
    # the difference between distilledVolumeGals and desiredVolumeGals is the volume of water added
    dilutedABV = baseABV * (distilledVolumeGals / desiredVolumeGals)
    return dilutedABV

# based on the Clare household strong ale recipe from:
# https://www.cs.cmu.edu/~pwp/tofi/medieval_english_ale.html
aleCerealPerGallon = Decimal(1.5)
aleMaltPerGallon = Decimal(4)
aleRoastedMaltPerGallon = Decimal(0.67)
aleABV = calculateABV(0, aleCerealPerGallon, aleMaltPerGallon, 1, 1)
gallonsPerBarrel = Decimal(30)
recipeStorage["ale, barrel"] = Recipe("brewer",(weightWaterOneGal * gallonsPerBarrel + getWeight("barrel") ,"lb"),
                              [("cereal",aleCerealPerGallon * gallonsPerBarrel)],
                              [("malted grain",aleMaltPerGallon * gallonsPerBarrel),("roasted malt",aleRoastedMaltPerGallon * gallonsPerBarrel),("barrel",1)],
                              unit=(gallonsPerBarrel,"gallon"),
                              description="in barrel; " + str(aleABV) + " percent alcohol")

pintsPerBarrel = gallonsPerBarrel * (Decimal(1)/gallonsPerPint) # 30 * 8 = 240
recipeStorage["ale, by the tankard"] = Recipe("brewer",(waterWeightOnePint,"lb"),
                                              [],
                                              [("ale, barrel",Decimal(1) / pintsPerBarrel)],
                                              unit=(1,"pint"),
                                              description = str(aleABV) + " percent alcohol")

recipeStorage["ale, bottled"] = Recipe("brewer",(waterWeightOnePint + getWeight("bottle, glass"),"lb"),
                                       [],
                                       [("ale, barrel",Decimal(1) / pintsPerBarrel), ("bottle, glass",1)],
                                       unit=(1,"pint"),
                                       description = str(aleABV) + " percent alcohol; in glass bottle")

# "To brewe beer; 10 quarters malt. 2 quarters wheat, 2 quarters oats, 40 lbs hops. To make 60 barrels of single beer."
# this is one of the recipes taken from http://brewery.org/library/PeriodRen.html
# a "quarter" equals 256 lbs of grain (b/c it's 64 gallons of dry volume and 1 gallon of grain ~= 4 lbs)
# a medieval barrel of beer was 36 gallons
# thus we have 2560 lbs malt, 512 lbs + 512 lbs = 1024 lbs cereal, 40 lbs hops = 2160 gallons.
# divide all amounts by 2160 to arrive at a 1-gallon recipe
originalGallons = 2160
beerCerealPerGallon = Decimal(1024)/originalGallons
beerMaltPerGallon = Decimal(2560)/originalGallons
beerHopsPerGallon = Decimal(40)/originalGallons
beerABV = calculateABV(0, beerCerealPerGallon, beerMaltPerGallon, 1, 1)
recipeStorage["beer, barrel"] = Recipe("brewer",(weightWaterOneGal * gallonsPerBarrel + getWeight("barrel"),"lb"),
                               [("cereal",beerCerealPerGallon * gallonsPerBarrel),("hops",beerHopsPerGallon * gallonsPerBarrel)],
                               [("malted grain",beerMaltPerGallon * gallonsPerBarrel),("barrel",1)],
                               unit=(gallonsPerBarrel,"gallon"),
                               description="in barrel; " + str(beerABV) + " percent alcohol")

recipeStorage["beer, by the tankard"] = Recipe("brewer",(waterWeightOnePint,"lb"),
                                               [],
                                               [("beer, barrel", Decimal(1) / pintsPerBarrel)],
                                               unit=(1,"pint"),
                                               description=str(beerABV) + " percent alcohol")

recipeStorage["beer, bottled"] = Recipe("brewer",(waterWeightOnePint + getWeight("bottle, glass"),"lb"),
                                        [],
                                        [("beer, barrel",Decimal(1)/pintsPerBarrel), ("bottle, glass", 1)],
                                        unit=(1,"pint"),
                                        description=str(beerABV) + " percent alcohol; in glass bottle")

weightPintVinegar = densityVinegar / cubicFootInPints
recipeStorage["vinegar"] = Recipe("brewer",(weightPintVinegar + getWeight("bottle, glass"), "lb"),
                                  [],
                                  [("beer, bottled",1)],
                                  unit=(1, "pint"),
                                  description="in glass bottle")

# production figures for greasy wool vary wildly, so I'll go with one sheep producing 25 lbs of greasy wool, which can be turned into 15 lbs of scoured wool (which must then be pounded)
recipeStorage["greasy wool"] = Recipe("farmer",(25,"lb"),
                                      [],
                                      [("mature ewe",1)])
semiGoods.append("greasy wool")


recipeStorage["fuller's earth"] = Recipe("potter",(1,"lb"),
                                         [],
                                         [("baked clay",3)],
                                         description = "certain clays used for scouring wool")
semiGoods.append("fuller's earth")

# again, I've decided that one 25-lb unit of greasy wool becomes 15 lbs of scoured
# wool is cleaned by scouring (washing) and using clay
recipeStorage["scoured wool"] = Recipe("fuller",(15,"lb"),
                                       [],
                                       [("fuller's earth",1),("greasy wool",1)])
semiGoods.append("scoured wool")

# final step in cleaning wool is pounding, which is done by mills
# ranges in color from brownish to whitish
recipeStorage["clean wool"] = Recipe("miller",(1,"lb"),
                                     [],
                                     [("scoured wool",Decimal(1/getWeight("scoured wool")))],
                                     description="either brownish or whitish in color")
semiGoods.append("clean wool")


# Wikipedia lists the weight of "medium" yarn at 120-200 m/100 gram
# that works out to 2,232.24592 ft / pound
# I'll round it to 2250
mediumYarnFeetPerLb = Decimal(2250)
recipeStorage["yarn, wool"] = Recipe("spinner",(1,"lb"),
                                     [],
                                     [("clean wool",1)],
                                     unit=(mediumYarnFeetPerLb,"feet"),
                                     description="useable as string, in ropemaking, etc.")

# wraps per inch is highly variable
mediumYarnWrapsInch = Decimal(1)/Decimal(16)/Decimal(12) # 1/16 of an inch
# doubling (for plain weave) is because we need both weft and warp
yarnFtPerClothSqFt = Decimal(2) * (Decimal(1) / mediumYarnWrapsInch)
# the weight calculation below works because the table lists 1 lb of yarn
woolClothWeight = (yarnFtPerClothSqFt/getUnitSize("yarn, wool")) * getWeight("yarn, wool")
recipeStorage["wool cloth"] = Recipe("weaver",(woolClothWeight,"lb"),
                                     [],
                                     [("yarn, wool",yarnFtPerClothSqFt / getUnitSize("yarn, wool"))],
                                     unit=(1,"sq ft"))

ratioYarnThreadThickness = Decimal(4)
threadWrapsInch = ratioYarnThreadThickness * mediumYarnWrapsInch
# treating it as 4 times thinner than yarn, and thus equivalent to "Super Fine (thin)" yarn
threadFtPerLb = ratioYarnThreadThickness * mediumYarnFeetPerLb
recipeStorage["thread"] = Recipe("spinner",(1,"lb"),
                                 [],
                                 [("clean wool",1)],
                                 unit=(threadFtPerLb,"feet"),
                                 description="useable for stitching cloth and textiles")

# similar to the processes for cleaning wool, but for cotton instead
# no need to scour it, just to clean it (carding, picking, combing, etc)
# the ratio of raw cotton to clean cotton is b/c approx 60% of the weight of raw cotton is in the boll,
# which is discarded
recipeStorage["clean cotton"] = Recipe("miller",(1,"lb"),
                                       [("cotton",2.5)],
                                       [])
semiGoods.append("clean cotton")

recipeStorage["yarn, cotton"] = Recipe("spinner",(1,"lb"),
                                       [],
                                       [("clean cotton",1)],
                                       unit=(getUnitSize("yarn, wool"),"feet"),
                                       description="useable as string, in ropemaking, etc.")

# the weight calculation below works because the table lists 1 lb of yarn.
cottonClothWeight = (yarnFtPerClothSqFt/getUnitSize("yarn, cotton")) * getWeight("yarn, cotton")
recipeStorage["cotton cloth"] = Recipe("weaver",(cottonClothWeight,"lb"),
                                       [],
                                       [("yarn, cotton",yarnFtPerClothSqFt / getUnitSize("yarn, cotton"))],
                                       unit=(1,"sq ft"))

recipeStorage["thread, cotton"] = Recipe("spinner",(1,"lb"),
                                 [],
                                 [("clean cotton",1)],
                                 unit=(threadFtPerLb,"feet"),
                                 description="useable for stitching cloth and textiles")


threadPerSqInchWeave = Decimal(12) * threadWrapsInch
# doubled for warp and weft
threadPerSqFt = Decimal(2) * Decimal(12) * threadPerSqInchWeave
threadSqFtUR = threadPerSqFt / getUnitSize("thread")
threadSqFtWt = threadSqFtUR * getWeight("thread")
laceEmptinessProprtion = Decimal(0.5)
laceWt = threadSqFtWt * (Decimal(1) - laceEmptinessProprtion)
recipeStorage["lace"] = Recipe("weaver",(laceWt,"lb"),
                               [],
                               [("thread",threadSqFtUR)],
                               unit=(1,"sq ft"),
                               difficulty=30)

embroideryWeight = threadSqFtWt
recipeStorage["embroidery"] = Recipe("embroiderer",
                                     (embroideryWeight,"lb"),
                                     [],
                                     [("thread",threadSqFtUR)],
                                     unit=(1,"sq ft"))
chemiseSqFt = Decimal(6)
chemiseThread = chemiseSqFt * 4
chemiseWeight = chemiseSqFt * getWeight("wool cloth")
recipeStorage["chemise"] = Recipe("tailor",(chemiseWeight, "lb"),
                                    [],
                                    [("wool cloth",chemiseSqFt),
                                     ("thread",chemiseThread/getUnitSize("thread"))],
                                    description="unisex; simple homespun shirt worn next to skin")

tunicSqFt = Decimal(0.8) * chemiseSqFt
tunicThread = tunicSqFt * 4
tunicWeight = tunicSqFt * getWeight("wool cloth")
recipeStorage["tunic"] = Recipe("tailor",(tunicWeight, "lb"),
                                    [],
                                    [("wool cloth",tunicSqFt),
                                     ("thread",tunicThread/getUnitSize("thread"))],
                                    description="short-sleeved upper garment") 

# at 3 places (collar and both cuffs), frilly lace is added to show off wealth
# each piece of lace is 1 inch wide, and is as long as a shirtsleeve is wide
# for now let's say that's 6 inches; once I establish standard sizes for shirtsleeves, leg tubes, etc., this can be changed
fancyChemiseFrillSqFt = Decimal(0.5) * Decimal(1)/Decimal(12)
fancyChemiseTotalFrillSqFt = Decimal(3) * fancyChemiseFrillSqFt
fancyChemiseTotalFrillUR = fancyChemiseTotalFrillSqFt / getUnitSize("lace")
fancyChemiseTotalFrillWt = fancyChemiseTotalFrillUR * getWeight("lace")
recipeStorage["chemise, fancy"] = Recipe("tailor",(getWeight("chemise") + fancyChemiseTotalFrillWt,"lb"),
                                         [],
                                         [("chemise",1), ("lace", fancyChemiseTotalFrillUR)],
                                         difficulty=5,
                                         description="chemise with lace-trimmed cuffs and collar")

# clogs are normally made from poplar
# compare this Dutch video of a clogmaker, De Klompenmaker
# https://www.youtube.com/watch?v=F-WrDDfTBVQ
# with this Discovery Channel episode about industrial manufacture of the same kind of shoe
# https://www.youtube.com/watch?v=gUDHPiJXkyU
# online websites list two clogs as weighing 1kg together
# I'll thus make each clog roughly one pound
clogWt = Decimal(1.1)
# the clog is made from a block, so I'll round this up to nearest whole num
clogCuFt = clogWt / densityTimber
recipeStorage["clog"] = Recipe("carver",(clogWt,"lb"),
                               [("timber",clogCuFt)],
                               [],
                               description="Dutch-style klomp; hand-carved wooden shoe")

# brown (or "raw") sugar, which still contains some molasses
# cane can yield 50% of its mass in juice; approximately 20% of that juice is sugar
poundsJuicePerPoundSugarcane = Decimal(0.5)
sugarcaneJuiceSugarPercentage = Decimal(0.2)
sugarPerPoundSugarcane = poundsJuicePerPoundSugarcane * sugarcaneJuiceSugarPercentage
sugarcaneForPoundSugar = 1 / sugarPerPoundSugarcane
# as for molasses, recipe is essentially the same as brown sugar, except for the ratio of inputs to product
# the sugar in the sugarcane juice is 20% of the juice mass;
# we can say the remaining 80% of the juice mass turns into molasses; thus 50% * 80% = 4 lbs of molasses per 10 lbs of sugarcane
# its' more than 4 lbs of molasses per gallon -- its about 12. so we divide the molasses per-gallon weight by 4 lbs, to get the number we multiply that 10 lbs of sugarcane by, to get the sugarcane for 1 gallon of molasses
sugarcaneForOneGallonMolasses = 10 * molassesGallonWeight / 4

recipeStorage["brown sugar"] = Recipe("miller",(1,"lb"),
                                      [("sugarcane",sugarcaneForPoundSugar)],
                                      [],
                                      difficulty=2)

recipeStorage["molasses"] = Recipe("miller",(molassesGallonWeight,"lb"),
                                   [("sugarcane",sugarcaneForOneGallonMolasses)],
                                   [],
                                   unit=(1,"gallon"))

# 6 month old pig for the slaughter, weighing 120 lbs
recipeStorage["pig"] = Recipe("farmer",(120, "lb"),
                              [],
                              [("feed, cattle/horse",504)],
                              description="6 months old, ready for slaughter")

# going off the web, carcass weight is 75% of live weight, and dress weight is 75% of carcass weight
pigDressPercentageOfLiveWeight = Decimal(0.75) * Decimal(0.75)
# times weight of slaughtered pig
pigDressWeight = pigDressPercentageOfLiveWeight * 150
recipeStorage["pork"] = Recipe("butcher",(1,"lb"),
                               [],
                               [("pig",Decimal(1/pigDressWeight))])

# working from a recipe in the London Art of Cookery, an early 1700s cookbook,
# as shown here: https://savoringthepast.net/2013/01/08/salted-meat-for-a-journey-at-sea/
# for each pound of meat, it works out to 4 oz (1/4 lb) salt + a mix of 1/3 lb salt and 1/6 lb brown sugar,
# (for a total of 9.33 oz salt and 2.67 oz brown sugar)
# numbers immediately below are calculated in lbs
saltForSaltBeef = Decimal(1/4) + Decimal(1/3)
brownSugarForSaltBeef = Decimal(1/6)
recipeStorage["beef jerky"] = Recipe("butcher",(1,"lb"),
                                     [("salt",saltForSaltBeef)],
                                     [("brown sugar",brownSugarForSaltBeef),
                                      ("beef",1)],
                                     description="will keep for a year if seldom exposed to air")

# salt pork, when compared to salt beef, is said to require more salt and less sugar (same source as salt beef)
saltForSaltPork = Decimal(1/4) + Decimal(2.5/6)
brownSugarForSaltPork = Decimal(0.5/6)
recipeStorage["salt pork"] = Recipe("butcher",(1,"lb"),
                                    [("salt",saltForSaltPork)],
                                    [("brown sugar",brownSugarForSaltPork),
                                     ("pork",1)],
                                    description="will keep for a year if seldom exposed to air")

recipeStorage["spearhead"] = Recipe("blacksmith",(1.5,"lb"),
                                    [],
                                    [("wrought iron",Decimal(0.9)),("steel",Decimal(0.6))])
semiGoods.append("spearhead")

spearHaftCuFt = cylinderCuFt(5,Decimal(0.5/12))
recipeStorage["spear haft"] = Recipe("carpenter",(spearHaftCuFt * densityTimber,"lb"),
                                     [("timber",spearHaftCuFt)],
                                     [])
semiGoods.append("spear haft")

spearWeight = recipeStorage["spearhead"].weight[0] + recipeStorage["spear haft"].weight[0]
recipeStorage["spear"] = Recipe("blacksmith",(spearWeight, "lb"),
                                [],
                                [("spearhead",1),("spear haft",1)],
                                description="1d6 damage, one-handed, melee or thrown 4/7/10; haft 5 ft. long")

maceShaftCrossSectionRadius = Decimal(0.5) # inches
maceHaftCuFt = cylinderCuFt(2,maceShaftCrossSectionRadius/12)
maceHaftMetalProportion = Decimal(0.25)
maceHaftWoodProportion = 1 - maceHaftMetalProportion
maceHaftMetalWeight = maceHaftMetalProportion * maceHaftCuFt * densityWroughtIron
maceHaftWoodWeight = maceHaftWoodProportion * maceHaftCuFt * densityTimber
recipeStorage["mace haft"] = Recipe("blacksmith",(maceHaftMetalWeight + maceHaftWoodWeight,"lb"),
                                    [("timber",maceHaftCuFt)],
                                    [("wrought iron",maceHaftMetalWeight)],
                                    description="wood reinforced with metal bands")
semiGoods.append("mace haft")

maceFlangeCuFt = triangularPrismCuFt(Decimal(1/12),Decimal(0.25),Decimal(0.1))
maceFlangeWeight = maceFlangeCuFt * densityWroughtIron
recipeStorage["mace flange"] = Recipe("blacksmith",(maceFlangeWeight,"lb"),
                                      [],
                                      [("wrought iron",maceFlangeWeight)])
semiGoods.append("mace flange")

recipeStorage["mace"] = Recipe("blacksmith",(getWeight("mace haft") + (6 * maceFlangeWeight),"lb"),
                               [],
                               [("mace haft",1),("mace flange",6)],
                               description="1d8 damage, one-handed, melee; haft is 2 ft.")

wroughtIronIngotCuFt = Decimal(1/12) * Decimal(1/12) * Decimal(3.57/12)
oneFootWireCuFt = cylinderCuFt(1,(gauge16WireThicknessInches/2/12))
feetOfWire = wroughtIronIngotCuFt / oneFootWireCuFt
# can be used for fastening, or turned into rings for mail
# weight of wire is the same as the 1 lb ingot of wrought iron; it's just turned into a different shape
recipeStorage["wire"] = Recipe("blacksmith",(1,"lb"),
                               [],
                               [("wrought iron",1)],
                               difficulty=3, # lots of hammering and then lots and lots of pulling
                               unit=(feetOfWire,"feet"),
                               description="thickness 16 gauge (diameter 0.05082 in.)")

# this is in feet b/c division by 12
mailRingRadius = Decimal(0.2) / 12
# this circumference is also the feet of wire needed for one ring
mailRingCircumference = 2 * Decimal(pi) * mailRingRadius
unitsWirePerRing = mailRingCircumference / getUnitSize("wire")
recipeStorage["mail ring"] = Recipe("blacksmith",(unitsWirePerRing,"lb"),
                                    [],
                                    [("wire",unitsWirePerRing)])
semiGoods.append("mail ring")

# rings overlap, which would mean more per linear foot, but we'll ignore that since mail can stretch a little too
ringsToReachOneFootLength = 1 / mailRingRadius
ringsInSquareFootMail = ringsToReachOneFootLength ** 2
recipeStorage["mail sqft"] = Recipe("blacksmith",(getWeight("mail ring") * ringsInSquareFootMail,"lb"),
                                    [],
                                    [("mail ring",ringsInSquareFootMail)],
                                    unit=(1,"sq ft"))
semiGoods.append("mail sqft")

hauberkSqFt = 9
recipeStorage["hauberk, mail"] = Recipe("blacksmith",(hauberkSqFt * getWeight("mail sqft"),"lb"),
                                        [],
                                        [("mail sqft",hauberkSqFt)],
                                        description="AC 5; has full sleeves, and covers torso to the knees")

haubergeonSqFt = 6
recipeStorage["haubergeon, mail"] = Recipe("blacksmith",(haubergeonSqFt * getWeight("mail sqft"),"lb"),
                                           [],
                                           [("mail sqft",haubergeonSqFt)],
                                           description="AC 6; has half-sleeves; covers torso to the waist")

# the leather pattern must be worked by a leatherworker with yarn, to make the bag;
# he sews the sides together, and adds the string for tying closed, with its holes
# 4 feet of yarn are used to sew the sides of the bag together, then 4 feet going over it for strength
# repeat that process to make the top flap secure

# I approximate the pattern of a leather backpack holding one cubic foot
# as the pattern which, when folded up, makes a cube, each side 1 foot long.
# Thus the pattern requires 6 square feet of leather (roughly the shape of a Christian cross).
# Then we add another 1 square foot of leather for the straps.
backpackPortionOfCowhide = Decimal(7) / getUnitSize("tanned cowhide")
backpackLeatherWeight = backpackPortionOfCowhide * getWeight("tanned cowhide")
backpackYarnFt = Decimal(16) + Decimal(2) # 2 extra feet for clasp
backpackYarnUR = backpackYarnFt / getUnitSize("yarn, wool")
backpackYarnWt = backpackYarnUR * getWeight("yarn, wool")
recipeStorage["backpack"] = Recipe("leatherworker",(backpackLeatherWeight + backpackYarnWt,"lb"),
                                   [],
                                   [("tanned cowhide",backpackPortionOfCowhide),
                                    ("yarn, wool",backpackYarnUR)],
                                   description="with string clasp; holds 30 lbs")

# belt pouch holds very little;
# the total square footage is (0.15^2)*6
beltpouchSqFt = (Decimal(0.15) ** 2) * 6
beltpouchPortionOfCowhide = beltpouchSqFt / getUnitSize("tanned cowhide")
recipeStorage["belt pouch"] = Recipe("leatherworker",(beltpouchPortionOfCowhide * getWeight("tanned cowhide"),"lb"),
                                     [],
                                     [("thread",Decimal(1.2) / getUnitSize("thread")),
                                      ("tanned cowhide",beltpouchPortionOfCowhide),
                                      ("yarn, wool",Decimal(1) / getUnitSize("yarn, wool"))],
                                     description="string clasp; holds 4.5 lbs or half-gallon fluid (1 day's worth)")

# let's say a belt is 3 feet long and 1 inch wide, and you cut to the appropriate length -- but the leatherworker is gonna charge you for the whole thing.
# you also need maybe 12 feet of thread to make the edges tough
beltSqFt = Decimal(1/12) * 3
beltPortionOfCowhide = beltSqFt / getUnitSize("tanned cowhide")
recipeStorage["belt"] = Recipe("leatherworker",(beltPortionOfCowhide * getWeight("tanned cowhide"),"lb"),
                               [],
                               [("thread",Decimal(12) / getUnitSize("thread")),
                                ("tanned cowhide",beltPortionOfCowhide)],
                               description="leather; can attach up to 3 belt-attachable items: weapon scabbard/loop/hook, belt pouch, quiver")

# approximate
whistleCuFt = cylinderCuFt(Decimal(0.25), Decimal(3)/(12))
whistleWeight = whistleCuFt * densityTimber
recipeStorage["whistle"] = Recipe("carpenter",(whistleWeight,"lb"),
                                  [("timber",whistleCuFt)],
                                  [],
                                  description="non-musical; 3 inches long")

# structurally it's a little hollow block
fippleCuFt = Decimal(1/12) * Decimal(1/12) * Decimal(2/12)
fippleWeight = fippleCuFt * densityTimber
recipeStorage["fipple"] = Recipe("carpenter",(fippleWeight,"lb"),
                                 [("timber", fippleCuFt)],
                                 [],
                                 description="whistle mouthpiece for certain instruments")
semiGoods.append("fipple")

recorderBodyCuFt = cylinderCuFt(Decimal(1.25), Decimal(0.75/12))
recorderBodyWeight = recorderBodyCuFt * densityTimber
recipeStorage["recorder"] = Recipe("carpenter",(recorderBodyWeight + fippleWeight,"lb"),
                                   [("timber",recorderBodyCuFt)],
                                   [("fipple",1)],
                                   description="type of wooden flute; 15 inches long")

# four strands of yarn are twisted into a rope strand, turning one direction;
# four rope strands are twisted into a rope, turning the other direction.
yarnStrandsPerRopeStrand = Decimal(4)
# the weight of one rope strand is the same as the yarn used to make it
# but the amount of feet is 1/yarnStrandsPerRopeStrand
recipeStorage["rope strand"] = Recipe("ropewalker",(getWeight("yarn, wool"),"lb"),
                                      [],
                                      [("yarn, wool",1)],
                                      unit=(getUnitSize("yarn, wool")/yarnStrandsPerRopeStrand,"feet"))
semiGoods.append("rope strand")

strandFeetPerSegmentOfRope = Decimal(4)
# the weight of one segment of rope is the same as the strands used to make it
# but the length of one segment is 1/ropeStrandsPerRope.
# conceptually, this is the same as forming rope strands from yarn
# however, there's a further consideration
# a single segment of rope is just too short to be useful
# the minimum length by which rope is sold must be longer than that.
# thus we calculate a rope's selling unit size as being the length of several segments "joined together"
# if there are X segments' worth of length of rope, then the weight must go up by X times, too
numberOfSegments = Decimal(8)
recipeStorage["rope"] = Recipe("ropewalker",(getWeight("rope strand")*numberOfSegments,"lb"),
                               [],
                               [("rope strand",numberOfSegments)],
                               unit=((getUnitSize("rope strand")/strandFeetPerSegmentOfRope) * numberOfSegments,
                               "feet"),
                               description="")


# felt is produced by squishing layers of clean wool together and adding lye
feltThickness = Decimal(1)/Decimal(8)/Decimal(12)
feltThicknessRelativeToWoolCloth = feltThickness / mediumYarnWrapsInch
poundsCleanWoolPerSqFtFelt = feltThicknessRelativeToWoolCloth * woolClothWeight
recipeStorage["felt"] = Recipe("fuller",(poundsCleanWoolPerSqFtFelt,"lb"),
                               [],
                               [("lye",Decimal(0.1)),("clean wool",poundsCleanWoolPerSqFtFelt)],
                               unit=(1,"sq ft"),
                               description="soft and thick wool textile")

# gambesons are thickly padded
gambesonLayers = 3
gambesonSqFt = 12 * gambesonLayers # 8 ft for the body, 2 sq ft for each arm
# thread goes around the perimeter of each layer, attaching it to the next, and then all of them are sewn together one more time
gambesonThread =  gambesonLayers * 4
recipeStorage["gambeson, quilted"] = Recipe("weaver",(gambesonSqFt * getWeight("wool cloth"),"lb"),
                                            [],
                                            [("wool cloth",gambesonSqFt),("thread",(gambesonThread/getUnitSize("thread")))],
                                            description="AC 9; padded cloth armor; full sleeves, and covers torso to the waist")

# some ad-hoc measurements for horns follow
hornRadius = Decimal(1.5)/Decimal(12)
hornLength = 4
hornCuFt = cylinderCuFt(hornLength, hornRadius)
hornWeight = hornCuFt * densityHorn
recipeStorage["horn, cow"] = Recipe("butcher",(hornWeight,"lb"),
                                    [],
                                    [("cow",Decimal(0.5))],
                                    unit=(1,"horn"),
                                    description=str(hornLength) + " ft long, " + str(hornRadius) + "-inch avg. radius")

gemshornRequiredHornLength = Decimal(8)/Decimal(12)
gemshornRequiredHornCuFt = gemshornRequiredHornLength * hornRadius
gemshornRequiredHornWeightRatio = (gemshornRequiredHornCuFt * densityHorn) / getWeight("horn, cow")
recipeStorage["gemshorn"] = Recipe("carpenter",(2,"lb"),
                                   [],
                                   [("fipple",1),("horn, cow",gemshornRequiredHornWeightRatio)],
                                   description="ocarina-type instrument made from bull horn; " + str(gemshornRequiredHornLength) + " inches long")

# this is really a small instrument, and it's not a solid block either, so these dimensions are about right
# I approximate its dimensions as a thin cylinder, which would then be bent into shape,
# i.e. curve into a sort of horseshoe shape,
# and the reed and tongue would be added (small pieces of scrap metal)
# the height (length) of the cylinder is given,
# but because it's bent more or less in half, the instrument length is half that.
jawHarpCuFt = cylinderCuFt(Decimal(1),Decimal(0.1/12))
jawHarpWeight = jawHarpCuFt * densityWroughtIron
recipeStorage["jaw harp"] = Recipe("blacksmith",(jawHarpWeight,"lb"),
                                   [],
                                   [("wrought iron",jawHarpWeight)],
                                   description="6 inches long")

handbellHandleSqFt = Decimal(0.5/12) * Decimal(4/12)
handbellHandleLeatherProportion = handbellHandleSqFt / getUnitSize("tanned cowhide")
handbellHandleWeight = handbellHandleLeatherProportion * getWeight("tanned cowhide")
recipeStorage["handbell handle"] = Recipe("leatherworker",(handbellHandleWeight,"lb"),
                                          [],
                                          [("tanned cowhide",handbellHandleLeatherProportion)])
semiGoods.append("handbell handle")

# modeled as a tiny block of bell metal which is pounded into shape
handbellClapperCuFt = Decimal(0.25/12) * Decimal(0.25/12) * Decimal(0.5/12)
handbellClapperWeight = handbellClapperCuFt * densityBellmetal
recipeStorage["handbell clapper"] = Recipe("blacksmith",(handbellClapperWeight,"lb"),
                                           [],
                                           [("bell metal",handbellClapperWeight)])
semiGoods.append("handbell clapper")

# a thin sheet of bell metal, pounded into shape
handbellBodyCuFt = Decimal(0.1/12) * Decimal(1.5/12) * Decimal(3.5/12)
handbellBodyWeight = handbellBodyCuFt * densityBellmetal
recipeStorage["handbell body"] = Recipe("blacksmith",(handbellBodyWeight,"lb"),
                                        [],
                                        [("bell metal",handbellBodyWeight)])
semiGoods.append("handbell body")

recipeStorage["handbell"] = Recipe("blacksmith",(handbellHandleWeight + handbellClapperWeight + handbellBodyWeight,"lb"),
                                   [],
                                   [("handbell handle",1),("handbell body",1),("handbell clapper",1)],
                                   description="has leather loop handle; body of bell ~1.5 inches tall") 

# some of the weight of the original clay is water;
# we account for that loss here so that we don't have to do it as part of calculation for weights of
# pottery pieces
recipeStorage["baked clay"] = Recipe("potter",(1,"lb"),
                                     [("clay",Decimal(1.15))],
                                     [])
semiGoods.append("baked clay")


clubCuFt = cylinderCuFt(2,1.5/12)
clubWeight = clubCuFt * densityTimber
recipeStorage["club"] = Recipe("carpenter",(clubWeight, "lb"),
                               [("timber",clubCuFt)],
                               [],
                               description="1d4+1 damage; melee one-handed; 2 feet long")

handaxeHaftCuFt = cylinderCuFt(2,0.25/12)
handaxeHaftWeight = handaxeHaftCuFt * densityTimber
recipeStorage["handaxe haft"] = Recipe("carpenter",(handaxeHaftWeight,"lb"),
                                       [("timber",handaxeHaftCuFt)],
                                       [])

semiGoods.append("handaxe haft")

# head made from  metal having approximately these dimensions
handaxeHeadCuFt = Decimal(3/12) * Decimal(4/12) * Decimal(0.5/12)
# I reviewed the handaxeHeadCuFt calculation after adding the triangularPrismCuFt function to see whether that would be more fitting,
# but decided that the rectangular solution was still more appropriate, as the metal chunk would be rectangular before being hammered into shape
handaxeHeadWeight = handaxeHeadCuFt * densitySteel
# I'm envisioning this as basically a tomahawk, not a francisca;
# thus it is both a melee and thrown weapon
recipeStorage["handaxe"] = Recipe("blacksmith",(handaxeHeadWeight + handaxeHaftWeight,"lb"),
                                  [],
                                  [("steel",handaxeHeadWeight),("handaxe haft",1)],
                                  description="1d4+1 damage; melee/thrown; range 4/6/8")

halberdLength = Decimal(6)
ratioHalberdLengthSpearLength = halberdLength/Decimal(5)
halberdHaftWeight = ratioHalberdLengthSpearLength * getWeight("spear haft")
halberdHeadWeight = 2 * handaxeHeadWeight # is wider and takes up more length along the haft
halberdTotalWeight = halberdHaftWeight + halberdHeadWeight
recipeStorage["halberd"] = Recipe("blacksmith",(halberdTotalWeight ,"lb"),
                                  [],
                                  [("spear haft", halberdHaftWeight),("steel",halberdHeadWeight)],
                                  description="1d8 dmg; 2hand; " + str(halberdLength) + " ft long. Attacks normally; enemies 2 hexes away are threatened")

quarterstaffCuFt = cylinderCuFt(5,Decimal(0.5/12))
recipeStorage["quarterstaff"] = Recipe("carpenter",(quarterstaffCuFt * densityTimber,"lb"),
                                       [("timber",quarterstaffCuFt)],
                                       [],
                                       description="1d6 damage; melee two-handed; 5 ft long")

ratioJavelinWeightSpearWeight = Decimal(3.5/5)
javelinWeight = recipeStorage["spearhead"].weight[0] + (recipeStorage["spear haft"].weight[0] * ratioJavelinWeightSpearWeight)
recipeStorage["javelin"] = Recipe("blacksmith",(javelinWeight ,"lb"),
                                  [],
                                  [("spear haft", ratioJavelinWeightSpearWeight),("spearhead",1)],
                                  description="1d4+1 damage; melee or thrown 6/9/12; " + str(ratioJavelinWeightSpearWeight * 5) + " ft long")

# string used for a sling is braided; thus 3 feet of yarn string make 1 foot of braid
# in total a sling will require 4 feet of braid, thus 12 feet of yarn
# the pocket for ammunition is a 2x2 in. leather square; the tab is 1x1 in.
# the question I can't quite answer yet is WHO makes the sling?
# for now I will just call it the leatherworker, although I think that's a pretty crappy choice.
slingYarnFt = 12
slingYarnUnitRatio = slingYarnFt / getUnitSize("yarn, wool")
slingYarnWeight = slingYarnUnitRatio * getWeight("yarn, wool")
slingLeatherSqFt = (Decimal(2/12) ** 2) + (Decimal(1/12) ** 2)
slingLeatherUnitRatio = slingLeatherSqFt / getUnitSize("tanned cowhide")
slingLeatherWeight = slingLeatherUnitRatio * getWeight("tanned cowhide")
recipeStorage["sling"] = Recipe("leatherworker",(slingLeatherWeight + slingYarnWeight,"lb"),
                                [],
                                [("yarn, wool",slingYarnWeight),("tanned cowhide",slingLeatherUnitRatio)],
                                description="1d4 damage (1d4-1, min. 0, with scavenged ammo); missile; range 10/16/22")

musicalBoneCuFt = Decimal(1/12) * Decimal(1/8/12) * Decimal(6/12)
# musical bones come in pairs
musicalBonePairCuFt = musicalBoneCuFt * 2
recipeStorage["musical bones"] = Recipe("carpenter",(musicalBonePairCuFt * densityTimber,"lb"),
                                        [("timber",musicalBonePairCuFt)],
                                        [],
                                        description="pair of 6-inch curved wooden slats; wrist is rotated to create percussive music")

# lamella: a rectangle-like piece of material laced together to form armor
# these will form the basis of leather armor
leatherLamellaWidth = Decimal(4)/Decimal(12)
leatherLamellaHeight = Decimal(2)/Decimal(12)
leatherLamellaSqFt = leatherLamellaHeight * leatherLamellaWidth
leatherLamellaUnitRatio = leatherLamellaSqFt / getUnitSize("rawhide")
leatherLamellaWeight = leatherLamellaUnitRatio * getWeight("rawhide")
recipeStorage["leather lamella"] = Recipe("leatherworker", (leatherLamellaWeight, "lb"),
                                          [],
                                          [("rawhide", leatherLamellaUnitRatio)],
                                          description="2x4 inches; punched with holes for lacing")
semiGoods.append("leather lamella")

# square footage is a rough guess, but I've tried to make the sq ft needed for each armor consisten with the stated amount of coverage
leatherArmorSqFt = 8
numberOfLeatherLamella = leatherArmorSqFt / leatherLamellaSqFt
yarnFtPerLamella = 2
leatherArmorTotalYarn = numberOfLeatherLamella * yarnFtPerLamella
leatherArmorYarnUnitRatio = leatherArmorTotalYarn / getUnitSize("yarn, wool")
leatherArmorYarnWeight = leatherArmorYarnUnitRatio * getWeight("yarn, wool")
leatherArmorWeight = (numberOfLeatherLamella * leatherLamellaWeight) + leatherArmorYarnWeight
recipeStorage["leather armor"] = Recipe("leatherworker", (leatherArmorWeight,"lb"),
                                        [],
                                        [("leather lamella",numberOfLeatherLamella),("yarn, wool", leatherArmorYarnWeight)],
                                        description="AC 8; lamellar construction; with full sleeves, and covers torso to the waist")

shieldWoodThickness = Decimal(0.5)/Decimal(12)

# timber for a round wooden shield, a foot in radius
shieldRadius = Decimal(1) # feet
shieldArea = shieldRadius * Decimal(3.14)
shieldPerimeter = 2 * shieldArea # circumference

shieldTimberCuFt = shieldArea * shieldWoodThickness
shieldTimberWeight = shieldTimberCuFt * densityTimber

# a strip of leather reinforces the edge of the shield
shieldEdgingSqFt = shieldPerimeter * shieldWoodThickness
shieldEdgingUnitRatio = shieldEdgingSqFt / getUnitSize("rawhide")
shieldEdgingWeight = shieldEdgingUnitRatio * getWeight("rawhide")

# two of these ropes act as straps to provide protection against dropping if Dex check failed when hit by crit, at cost of taking time to secure them beforehand
shieldRopeStrapLength = Decimal(1) # 1 foot
shieldRopeStrapUnitRatio = shieldRopeStrapLength / getUnitSize("rope")
shieldRopeStrapWeight = shieldRopeStrapUnitRatio * getWeight("rope")

# handle, a u-shaped cylinder of wood attached to the shield's back
shieldHandleCuFt = cylinderCuFt(Decimal(6)/Decimal(12),Decimal(0.25)/Decimal(12))
shieldHandleWeight = shieldHandleCuFt * densityTimber

recipeStorage["shield, round wooden"] = Recipe("carpenter",(shieldTimberWeight + (shieldRopeStrapWeight * 2) + shieldHandleWeight + shieldEdgingWeight,"lb"),
                                               [("timber",shieldTimberCuFt + shieldHandleCuFt)],
                                               [("rope",shieldRopeStrapUnitRatio * 2), ("rawhide",shieldEdgingUnitRatio)],
                                               description="improves AC by -1; wooden shield " + str(shieldRadius * 2) + " feet across. has handle and rope straps")


# 2 ounces, or 1/8 lb, of pigment for a gallon of paint
poundsOfPigmentPerGallonPaint = Decimal(1)/Decimal(8)
# but we are doing only 1 quart of paint, so we divide by 4
poundsPigmentQuartPaint = poundsOfPigmentPerGallonPaint / 4
squareFeetPaintCanCover = Decimal(75)
recipeStorage["paint, red/yellow"] = Recipe("potter",(poundsPigmentQuartPaint + milkGallonWeight/Decimal(4),"lb"),
                                            [],
                                            [("cow milk",0.25),("pigment, red/yellow",poundsPigmentQuartPaint)],
                                            unit=(1,"quart"),
                                            description="in powder form; covers " + str(squareFeetPaintCanCover) + " sq ft. Keeps for 6 mo. sealed or 4 days once once opened")

recipeStorage["paint, ultramarine blue"] = Recipe("potter",(poundsPigmentQuartPaint + milkGallonWeight/Decimal(4),"lb"),
                                                  [],
                                                  [("cow milk",0.25),("pigment, ultramarine",poundsPigmentQuartPaint)],
                                                  unit=(1,"quart"),
                                                  description=recipeStorage["paint, red/yellow"].description)

# sling bullet is a 1-inch sphere, pressed into almondish shape
slingBulletCuFt = sphereCuFt(Decimal(1)/Decimal(12))
slingBulletWeight = slingBulletCuFt * densityClay
recipeStorage["sling bullet"] = Recipe("potter",(slingBulletWeight,"lb"),
                                       [],
                                       [("baked clay",slingBulletWeight)],
                                       unit=(1,"bullet"),
                                       description="made of clay, with almond-like shape")

recipeStorage["sling bullet, inscribed"] = Recipe("potter",(slingBulletWeight,"lb"),
                                                  [],
                                                  [("baked clay",slingBulletWeight)],
                                                  difficulty=4,
                                                  unit=(1,"bullet"),
                                                  description="inscribed with symbol, or word up to 5 chars")

# http://www.maritime.org/conf/conf-kaye-tar.htm
# this source gives 4,000 lbs of "light wood" per 40-60 gallons of pitch
# I'll go ahead and say it's 50 gallons per 4000 lbs
# thus, for 1 gallon, it's 4000/50 or 80 lbs of wood
lbsTimberPerGallonPitch = 80
timberCuFtPerGallonPitch = lbsTimberPerGallonPitch / densityTimber
recipeStorage["pitch, bulk"] = Recipe("potter",(weightWaterOneGal,"lb"),
                                      [("timber",timberCuFtPerGallonPitch)],
                                      [],
                                      unit=(1,"gallon"),
                                      description="viscous fluid derived from trees; customer supplies container")

semiGoods.append("pitch, bulk")
# temporarily renamed and made a semigood until I've sorted out a container for it,
# i.e. done programming to do accurate pricing for container + components scenarios


bicorneFeltSqFt = Decimal(1)
bicorneFeltUnitRatio = bicorneFeltSqFt / getUnitSize("felt")
bicorneWeight = bicorneFeltSqFt * getWeight("felt")
recipeStorage["hat, bicorne"] = Recipe("hatter",(bicorneWeight,"lb"),
                                       [],
                                       [("felt",bicorneFeltUnitRatio)],
                                       description="hat with both sides of brim turned up")

tricorneFeltSqFt = Decimal(1.25)
tricorneFeltUnitRatio = tricorneFeltSqFt / getUnitSize("felt")
tricorneWeight = tricorneFeltSqFt * getWeight("felt")
recipeStorage["hat, tricorne"] = Recipe("hatter",(tricorneWeight,"lb"),
                                        [],
                                        [("felt",tricorneFeltUnitRatio)],
                                        description="hat with brim folded up in a triangular shape")

# model the amount of clay needed for a cup,
# as the volume of a cylinder 4 inches high and 1 inch radius, minus the inner volume,
# a cylinder 3.5 inches high and 0.875 in radius
cupOuterVolume = cylinderCuFt(Decimal(4)/Decimal(12),Decimal(1)/Decimal(12))
cupInnerVolume = cylinderCuFt(Decimal(3.5)/Decimal(12),Decimal(0.875)/Decimal(12))
cupCuFt = cupOuterVolume - cupInnerVolume
cupClayWeight = cupCuFt * densityClay
recipeStorage["cup, earthenware"] = Recipe("potter",(cupClayWeight,"lb"),
                                           [],
                                           [("baked clay",cupClayWeight)],
                                           description="4 in. high, 2 in. diameter; no handle")

# using clay in place of sand
# 80/20 mix of sand to quicklime
cupGlassWeightClay = cupClayWeight * percentageClayInGlass
cupGlassWeightQl = cupClayWeight - cupGlassWeightClay
recipeStorage["cup, glass, clear"] = Recipe("glassblower",(cupClayWeight,"lb"),
                                            [],
                                            [("baked clay",cupGlassWeightClay),("quicklime",cupGlassWeightQl)],
                                            description="4 in. high, 2 in. diameter; no handle")

# shape is roughly a square pyramid
# 3-inch edge, 5-inches heigh
flaskInnerVolume = squarePyramidCuFt(Decimal(3)/Decimal(12),Decimal(5)/Decimal(12))
flaskOuterVolume = squarePyramidCuFt(Decimal(3.25)/Decimal(12),Decimal(5.25)/Decimal(12))
flaskCuFt = flaskOuterVolume - flaskInnerVolume
flaskClayWeight = flaskCuFt * densityClay
flaskStopperCuFt = cylinderCuFt(Decimal(0.75)/Decimal(12),Decimal(0.125)/Decimal(12))
recipeStorage["flask, earthenware"] = Recipe("potter",(flaskClayWeight,"lb"),
                                             [("timber",flaskStopperCuFt)],
                                             [("baked clay",flaskClayWeight)],
                                             description="holds 8 fl oz (1/2 a pint); with wooden stopper; 5 in. high")

flaskGlassWeightClay = flaskClayWeight * percentageClayInGlass
flaskGlassWeightQl = flaskClayWeight - flaskGlassWeightClay
recipeStorage["flask, glass"] = Recipe("glassblower",(flaskClayWeight,"lb"),
                                       [("timber",flaskStopperCuFt)],
                                       [("baked clay",flaskGlassWeightClay),("quicklime",flaskGlassWeightQl)],
                                       description="holds 8 fl oz (1/2 a pint); with wooden stopper; 5 in. high")

# inches
jarHeight = Decimal(28)
jarRadius = Decimal(2)
jarInnerVolume = cylinderCuFt(jarHeight/Decimal(12),jarRadius/Decimal(12))
jarOuterHeight = jarHeight + Decimal(0.25)
jarOuterRadius = jarRadius + Decimal(0.25)
jarOuterVolume = cylinderCuFt(jarOuterHeight/Decimal(12), jarOuterRadius/Decimal(12))
# sphere part of lid is a little knob for lifting it out
jarLidCuFt = cylinderCuFt(Decimal(0.5)/Decimal(12),jarOuterRadius/Decimal(12)) + sphereCuFt(Decimal(0.125)/Decimal(12))
jarCuFt = jarOuterVolume - jarInnerVolume + jarLidCuFt
jarClayWeight = jarCuFt * densityClay
recipeStorage["jar, earthenware"] = Recipe("potter",(jarClayWeight,"lb"),
                                           [],
                                           [("baked clay",jarClayWeight)],
                                           description="lidded; holds 12 and 1/8 pints; approx 28\" tall, 4.5\" diameter")

# bulk pitch is sold by the gallon
# we want to divide its price (or its weight) by 128 to get the per-oz price,
# then multiply that by 8 since pitch comes in an 8-fl-oz container
pitchConversionFactor = (Decimal(1)/Decimal(128)) * 8
pitchInFlaskWeightPitch = getWeight("pitch, bulk") * pitchConversionFactor
recipeStorage["pitch"] = Recipe("potter",(pitchInFlaskWeightPitch + getWeight("flask, earthenware"),"lb"),
                                [],
                                [("pitch, bulk",pitchConversionFactor),("flask, earthenware",1)],
                                unit=(8,"fl oz"),
                                description="contained in earthenware flask")

# in feet, as always
# one sixteenth of an inch
buttonHeight = (Decimal(1)/Decimal(16))/Decimal(12)
buttonRadius = (Decimal(1)/Decimal(4))/Decimal(12)
buttonCuFt = cylinderCuFt(buttonHeight, buttonRadius)
# the above can apply to all buttons unless otherwise desired

buttonClayWeight = buttonCuFt * densityClay
recipeStorage["button, ceramic"] = Recipe("potter",(buttonClayWeight,"lb"),
                                          [],
                                          [("baked clay",buttonClayWeight*24)],
                                          unit=(24,"ct"),
                                          description="two dozen buttons")

buttonGlassWeightClay = buttonClayWeight * percentageClayInGlass
buttonGlassWeightQl = buttonClayWeight - buttonGlassWeightClay
recipeStorage["button, glass"] = Recipe("glassblower",(buttonClayWeight,"lb"),
                                        [],
                                        [("baked clay",buttonGlassWeightClay*24),("quicklime",buttonGlassWeightQl*24)],
                                        unit=(24,"ct"),
                                        description="two dozen buttons")

waistcoatLayers = 2
waistcoatSqFtWool = 8 * waistcoatLayers
waistcoatNumButtons = 12
waistcoatThread = 4 * waistcoatSqFtWool
waistcoatThreadUnitRatio = waistcoatThread / getUnitSize("thread")
waistcoatThreadWeight = waistcoatThreadUnitRatio * getWeight("thread")
waistcoatWeightWool = waistcoatSqFtWool * getWeight("wool cloth")
recipeStorage["waistcoat"] = Recipe("tailor",(waistcoatWeightWool + waistcoatThreadWeight,"lb"),
                                    [],
                                    [("wool cloth",waistcoatSqFtWool), ("thread",waistcoatThreadUnitRatio),("button, ceramic",0.5)],
                                    description="men's torso garment, with 12 buttons; worn by all levels of society")

dressSqFtWool = 20
dressThread = 4 * dressSqFtWool
dressThreadUnitRatio = dressThread / getUnitSize("thread")
dressThreadWeight = dressThreadUnitRatio * getWeight("thread")
dressWeightWool = dressSqFtWool * getWeight("wool cloth")
recipeStorage["dress"] = Recipe("tailor",(dressWeightWool + dressThreadWeight,"lb"),
                                [],
                                [("wool cloth",dressSqFtWool), ("thread",dressThreadUnitRatio)],
                                description="women's garment")

# here "cowl" doesn't just mean hood, but rather the flowy wide-sleeved garment worn by monks
cowlSqFt = Decimal(1.25) * dressSqFtWool
cowlClothWt = cowlSqFt * getWeight("wool cloth")
cowlThread = cowlSqFt * 4
cowlThreadUR = cowlThread / getUnitSize("thread")
cowlThreadWt = cowlThreadUR * getWeight("thread")
recipeStorage["cowl"] = Recipe("tailor",(cowlThreadWt + cowlClothWt,"lb"),
                               [],
                               [("wool cloth", cowlSqFt),
                                ("thread", cowlThreadUR)],
                               difficulty=Decimal(0.5), # because they are roughly made
                               description="hooded, wide-sleeved full-body garment, commonly worn by monks")

# model this as fancier cowl
recipeStorage["cassock"] = Recipe("tailor",(cowlThreadWt + cowlClothWt,"lb"),
                                  [],
                                  [("cowl",1),
                                   ("button, ceramic",1)],
                                  difficulty=2,
                                  description="buttoned full-body garment, commonly worn by priests")

scapularRawClothSqFt = Decimal(1.5) * Decimal(10)
scapularHeadCutout = Decimal(pi) * (Decimal(0.5) ** 2)
scapularFinalClothSqFt = scapularRawClothSqFt - scapularHeadCutout
scapularWt = (scapularFinalClothSqFt / getUnitSize("wool cloth")) *  getWeight("wool cloth")
recipeStorage["scapular"] = Recipe("tailor",(scapularWt,"lb"),
                                   [],
                                   [("wool cloth", scapularRawClothSqFt)],
                                   description="long tabard-like garment; front and back drape to floor")

tabardRawClothSqFt = Decimal(0.5) * scapularRawClothSqFt
tabardHeadCutout = Decimal(pi) * (Decimal(0.5) ** 2)
tabardFinalClothSqFt = tabardRawClothSqFt - tabardHeadCutout
tabardWt = (tabardFinalClothSqFt / getUnitSize("wool cloth")) *  getWeight("wool cloth")
recipeStorage["tabard"] = Recipe("tailor",(tabardWt,"lb"),
                                   [],
                                   [("wool cloth", tabardRawClothSqFt)],
                                   description="torso garment; usually additionally decorated with coat of arms")


# assuming 30-inch waist and falling 2 feet to mid-calf, we have 720 square inches or 5 square feet
skirtSqFtWool = 5
skirtThread = 4 # one 2-foot thread connecting it together like a tube, doubled for strength
skirtThreadUnitRatio = skirtThread / getUnitSize("thread")
skirtThreadWeight = skirtThreadUnitRatio * getWeight("thread")
skirtWeightWool = skirtSqFtWool * getWeight("wool cloth")
recipeStorage["skirt"] = Recipe("tailor",(skirtWeightWool + skirtThreadWeight,"lb"),
                                [],
                                [("wool cloth",skirtSqFtWool), ("thread",skirtThreadUnitRatio)],
                                description="mid-calf length; worn with bodice or layered under dress")

bodiceSqFtWool = 6
bodiceThread = (4 * bodiceSqFtWool) # the normal 4 * wool sqft
bodiceThreadUnitRatio = bodiceThread / getUnitSize("thread")
bodiceThreadWeight = bodiceThreadUnitRatio * getWeight("thread")
bodiceWeightWool = bodiceSqFtWool * getWeight("wool cloth")

bodiceLacingFt = 4
bodiceLacingUR = bodiceLacingFt / getUnitSize("yarn, wool")
bodiceLacingWeight = bodiceLacingUR * getWeight("yarn, wool")
recipeStorage["bodice"] = Recipe("tailor",(bodiceWeightWool + bodiceThreadWeight + bodiceLacingWeight,"lb"),
                                 [],
                                 [("wool cloth", bodiceSqFtWool),
                                  ("thread", bodiceThreadUnitRatio),
                                  ("yarn, wool", bodiceLacingUR)],
                                 description="women's garment, laced in front; not restrictive like corset")

# let's just pretent its a tube 2 feet around (circumference of my head at ear level) and 8 inches high, then the tube is closed at the top
knitCapSqFtWool = Decimal(2) * (Decimal(2) / Decimal(3))
knitCapWeightWool = knitCapSqFtWool * getWeight("wool cloth")
# no thread needed, it's just knitted in one go
recipeStorage["knit cap"] = Recipe("tailor",(knitCapWeightWool,"lb"),
                                   [],
                                   [("wool cloth",knitCapSqFtWool)],
                                   description="woolen cap, like a tuque")

# model as a tube 1 foot long (my foot) plus 18 inches (ankle to knee), with width 1 foot
stockingSqFtWool = Decimal(2.5) * Decimal(1)
stockingWeightWool = stockingSqFtWool * getWeight("wool cloth")
stockingNumberSold = 2
recipeStorage["stockings"] = Recipe("tailor",(stockingWeightWool * stockingNumberSold,"lb"),
                                   [],
                                   [("wool cloth",stockingSqFtWool * stockingNumberSold)],
                                   description=str(stockingNumberSold) + " stockings; unisex; rises to knee")

hoseSqFtWool = stockingSqFtWool * Decimal(1.5) * Decimal(2)
hoseWeightWool = hoseSqFtWool * getWeight("wool cloth")
recipeStorage["hose"] =  Recipe("tailor",(hoseWeightWool,"lb"),
                                   [],
                                   [("wool cloth",hoseSqFtWool)],
                                   description="tights covering BOTH LEGS from foot to waist")

# waist section is modeled as 36-inch by 1 foot tube
# leg sections are modeled as two conic shells, two feet at top of thigh and 1.5 feet at knee; length 1.25 ft
breechWaistSqFt = Decimal(3)
breechLegSqFt = truncatedConeCuFt(Decimal(2), Decimal(1.5), Decimal(1.25)) - truncatedConeCuFt(Decimal(1.8), Decimal(1.3), Decimal(1.25))
breechesWoolSqFt = breechWaistSqFt + (2 * breechLegSqFt)
breechesWoolWeight = breechesWoolSqFt * getWeight("wool cloth")
breechesThreadFeet = 4 * breechesWoolSqFt
breechesThreadUnitRatio = breechesThreadFeet / getUnitSize("yarn, wool")
breechesThreadWeight = breechesThreadUnitRatio * getWeight("yarn, wool")
breechesTotalWeight = breechesWoolWeight + breechesThreadWeight
recipeStorage["breeches"] = Recipe("tailor",(breechesWoolWeight,"lb"),
                                   [],
                                   [("wool cloth",breechesWoolSqFt),("thread",breechesThreadWeight),("button, ceramic",0.75)], #uses 18 buttons
                                   description="tight knee-length pants; no pockets; worn by middle and upper class")


shoeHeelTimberCuFt = ((Decimal(1)/Decimal(12)) ** 2) * (Decimal(0.5)/Decimal(12))
shoeHeelTimberWeight = shoeHeelTimberCuFt * densityTimber
shoeLeatherSqFt = 1
shoeLeatherUnitRatio = shoeLeatherSqFt / getUnitSize("tanned cowhide")
shoeLeatherWeight = shoeLeatherUnitRatio * getWeight("tanned cowhide")
recipeStorage["shoe"] = Recipe("cobbler",(shoeLeatherWeight + shoeHeelTimberWeight,"lb"),
                               [("timber",shoeHeelTimberCuFt)],
                               [("tanned cowhide",shoeLeatherUnitRatio)],
                               # NOT the weight of the leather:
                               # with leather components, you want to use the unitRatio, since that represents the amount of units of e.g. cowhide which you are using up
                               # e.g. a cowhide is 50 square foot and you are using 1 square foot for a shoe, thus 1/50 of a cowhide is being used
                               # trying to do it by weight adds an extra layer of redirection
                               description="leather and wood construction")

recipeStorage["mace, masterwork"] = Recipe("blacksmith",(getWeight("mace haft") + (6 * maceFlangeWeight),"lb"),
                                           [],
                                           [("mace haft",1),("mace flange",6)],
                                           difficulty=8,
                                           description="1d8 damage, one-handed, melee; haft is 2 ft.")

hoodSqFtWool = knitCapSqFtWool * 4 # it's larger and it includes capelet
hoodWeightWool = hoodSqFtWool * getWeight("wool cloth")
recipeStorage["hood"] = Recipe("tailor",(hoodWeightWool,"lb"),
                               [],
                               [("wool cloth",hoodSqFtWool)],
                               description="with attached capelet, covers head and neck")

# thicker and more crinkled than a hood, but less material overall
wimpleSqFtWool = hoodSqFtWool / Decimal(2)
wimpleWeightWool = wimpleSqFtWool * getWeight("wool cloth")
recipeStorage["wimple"] = Recipe("tailor",(wimpleWeightWool,"lb"),
                               [],
                               [("wool cloth",wimpleSqFtWool)],
                               description="thick headdress commonly worn by nuns")


aquaFortisWeight = waterWeightOnePint / Decimal(2)
recipeStorage["aqua fortis"] = Recipe("alchemist",(aquaFortisWeight + getWeight("flask, glass"),"lb"),
                                      [("copper ore",3)],
                                      [],
                                      unit=(8,"fl oz"),
                                      difficulty=4, # for cleaning and separating the ore and doing the lab work
                                      description="moderate-strength; on successful (breaking) throw, 1d3 damage and 1 splash")

# chicken takes ~6 months to reach maturity, and then produces eggs
# alternatively can be slaughtered (in reality it only takes about 4 months until it's slaughterable)
# 6 months of food, 4 weeks per month, and let's say 1 lb of feed per week
chickenFeedLbs = 6 * 4
recipeStorage["chicken, mature"] = Recipe("farmer",(5,"lb"),
                                          [], # we say the cost of land for chickens is negligible
                                          [("feed, cattle/horse",chickenFeedLbs)],
                                          description="can be slaughtered or kept to lay eggs")

recipeStorage["chicken, killed"] = Recipe("butcher",(5,"lb"),
                                          [],
                                          [("chicken, mature",1)],
                                          description="not plucked, just dead")

chickenDressPercentage = Decimal(0.67)
recipeStorage["chicken, butchered"] = Recipe("butcher",(chickenDressPercentage * getWeight("chicken, killed"), "lb"),
                                             [],
                                             [("chicken, killed",1)],
                                             description="plucked and ready for cooking")

# let's declare that feathers make up 5% of the chicken's of body weight (figures vary)
feathersPercentageOfChickenWeight = Decimal(0.05)
# furthermore, let's base the price of the feathers on the weight of the non-meat portion of the chicken carcass
chickenNonDressPercentage = 1 - chickenDressPercentage
recipeStorage["feathers, chicken"] = Recipe("butcher",(feathersPercentageOfChickenWeight * getWeight("chicken, killed"),"lb"),
                                            [],
                                            [("chicken, killed",chickenNonDressPercentage)],
                                            unit=("4000","unit"),
                                            description="from one chicken")

# a single chicken, once mature, will produce eggs
# it will produce approximately 300 eggs in the first year, and less in future years, so let's adjust that first-year figure to 250 for a more average number
# in the meantime it must be fed for a year -- 2 lbs of feed per week
egglayingChickenFeedLbs = 52 * 2 # 52 weeks per year
eggsChickenPerYear = 250
# we will price a single egg
recipeStorage["egg, chicken"] = Recipe("farmer",(Decimal(0.125),"lb"),
                                       [],
                                       [("chicken, mature",1/eggsChickenPerYear),("feed, cattle/horse",egglayingChickenFeedLbs/eggsChickenPerYear)])

# base volume of starting material: 6 x 2 x 2 inches
statuetteCuFt = (Decimal(6)/Decimal(12)) * (Decimal(2)/Decimal(12)) * (Decimal(2)/Decimal(12))
# let's assume 1/4 of the material is carved away
statuetteWoodWeight = Decimal(0.75) * (statuetteCuFt * densityTimber)
recipeStorage["statuette, wooden, small"] = Recipe("carver",(statuetteWoodWeight,"lb"),
                                                   [("timber",statuetteCuFt)],
                                                   [],
                                                   description="6x2x2 in.")

# life size, thus starting from a block of wood six feet tall, and 1 foot on a side
statueCuFt = 6 * 1 * 1
# let's assume 1/4 of the material is carved away
statueWoodWeight = Decimal(0.75) * (statueCuFt * densityTimber)
recipeStorage["statue, wooden, life-size"] = Recipe("carver",(statueWoodWeight,"lb"),
                                                    [("timber",statueCuFt)],
                                                    [],
                                                    difficulty=4,
                                                    description="purchaser must wait 1d4 weeks before completion (ask DM about waiting dice); subject of statue must pose for 3 days of that time")

gongSmallRadius = 1
gongSmallThickness = Decimal(0.5)/12
gongSmallBodyCuFt = cylinderCuFt(gongSmallRadius,gongSmallThickness)
# the 'button' in the middle of the gong, modeled as a sphere's worth of metal,
# with one half on each side of the gong
gongSmallButtonRadius = 1/12
gongSmallButtonCuFt = sphereCuFt(gongSmallButtonRadius)
# the total cubic feet is the body, plus the button,
# MINUS the chunk of the middle where the body and button volumes would intersect
# (if they were actually separate pieces, although they're not)
# that intersection volume is a cylinder as wide as the button,
# and as high as the body.
# in addition, we must also subtract away the volumes of two 1 inch holes,
# through which ropes are passed to hold the gong in its frame
gongSmallIntersectionCuFt = cylinderCuFt(gongSmallButtonRadius, gongSmallThickness)
gongHoleCuFt = cylinderCuFt(0.5/12, gongSmallThickness)
gongSmallTotalCuFt = gongSmallBodyCuFt + gongSmallButtonCuFt - gongSmallIntersectionCuFt - (2*gongHoleCuFt)
gongSmallWeight = gongSmallTotalCuFt * densityBronze
recipeStorage["gong, small"] = Recipe("blacksmith",(gongSmallWeight,"lb"),
                                      [],
                                      [("bronze",gongSmallWeight)],
                                      description="bronze button gong; " + str(2*gongSmallRadius) + " feet across; with 2 holes for hanging")

# gong frame for small gong
# made from 6 chunks of wood, all being 1x1 inches wide and high
# the 4 longer pieces form a square frame around the gong,
# the 2 shorter pieces are attached perpendicular to the frame, forming the base
gongSmallFrameCommonElement = Decimal(1)/Decimal(12) ** 2
gongSmallFrameLongPiece = gongSmallFrameCommonElement * Decimal(1.5 * (2 * gongSmallRadius))
gongSmallFrameShortPiece = gongSmallFrameCommonElement * gongSmallRadius
gongSmallFrameTotalCuFt = (4 * gongSmallFrameLongPiece) + (2 * gongSmallFrameShortPiece)
gongSmallFrameWeight = gongSmallFrameTotalCuFt * densityTimber
recipeStorage["gong frame, small, plain"] = Recipe("carpenter",(gongSmallFrameWeight,"lb"),
                                                   [("timber",gongSmallFrameTotalCuFt)],
                                                   [],
                                                   description="square wooden frame to hold gong; requires 2 6-inch ropes")

torchStakeRadius = Decimal(0.5)/Decimal(12)
torchStakeLength = 3 # feet
torchStakeCuFt = cylinderCuFt(torchStakeLength, torchStakeRadius)
torchStakeWeight = torchStakeCuFt * densityTimber
recipeStorage["torch stake"] = Recipe("carver",(torchStakeWeight,"lb"),
                                      [("timber",torchStakeCuFt)],
                                      [],
                                      description="reusable; " + str(torchStakeLength) + " feet long")

# 4 inches by 2 feet
torchFuelWoolSqFt = 2 * Decimal(4)/Decimal(12)
torchFuelWoolWeight = torchFuelWoolSqFt * getWeight("wool cloth")
recipeStorage["torch fuel"] = Recipe("carver",(torchFuelWoolWeight + pitchInFlaskWeightPitch,"lb"),
                                     [],
                                     [("wool cloth",torchFuelWoolSqFt),("pitch",1)],
                                     description="illuminates 5-hex radius for 30 minutes. Wool, soaked in pitch")

spikeLength = Decimal(0.5)
spikeRadius = Decimal(0.75)/Decimal(12)
spikeCuFt = coneCuFt(spikeLength,spikeRadius)
spikeWeight = spikeCuFt * densityWroughtIron
recipeStorage["spike"] = Recipe("blacksmith",(spikeWeight,"lb"),
                                [],
                                [("wrought iron",spikeWeight)],
                                description="for affixing ropes and chains; " + str(spikeLength) + " ft long, " + str(2 * spikeRadius) + " in. thick")

cakeSpongeNumEggs = 3
cakeSpongeWeightEggs = cakeSpongeNumEggs * getWeight("egg, chicken")
# the recipe I found said to use the same weight of sugar, flour, and fat (suet) as the eggs
recipeStorage["cake, sponge"] = Recipe("baker",(cakeSpongeWeightEggs*4,"lb"),
                                       [],
                                       [("egg, chicken",3),("brown sugar",cakeSpongeWeightEggs),("flour",cakeSpongeWeightEggs),("suet",cakeSpongeWeightEggs)],
                                       description="light and fluffy cake")

tankardInnerRadius = Decimal(1.25)/Decimal(12)
tankardInnerHeight = Decimal(6)/Decimal(12)
# the inner volume is the amount of liquid it can hold, the size of the "inner" cylinder
tankardInnerVolume = cylinderCuFt(tankardInnerHeight, tankardInnerRadius)
tankardInnerVolumeInPints = tankardInnerVolume / (cuFtPerGallonLiquid / 8)
tankardOuterRadius = tankardInnerRadius + Decimal(0.125)/Decimal(12)
tankardOuterHeight = tankardInnerHeight + Decimal(0.25)/Decimal(12)
# the outer volume is the size of the tankard if it were a solid cylinder
tankardOuterVolume = cylinderCuFt(tankardOuterHeight, tankardOuterRadius)
# thus, we can find the total volume of the body of the tankard by subtracting the liquid-holding volume from the solid-body cylinder
tankardCuFt = tankardOuterVolume - tankardInnerVolume

clayTankardWeight = tankardCuFt * densityClay
recipeStorage["tankard"] = Recipe("potter",(clayTankardWeight,"lb"),
                                  [],
                                  [("baked clay",clayTankardWeight)],
                                  description="earthenware, " + str(tankardOuterHeight * 12) + " in. tall; holds " + str(tankardInnerVolumeInPints) + " pints")


# chalice is composed of three parts:
# bowl, stem, base
# bowl is a half-sphere, minus an interior half sphere slightly smaller
chaliceBowlRadius = Decimal(2/12)
chaliceBowlThickness = Decimal(1/8)/Decimal(12)
chaliceBowlOuterVolume = sphereCuFt(chaliceBowlRadius)/2
chaliceBowlInnerVolume = sphereCuFt(chaliceBowlRadius-chaliceBowlThickness)/2
chaliceBowlCuFt = chaliceBowlOuterVolume - chaliceBowlInnerVolume
# let's find the amount we can hold inside the chalice
chaliceBowlInnerVolumePints = chaliceBowlInnerVolume * cubicFootInPints
# stem
chaliceStemRadius = Decimal(0.5)/Decimal(12)
chaliceStemHeight = Decimal(1)/Decimal(12)
chaliceStemCuFt = cylinderCuFt(chaliceStemHeight, chaliceStemRadius)
# base
# a truncated cone, with the area of the smaller circular face being the same width as the stem height b/c that's where the stem's volume attaches
chaliceBaseBigRadius = Decimal(2)/Decimal(12)
chaliceBaseSmallRadius = chaliceStemRadius
chaliceBaseHeight = Decimal(1)/Decimal(12)
chaliceBaseCuFt = truncatedConeCuFt(chaliceBaseBigRadius, chaliceBaseSmallRadius, chaliceBaseHeight)
chaliceTotalHeight = chaliceBowlRadius + chaliceStemHeight + chaliceBaseHeight
chaliceTotalCuFt = chaliceBowlCuFt + chaliceStemCuFt + chaliceBaseCuFt

leadChaliceWeight = chaliceTotalCuFt * densityLead
recipeStorage["chalice"] = Recipe("tinsmith",(leadChaliceWeight,"lb"),
                                  [("lead ore",leadChaliceWeight)],
                                  [],
                                  description="lead; " + str(chaliceTotalHeight * 12) + " inches tall; holds " + str(chaliceBowlInnerVolumePints) + " pints")

# goblet: a chalice with a tall stem
gobletStemHeight = Decimal(4)/Decimal(12)
gobletStemCuFt = cylinderCuFt(gobletStemHeight, chaliceStemRadius)
gobletTotalHeight = chaliceBowlRadius + gobletStemHeight + chaliceBaseHeight
gobletTotalCuFt = chaliceBowlCuFt + gobletStemCuFt + chaliceBaseCuFt

leadGobletWeight = gobletTotalCuFt * densityLead
recipeStorage["goblet"] = Recipe("tinsmith",(leadGobletWeight,"lb"),
                                 [("lead ore",leadGobletWeight)],
                                 [],
                                 description="long-stemmed chalice; " + str(gobletTotalHeight * 12) + " inches tall")


# TODO: bricks need straw or flax in them to make them strong!!!
brickSqFt = Decimal(4)/Decimal(12) * Decimal(8)/Decimal(12) * Decimal(2)/Decimal(12)
brickWeight = brickSqFt * densityClay
recipeStorage["brick"] = Recipe("potter",(brickWeight,"lb"),
                                [],
                                [("baked clay",brickWeight)])

spiritMashWaterGal = gallonsPerBarrel
spiritMashBrownSugarLbs = 6 * spiritMashWaterGal
desiredVolumeSpiritGal = gallonsPerBarrel
spiritDilutedABV = calculateABV(spiritMashBrownSugarLbs, 0, 0, spiritMashWaterGal, desiredVolumeSpiritGal)
recipeStorage["rum, barrel"] = Recipe("brewer",(weightWaterOneGal * gallonsPerBarrel + getWeight("barrel"),"lb"),
                                      [],
                                      [("brown sugar",spiritMashBrownSugarLbs),("barrel",1)],
                                      unit=(gallonsPerBarrel,"gallon"),
                                      description="light rum; in barrel; " + str(spiritDilutedABV) + "% alcohol")

flaskRumWeight = Decimal(0.5) * waterWeightOnePint + getWeight("flask, glass")
recipeStorage["rum, flask"] = Recipe("brewer",(flaskRumWeight,"lb"),
                              [],
                              [("rum, barrel",Decimal(0.5)/pintsPerBarrel),("flask, glass",1)],
                              unit=(8,"fl oz"),
                              description="light rum; in half-pint glass flask; " + str(spiritDilutedABV) + "% alcohol")


recipeStorage["tobacco, uncured"] = Recipe("farmer",(1,"lb"),
                                           [("tobacco",1)],
                                           [])
semiGoods.append("tobacco, uncured")

recipeStorage["tobacco, cured"] = Recipe("farmer",(1,"lb"),
                                         [],
                                         [("tobacco, uncured",5)])
semiGoods.append("tobacco, cured")

pipeTobaccoInOz = 2
pipeTobaccoWeight = Decimal(pipeTobaccoInOz)/Decimal(16)
clothTwistSqFt = Decimal(4)/Decimal(12) ** 2
clothTwistWoolWeight = clothTwistSqFt * getWeight("wool cloth")
recipeStorage["pipe tobacco"] = Recipe("tobacconist",(pipeTobaccoWeight + clothTwistSqFt,"lb"),
                                       [],
                                       [("tobacco, cured",pipeTobaccoWeight),("wool cloth",clothTwistSqFt)],
                                       unit=(pipeTobaccoInOz,"oz"),
                                       description="wrapped in cloth twist")


pipeSmokingWeight = Decimal(0.33)
recipeStorage["pipe, smoking"] = Recipe("potter",(pipeSmokingWeight,"lb"),
                                        [],
                                        [("baked clay",pipeSmokingWeight)],
                                        description="long-stemmed tobacco pipe")

recipeStorage["herring, fresh"] = Recipe("fishmonger",(1,"lb"),
                                         [("herring",1)],
                                         [])
semiGoods.append("herring, fresh")

recipeStorage["cod, fresh"] = Recipe("fishmonger",(1,"lb"),
                                     [("cod",1)],
                                     [])
semiGoods.append("cod, fresh")

def recipeSaltFish(freshFishName, startWeight):
    saltAmount = Decimal(0.1) * startWeight
    # I assume the fish ultimately increases in weight by half the weight of the salt used
    finalWeight = startWeight + Decimal(0.5) * saltAmount
    return Recipe("fishmonger",(finalWeight,"lb"),
                  [("salt",saltAmount)],
                  [(freshFishName, startWeight)],
                  description="salted fish fillets")

recipeStorage["salt herring"] = recipeSaltFish("herring, fresh",1)
recipeStorage["salt cod"] = recipeSaltFish("cod, fresh",1)


def steelPlatingWeight(thickness):
    """Returns the amount of steel needed to produce 1 square foot of plating at a given thickness (also expressed in feet).
    (To make this function generic to any kind of metal, I would first need to move away from the current system, in which material densities are stored in variable names,
    and instead store them in a dictionary with names as keys and densities as values.)"""
    cuFt = 1 * 1 * thickness
    return cuFt * densitySteel

breastplateThickness = Decimal(0.1)/Decimal(12)
breastplateSqFt = 6
breastplateWeight = breastplateSqFt * steelPlatingWeight(breastplateThickness)
recipeStorage["breastplate"] = Recipe("blacksmith",(breastplateWeight,"lb"),
                                      [],
                                      [("steel",breastplateWeight)],
                                      description="AC 5 when worn on its own; part of half- and full-plate")

fauldThickness = Decimal(0.1)/Decimal(12)
fauldSqFt = 2
fauldWeight = fauldSqFt * steelPlatingWeight(fauldThickness)
recipeStorage["fauld"] = Recipe("blacksmith",(fauldWeight,"lb"),
                                [],
                                [("steel",fauldWeight)],
                                description="hip and groin armor; part of full-plate")

pauldronThickness = Decimal(0.05)/Decimal(12)
pauldronSqFt = Decimal(0.5)
pauldronWeight = pauldronSqFt * steelPlatingWeight(pauldronThickness)
recipeStorage["pauldron"] = Recipe("blacksmith",(pauldronWeight,"lb"),
                                   [],
                                   [("steel",pauldronWeight)],
                                   description="shoulder armor; part of half- and full-plate")

rerebraceThickness = Decimal(0.075)/Decimal(12)
rerebraceSqFt = Decimal(8)/Decimal(12)
rerebraceWeight = rerebraceSqFt * steelPlatingWeight(rerebraceThickness)
recipeStorage["rerebrace"] = Recipe("blacksmith",(rerebraceWeight,"lb"),
                                    [],
                                    [("steel",rerebraceWeight)],
                                    description="armor for upper arm; part of half- and full-plate")
vambraceThickness = Decimal(0.075)/Decimal(12)
vambraceSqFt = Decimal(8)/Decimal(12) * Decimal(9)/Decimal(12)
vambraceWeight = vambraceSqFt * steelPlatingWeight(vambraceThickness)
recipeStorage["vambrace"] = Recipe("blacksmith",(vambraceWeight,"lb"),
                                   [],
                                   [("steel",vambraceWeight)],
                                   description="armor for forearm; part of half- and full-plate")

cuissThickness = Decimal(0.075)/Decimal(12)
cuissSqFt = Decimal(8)/Decimal(12) * Decimal(20)/Decimal(12)
cuissWeight = cuissSqFt * steelPlatingWeight(cuissThickness)
recipeStorage["cuiss"] = Recipe("blacksmith",(cuissWeight,"lb"),
                                [],
                                [("steel",cuissWeight)],
                                description="armor for thigh; part of full-plate")

greaveThickness = Decimal(0.075)/Decimal(12)
greaveSqFt = 1
greaveWeight = greaveSqFt * steelPlatingWeight(greaveThickness)
recipeStorage["greave"] = Recipe("blacksmith",(greaveWeight,"lb"),
                                 [],
                                 [("steel",greaveWeight)],
                                 description="armor for lower leg; part of full-plate")

halfPlateWeight = breastplateWeight + 2 * pauldronWeight + 2 * rerebraceWeight + 2 * vambraceWeight
fullPlateWeight = halfPlateWeight + fauldWeight + 2 * cuissWeight + 2 * greaveWeight

recipeStorage["half-plate armor"] = Recipe("blacksmith",(halfPlateWeight,"lb"),
                                           [],
                                           [("breastplate",1),("pauldron",2),("rerebrace",2),("vambrace",2)],
                                           description="AC 4; includes breastplate, pauldrons, rerebraces, and vambraces")

recipeStorage["full-plate armor"] = Recipe("blacksmith",(fullPlateWeight,"lb"),
                                           [],
                                           recipeStorage["half-plate armor"].subRecipes + [("fauld",1),("cuiss",2),("greave",2)],
                                           description="AC 3; as half-plate, plus fauld, cuisses, and greaves")

cinnabarPercentMercury = Decimal(86.218)
weightMercuryHalfPint = (densityMercury / cubicFootInPints) / Decimal(2)
cinnabarForHalfPintMercury = weightMercuryHalfPint / (cinnabarPercentMercury / 100)
recipeStorage["mercury"] = Recipe("smelter", (weightMercuryHalfPint,"lb"),
                                  [("cinnabar",cinnabarForHalfPintMercury)],
                                  [("quicklime",cinnabarForHalfPintMercury)], # following the method presented in Subterraneal Treasure: use as much lime as cinnabar
                                  unit=(0.5,"pint"),
                                  description="liquid phase; customer supplies container")

# coat of plates
# the best of the leather-type armors, before giving way to the haubergeon
coatOfPlatesRawhideSqFt = Decimal(leatherArmorSqFt)
coatOfPlatesSteelSqFt = coatOfPlatesRawhideSqFt / Decimal(2)
coatOfPlatesSteelThickness = Decimal(0.05)/Decimal(12)
coatOfPlatesSteelWeight = coatOfPlatesSteelSqFt * steelPlatingWeight(coatOfPlatesSteelThickness)
coatOfPlatesRawhideUnitRatio = coatOfPlatesRawhideSqFt / getUnitSize("rawhide")
coatOfPlatesRawhideWeight = coatOfPlatesRawhideUnitRatio * getWeight("rawhide")
coatOfPlatesTotalWeight = coatOfPlatesSteelWeight + coatOfPlatesRawhideWeight
recipeStorage["coat of plates"] = Recipe("leatherworker", (coatOfPlatesTotalWeight,"lb"),
                                         [],
                                         [("rawhide",coatOfPlatesRawhideUnitRatio),("steel",coatOfPlatesSteelWeight)],
                                         description="AC 7; toughened leather with internal steel plates")


arrowShaftLength = 3
arrowShaftRadius = Decimal(0.125)/Decimal(12)
arrowShaftCuFt = cylinderCuFt(arrowShaftLength, arrowShaftRadius)
arrowShaftWeight = arrowShaftCuFt * densityTimber
recipeStorage["arrow shaft"] = Recipe("carver",(arrowShaftWeight,"lb"),
                                      [("timber",arrowShaftCuFt)],
                                      [])
semiGoods.append("arrow shaft")

# arrowhead shape can be decomposed into a tang and a point
# the former is a cylinder, the latter is a cone
arrowheadPointLength = Decimal(2)/Decimal(12)
arrowheadTangLength = Decimal(1)/Decimal(12)
arrowheadPointCuFt = coneCuFt(arrowheadPointLength,Decimal(0.125)/Decimal(12))
arrowheadTangCuFt = cylinderCuFt(arrowheadTangLength,Decimal(0.0625)/Decimal(12))
arrowheadCuFt = arrowheadTangCuFt + arrowheadPointCuFt
arrowheadWeight = arrowheadCuFt * densitySteel
recipeStorage["arrowhead"] = Recipe("blacksmith",(arrowheadWeight, "lb"),
                                    [],
                                    [("steel",arrowheadWeight)])
semiGoods.append("arrowhead")

feathersPerFinishedArrow = 4
# let's assume that only 1/4 of chicken feathers, the wing ones, can be used for fletching
fletcherUsableFeatherPercentage = Decimal(0.25)
feathersToFinishArrow = feathersPerFinishedArrow / fletcherUsableFeatherPercentage
arrowFeathersUnitRatio = feathersToFinishArrow / getUnitSize("feathers, chicken")
arrowFeathersWeight = arrowFeathersUnitRatio * getWeight("feathers, chicken")
arrowTotalWeight = getWeight("arrow shaft") + getWeight("arrowhead") + arrowFeathersWeight
# for now, I'll use the bowyer for both bowmaking and fletching recipes
recipeStorage["arrow"] = Recipe("bowyer",(arrowTotalWeight,"lb"),
                                [],
                                [("feathers, chicken",arrowFeathersWeight),
                                 ("arrow shaft",1),
                                 ("arrowhead",1)],
                                description="for bows; " + str(arrowShaftLength) + "-ft shaft")

# lime is not necessarily needed, it can be done just by boiling
hideGlueDesiredWeight = Decimal(1)
# assuming that the final glue weight is not all of the weight of the hides
hideGlueYield = Decimal(0.75)
hideGlueWeightOfHides = hideGlueDesiredWeight / hideGlueYield
# we use weight here since, unlike normal, we area only concerned with the hide weight here
hideGlueWeightRatio = hideGlueWeightOfHides / getWeight("rawhide")
# assuming that the density of paint is the same as the density of glue
squareFeetGlueCanCover = hideGlueDesiredWeight / getWeight("paint, ultramarine blue") * squareFeetPaintCanCover
recipeStorage["hide glue"] = Recipe("tanner",(hideGlueDesiredWeight, "lb"),
                                    [],
                                    [("rawhide",hideGlueWeightRatio)],
                                    description="customer supplies container; covers " + str(squareFeetGlueCanCover) + " sq ft; heat 1 pt glue in 2 pts water to use")

recipeStorage["gelatin"] = Recipe("tanner",(1,"lb"),
                                  [],
                                  [("hide glue",1)],
                                  description="as hide glue, but heat 1 pt in 3 pts water to use")


bowHeight = Decimal(5)
bowstringLength = bowHeight * Decimal(1.10) # extra is for tying knots at each end of the bow
bowstringWidth = Decimal(0.125)/Decimal(12) # eighth of an inch
bowstringSqFt = bowstringLength * bowstringWidth
bowstringUnitRatio = bowstringSqFt / getUnitSize("rawhide")
bowstringWeight = bowstringUnitRatio * getWeight("rawhide")
strandsPerBowstring = Decimal(3)
recipeStorage["bowstring strand"] = Recipe("leatherworker",(bowstringWeight/strandsPerBowstring,"lb"),
                                           [],
                                           [("rawhide",bowstringUnitRatio/strandsPerBowstring)])
semiGoods.append("bowstring strand")

recipeStorage["bowstring"] = Recipe("leatherworker",(bowstringWeight,"lb"),
                                    [],
                                    [("bowstring strand",strandsPerBowstring)])

# the bow is a flatbow, i.e. has flat limbs, but is not a selfbow, i.e. is not made entirely of one length of wood
# assuming uniform width and depth
bowLimbWidth = Decimal(1.5)/Decimal(12)
bowLimbTotalDepth = Decimal(1.2)/Decimal(12)
# length of the metal section joining the two limbs of the bow, which we'll need when calculating limb component sizes
bowRiserLength = Decimal(2)/Decimal(12)

# bow limb is divided into two layers: wood and horn
bowLimbHeight = ((bowHeight-bowRiserLength)/2)
bowLimbWoodSectionDepth = bowLimbTotalDepth * Decimal(0.75)
bowLimbWoodSectionCuFt = bowLimbWidth * bowLimbWoodSectionDepth * bowLimbHeight
bowLimbWoodWeight = bowLimbWoodSectionCuFt * densityTimber
recipeStorage["bow limb wood section"] = Recipe("bowyer",(bowLimbWoodWeight,"lb"),
                                                [("timber",bowLimbWoodSectionCuFt)],
                                                [])
semiGoods.append("bow limb wood section")

bowLimbHornSectionDepth = bowLimbTotalDepth - bowLimbWoodSectionDepth
bowLimbHornSectionCuFt = bowLimbWidth * bowLimbHornSectionDepth * bowLimbHeight
bowLimbHornWeight = bowLimbHornSectionCuFt * densityHorn
bowLimbHornRatio = bowLimbHornWeight / getWeight("horn, cow")
recipeStorage["bow limb horn section"] = Recipe("carver",(bowLimbHornWeight,"lb"),
                                                [],
                                                [("horn, cow",bowLimbHornRatio)])
semiGoods.append("bow limb horn section")

bowLimbCrossSectionSqFt = bowLimbHeight * bowLimbWidth
bowLimbRawhideUnitRatio = bowLimbCrossSectionSqFt / getUnitSize("rawhide")
bowLimbRawhideWeight = bowLimbRawhideUnitRatio * getWeight("rawhide")
bowLimbWeight = bowLimbWoodWeight + bowLimbHornWeight + bowLimbRawhideWeight
bowLimbGlueUnitRatio = bowLimbCrossSectionSqFt / squareFeetGlueCanCover
bowLimbGlueWeight = bowLimbGlueUnitRatio * getWeight("hide glue")
recipeStorage["bow limb"] = Recipe("bowyer",(bowLimbWeight,"lb"),
                                   [],
                                   [("bow limb wood section",1),
                                    ("bow limb horn section",1),
                                    ("rawhide",bowLimbRawhideUnitRatio),
                                    ("hide glue",bowLimbGlueWeight)])

bowRiserRadius = Decimal(0.125)/Decimal(12)
bowRiserCuFt = cylinderCuFt(bowRiserLength,bowRiserRadius)
bowRiserWeight = bowRiserCuFt * densityWroughtIron
recipeStorage["bow riser"] = Recipe("blacksmith",(bowRiserWeight,"lb"),
                                    [],
                                    [("wrought iron",bowRiserWeight)],
                                    description="metal rod which joins the limbs of a bow")
semiGoods.append("bow riser")

bowTotalWeight = bowstringWeight + bowRiserWeight + 2 * bowLimbWeight
recipeStorage["bow"] = Recipe("bowyer",(bowTotalWeight,"lb"),
                              [],
                              [("bowstring",1),
                               ("bow riser",1),
                               ("bow limb", 2)],
                              description="1d6 damage; range 12/24/36; " + str(bowHeight) + " ft tall; includes 1 bowstring")

# we can consider a rope ladder as constructed of a certain number of units, PLUS the top rung, plus some kind of solid metal hook with a long "arm" and a generous curve on the business end, to grab onto surfaces/bite into dirt
# plus, of course, the rope to secure the spike to the top rung.
# each unit is composed of a rung plus the rope needed to bridge the gap to the next rung and then secure the two rungs together
# each rung is a solid wooden rod, perhaps sanded against the grain to provide a rough grippy surface or something like that (not sure how that would have been done)
# we can use these rungs for both rope and wooden ladders
ladderRungDiameter = Decimal(1.5)/Decimal(12)
ladderRungLength = Decimal(1)
ladderRungCuFt = cylinderCuFt(ladderRungLength,ladderRungDiameter/Decimal(2))
ladderRungWeight = ladderRungCuFt * densityTimber
recipeStorage["ladder rung"] = Recipe("carver",(ladderRungWeight,"lb"),
                                      [("timber",ladderRungCuFt)],
                                      [])
semiGoods.append("ladder rung")

# let's says it's 1.5 feet per side to bridge the gap plus another foot per side to secure with knots
ropeLadderUnitBridgingRopeLength = Decimal(1.5)
ropeLadderUnitSecuringRopeLength = Decimal(1)
ropeLadderUnitRopeFt = (ropeLadderUnitBridgingRopeLength + ropeLadderUnitSecuringRopeLength)
ropeLadderUnitRopeRatio = ropeLadderUnitRopeFt / getUnitSize("rope")
ropeLadderUnitRopeWeight = ropeLadderUnitRopeRatio * getWeight("rope")

ropeLadderUnitWeight = ropeLadderUnitRopeWeight + ladderRungWeight
ropeLadderUnitHeight = ropeLadderUnitBridgingRopeLength + ladderRungDiameter

def ropeLadderBodyLength(num):
    """Return the length of a rope ladder body having num units.
    The extra rung diameter is for the bottom rung."""
    return (ropeLadderUnitHeight * num) + ladderRungDiameter

# model the hook at the top of the rope ladder as a long spike, bent into a hook shape, with an eyelet at the bottom for rope
# see /D&D/support_inspiration/images/ladder_pictures.jpg for an example
ropeLadderTophookCuFt = coneCuFt(Decimal(1),spikeRadius)
ropeLadderTophookWeight = ropeLadderTophookCuFt * densityWroughtIron
recipeStorage["rope ladder tophook"] = Recipe("blacksmith",(ropeLadderTophookWeight,"lb"),
                                              [],
                                              [("wrought iron",ropeLadderTophookWeight)],
                                              description="metal hook for suspending rope ladder")
semiGoods.append("rope ladder tophook")

# rope to go through the eyelet of each tophook
ropeLadderHookRopeLength = Decimal(3)
ropeLadderHookRopeUnitRatio = ropeLadderHookRopeLength/getUnitSize("rope")
ropeLadderHookRopeWeight = ropeLadderHookRopeUnitRatio * getWeight("rope")

ropeLadderUnitCount = 15
ropeLadderTotalRopeUnitRatio = ropeLadderUnitRopeRatio * ropeLadderUnitCount + ropeLadderHookRopeUnitRatio
ropeLadderTotalWeight = (ropeLadderUnitRopeWeight * ropeLadderUnitCount) + (ladderRungWeight * (ropeLadderUnitCount + 1)) + (ropeLadderTophookWeight * 2) + (ropeLadderHookRopeWeight * 2)
recipeStorage["ladder, rope"] = Recipe("ropewalker",(ropeLadderTotalWeight,"lb"),
                                      [],
                                      [("rope", ropeLadderTotalRopeUnitRatio),
                                       ("ladder rung", ropeLadderUnitCount+1),
                                       ("rope ladder tophook",2)],
                                      description="rollable; 2x hook -> no need to spike; as hard to climb as rope due to swinging; body height: " + str(ropeLadderBodyLength(ropeLadderUnitCount)) + " ft")


# rigid ladders of the shortest variety are two long thick planks
# each plank has divots drilled for installing rungs
woodenLadderDistanceBetweenRungs = ropeLadderUnitBridgingRopeLength
woodenLadderNumRungs = 10
# the height of each plank is two feet higher than the distance the rungs traverse
woodenLadderHeight = (woodenLadderNumRungs * woodenLadderDistanceBetweenRungs) + 2
woodenLadderPlankCuFt = woodenLadderHeight * Decimal(2)/Decimal(12) * Decimal(2)/Decimal(12)
woodenLadderPlankWeight = woodenLadderPlankCuFt * densityTimber
recipeStorage["wooden ladder plank"] = Recipe("carpenter",(woodenLadderPlankWeight,"lb"),
                                              [("timber",woodenLadderPlankCuFt)],
                                              [])
semiGoods.append("wooden ladder plank")

woodenLadderTotalWeight = (woodenLadderPlankWeight * 2) + (ladderRungWeight * woodenLadderNumRungs)
recipeStorage["ladder, wooden"] = Recipe("carpenter",(woodenLadderTotalWeight,"lb"),
                                        [],
                                        [("wooden ladder plank",2),
                                         ("ladder rung", woodenLadderNumRungs)],
                                        description="height " + str(woodenLadderHeight) + " ft")

fishingLineFeet = Decimal(45)
fishingLineUnitRatio = fishingLineFeet / getUnitSize("yarn, wool")
fishingLineWeight = fishingLineUnitRatio * getWeight("yarn, wool")
recipeStorage["fishing line"] = Recipe("weaver",(fishingLineWeight,"lb"),
                                       [],
                                       [("yarn, wool",fishingLineWeight)],
                                       description="sold in " + str(fishingLineFeet) + "-ft roll")

fishHookCuFt = cylinderCuFt(Decimal(3)/Decimal(12),Decimal(0.125)/Decimal(12))
fishHookWeight = fishHookCuFt * densityWroughtIron
recipeStorage["fish hook"] = Recipe("blacksmith",(fishHookWeight,"lb"),
                                    [],
                                    [("wrought iron",fishHookWeight)])

# a cylinder of metal bent into a little circle
# only one at the tip; no guide loops, that was a later invention
fishingRodTipLoopLength = Decimal(1)/Decimal(12)
fishingRodTipLoopDiameter = Decimal(0.25)/Decimal(12)
fishingRodTipLoopCuFt = cylinderCuFt(fishingRodTipLoopLength, fishingRodTipLoopDiameter/Decimal(2))
fishingRodTipLoopWeight = fishingRodTipLoopCuFt * densityWroughtIron

# it seems crazy long, but this is how long they used to be!
fishingRodLength = Decimal(18)
fishingRodDiameter = Decimal(0.75)/Decimal(12)
fishingRodCuFt = cylinderCuFt(fishingRodLength,fishingRodDiameter/Decimal(2))
fishingRodWeight = fishingRodCuFt * densityTimber
fishingRodTotalWeight = fishingRodWeight + fishingRodTipLoopWeight

recipeStorage["fishing rod"] = Recipe("carver",(fishingRodTotalWeight,"lb"),
                                      [("timber",fishingRodCuFt)],
                                      [("wrought iron",fishingRodTipLoopWeight)],
                                      description="for angling; " + str(fishingRodLength) + " feet long; breaks down into 3 6-fot sections (dis/assembly time 1 minute)")

# this is the value by which innkeeper expenses will be divided,
# to find the proportion of the total each patron is paying for their stay
innMainRoomMaxPatrons = Decimal(20)
# part of the price of staying in communal main room is coal to heat it at night
innDailyCoal = Decimal(10) # lbs, a TOTAL guess, I have still not figured out coal heating values at all
# the other part: the cost of paying inn employees
# for now I can find a cost by saying the employees get paid according to some value of bread and beer
innEmployeeDailyBread = Decimal(3) # pounds
innEmployeeDailyBeer = Decimal(4) # pints
# the innkeeper himself, plus cook, cleaning boy or maid, barkeep, and one more for good measure, perhaps representing fees, taxes, municipal services
# not yet sure how those things worked in 17th century
innEmployeeCount = Decimal(5)
innTotalEmployeeDailyBread = innEmployeeDailyBread * innEmployeeCount
innTotalEmployeeDailyBeer = innEmployeeDailyBeer * innEmployeeCount
recipeStorage["room at inn, communal"] = Recipe("innkeeper",(0,"lb"),
                                                [],
                                                [("bread",innTotalEmployeeDailyBread/innMainRoomMaxPatrons),
                                                 ("beer, barrel",innTotalEmployeeDailyBeer/innMainRoomMaxPatrons * Decimal(1)/pintsPerBarrel)],
                                                unit=(1,"night"),
                                                description="IGNORE NON-ZERO AVAILABILITY; sleep in huddle; fire")



# egg yolk density: 64.12 lb/cu ft
eggOilFlOz = Decimal(8)
eggsPerFlOzOil = Decimal(10)
totalEggs = eggOilFlOz * eggsPerFlOzOil
recipeStorage["egg oil"] = Recipe("alchemist",((waterWeightOnePint / Decimal(2)) + getWeight("flask, glass"),"lb"),
                                  [],
                                  [("egg, chicken",totalEggs),("flask, glass",1)],
                                  unit = (Decimal(0.5),"pint"),
                                  description="in glass flask; cosmetic or ointment for skin and hair")

# raw:dried ratio taken from Timothy Barrett "European Papermaking 1300-1800" website http://paper.lib.uiowa.edu/european.php
recipeStorage["flax, dried"] = Recipe("farmer",(1,"lb"),
                                      [("flax",4)],
                                      [])
semiGoods.append("flax, dried")

# I assign this to millers because it would often be done where streams which powered mills were also located
# retted:dried ratio is equivalent to the 4.4:25 ratio given by Barrett,
# simplified into 1:5.682
recipeStorage["flax, retted"] = Recipe("miller",(1,"lb"),
                                       [],
                                       [("flax, dried",Decimal(5.682))],
                                       description="after fermentation to break down plant structure")
semiGoods.append("flax, retted")

recipeStorage["flax, beaten"] = Recipe("miller",(1,"lb"),
                                       [],
                                       [("flax, retted",Decimal(1))],
                                       description="after going through stamping process")
semiGoods.append("flax, beaten")

# using the combed:papermaking ratio from Barrett's table, but for the beaten flax, since that step comes between retting and sheetmaking
ratioFlaxPaper = Decimal(4.18)/Decimal(1.69)
foolscapReamLeaves = Decimal(255)
foolscapReamWeight = Decimal(1)
foolscapHeight = Decimal(13) # inches
foolscapLength = Decimal(16) # inches
foolscapLeafPoundsPerSqFt = ratioFlaxPaper / ((foolscapHeight / Decimal(12)) * (foolscapLength / Decimal(12))) / foolscapReamLeaves
# works out to 3.5 grams per leaf, that's not bad
recipeStorage["paper, foolscap, unfinished"] = Recipe("miller",(foolscapReamWeight,"lb"),
                                            [],
                                            [("flax, beaten",ratioFlaxPaper * foolscapReamWeight)],
                                            unit=(foolscapReamLeaves,"leaf"),
                                            description="one ream; neither cut nor coated with size")
semiGoods.append("paper, foolscap, unfinished")

# Barrett estimates 5,114 grams of dry gelatin for 15 reams of paper (crown paper, not foolscap, but oh well)
# that's 11.27 pounds
# to get a per-ream figure, just divide
gelatinPerReam = Decimal(11.27)/Decimal(15)
recipeStorage["paper, foolscap, sized"] = Recipe("miller",(1,"lb"),
                                          [],
                                          [("paper, foolscap, unfinished",1),
                                           ("gelatin",gelatinPerReam)],
                                          unit=recipeStorage["paper, foolscap, unfinished"].unit,
                                          description="coated in gelatin size")
semiGoods.append("paper, foolscap, sized")

# finally, the paper is finished by being scraped with a smooth stone
recipeStorage["paper, foolscap, looseleaf"] = Recipe("miller",(1,"lb"),
                                          [],
                                          [("paper, foolscap, sized",1)],
                                          unit=recipeStorage["paper, foolscap, unfinished"].unit,
                                          description=str(foolscapHeight) + "x" + str(foolscapLength) + "in.")

# foolscap leaf: 16 by 13
# foolscap folio: foolscap folded in two, to make two sheets of 8 by 13
# each sheet has a front and a back, thus forming 2 pages as we think of them today
# if a quire is 25 leaves, and a leaf makes two sheets, and a sheet makes 2 pages, then one quire makes 100 pages
pagesPerFolioSheet = Decimal(2)
folioSheetsPerLeaf = Decimal(2)
leavesPerQuire = Decimal(25)
pagesPerQuire = leavesPerQuire * folioSheetsPerLeaf * pagesPerFolioSheet

# stitched up and down, twice
quireThreadFt = Decimal(4) * (foolscapHeight / Decimal(12))
quireThreadUnitRatio = quireThreadFt / getUnitSize("yarn, cotton")
quireThreadWeight = quireThreadUnitRatio * getWeight("yarn, cotton")
quirePaperUnitRatio = leavesPerQuire / getUnitSize("paper, foolscap, looseleaf")
quirePaperWeight = quirePaperUnitRatio * getWeight("paper, foolscap, looseleaf")
quireWeight = quireThreadWeight + quirePaperWeight
recipeStorage["paper, foolscap, quire"] = Recipe("bookbinder",(quireWeight,"lb"),
                                          [],
                                          [("paper, foolscap, looseleaf",quirePaperUnitRatio),
                                           ("yarn, cotton",quireThreadWeight)],
                                          unit=(Decimal(100),"page"),
                                          description="bound folio sheets (8x13 in.)")

cigPaperLength = Decimal(6)/Decimal(12)
cigPaperWidth = Decimal(2)/Decimal(12)
cigPaperSqFt = cigPaperLength * cigPaperWidth
cigPaperUnitRatio = cigPaperSqFt / (getUnitSize("paper, foolscap, unfinished") * foolscapHeight * foolscapLength)
cigPaperWeight = cigPaperUnitRatio * getWeight("paper, foolscap, unfinished")
cigTobaccoGrams = Decimal(2.5)
cigTobaccoOz = cigTobaccoGrams / gramsPerOz
cigTobaccoLb = cigTobaccoOz / Decimal(16)
recipeStorage["cigar"] = Recipe("tobacconist",(cigTobaccoLb + cigPaperWeight,"lb"),
                                    [],
                                    [("paper, foolscap, unfinished",cigPaperUnitRatio),
                                     ("tobacco, cured",cigTobaccoLb)])

# Source: A Booke of Secrets [...] written first in Italian, and now newly translated into English, by W.P., London, Edward White, 1596
# Take halfe a pint of water, a pint wanting a quarter of wine, and as much vineger, which being mixed together make a quart and a quarter of a pint more, then take six ounces of gauls beaten into small pouder and sifted through a sive, put this pouder into a pot by it selfe, and poure halfe the water, wine and vineger into it, take likewise foure ounces of vietriall, and beat it into pouder, and put it also in a pot by it selfe, whereinto put a quarter of the wine, water, and vineger that remaineth, and to the other quarter, put foure ounces of gum Arabike beaten to pouder, that done, cover the three pots close, and let them stand three or foure daies together, stirring them every day three or foure times, on the first day set the pot with gaules on the fire, and when it begins to seeth, stir it about till it be throughly warme, then straine it through a cloath into another pot, and mixe it with the other two pots, stirring them well together, and being covered, then let it stand three daies, til thou meanest to use it, on the fourth day, when it is setled, poure it out, and it wil be good inke.
# If there remaine any dregs behind, poure some raine water that hath stand long in a tub or vessell into it, for the older the water is, the better it is, and keepe that untill you make more inke, so it is better then clean water."

# from this we can extrapolate:
# 0.5 pint water + 0.75 pint ale + 0.75 pint vinegar + 6 oz tannin + 4 oz gelatin (binder) + 4 oz vitriol
# vitriol here refers green vitriol (iron sulfate), confusingly also called "copperas"
# assuming the liquids retain their volume, this makes 2 pints of fluid
# thus, to make one pint (16 floz) we want 4 floz water, 6 floz ale, 6 floz vinegar
# thus, to make one pint (16 floz) we want 3 oz tannin, 2 oz gelatin, 2 oz vitriol


recipeStorage["green vitriol"] = Recipe("alchemist",(1,"lb"),
                                        [("iron ore",4)],
                                        [],
                                        difficulty=4, # so-far standard difficulty for basic alchemy
                                        description="AKA copperas")
semiGoods.append("green vitriol")

recipeStorage["timber, ground"] = Recipe("miller",(1,"lb"),
                                         [("timber",1/densityTimber)], # 1 lb / density = desired volume
                                         [],
                                         description="for extraction of tannin")
semiGoods.append("timber, ground")

# this is the figure for most high-tannin woods
tanninPercentInWood = Decimal(0.1)
tanninOutputWeight = Decimal(1)
tanninWoodInputWeight = tanninOutputWeight / tanninPercentInWood
tanninWoodCuFt = tanninWoodInputWeight / densityTimber
recipeStorage["tannin"] = Recipe("dyer",(tanninOutputWeight,"lb"),
                                 [],
                                 [("timber, ground",tanninWoodCuFt)])


inkBlackPoundsTanninPerPint = Decimal(3)/Decimal(16)
inkBlackPoundsGelatinPerPint = Decimal(2)/Decimal(16)
inkBlackPoundsVitriolPerPint = inkBlackPoundsGelatinPerPint
inkBlackSolidWeight = inkBlackPoundsTanninPerPint + inkBlackPoundsGelatinPerPint + inkBlackPoundsVitriolPerPint
inkBlackWaterPerPint = Decimal(4)/Decimal(16)
inkBlackAlePerPint = Decimal(6)/Decimal(16)
inkBlackVinegarPerPint = Decimal(6)/Decimal(16)
inkBlackLiquidWeight = (inkBlackWaterPerPint * waterWeightOnePint) + (inkBlackAlePerPint * waterWeightOnePint) + (inkBlackVinegarPerPint * weightPintVinegar)
inkBlackTotalWeight = inkBlackSolidWeight + inkBlackLiquidWeight
inkSaleUnit = Decimal(0.5)
recipeStorage["ink, black"] = Recipe("dyer",((inkBlackTotalWeight * inkSaleUnit) + getWeight("flask, glass"),"lb"),
                                            [],
                                            [("ale, barrel",(inkBlackAlePerPint * inkSaleUnit) / pintsPerBarrel),
                                             ("vinegar",inkSaleUnit),
                                             ("tannin",inkBlackPoundsTanninPerPint * inkSaleUnit),
                                             ("gelatin",inkBlackPoundsGelatinPerPint * inkSaleUnit),
                                             ("green vitriol",inkBlackPoundsVitriolPerPint * inkSaleUnit),
                                             ("flask, glass",1)],
                                            unit=(Decimal(0.5),"pint"),
                                            description="iron gall ink, in glass flask")

inkColorWaterPerPint = Decimal(0.8)
inkColorLiquidWeight = inkColorWaterPerPint * waterWeightOnePint
# gelatin is the binder
# the amounts for gelatin and pigment are made up; since after considerable searching I couldn't find anything
inkColorPoundsGelatinPerPint = Decimal(1)/Decimal(16)
inkColorPoundsPigmentPerPint = Decimal(1)/Decimal(16)
inkColorSolidWeight = inkColorPoundsGelatinPerPint + inkColorPoundsPigmentPerPint
inkColorTotalWeight = inkColorLiquidWeight + inkColorSolidWeight
recipeStorage["ink, ultramarine blue"] = Recipe("dyer",(inkColorTotalWeight + getWeight("flask, glass"),"lb"),
                                                [],
                                                [("gelatin",inkColorPoundsGelatinPerPint * inkSaleUnit),
                                                 ("pigment, ultramarine",inkColorPoundsPigmentPerPint * inkSaleUnit)],
                                                unit=(Decimal(0.5),"pint"),
                                                description="in glass flask")

recipeStorage["ink, red/yellow"] = Recipe("dyer",(inkColorTotalWeight + getWeight("flask, glass"),"lb"),
                                                [],
                                                [("gelatin",inkColorPoundsGelatinPerPint * inkSaleUnit),
                                                 ("pigment, red/yellow",inkColorPoundsPigmentPerPint * inkSaleUnit)],
                                                unit=(Decimal(0.5),"pint"),
                                                description="in glass flask")


tattooNeedleLength = Decimal(1)
tattooNeedleMaxDiameter = Decimal(0.25)/Decimal(12)
tattooNeedleCuFt = coneCuFt(tattooNeedleLength,tattooNeedleMaxDiameter/Decimal(2))
tattooNeedleWeight = tattooNeedleCuFt * densitySteel
recipeStorage["tattoo needle"] = Recipe("blacksmith",(tattooNeedleWeight,"lb"),
                                        [],
                                        [("steel",tattooNeedleWeight)],
                                        difficulty=4)

cuFtPerPintLiquid = cuFtPerGallonLiquid / Decimal(8)
# the "thickness" of the tattoo under the skin, so we can calculate volume for a given square area of tattooed skin
tattooThickness = Decimal(0.01)/Decimal(12) # i.e. one hundredth of an inch
# for a square inch, width and length equal 1, thus only relevant dimension is thickness, thus volume = thickness
tattooPintsInkSquareInch = tattooThickness / cuFtPerPintLiquid

for color in ["black","ultramarine blue","red/yellow"]:
    ink = "ink, " + color
    geom = "tattoo, geometric, " + color
    recipeStorage[geom] = Recipe("sailor",(0,"lb"),
                                 [],
                                 [("tattoo needle",1),
                                  (ink,tattooPintsInkSquareInch)],
                                 unit=(Decimal(1),"sq in"),
                                 description="includes lines, shapes, and tribal patterns")
    letter = "tattoo, lettering, " + color
    recipeStorage[letter] = Recipe("sailor",(0,"lb"),
                                   [],
                                   [("tattoo needle",1),
                                  (ink,tattooPintsInkSquareInch)],
                                   unit=(Decimal(1),"sq in"),
                                   difficulty=3,
                                   description="includes all types of lettering")
    figure = "tattoo, figure, " + color
    recipeStorage[figure] = Recipe("sailor",(0,"lb"),
                                   [],
                                   [("tattoo needle",1),
                                    (ink,tattooPintsInkSquareInch)],
                                   unit=(Decimal(1),"sq in"),
                                   difficulty=6,
                                   description="includes people and creatures")

for service in allServiceNames:
    recipeStorage["hireling, " + service] = Recipe(service, (0,"lb"),
                                                   [("labor",Decimal(1)/Decimal(500))],
                                                   [],
                                                   unit=(Decimal(1),"head"),
                                                   description="weekly wage")
basicWeapons = ["dagger","shortsword","spear","sling"]

paymentsPerYear = Decimal(12)
XPbeforeCombatTraining = Decimal(500)
XPforLevelOne = Decimal(1500)
mercenaryImprovementOverLaborer = XPbeforeCombatTraining / XPforLevelOne
mercenaryPersonValue = Decimal(1) + Decimal(1) * mercenaryImprovementOverLaborer
recipeStorage["hireling, mercenary"] = Recipe("laborer",(0,"lb"),
                                              [],
                                              [("hireling, laborer",mercenaryPersonValue)] + [(weapon,Decimal(1)/paymentsPerYear) for weapon in basicWeapons],
                                              unit=(Decimal(1),"head"),
                                              description="weekly wage; trained with " + ", ".join(basicWeapons))

XPafterCombatTraining = XPforLevelOne - XPbeforeCombatTraining
levelOneImprovementOverMercenary = XPafterCombatTraining / XPforLevelOne
levelOnePersonValue = Decimal(1) + Decimal(1) * levelOneImprovementOverMercenary
recipeStorage["hireling, fighter, level 1"] = Recipe("laborer",(0,"lb"),
                                                     [],
                                                     [("hireling, mercenary",levelOnePersonValue)],
                                                     unit=(Decimal(1),"head"),
                                                     description="weekly wage")
# caulk = pitch plus cotton fibers, i.e. the recipe "clean cotton"
caulkPitchPercentage = Decimal(0.75) # by weight
caulkCottonPercentage = Decimal(1) - caulkPitchPercentage
caulkCottonWeight = caulkCottonPercentage * pitchInFlaskWeightPitch
caulkWeight = pitchInFlaskWeightPitch + caulkCottonWeight
caulkSqFtCoverage = (caulkWeight / hideGlueDesiredWeight) * squareFeetGlueCanCover
recipeStorage["caulk"] = Recipe("shipwright",(caulkWeight + getWeight("flask, earthenware"),"lb"),
                                [],
                                [("pitch",1), ("clean cotton",caulkCottonWeight), ("flask, earthenware",1)],
                                description="in earthenware flask; covers " + str(caulkSqFtCoverage) + " sqft")

rivetWeight = Decimal(0.025)
recipeStorage["rivet"] = Recipe("coppersmith",(rivetWeight,"lb"),
                                [],
                                [("copper",rivetWeight)])

faeringKeelLength = Decimal(14)
faeringKeelWidth= Decimal(2)/Decimal(12)
faeringKeelHeight= Decimal(3)/Decimal(12)
faeringKeelCuFt = faeringKeelLength * faeringKeelWidth * faeringKeelHeight
faeringKeelWeight = faeringKeelCuFt * densityTimber
recipeStorage["keel, faering"] = Recipe("shipwright",(faeringKeelWeight,"lb"),
                                        [("timber",faeringKeelCuFt)],
                                        [])

faeringStemLength = Decimal(2)
faeringStemWidth = faeringKeelWidth
faeringStemHeight = Decimal(2)/Decimal(12)
faeringStemCuFtMain = faeringStemLength * faeringStemWidth * faeringStemHeight
# model stem as a rectangular piece plus a triangular piece under it
faeringStemCuFtSupp = triangularPrismCuFt(faeringStemWidth,
                                          faeringKeelHeight - faeringStemHeight,
                                          faeringStemLength)
faeringStemTotalCuFt = faeringStemCuFtMain + faeringStemCuFtSupp
faeringStemWeight = faeringStemTotalCuFt * densityTimber
recipeStorage["stem, faering"] = Recipe("shipwright",(faeringStemWeight,"lb"),
                                        [("timber",faeringStemTotalCuFt)],
                                        [])
semiGoods.append("stem, faering")

recipeStorage["stem, faering, shaped"] = Recipe("shipwright",(getWeight("stem, faering"),"lb"),
                                                 [],
                                                 [("stem, faering",1)])
semiGoods.append("stem, faering, shaped")


faeringGarboardLength = faeringKeelLength + Decimal(0.75)
faeringGarboardWidth = Decimal(14)/Decimal(12)
faeringGarboardHeight = Decimal(0.5)/Decimal(12)
faeringGarboardCuFt = faeringGarboardLength * faeringGarboardWidth * faeringGarboardHeight
faeringGarboardWeight = faeringGarboardCuFt * densityTimber
recipeStorage["garboard, faering"] = Recipe("shipwright",(faeringGarboardWeight,"lb"),
                                            [("timber",faeringGarboardCuFt)],
                                            [])
semiGoods.append("garboard, faering")

recipeStorage["garboard, faering, shaped"] = Recipe("shipwright",(getWeight("garboard, faering"),"lb"),
                                                     [],
                                                     [("garboard, faering",1)])
semiGoods.append("garboard, faering, shaped")

faeringBilgestrakeLength = faeringKeelLength * Decimal(1)
faeringBilgestrakeWidth = Decimal(16)/Decimal(12)
faeringBilgestrakeHeight = Decimal(0.25)/Decimal(12)
faeringBilgestrakeCuFt = faeringBilgestrakeLength * faeringBilgestrakeWidth * faeringBilgestrakeHeight
faeringBilgestrakeWeight = faeringBilgestrakeCuFt * densityTimber
recipeStorage["bilgestrake, faering"] = Recipe("shipwright",(faeringBilgestrakeWeight,"lb"),
                                             [("timber",faeringBilgestrakeCuFt)],
                                             [])
semiGoods.append("bilgestrake, faering")

recipeStorage["bilgestrake, faering, shaped"] = Recipe("shipwright",(getWeight("bilgestrake, faering"),"lb"),
                                                     [],
                                                     [("bilgestrake, faering",1)])
semiGoods.append("bilgestrake, faering, shaped")

faeringSheerstrakeLength = faeringKeelLength * Decimal(1.25)
faeringSheerstrakeWidth = Decimal(8)/Decimal(12)
faeringSheerstrakeHeight = Decimal(0.125)/Decimal(12)
faeringSheerstrakeCuFt =faeringSheerstrakeLength * faeringSheerstrakeWidth * faeringSheerstrakeHeight
faeringSheerstrakeWeight = faeringSheerstrakeCuFt * densityTimber
recipeStorage["sheerstrake, faering"] = Recipe("shipwright",(faeringSheerstrakeWeight,"lb"),
                                               [("timber",faeringSheerstrakeCuFt)],
                                               [])
semiGoods.append("sheerstrake, faering")

recipeStorage["sheerstrake, faering, shaped"] = Recipe("shipwright",(getWeight("sheerstrake, faering"),"lb"),
                                                       [],
                                                       [("sheerstrake, faering",1)])
semiGoods.append("sheerstrake, faering, shaped")

faeringGunwaleLength = faeringSheerstrakeLength
faeringGunwaleWidth = Decimal(3)/Decimal(12)
faeringGunwaleHeight = faeringSheerstrakeHeight
faeringGunwaleCuFt = faeringGunwaleLength * faeringGunwaleWidth * faeringGunwaleHeight
faeringGunwaleWeight = faeringGunwaleCuFt * densityTimber
recipeStorage["gunwale, faering"] = Recipe("shipwright",(faeringGunwaleWeight,"lb"),
                                           [("timber",faeringGunwaleCuFt)],
                                           [])
semiGoods.append("gunwale, faering")

recipeStorage["gunwale, faering, shaped"] = Recipe("shipwright",(getWeight("gunwale, faering"),"lb"),
                                                   [],
                                                   [("gunwale, faering",1)])
semiGoods.append("gunwale, faering, shaped")

faeringMidshipFrameTimberLength = Decimal(4)
faeringFrameTimberWidth = Decimal(0.75)/Decimal(12)
faeringFrameTimberHeight = Decimal(1)/Decimal(12)
faeringMidshipFrameTimberCuFt = faeringMidshipFrameTimberLength * faeringFrameTimberHeight * faeringFrameTimberWidth
faeringMidshipFrameTimberWeight = faeringMidshipFrameTimberCuFt * densityTimber
recipeStorage["midship frame timber, faering"] = Recipe("shipwright",(faeringMidshipFrameTimberWeight,"lb"),
                                                        [("timber",faeringMidshipFrameTimberCuFt)],
                                                        [])
semiGoods.append("midship frame timber, faering")

faeringAftFrameTimberLength = Decimal(3)
faeringAftFrameTimberCuFt = faeringAftFrameTimberLength * faeringFrameTimberHeight * faeringFrameTimberWidth
faeringAftFrameTimberWeight = faeringAftFrameTimberCuFt * densityTimber
recipeStorage["aft frame timber, faering"] = Recipe("shipwright",(faeringAftFrameTimberWeight,"lb"),
                                                        [("timber",faeringAftFrameTimberCuFt)],
                                                        [])
semiGoods.append("aft frame timber, faering")

faeringForeFrameTimberLength = Decimal(3)
faeringForeFrameTimberCuFt = faeringForeFrameTimberLength * faeringFrameTimberHeight * faeringFrameTimberWidth
faeringForeFrameTimberWeight = faeringForeFrameTimberCuFt * densityTimber
recipeStorage["fore frame timber, faering"] = Recipe("shipwright",(faeringForeFrameTimberWeight,"lb"),
                                                        [("timber",faeringForeFrameTimberCuFt)],
                                                        [])
semiGoods.append("fore frame timber, faering")

faeringRongeFrameTimberLength = Decimal(2.5)
faeringRongeFrameTimberCuFt = faeringRongeFrameTimberLength * faeringFrameTimberHeight * faeringFrameTimberWidth
faeringRongeFrameTimberWeight = faeringRongeFrameTimberCuFt * densityTimber
recipeStorage["ronge frame timber, faering"] = Recipe("shipwright",(faeringRongeFrameTimberWeight,"lb"),
                                                        [("timber",faeringRongeFrameTimberCuFt)],
                                                        [])
semiGoods.append("ronge frame timber, faering")

faeringFlooringHeight = Decimal(0.125)/Decimal(12)
faeringMidshipFlooringLength = Decimal(3)
faeringMidshipFlooringCuFt = faeringFlooringHeight * faeringMidshipFlooringLength * faeringMidshipFrameTimberLength
faeringMidshipFlooringWeight = faeringMidshipFlooringCuFt * densityTimber
recipeStorage["midship flooring, faering"] = Recipe("shipwright",(faeringMidshipFlooringWeight,"lb"),
                                                    [("timber",faeringMidshipFlooringCuFt)],
                                                    [],
                                                    description="two required for construction")
semiGoods.append("midship flooring, faering")

faeringForeFlooringLength = Decimal(3)
faeringForeFlooringCuFt = triangularPrismCuFt(faeringForeFrameTimberLength,faeringForeFlooringLength,faeringFlooringHeight)
faeringForeFlooringWeight = faeringForeFlooringCuFt * densityTimber
recipeStorage["fore flooring, faering"] = Recipe("shipwright",(faeringForeFlooringWeight,"lb"),
                                                    [("timber",faeringForeFlooringCuFt)],
                                                    [])
semiGoods.append("fore flooring, faering")

faeringAftFlooringLength = Decimal(3)
faeringAftFlooringCuFt = triangularPrismCuFt(faeringAftFrameTimberLength,faeringAftFlooringLength,faeringFlooringHeight)
faeringAftFlooringWeight = faeringAftFlooringCuFt * densityTimber
recipeStorage["aft flooring, faering"] = Recipe("shipwright",(faeringAftFlooringWeight,"lb"),
                                                    [("timber",faeringAftFlooringCuFt)],
                                                    [])
semiGoods.append("aft flooring, faering")


# width of overlap between each strake: an estimate
faeringLapWidth = Decimal(2)/Decimal(12)
# times 2, once for each side
faeringHullJoinLinearFeet = (Decimal(2) * (faeringRongeFrameTimberLength +
                                           faeringKeelLength +
                                           faeringGarboardLength +
                                           faeringBilgestrakeLength +
                                           faeringSheerstrakeLength +
                                           faeringGunwaleLength +
                                           faeringAftFlooringLength +
                                           faeringForeFlooringLength +
                                           (Decimal(2) * faeringMidshipFlooringLength) +
                                           # times 2, once for attachment to each stem
                                           Decimal(2) * (faeringGarboardWidth +
                                                         faeringBilgestrakeWidth +
                                                         faeringSheerstrakeWidth +
                                                         faeringGunwaleWidth)))
faeringHullJoinLinearFeet += faeringMidshipFrameTimberLength + faeringAftFrameTimberLength + faeringForeFrameTimberLength


faeringHullJoinSquareFeet = Decimal(2) * ( (faeringKeelLength * faeringKeelHeight) +
                                           (faeringGarboardLength * faeringLapWidth) +
                                           (faeringBilgestrakeLength * faeringLapWidth) +
                                           (faeringSheerstrakeLength * faeringLapWidth) )
faeringHullJoinSquareFeet += faeringFrameTimberWidth * (faeringMidshipFrameTimberLength + faeringForeFrameTimberLength + faeringAftFrameTimberLength + (Decimal(2) * faeringRongeFrameTimberLength))

# caulk and rivets are applied between each of the wooden sections
# the caulk units is here is both (a) the weight of the caulk needed and (b) the number of units to use in the recipe, since that's how many flasks of caulk would be needed
faeringHullCaulk = (faeringHullJoinSquareFeet / caulkSqFtCoverage) * caulkWeight
# rivet spacing is 1 per 3 inches (4 per foot)
faeringHullRivets = faeringHullJoinLinearFeet * Decimal(4)
faeringHullTotalWeight = getWeight("keel, faering") + (Decimal(2) * getWeight("garboard, faering")) + (Decimal(2) * getWeight("bilgestrake, faering")) + (Decimal(2) * getWeight("sheerstrake, faering")) + (Decimal(2) * getWeight("bilgestrake, faering")) + (faeringHullRivets * getWeight("rivet")) + faeringHullCaulk
faeringHullTotalWeight += getWeight("midship frame timber, faering") + getWeight("fore frame timber, faering") + getWeight("aft frame timber, faering") + (Decimal(2) * getWeight("ronge frame timber, faering"))
faeringHullTotalWeight += getWeight("aft flooring, faering") + getWeight("fore flooring, faering") + (Decimal(2) * getWeight("midship flooring, faering"))
recipeStorage["hull, faering"] = Recipe("shipwright",(faeringHullTotalWeight,"lb"),
                                        [],
                                        [("caulk",faeringHullCaulk),
                                         ("rivet",faeringHullRivets),
                                         ("keel, faering",1),
                                         ("garboard, faering, shaped",2),
                                         ("bilgestrake, faering, shaped",2),
                                         ("sheerstrake, faering, shaped",2),
                                         ("gunwale, faering, shaped",2),
                                         ("midship frame timber, faering",1),
                                         ("ronge frame timber, faering",2),
                                         ("fore frame timber, faering",1),
                                         ("aft frame timber, faering",1),
                                         ("midship flooring, faering",2),
                                         ("fore flooring, faering",1),
                                         ("aft flooring, faering",1)])


outfitMonkParts = [("chemise",1),
                   ("cowl",1),
                   ("stockings",1),
                   ("scapular",1),
                   ("clog",2)]
outfitMonkWt = sum([getWeight(x)*y for x,y in outfitMonkParts])
recipeStorage["outfit, monk"] = Recipe("tailor",(outfitMonkWt,"lb"),
                                       [],
                                       outfitMonkParts,
                                       description="contains: " + ", ".join([str(y) + "x " + x for x, y in outfitMonkParts]))

def outfit(parts):
    weight = sum([getWeight(x)*y for x,y in parts])
    desc = ", ".join([str(y) + "x " + x for x, y in parts])
    return Recipe("tailor",(weight,"lb"),
                  [],
                  parts,
                  description="contains: " + desc)

def add_outfit(person, parts):
    recipeStorage["outfit, " + person] = outfit(parts)

add_outfit("rich peasant", [("chemise, fancy", 1), ("shoe", 2), ("hose", 1)])

add_outfit("peasant", [("tunic", 1), ("chemise", 1), ("clog", 2), ("stockings", 1)])

add_outfit("priest", [("chemise", 1), ("cassock", 1), ("hose", 1), ("clog", 2)])

recipeStorage["bedroll"] = Recipe("tailor",
                                  (45/getUnitSize("wool cloth"), "lb"),
                                  [],
                                  [("wool cloth",45)],
                                  description="sleeping cloth")


# tarpWidth = Decimal(10)

# recipeStorage["tarp"] = Recipe("tailor",(10, "lb"),
#                                     [],
#                                     [("wool cloth",tarpWidth)],
#                                     description="sleeping cloth: ")
# all coal in use is assumed to be lignite
# that's a huge simplification from the real world, but that's OK:
# I can add the other types of coal in once I've programmed the recipe runner's price calculator to pick from a list of possible ingredients by price, instead of hard coding each recipe's ingredients to a single type
# then I'll be more able to vary coal, or grains, or things like that (e.g. bread could be made from any grain, changing depending on what's local. descriptions could depend too!)

#ligniteHeatingValue = Decimal(6900) # BTU per pound of coal
#sizeOfHearth = 1 * 3 * 5 # height, length, width
#def heatingCoal(oreMeltingPoint):
#"""Determine how much coal is needed to achieve the melting point of the ore.
#Desired heat is assumed to be reached over one hour, for one pound of ore.
#Thus, for increased time (such as for smelting) or for increased amounts of ore,
#simply multiply the value returned by this function by the appropriate factor."""
#return result

# cannonball/cannon info
# The bore diameter (caliber) of a smoothbore cannon was often given as mass (or weight at sea level...) of a lead sphere of appropriate size to fit the cannon.
# A 3pdr would fire an approx. 70mm ball, a 6pdr 85mm, and a 12pdr 110mm. Very roughly (based on Wikipedia data).
