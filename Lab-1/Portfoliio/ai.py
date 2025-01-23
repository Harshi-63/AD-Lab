import networkx as nx
import matplotlib.pyplot as plt
import time
from fpdf import FPDF
import os

# Bi-directional BFS
def bidirectional_bfs(graph, start, goal):
    if start == goal:
        return [start]

    front_start = {start}
    front_goal = {goal}
    visited_start = {start: None}
    visited_goal = {goal: None}

    while front_start and front_goal:
        # Expand from start
        next_front = set()
        for node in front_start:
            for neighbor in graph[node]:
                if neighbor not in visited_start:
                    visited_start[neighbor] = node
                    next_front.add(neighbor)
                    if neighbor in visited_goal:
                        return reconstruct_path(visited_start, visited_goal, neighbor)
        front_start = next_front

        # Expand from goal
        next_front = set()
        for node in front_goal:
            for neighbor in graph[node]:
                if neighbor not in visited_goal:
                    visited_goal[neighbor] = node
                    next_front.add(neighbor)
                    if neighbor in visited_start:
                        return reconstruct_path(visited_start, visited_goal, neighbor)
        front_goal = next_front

    return None


def reconstruct_path(visited_start, visited_goal, meeting_point):
    path = []
    node = meeting_point
    while node is not None:
        path.append(node)
        node = visited_start[node]
    path.reverse()
    node = visited_goal[meeting_point]
    while node is not None:
        path.append(node)
        node = visited_goal[node]
    return path


# BFS
def bfs(graph, start, goal):
    queue = [start]
    visited = {start: None}

    while queue:
        current = queue.pop(0)
        if current == goal:
            return reconstruct_single_path(visited, goal)

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited[neighbor] = current
                queue.append(neighbor)
    return None


# DFS
def dfs(graph, start, goal):
    stack = [start]
    visited = {start: None}

    while stack:
        current = stack.pop()
        if current == goal:
            return reconstruct_single_path(visited, goal)

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited[neighbor] = current
                stack.append(neighbor)
    return None


def reconstruct_single_path(visited, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = visited[node]
    path.reverse()
    return path


# Visualization
def visualize(graph, path, filename):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(10, 8))

    nx.draw(graph, pos, with_labels=True, node_color="lightblue", node_size=800, edge_color="gray")

    if path:
        edges_in_path = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(graph, pos, edgelist=edges_in_path, edge_color="red", width=2)

    plt.title("Graph Visualization")
    plt.savefig(filename)
    plt.close()


# Main Code
if __name__ == "__main__":
    G = nx.Graph()
    G.add_edges_from([
        ('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'),
        ('C', 'E'), ('D', 'F'), ('E', 'F'), ('F', 'G'),
        ('G', 'H'), ('H', 'I'), ('I', 'J')
    ])

    start, goal = 'A', 'J'
    algorithms = [("Bi-Directional BFS", bidirectional_bfs), ("BFS", bfs), ("DFS", dfs)]

    results = []
    images = []

    for algo_name, algo in algorithms:
        start_time = time.time()
        path = algo(G, start, goal)
        elapsed = time.time() - start_time

        results.append((algo_name, path, elapsed))
        print(f"{algo_name}: Path = {path}, Time = {elapsed:.6f} seconds")

        image_file = f"{algo_name.replace(' ', '_')}_visualization.png"
        visualize(G, path, image_file)
        images.append(image_file)

    g
    for image in images:
        if os.path.exists(image):
            os.remove(image)