# also writen by David Eppstein (see below)
from .priodict import priorityDictionary

# Dijkstra's algo for shortest paths
# David Eppstein, UC Irvine, 4 April 2002
# https://code.activestate.com/recipes/522995-priority-dict-a-priority-queue-with-updatable-prio/
def Dijkstra(G,start,end=None):
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
                    raise ValueError("Dijkstra: found better path to already-final vertex")
            elif w not in estimates or length < estimates[w]:
                estimates[w] = length
                P[w] = vert

    return (D,P)

def shortestPath(G,start,end):
    """Find a single shortest path from start to end.
    Input is same as Dijkstra, above.
    Output is list of vertices in order along the shortest path.
    """
    D,P = Dijkstra(G,start,end)
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

# code from Eppstein ends here
