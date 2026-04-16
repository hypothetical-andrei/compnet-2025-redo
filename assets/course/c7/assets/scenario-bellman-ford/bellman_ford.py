def bellman_ford(graph, source):
    # Initialize all distances to infinity — we haven't found a path to anyone yet.
    # The source node is 0 — it costs nothing to "reach" where you already are.
    distances = {v: float("inf") for v in graph}
    distances[source] = 0

    # predecessors[v] will eventually tell us which node comes just before v
    # on the shortest path from source. Used to reconstruct the full path later.
    predecessors = {v: None for v in graph}

    vertices = list(graph.keys())

    print("INITIAL distances:", distances)
    print("INITIAL predecessors:", predecessors)
    print()

    # We need at most |V| - 1 iterations.
    # Reasoning: the shortest path between any two nodes in a graph with no
    # negative cycles can visit at most |V| - 1 edges. Each iteration
    # guarantees that paths using at most (i+1) edges are correctly computed.
    for i in range(len(vertices) - 1):
        changed = False

        # Examine every directed edge (u -> v) with weight w in the graph.
        for u in vertices:
            for v, w in graph[u].items():
                # "Relaxation": if going through u gives a cheaper route to v,
                # update v's distance and remember that u is now v's predecessor.
                #
                # The guard `distances[u] != inf` avoids propagating infinity
                # (inf + w is still inf mathematically, but we skip it explicitly
                # to stay correct and avoid potential float arithmetic issues).
                if distances[u] != float("inf") and distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w
                    predecessors[v] = u
                    changed = True  # at least one update happened this round

        print(f"ITERATION {i + 1} distances:", distances)
        print(f"PREDECESSORS:", predecessors)

        # Early termination: if no distance was updated in this entire iteration,
        # the algorithm has already converged — further iterations won't change
        # anything, so we can stop.
        if not changed:
            print("No changes, stopping early.")
            break

    # --- Negative cycle detection ---
    # After |V| - 1 iterations, shortest paths are finalized IF no negative
    # cycle exists. We do one extra relaxation pass: if any distance can STILL
    # be reduced, it means there is a cycle with negative total weight that we
    # could loop around indefinitely, making the "shortest" path -infinity.
    # In that case we signal failure by returning None.
    for u in vertices:
        for v, w in graph[u].items():
            if distances[u] != float("inf") and distances[u] + w < distances[v]:
                return None, None  # negative cycle found

    return distances, predecessors


def main():
    # Undirected-style graph represented as adjacency dict of dicts.
    # graph[u][v] = w means there is a directed edge from u to v with cost w.
    # Each edge appears twice (both directions) to simulate an undirected graph.
    graph = {
        "A": {"B": 4, "C": 2},
        "B": {"D": 2, "E": 3, "A": 4},
        "C": {"D": 3, "E": 1, "A": 2},
        "D": {"C": 3, "B": 2},
        "E": {"B": 3, "C": 1},
    }
    source = "D"

    distances, predecessors = bellman_ford(graph, source)

    if distances is None:
        print("Negative cycle detected — shortest paths are undefined.")
        return

    print()
    print("Shortest distances from", source)
    for v in sorted(distances.keys()):
        print(v, ":", distances[v])


if __name__ == "__main__":
    main()