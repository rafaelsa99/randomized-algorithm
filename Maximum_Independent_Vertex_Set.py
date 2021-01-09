
"""Maximum_Independent_Vertex_Set.py: Determine the (one) independent set of maximum cardinality vertices
        of a given non-oriented graph G, with n vertices and m edges, using a randomized algorithm."""

__author__ = "Rafael Sá, 104552, rafael.sa@ua.pt, MEI"

import math
import random
import time
import csv
from itertools import combinations

MAX_ATTEMPTS = 5000
PERCENTAGE_OF_SETS = 0.3

count_verifications = 0
graph_num_vertices = 0
graph_percentage_edges = 0


def generate_graphs_to_file(min_vertices, max_vertices, percent_edges, filename):
    """Generates the graphs corresponding to the combinations between
    the number of vertices and the percentage of edges."""
    file = open(filename, "w")
    for pct_edges in list(percent_edges):
        for num_vert in range(min_vertices, max_vertices + 1, 1):
            graph = [[0 for i in range(num_vert)] for j in range(num_vert)]
            num_edges = 0
            while get_percentage_edges(num_edges, num_vert) < pct_edges:
                i = random.randint(0, num_vert - 1)
                j = random.randint(0, num_vert - 1)
                if j != i and graph[i][j] == 0:
                    edge = random.randint(0, 1)
                    graph[i][j] = edge
                    graph[j][i] = edge
                    num_edges += edge
                    if get_percentage_edges(num_edges, num_vert) >= pct_edges:
                        write_graph_to_file(graph, file, num_vert, pct_edges)
                        break
    file.close()


def write_graph_to_file(graph, file_descriptor, num_vertices, percent_edges):
    """Write a given graph with n vertices and e edges to a file"""
    file_descriptor.write(str(num_vertices) + "," + str(percent_edges) + "\n")
    for row in graph:
        for v in row:
            file_descriptor.write(str(v) + " ")
        file_descriptor.write("\n")
    file_descriptor.write("\n")


def get_percentage_edges(num_edges, num_vert):
    """Return percentage of edges."""
    max_edges = (num_vert * (num_vert - 1)) / 2
    if max_edges > 0:
        return int((num_edges / max_edges) * 100)
    return 0


def read_graph_from_file(file_descriptor):
    """Read the next graph of a file"""
    global graph_num_vertices
    global graph_percentage_edges
    graph_info = file_descriptor.readline().rstrip('\n').split(',')
    if len(graph_info) < 2:
        return None
    graph_num_vertices = int(graph_info[0])
    graph_percentage_edges = int(graph_info[1])
    graph = [[0 for i in range(graph_num_vertices)] for j in range(graph_num_vertices)]
    line = 0
    while True:
        graph_line = file_descriptor.readline()
        if graph_line == '\n':
            break
        graph_line = graph_line.rstrip('\n').rstrip().split(' ')
        for v in range(len(graph_line)):
            graph[line][v] = int(graph_line[v])
        line += 1
    return graph


def check_independence(graph, candidate_subset):
    """Check if the candidate subset of the G vertices is independent."""
    global count_verifications
    count_verifications += 1
    comb = combinations(candidate_subset, 2)
    for c in list(comb):
        if graph[c[0]][c[1]] == 1:
            return False
    return True


def get_maximum_independent_set_exhaustive(graph):
    """Determine and return the first maximum independent vertex set of a graph g
    using an exhaustive search algorithm."""
    global graph_num_vertices
    vertices = [i for i in range(graph_num_vertices)]
    for i in range(graph_num_vertices, 0, -1):
        comb = combinations(vertices, i)
        for c in list(comb):
            if check_independence(graph, c):
                return c
    return None


def get_max_attempts(percentage):
    """Return a percentage of the total number of sets"""
    global graph_num_vertices
    total_sets = math.pow(2, graph_num_vertices) - 1
    result = round(total_sets * percentage)
    if result == 0:
        result = 1
    return result


def check_repetition(sets_verified, candidate):
    """Check if a candidate set has already been checked"""
    if len(sets_verified) == 0:
        return False
    for s in sets_verified:
        is_different = False
        for element in s:
            if element not in candidate:
                is_different = True
        if not is_different:
            return True
    return False


def get_maximum_independent_set_randomized(graph, max_attempts):
    """Try to determine and return a possible maximum independent vertex set of a graph g
    using a randomized algorithm."""
    global graph_num_vertices
    global count_verifications
    if max_attempts > MAX_ATTEMPTS:
        max_attempts = MAX_ATTEMPTS
    count_attempts = 0
    sets_verified = []
    vertices = [i for i in range(graph_num_vertices)]
    size = 1
    best_set = []
    while count_attempts < max_attempts and size <= graph_num_vertices:
        candidate = random.sample(vertices, k=size)
        count_attempts += 1
        if not check_repetition(sets_verified, candidate):
            sets_verified.append(candidate)
            if check_independence(graph, candidate):
                best_set = candidate
                size += 1
                sets_verified = []
    return best_set


if __name__ == '__main__':
    filename_graphs = "graphs.txt"
    filename_results = "results.txt"
    filename_results_excel = "results_to_excel.csv"

    # Generate Graphs
    percentage_edges = [25, 50, 75]
    min_vert = 2
    max_vert = 25
    generate_graphs_to_file(min_vert, max_vert, percentage_edges, filename_graphs)

    # Read Graphs
    total_graphs = 0
    count_optimal_result = 0
    file_graphs = open(filename_graphs, "r")
    file_results = open(filename_results, "w")
    file_results_to_excel = open(filename_results_excel, "w", newline='')
    excel_writer = csv.writer(file_results_to_excel, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_results.write("Results for the problem: Maximum Independent Vertex Set\n")
    file_results.write("Results regarding the graphs of the file \"" + filename_graphs + "\"\n\n")
    excel_writer.writerow(['Percentage of Edges', 'Number of Vertices', 'Number of Tested Solutions',
                           'Execution Time', 'Percentage of Optimal Results'])
    current_percentage_edges = 0
    while True:
        g = read_graph_from_file(file_graphs)
        if g is None:
            break
        if graph_percentage_edges != current_percentage_edges:
            total_graphs = 0
            count_optimal_result = 0
            current_percentage_edges = graph_percentage_edges
        total_graphs += 1
        file_results.write("Testing graph with: " + str(graph_num_vertices) + " vertices and " +
                           str(graph_percentage_edges) + "% edges:\n\n")
        attempts = get_max_attempts(PERCENTAGE_OF_SETS)
        count_verifications = 0
        start = time.time()
        rand = get_maximum_independent_set_randomized(g, attempts)
        end = time.time()
        tested_solutions = count_verifications
        file_results.write("Randomized Algorithm:\n")
        file_results.write("\tResult: " + str(rand) + "\n")
        file_results.write("\tCardinality of the set: " + str(len(rand)) + "\n")
        file_results.write("\tNumber of Tested Solutions: " + str(count_verifications) + "\n")
        file_results.write("\tNumber of Maximum Attempts: " + str(attempts) + "\n")
        file_results.write(f"\tExecution time: {(end - start):.2f} seconds\n")
        startE = time.time()
        exhaustive = get_maximum_independent_set_exhaustive(g)
        endE = time.time()
        file_results.write("Exhaustive Search Algorithm:\n")
        file_results.write("\tResult: " + str(exhaustive) + "\n")
        file_results.write("\tCardinality of the set: " + str(len(exhaustive)) + "\n")
        file_results.write(f"\tExecution time: {(endE - startE):.2f} seconds\n")
        if len(rand) == len(exhaustive):
            count_optimal_result += 1
        file_results.write("Percentage of optimal results: " +
                           str(round((count_optimal_result / total_graphs) * 100, 2)) + "%\n\n")
        excel_writer.writerow([graph_percentage_edges, graph_num_vertices, tested_solutions,
                               (end - start), round((count_optimal_result / total_graphs) * 100, 2)])
    file_results.close()
    file_results_to_excel.close()
    file_graphs.close()
    print("\nResults written to the file: \"" + filename_results + "\"")
    print("Results to use in excel written to the file: \"" + filename_results_excel + "\"")
