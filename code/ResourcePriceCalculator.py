from decimal import *
import copy
from .WorldGenerator import towns, shortestPathMatrix
from .HexResources import worldProductionMatrix

#set up the Decimal environment
getcontext().prec = 4

# this is used to adjust prices in a blunt way
# basically it's the percentage of the world's references (to a given resource) which an "average" city is assumed to have
pseudoAverageRefPercent = Decimal(0.05)

# get names of all resources available in the economy
# get names of all services available in the economy
allResourceNames = []
allServiceNames = []
for t,d in towns.items():
    allResourceNames = allResourceNames + list(d.resources.keys())
    allServiceNames = allServiceNames + list(d.services.keys())
allResourceNames = list(set(allResourceNames))
allServiceNames = list(set(allServiceNames))
allResourceNames.sort()
allServiceNames.sort()

# for each town, for each service and resource it doesn't have an entry for,
# add one with a count of 0, so that stuff can be added to it in the import step
# without having to muddy that code with repetitive checking for null values
for t,d in towns.items():
    for r in allResourceNames:
        if r in d.resources:
            pass
        else:
            d.resources[r] = Decimal(0)
    for s in allServiceNames:
        if s in d.services:
            pass
        else:
            d.services[s] = Decimal(0)

# now we create a deep copy of the towns data.
# why? because for importing we're going to be updating resource and service values in place,
# but in order to perform the import calculations,
# we need to be able to refer to the original values.

originalTowns = copy.deepcopy(towns)
# set up the original, pre-import counts of each resource (not service)
# these are used later, when establishing the size of a reference
originalWorldResourceCounts = {}
originalWorldServiceCounts = {}
for ot,d in originalTowns.items():
    for r,val in d.resources.items():
        if r in originalWorldResourceCounts:
            originalWorldResourceCounts[r] += Decimal(val)
        else:
            originalWorldResourceCounts[r] = Decimal(val)
    for t,val in d.services.items():
        if t in originalWorldServiceCounts:
            originalWorldServiceCounts[t] += Decimal(val)
        else:
            originalWorldServiceCounts[t] = Decimal(val)

# let's replace the pseudo-average ref percent with an actual calculation of the average references to a resource per town
# it's simple: divide the total pre-import references T to a resource R by the size of the town list
averageResourceReferences = {}
for name in allResourceNames:
    averageResourceReferences[name] = originalWorldResourceCounts[name] / Decimal(len(list(originalTowns.keys())))

averageServiceReferences = {}
for name in allServiceNames:
    averageServiceReferences[name] = originalWorldServiceCounts[name] / Decimal(len(list(originalTowns.keys())))

# next, we'll divvy up the world production of each resource
# INTO the number of extant references of the resource
# e.g. if world production of iron ore is 1000 lbs, and the world total refcount is 5,
# the result will be 20 lbs per ref
# these calculations are based on the ORIGINAL reference count, not the one adjusted for imports
singleReferenceProduction = {}
for n in allResourceNames:
    production, unit = worldProductionMatrix[n]
    perRef = Decimal(production) / Decimal(originalWorldResourceCounts[n])
    singleReferenceProduction[n] = (perRef, unit)

def quantityToImport(source, destination, sourceAmount):
    """
    Calculates the fraction of the sourceAmount which gets imported to destination.
    :param source: city from which resource is being imported
    :param destination: city which is receiving the import
    :param sourceAmount: the number of abstract units of some resource (or service)
    :return: the fraction of sourceAmount which will be added to the amount at destination
    """
    distance = shortestPathMatrix[source][destination]
    quantity = Decimal(sourceAmount) / Decimal((distance + 1))
    # 1 is added to distance so that when a destination is 1 away from its source, it does not receive exactly as much
    # as exists at the source
    return quantity

# now: the import step
# we base the quantity of each resource to be imported on the ORIGINAL amount available,
# and add the appropriate fraction of that amount to each importing town
for source, sourceData in originalTowns.items():
    for dest, destData in towns.items():
        if source == dest:
            pass
        else:
            for res, count in sourceData.resources.items():
                q = quantityToImport(source, dest, count)
                destData.resources[res] += q
            for serv, count in sourceData.services.items():
                q = quantityToImport(source, dest, count)
                destData.services[serv] += q

# now: finding the value of a gold-ore reference in copper pieces.
# 1 oz gold ore equals 8 gold pieces
# (it's not actually that much metal, that's just its official value)
# 16 oz in a lb (the unit for gold references)
# then, multiply by the size of a gold reference
# finally, multiply by 100, since one gold piece (GP) is worth 100 copper pieces (CP)
goldRefPriceCP = Decimal(8) * Decimal(16) * singleReferenceProduction["gold ore"][0] * 100
# thus we arrive at the copper-piece value of one refernence to gold ore,
# which we also take as the CP value of one ref of ANY material resource.
# what causes differenation is the SIZE and UNIT of other references:
# it's the value that stays constant.

# finally, we need a price per production UNIT of each raw resource
# e.g. if the size of an iron reference is 1,000 tons, we want to find what 1 ton costs
pricesPerProductionUnit = {}
for t,d in towns.items():
    pricesPerProductionUnit[t] = {}
    for rawMat in allResourceNames:
        # ratio of local references (post-import) to original world total (calculated pre-import)
        localRefToWorldRefRatio = d.resources[rawMat] / (pseudoAverageRefPercent * originalWorldResourceCounts[rawMat])
        # adjust base CP-per-reference of any good to reflect said ratio
        adjustedBasePrice = goldRefPriceCP / localRefToWorldRefRatio
        # divide adjusted base price by size of one reference to get price per unit
        size, unit = singleReferenceProduction[rawMat]
        pricePerUnit = adjustedBasePrice / size
        pricesPerProductionUnit[t][rawMat] = (pricePerUnit, unit)

# and with that, we are ready to move into the final economy step: recipes!
# in which we use these raw material prices together with services
# to arrive at prices for actual items which the players can buy

def main():
    print("\n")
    for t,vals in pricesPerProductionUnit.items():
        print(t)
        for name in allResourceNames:
            price, unit = vals[name]
            print(name,"costs",str(price),"CP per",unit)

if __name__ == "__main__":
    main()
