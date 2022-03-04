import heapq


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


def a_star_search(graph, start, goal, key="hexes to"):
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

        direct_connections = graph[current][key]
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
