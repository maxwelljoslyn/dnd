import noise
from decimal import *
from math import pi
import random

from .HexResources import *
from .Direction import *
from .AStarSearch import *
from .ShortestPaths3 import shortestPath
from .TownInfo import towns, connections
from .Triangles import getHexTypeAndConfiguration, getConfiguration

# desired seed for the RNG
# ALL PORTIONS OF WORLD GENERATION WHICH USE RANDOMNESS
# SHOULD RESET THE RNG TO THIS SEED BEFORE PROCEEDING WITH GENERATION
# THIS IS FOR REPLICABILITY
mySeed = 42
random.seed(mySeed)

# set up the Decimal environment
getcontext().prec = 6

# number of rings on the world map, with 0 = just the center hex
mapSize = 80

# equatorial diameter of the planet
# remember, I'm only generating one hemisphere right now
# one hex is 20 miles, and diameter == radius * 2pi
planetDiameter = mapSize * 20 * 2 * pi
# mapSize needed to match earth's equatorial diameter: 198

# All possible valid cube coordinates for a given mapSize,
# for a hexagon-shaped world map.
# In cube coordinates, there are three values,
# not two as with cartesian coordinates,
# but the third value (denoted "s") is dependent on the other two.
# I store it so it doesn't have to be calculated every time;
# thus, there's less risk of an arithmetic mistake popping up elsewhere.
possibleCoords = set()
# algorithm (for the coords fitting into a hexagon-shaped hexmap) sourced from:
# http://www.redblobgames.com/grids/hexagons/implementation.html
for q in range(-mapSize, mapSize+1):
    rStart = max(-mapSize, -q - mapSize)
    rEnd = min(mapSize, -q + mapSize)
    for r in range(rStart, rEnd+1):
        possibleCoords.add((q,r,0-q-r))

def addCoord(coord1, coord2):
    """Addition of cubic coordinates."""
    q = coord1[0] + coord2[0]
    r = coord1[1] + coord2[1]
    s = coord1[2] + coord2[2]
    return q, r, s

def getNeighbor(coord, direction):
    """Return coord's neighboring coordinate in the given direction.
    Calculate what that neighbor is,
    regardless of validity of its coord for the mapSize.
    If it would be off the grid (i.e. is not in possibleCoords), return None.
    Otherwise, return the neighbor's coordinate as calculated."""
    intermediate = addCoord(coord, direction.value)
    if intermediate in possibleCoords:
        return intermediate
    else:
        return None

def getTriangleNeighbors(dir, hex, worldModel):
    """Return the hexes and directions indicating triangle neighbors of the triangle at direction dir,
    which is in hex. Returns either two or three tuples of (parent hex,triangle dir)."""
    dirs = list(Direction.__members__.keys())
    index = dirs.index(dir)
    # no need for modulo, thanks to Python's negative indexing
    forwardNeighborDir = dirs[index-1]
    forwardNeighbor = (hex, forwardNeighborDir)
    # modulo is necessary to avoid overshooting length of dirs
    backwardNeighborDir = dirs[(index+1)%len(dirs)]
    backwardNeighbor = (hex, backwardNeighborDir)
    # if the parent hex has a neighbor in the direction of dir,
    # then this triangle also has a neighbor there.
    # otherwise it only has two neighbors.
    result = [forwardNeighbor, backwardNeighbor]
    neighboringHex = worldModel[hex].neighbors[dir]
    if neighboringHex:
        oppositeNeighbor = (neighboringHex, oppositeDirection(dir))
        result.append(oppositeNeighbor)
    else:
        pass
    return result 


# http://www.redblobgames.com/grids/hexagons/#range
def nearbyCoords(startCoord, distance):
    """Return all hexes which are distance or fewer hexes away from starting point.
    Since this operates on and returns coords, it doesn't test for existence in
    the possibleCoords set (which really ought to be called possibleHexes.)"""
    results = []
    for x in range(-distance,distance+1):
        rangeBot = max(-distance,(-x) - distance)
        rangeTop = min(distance,(-x)+distance)
        for y in range(rangeBot,rangeTop+1):
            z = -x - y
            results.append(addCoord(startCoord,(x,y,z)))
    # the returned hexes include the start hex, so we want to throw that out
    results.remove(startCoord)
    return results

def diffOfLists(a,b):
    """Return elements in a which are not in b."""
    b = set(b)
    return [item for item in a if item not in b]

def nthRingCoords(startCoord, ringNumber):
    """Returns all coords which are in the nth ring away from the starting coord.
    As with nearbyCoords, this function returns coords, not hexes as filtered thru possibleCoords.
    To get only those which are actually hexes in the world map, use nthRingHexes."""
    if ringNumber < 1:
        raise ValueError("ringNumber argument to nthRingCoords must be an integer 1 or greater")
    coordsAtDistanceN = nearbyCoords(startCoord, ringNumber)
    coordsLessThanDistanceN = nearbyCoords(startCoord, ringNumber - 1)
    coordsInRingN = diffOfLists(coordsAtDistanceN,coordsLessThanDistanceN)
    return coordsInRingN

def nthRingHexes(startCoord, ringNumber):
    """As nthRingCoords, but with coords not in possibleCoords filtered out."""
    res = nthRingCoords(startCoord,ringNumber)
    res = [r for r in res if r in possibleCoords]
    return res


def nearbyHexes(startHex, distance):
    """Calls nearbyCoords but then filters for membership in possibleCoords."""
    res = nearbyCoords(startHex, distance)
    res = [r for r in res if r in possibleCoords]
    return res

class HexData:
    """Stores the metadata information associated with a given hexagon."""
    def __init__(self):
        self.elevation = Decimal()
        self.temperature = Decimal()
        self.isLand = None
        self.neighbors = {}
        self.moisture = Decimal(0)
        self.climate = ""
        self.resources = {}
        self.subConfigurationType = 0 # an invalid setting, on purpose
        self.subs = {}
        self.infrastructure = Decimal(0)

def tempAtCoord(coord):
    """Return a heat number for the hex at coord.
    Low 'never hot', high means 'always hot',
    and in between means variation, meaning seasonal heat changes."""
    distanceFromCenter = cubeDistance((0,0,0),coord)
    # 0 at center hex, 1 on first ring, 2 on next ring, etc
    minTemp = Decimal(-30)
    # temp at (0,0,0), the center of the map and the North Pole
    maxTemp = Decimal(90)
    # temp at outer edge of map, the equator
    stepSize = Decimal((abs(minTemp) + maxTemp) / mapSize)
    adjustment = Decimal(distanceFromCenter) * stepSize
    return(minTemp + adjustment)

# TODO: write my own noise generator (see AmitP noise page)
def initialize():
    """Build up the HexData for each coord on the grid."""
    worldModel = {}
    for coord in possibleCoords:
        worldModel[coord] = HexData()
    octaves = 4
    frequency = 12.0 * octaves

    # first data-assignment for loop
    for coord, data in worldModel.items():
        # assign elevation
        q = coord[0]
        r = coord[1]
        data.elevation = (Decimal(noise.snoise3(q/frequency, r/frequency, 2, octaves)) + Decimal(1))
        # this will be changed in the next loop, it's just a starting point
        data.temperature = tempAtCoord(coord)
        # fill in neighbors list
        for name, member in Direction.__members__.items():
            data.neighbors[name] = getNeighbor(coord, member)

    # normalize terrain to be between 0 and 1
    elevations = [d.elevation for c,d in worldModel.items()]
    elevMax = max(elevations)
    elevMin = min(elevations)
    seaLevel = 0.46
    # this value gives most aesthetically-pleasing shapes for landmasses, islands

    # assign elevation, land/sea
    for coord, data in worldModel.items():
        normalizedElevation = (data.elevation - elevMin) / (elevMax - elevMin)
        data.elevation = normalizedElevation
        # land/sea distinction
        if data.elevation >= seaLevel:
            data.isLand = True
        else:
            data.isLand = False

    # next for loop
    # moistureLine requires all the elevations to be assigned
    # before it works properly,
    # which means the previous loop has to be completely done before proceeding.
    # because there are six moisture passes,
    # any of which might alter part of the map,
    # we have to do all of them before proceeding onto the next assignment loop.
    for coord, data in worldModel.items():
        # initial conditions for moisture: 0 (default) for land, 1 for water
        if data.isLand == False:
            data.moisture = Decimal(1)

        def moistureLine(aCoord, aDir):
            """Move moisture from one hex to another.
            Defined within this loop because it uses generated elevations."""
            currentHex = worldModel[aCoord]
            currentMoisture = currentHex.moisture

            # abort if moisture is too low to keep spreading
            while currentMoisture > 0.3:
                neighborLocation = currentHex.neighbors[aDir]
                if neighborLocation is None:
                    break
                neighbor = worldModel[neighborLocation]
                if neighbor.isLand is False:
                    break
                else:
                    if neighbor.elevation < currentHex.elevation:
                        neighbor.moisture = max(neighbor.moisture, Decimal(0.8) * currentMoisture)
                    else:
                        deltaElevation = abs(currentHex.elevation - neighbor.elevation)
                        neighbor.moisture = max(neighbor.moisture, currentMoisture - (Decimal(2.5) * Decimal(deltaElevation)))
                currentHex = neighbor
                currentMoisture = neighbor.moisture

        # starting at the sea hexes, move in each direction,
        # spreading moisture as we go
        if data.isLand is False:
            for name, member in Direction.__members__.items():
                moistureLine(coord, name)

    # climate assignment
    for coord, data in worldModel.items():
        m = data.moisture
        t = data.temperature
        if m == 1:
            data.climate = "Water"
        elif m < 0.25 and t >= 60:
            data.climate = "Desert"
        elif m < 0.25 and t >= 45:
            data.climate = "Mediterranean"
        elif m < 0.25 and t >= 0:
            data.climate = "HotSummerContinental"
        elif m < 0.25:
            data.climate = "Tundra"
        elif m < 0.5 and t >= 60:
            data.climate = "Savannah"
        elif m < 0.5 and t >= 45:
            data.climate = "Mediterranean"
        elif m < 0.5 and t >= 0:
            data.climate = "HotSummerContinental"
        elif m < 0.5 and t >= -15:
            data.climate = "ColdContinental"
        elif m < 0.5:
            data.climate = "IceCap"
        elif m < 0.75 and t >= 75:
            data.climate = "Monsoon"
        elif m < 0.75 and t >= 60:
            data.climate = "Steppe"
        elif m < 0.75 and t >= 15:
            data.climate = "Oceanic"
        elif m < 0.75 and t >= 0:
            data.climate = "ColdOceanic"
        elif m < 0.75 and t >= -15:
            data.climate = "Taiga"
        elif m < 0.75:
            data.climate = "IceCap"
        elif m >= 0.75 and t >= 75:
            data.climate = "TropicalRainforest"
        elif m >= 0.75 and t >= 45:
            data.climate = "HumidSubtropical"
        elif m >= 0.75 and t >= 15:
            data.climate = "WetContinental"
        elif m >= 0.75 and t >= -15:
            data.climate = "Taiga"
        else:
            data.climate = "IceCap"

    # build the name-indexed road model (roads from town to town and their distances)
    roadModelByName = {}
    for t,d in towns.items():
        if t in roadModelByName:
            pass
        else:
            roadModelByName[t] = {}
        for c in connections[t]:
            distance, path = AStarSearch(worldModel,d.coord,towns[c].coord)
            roadModelByName[t][c] = distance,path
            if c not in roadModelByName:
                roadModelByName[c] = {}
            roadModelByName[c][t] = distance,path

    # build the coord-indexed road model (for map rendering) from the name-indexed one
    roadModelByCoord = {}
    for name,targets in roadModelByName.items():
        coord = towns[name].coord
        roadModelByCoord[coord] = {}
        for targetName,data in targets.items():
            targetCoord = towns[targetName].coord
            roadModelByCoord[coord][targetCoord] = data
    
    # instantiate subtriangles and assign starting data to them
    for coord, data in worldModel.items():
        data.subs = {x:{} for x in Direction.__members__.keys()}
        subsType = None
        subsConfiguration = None
        if data.isLand:
            # all random
            data.subConfigurationType, subsConfiguration = getHexTypeAndConfiguration()
        else:
            # water hexes are considered to be type 1 (ALL wild), always;
            # we let degrees of wilderness handle just how wild each bit of water is
            data.subConfigurationType = 1
            subsConfiguration = getConfiguration(1)
        for sub,info in data.subs.items():
            info["Elevation"] = normalizedElevation
            info["Quality"] = "Civilized"
            # just setting all of these to "Civilized" until I can establish a rating based on infrastructure numbers
            info["Neighbors"] = getTriangleNeighbors(sub,coord,worldModel)

    # the wild/civ divide and the exact nature thereof should be calculated based on infra
    # ie. the loop above where triangles are assigned wild/civ arrangements ought to
    # come after infrastructure assignemnt, and take those infra values into account.
    # TODO

    # infrastructure, part 1: assign base infrastructure values to towns
    for town, info in towns.items():
        worldModel[info.coord].infrastructure += info.population / Decimal(100)

    # infrastructure, part 2: much like moisture, above,
    # we want to spread infrastructure values hex-to-hex
    # one thing to be careful of:
    # we want to spread the values out based on the original numbers,
    # which means we don't want to touch (i.e. destructively update)
    # the *original* values for infrastructure by the above loop,
    # UNTIL we are done calcuating the propagation of infra values.
    # i.e. we want to store results from the propagation algo in a separate dictionary,
    # then, having accumuluated the results, add them in to their respective coords' infra values
    # within the worldModel.
    # this is similar to importing phenomenon in the ResourcePriceCalculator:
    # there, we use each town's original count for each resource,
    # and spread those out to other towns,
    # only at the end accumulating the results into each town's post-import totals for each resource.
    accumulatedInfrastructureAdjustments = {}
    def findInfraToSpread(startCoord):
        """Add infrastructure points to nearby hexes.
        The points at aCoord are not depleted when this happens."""
        startData = worldModel[startCoord]
        possibleReachableHexes = nearbyHexes(startCoord, 10)
        # 10 is a magic constant for now, I'm still tweaking it and haven't figured out anything on which I could base a limit to spreading
        for p in possibleReachableHexes:
            cost, path = AStarSearch(worldModel, startCoord, p)
            potentialInfrastructure = Decimal(startData.infrastructure / (2 ** cost))
            if potentialInfrastructure < 1:
                pass
            else:
                if p in accumulatedInfrastructureAdjustments:
                    # update value at that key
                    accumulatedInfrastructureAdjustments[p] += potentialInfrastructure
                else:
                    # create initial value at that key
                    accumulatedInfrastructureAdjustments[p] = potentialInfrastructure


    # now let's actually use the above function
    for coord,data in worldModel.items():
        if data.infrastructure == 0:
            pass
        else:
            findInfraToSpread(coord)
    # initialize variables which we will use for infrastructure normalization
    infraMin = 1000000
    infraMax = 0
    for coord, additionToInfrastructure in accumulatedInfrastructureAdjustments.items():
        worldModel[coord].infrastructure += additionToInfrastructure
        # now that the infrastructure has been updated at this hex,
        # see if we need to update our min or max values
        infra = worldModel[coord].infrastructure
        if infra < infraMin:
            infraMin = infra
        if infra > infraMax:
            infraMax = infra

    # normalize infrastructure from 0 to 1
    for coord,data in worldModel.items():
        if data.infrastructure == Decimal(0):
            pass
        else:
            normalizedInfra = (data.infrastructure - infraMin) / (infraMax - infraMin)
            data.infrastructure = normalizedInfra

    return worldModel, roadModelByName, roadModelByCoord

worldModel, roadModelByName, roadModelByCoord = initialize()

# in order to run this implementation of shortest path (and therefore Dijkstra),
# we have to strip the road information out of the roadModel,
# leaving only the raw distance numbers.
strippedRoadModel = {src:{dest:data[0] for dest,data in goesTo.items()} for src,goesTo in roadModelByName.items()}
# building the all-pairs shortest path matrix from the road model,
# giving us distances from each town to each other town
# this is used in resourcePriceCalculator; it's calculated here there are so fewer imports from this file to that one
shortestPathMatrix = {}
for source in strippedRoadModel:
    shortestPathMatrix[source] = {}
    for dest in strippedRoadModel:
        if source == dest:
            pass
        else:
#            print("debug: finding path from",source,"to",dest)
            finalDists, path = shortestPath(strippedRoadModel, source, dest)
            d = finalDists[dest]
#            print("Debug: distance is",str(d))
            shortestPathMatrix[source][dest] = d

def main():
    with open("inputWorldParser.txt", "w") as f:
        for c,d in worldModel.items():
            subsList = ",".join([str(sub) + " Elevation " + str(info["Elevation"]) + " Quality " + info["Quality"] for sub,info in d.subs.items()])
            outputString = "Hex Coord " + str(c) + \
              " Elevation " + str(d.elevation) + \
              " Temperature " + str(d.temperature) + \
              " Land " + str(d.isLand) + \
              " Moisture " + str(d.moisture) + \
              " Climate " + d.climate + \
              " Infrastructure " + str(d.infrastructure) + \
              " Subs [" + subsList + "]" + "\n"
            f.write(outputString)

    with open("inputTownParser.txt", "w") as f:
        for t,d in towns.items():
            outputString = "Coord " + str(d.coord) + " Name " + t + "\n"
            f.write(outputString)

    with open("inputRoadParser.txt", "w") as f:
        for coord, targets in roadModelByCoord.items():
            for target, data in targets.items():
                distance = data[0]
                path = data[1]
                pathString = ",".join([("Coord " + str(x)) for x in path])
                outputString = "[" + pathString + "]\n"
                f.write(outputString)

if __name__ == "__main__":
    main()
