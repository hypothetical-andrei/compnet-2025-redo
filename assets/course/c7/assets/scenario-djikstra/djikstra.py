from heapq import heappop, heappush

def dijkstra(graph, source):
    # Initialize all distances to infinity — no path known yet to any node.
    # The source costs 0 to reach (we start there).
    distances = {v: float("inf") for v in graph}
    distances[source] = 0

    # predecessors[v] records which node comes just before v on the shortest
    # path from source. Useful for reconstructing the full path after the
    # algorithm finishes.
    predecessors = {v: None for v in graph}

    # Priority queue (min-heap): each entry is (cost, node).
    # We start by "visiting" the source at cost 0.
    pq = [(0, source)]

    while pq:
        # Pop the node with the currently lowest known distance.
        # This is the greedy step: because all weights are non-negative,
        # the cheapest unvisited node cannot be improved further.
        dist_u, u = heappop(pq)

        # Stale entry check: if we already found a better path to u since
        # this entry was pushed, skip it. This replaces the need for a
        # "visited" set — we simply ignore outdated heap entries.
        if dist_u != distances[u]:
            continue

        print(f"Visiting {u} (dist={dist_u}) | distances: {distances}")

        # Relaxation: for each neighbor v of u, check if going through u
        # gives a cheaper route to v than what we currently know.
        for v, w in graph[u].items():
            nd = dist_u + w
            if nd < distances[v]:
                distances[v] = nd
                predecessors[v] = u
                # Push the improved distance to the heap.
                # The old (worse) entry for v remains in the heap but will
                # be discarded by the stale entry check above when popped.
                heappush(pq, (nd, v))

    return distances, predecessors


def main():
    # Undirected-style graph as adjacency dict of dicts.
    # graph[u][v] = w means directed edge u -> v with cost w.
    # Each edge appears in both directions to simulate an undirected graph.
    graph = {
        "A": {"B": 4, "C": 2},
        "B": {"D": 2, "E": 3, "A": 4},
        "C": {"D": 3, "E": 1, "A": 2},
        "D": {"C": 3, "B": 2},
        "E": {"B": 3, "C": 1},
    }
    source = "C"

    # We only need distances here; predecessors are ignored with _.
    distances, _ = dijkstra(graph, source)

    print("Shortest distances from", source)
    for v in sorted(distances.keys()):
        print(v, ":", distances[v])


if __name__ == "__main__":
    main()