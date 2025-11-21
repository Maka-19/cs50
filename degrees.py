#!/usr/bin/env python3
"""
degrees.py

Usage:
    python degrees.py <directory>

Example:
    python degrees.py large
"""

import csv
import sys
from collections import deque, defaultdict

# Maps names to a set of corresponding person_ids
names = defaultdict(set)

# Maps person_id -> {"name": str, "birth": str, "movies": set(movie_ids)}
people = {}

# Maps movie_id -> {"title": str, "year": str, "stars": set(person_ids)}
movies = {}

def load_data(directory):
    """Load data from CSV files into memory."""
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            person_id = row["id"]
            people[person_id] = {
                "name": row["name"],
                "birth": row.get("birth", ""),
                "movies": set()
            }
            names[row["name"].lower()].add(person_id)

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = row["id"]
            movies[movie_id] = {
                "title": row["title"],
                "year": row.get("year", ""),
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = row["movie_id"]
            person_id = row["person_id"]
            if person_id in people:
                people[person_id]["movies"].add(movie_id)
            if movie_id in movies:
                movies[movie_id]["stars"].add(person_id)


def person_id_for_name(name):
    """
    Resolve a name to a person_id.
    If multiple people have the same name, prompt the user to pick.
    Returns person_id (string) or None if not found.
    """
    person_ids = list(names.get(name.lower(), set()))
    if not person_ids:
        return None
    if len(person_ids) == 1:
        return person_ids[0]

    # Ambiguous — ask user to choose
    print(f"Which '{name}'?")
    for pid in person_ids:
        person = people[pid]
        print(f"ID: {pid}, Name: {person['name']}, Birth: {person['birth']}")
    try:
        chosen = input("Enter the ID for the intended person: ").strip()
    except EOFError:
        return None
    if chosen in person_ids:
        return chosen
    return None


def shortest_path(source_id, target_id):
    """
    Return the shortest list of (movie_id, person_id) pairs
    that connect source_id to target_id (BFS).
    If no connection, return None.
    Each step describes an edge: source_person --movie--> next_person
    """

    # Edge case
    if source_id == target_id:
        return []

    # BFS structures
    frontier = deque()
    frontier.append(source_id)
    # parent maps person_id -> (parent_person_id, movie_id)
    parent = {source_id: None}
    visited = {source_id}

    while frontier:
        current = frontier.popleft()
        for movie_id in people[current]["movies"]:
            for neighbor in movies[movie_id]["stars"]:
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parent[neighbor] = (current, movie_id)
                if neighbor == target_id:
                    # Reconstruct path from source -> target as list of (movie_id, person_id)
                    path = []
                    cur = neighbor
                    while parent[cur] is not None:
                        par_person, par_movie = parent[cur]
                        path.append((par_movie, cur))  # edge: par_person --par_movie--> cur
                        cur = par_person
                    path.reverse()
                    return path
                frontier.append(neighbor)
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python degrees.py <directory>")

    directory = sys.argv[1]

    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    # Get source person
    try:
        name1 = input("Name: ").strip()
    except EOFError:
        sys.exit("No input provided.")
    source = person_id_for_name(name1)
    if source is None:
        sys.exit(f"{name1} not found.")

    # Get target person
    try:
        name2 = input("Name: ").strip()
    except EOFError:
        sys.exit("No input provided.")
    target = person_id_for_name(name2)
    if target is None:
        sys.exit(f"{name2} not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
        return

    degrees = len(path)
    print(f"{degrees} degrees of separation.")

    # Print each step: i: NameA and NameB starred in MovieTitle
    current_person = source
    for i, (movie_id, person_id) in enumerate(path, start=1):
        person_a = people[current_person]["name"]
        person_b = people[person_id]["name"]
        movie_title = movies[movie_id]["title"]
        print(f"{i}: {person_a} and {person_b} starred in {movie_title}")
        current_person = person_id


if __name__ == "__main__":
    main()
