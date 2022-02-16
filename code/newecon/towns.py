import heapq
import math
from decimal import Decimal, getcontext
from collections import defaultdict
import references
from references import world_references

# set up the Decimal environment
getcontext().prec = 6

# todo don't forget that the TRADE distance is 1 more than the number of days away (so that places 1 day away do not export 100% of references)
towns = {
    # todo add location: Hex(q, r, s)
    # todo add whether a route is by land, sea, or river
    # todo add whether a route is one-way-only
    "Pearl Island": {
        "population": 3000,
        "references": {"olives": 1, "fish": 1, "dried fish": 1},
        "days to": {"Allrivers": 1.5, "Northshore": 2},
    },
    "Allrivers": {
        "population": 15000,
        "references": {"timber": 3, "markets": 1},
        "days to": {"Northshore": 2, "Gingol": 1.5, "Orii": 1, "Pearl Island": 1.5},
    },
    "Northshore": {
        "population": 5000,
        "references": {"timber": 1, "markets": 1},
        "days to": {"Allrivers": 2, "Ribossi": 1.5},
    },
    "Gingol": {
        "population": 10000,
        "references": {"cereals": 1, "markets": 1},
        "days to": {"Glimmergate": 2.5, "Allrivers": 1.5},
    },
    "Orii": {
        "population": 7000,
        "references": {"cereals": 1},
        "days to": {"Allrivers": 1, "Gingol": 3},
    },
    "Ribossi": {
        "population": 2000,
        "references": {"cattle": 1},
        "days to": {"Northshore": 1.5},
    },
    "Glimmergate": {
        "population": 22000,
        "references": {"sandstone": 1, "limestone": 1, "markets": 1, "smelting": 1},
        "days to": {"Gingol": 2.5},
    },
}


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def reconstruct_path(came_from, start, goal):
    """Processes a_star_search's path return value into a more readable list."""
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    # print(f"debug: searching from {start} to {goal}")

    while not frontier.empty():
        current = frontier.get()

        # early exit if the goal is reached
        if current == goal:
            break

        direct_connections = graph[current]["days to"]
        # print(f"debug: {direct_connections}")

        for next, local_distance in direct_connections.items():
            new_cost = cost_so_far[current] + local_distance
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                # the best way to get to to next from current has changed
                cost_so_far[next] = new_cost
                # quick and dirty heuristic
                priority = new_cost * 2
                frontier.put(next, priority)
                came_from[next] = current
    # print(f"debug: finished from {start} to {goal}")
    c = cost_so_far[goal]
    r = reconstruct_path(came_from, start, goal)
    return c, r


# decimalize all distances
for town, info in towns.items():
    info["days to"] = {k: Decimal(v) for k, v in info["days to"].items()}


# fill out towns with all-pairs distances
for source in towns:
    for target in towns:
        if source == target:
            pass
        elif target in towns[source]["days to"]:
            # distance from s to t is stipulated in original defn of towns, so reuse it
            # this assumes all distances between source and target are two-way traversable
            towns[target]["days to"][source] = towns[source]["days to"][target]
        else:
            distance, path = a_star_search(towns, source, target)
            towns[source]["days to"][target] = distance

towns["Far Away"] = {"references": {}, "days to": {}}
# initialize Far Away
for t in towns:
    towns[t]["days to"]["Far Away"] = Decimal(100)
    towns["Far Away"]["days to"][t] = Decimal(100)
total_assigned_refs = defaultdict(int)
for d in [info["references"] for t, info in towns.items()]:
    for k, v in d.items():
        total_assigned_refs[k] += v
for k, info in world_references.items():
    refs = info["references"]
    remaining_global_refs = max(0, refs - total_assigned_refs[k])
    towns["Far Away"]["references"][k] = remaining_global_refs
