from enum import Enum

class Direction(Enum):
    """The six directions on a grid of flat-topped hexagons: up-left, up,
    up-right, down-right, down, down-left.
    These aren't called NW/northwest, TN/true north, etc. because on my map,
    the coordinate (0,0,0), the center of the map, is the North Pole.
    So going north on the map is not the same as going up."""
    UL = (-1,1,0)
    UP = (0,1,-1)
    UR = (1,0,-1)
    DR = (1,-1,0)
    DN = (0,-1,1)
    DL = (-1,0,1)

def oppositeDirection(dir):
    if dir == "UP":
        return "DN"
    elif dir == "DN":
        return "UP"
    elif dir == "UL":
        return "DR"
    elif dir == "DR":
        return "UL"
    elif dir == "UR":
        return "DL"
    elif dir == "DL":
        return "UR"
    else:
        raise ValueError("not a recognized direction!")
        
