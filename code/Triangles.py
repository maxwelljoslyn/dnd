from .Direction import Direction
from random import *

dirs = Direction.__members__.keys()

# these types have only a single inhabitant hex each
# one is all wild, the other is all civilized
type1 = {x:"Wild" for x in dirs}
type7 = {x:"Civilized" for x in dirs}

# construct the possible triangle arrangements for type 2 hexes
type2s = []
for dir in dirs:
    res = type1.copy()
    res[dir] = "Civilized"
    type2s.append(res)


# construct the possible triangle arrangements for type 6 hexes
type6s = []
for dir in dirs:
    res = type7.copy()
    res[dir] = "Wild"
    type6s.append(res)

# construct arrangements for type 3 hexes
type3s = []
for dir1 in dirs:
    for dir2 in dirs:
        if dir1 == dir2:
            # when they are equal, only one subtriangle would be civilized, thus we'd have an overlap with type 2
            # that is undesirable
            pass
        else:
            res = type1.copy()
            res[dir1] = "Civilized"
            res[dir2] = "Civilized"
            if res in type3s:
                # since both dir1 and dir2 are drawn from the same list,
                # and it doesn't matter which one is which direction,
                # we might have already put a particular pair of them into type3s
                # for example, suppose dir1 is UL and dir2 is DN
                # a few iterations later we might see dir1 = DN and dir2 = UL
                # we'd want to pass on that iteration, to avoid re-adding the DN/UL pair
                pass
            else:
                type3s.append(res)

# construct arrangements for type 5 hexes
# same as type 5, but it starts with type 7 and modifies by adding Wild hexes, not Civilized ones
type5s = []
for dir1 in dirs:
    for dir2 in dirs:
        if dir1 == dir2:
            # when they are equal, only one subtriangle would be civilized, thus we'd have an overlap with type 2
            # that is undesirable
            pass
        else:
            res = type7.copy()
            res[dir1] = "Wild"
            res[dir2] = "Wild"
            if res in type5s:
                pass
            else:
                type5s.append(res)

# construct arrangements for type 4 hexes, which have an equal amount of wilderness and civilization
type4s = []
for dir1 in dirs:
    for dir2 in dirs:
        for dir3 in dirs:
            if dir1 == dir2 or dir2 == dir3 or dir1 == dir3:
                pass
            else:
                res = type1.copy()
                res[dir1] = "Civilized"
                res[dir2] = "Civilized"
                res[dir3] = "Civilized"
                if res in type4s:
                    pass
                else:
                    type4s.append(res)
                

totalConfigurations = 1+1+len(list(type2s))+len(list(type3s))+len(list(type4s))+len(list(type5s))+len(list(type6s))

def getConfigurationType(roll):
    if roll == 1 or roll == 2:
        return 1
    elif roll == 3:
        return 2
    elif roll == 4 or roll == 5:
        return 3
    elif roll == 6 or roll == 7:
        return 4
    elif roll == 8 or roll == 9:
        return 5
    elif roll == 10 or roll == 11:
        return 6
    elif roll == 12:
        return 7
    else:
        raise ValueError("The argument to this function is hardcoded to be interpreted within the range of a 1d12; you've given a value higher than 12, or a nonsensical value less than 1.")

configurationTypeMapping = {1:[type1],2:type2s,3:type3s,4:type4s,5:type5s,6:type6s,7:[type7]}

def getConfiguration(type):
    return choice(configurationTypeMapping[type])

def getHexTypeAndConfiguration():
    roll = randint(1,12)
    """Return the type of the configuration, and the configuration itself."""
    configType = getConfigurationType(roll)
    configuration = getConfiguration(configType)
    return configType, configuration
