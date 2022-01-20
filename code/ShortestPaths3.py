# Priority dictionary using binary heaps
# all code in this module originally by David Eppstein (UC Irvine, 2002) and released under the Unlicense
# https://code.activestate.com/recipes/522995-priority-dict-a-priority-queue-with-updatable-prio/

# see also:
# http://www.grantjenks.com/docs/sortedcontainers/

from __future__ import generators


class priorityDictionary(dict):
    def __init__(self):
        """Initialize priorityDictionary by creating binary heap
        of pairs (value,key).  Note that changing or removing a dict entry will
        not remove the old pair from the heap until it is found by smallest() or
        until the heap is rebuilt."""
        self.__heap = []
        dict.__init__(self)

    def smallest(self):
        """Find smallest item after removing deleted items from heap."""
        if len(self) == 0:
            raise IndexError("smallest of empty priorityDictionary")
        heap = self.__heap
        while heap[0][1] not in self or self[heap[0][1]] != heap[0][0]:
            lastItem = heap.pop()
            insertionPoint = 0
            while 1:
                smallChild = 2 * insertionPoint + 1
                if (
                    smallChild + 1 < len(heap)
                    and heap[smallChild] > heap[smallChild + 1]
                ):
                    smallChild += 1
                if smallChild >= len(heap) or lastItem <= heap[smallChild]:
                    heap[insertionPoint] = lastItem
                    break
                heap[insertionPoint] = heap[smallChild]
                insertionPoint = smallChild
        return heap[0][1]

    def update(self, other):
        for key in other.keys():
            self[key] = other[key]

    def __iter__(self):
        """Create destructive sorted iterator of priorityDictionary."""

        def iterfn():
            while len(self) > 0:
                x = self.smallest()
                yield x
                del self[x]

        return iterfn()

    def __setitem__(self, key, val):
        """Change value stored in dictionary and add corresponding
        pair to heap.  Rebuilds the heap if the number of deleted items grows
        too large, to avoid memory leakage."""
        dict.__setitem__(self, key, val)
        heap = self.__heap
        if len(heap) > 2 * len(self):
            self.__heap = [(v, k) for k, v in self.iteritems()]
            self.__heap.sort()  # builtin sort likely faster than O(n) heapify
        else:
            newPair = (val, key)
            insertionPoint = len(heap)
            heap.append(None)
            while insertionPoint > 0 and newPair < heap[(insertionPoint - 1) // 2]:
                heap[insertionPoint] = heap[(insertionPoint - 1) // 2]
                insertionPoint = (insertionPoint - 1) // 2
            heap[insertionPoint] = newPair

    def setdefault(self, key, val):
        """Reimplement setdefault to call our customized __setitem__."""
        if key not in self:
            self[key] = val
        return self[key]


def Dijkstra(G, start, end=None):
    # dict of final distances
    D = {}
    # dict of predecessors
    P = {}
    # estimated distances of non-final vertices
    estimates = priorityDictionary()
    estimates[start] = 0

    for vert in estimates:
        D[vert] = estimates[vert]
        if vert == end:
            break
        for w in G[vert]:
            length = D[vert] + G[vert][w]
            if w in D:
                if length < D[w]:
                    raise ValueError(
                        "Dijkstra: found better path to already-final vertex"
                    )
            elif w not in estimates or length < estimates[w]:
                estimates[w] = length
                P[w] = vert

    return (D, P)


def shortestPath(G, start, end):
    """Find a single shortest path from start to end.
    Input is same as Dijkstra, above.
    Output is list of vertices in order along the shortest path.
    """
    D, P = Dijkstra(G, start, end)
    #    print("final distances",D,"\n","preds",P)
    #    print("assembling path")
    path = []
    #    print(path)
    while 1:
        path.append(end)
        #        print(path)
        if end == start:
            break
        end = P[end]
    path.reverse()
    return D, path
