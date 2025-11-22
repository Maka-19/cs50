import copy
import random
import sys

from crossword import *


class CrosswordCreator:
    """
    Crossword puzzle CSP solver.
    """

    def __init__(self, crossword):
        """
        Create generator for given Crossword object.
        """
        self.crossword = crossword
        # Domains: each variable -> set of possible words
        self.domains = {
            var: set(self.crossword.words)
            for var in self.crossword.variables
        }

    def enforce_node_consistency(self):
        """
        Remove values from domains that violate unary constraints:
        word length must equal variable.length.
        """
        for var in list(self.domains.keys()):
            self.domains[var] = {w for w in self.domains[var] if len(w) == var.length}

    def revise(self, x, y):
        """
        Make variable x arc-consistent with y.
        Remove any value in domain[x] that has no corresponding
        compatible value in domain[y] according to overlap.
        Return True if we removed a value.
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False

        i, j = overlap
        to_remove = set()
        for vx in set(self.domains[x]):
            # Check if exists vy in domain[y] matching overlap
            found = False
            for vy in self.domains[y]:
                if vx[i] == vy[j]:
                    found = True
                    break
            if not found:
                to_remove.add(vx)

        if to_remove:
            self.domains[x] -= to_remove
            return True
        return False

    def ac3(self, arcs=None):
        """
        AC-3 algorithm. If arcs is None, initialize with all arcs (x,y)
        where y is neighbor of x. Return False if some domain becomes empty.
        """
        if arcs is None:
            queue = [(x, y) for x in self.crossword.variables for y in self.crossword.neighbors(x)]
        else:
            queue = list(arcs)

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if every variable has an assignment.
        """
        return set(assignment.keys()) == set(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if assignment satisfies:
         - All assigned words have correct length
         - All assigned words are unique (no duplicates)
         - All overlaps between assigned variables match characters
        """
        # Unique check
        values = list(assignment.values())
        if len(values) != len(set(values)):
            return False

        for var, word in assignment.items():
            # length check
            if len(word) != var.length:
                return False
            # overlaps
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap is None:
                        continue
                    i, j = overlap
                    if word[i] != assignment[neighbor][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return list of values in var's domain, ordered by least-constraining-value (LCV).
        For each value, count how many possible values it rules out for neighboring unassigned variables.
        Sort ascending by that count.
        """
        def ruled_out_count(value):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap is None:
                    continue
                i, j = overlap
                # For each neighbor domain value, if incompatible, it would be ruled out
                for w in self.domains[neighbor]:
                    if value[i] != w[j]:
                        count += 1
            return count

        return sorted(self.domains[var], key=ruled_out_count)

    def select_unassigned_variable(self, assignment):
        """
        Choose an unassigned variable using MRV, breaking ties by degree heuristic.
        MRV: variable with fewest remaining values in domain.
        Degree: variable with most neighbors.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # If none unassigned (shouldn't happen here), return None
        if not unassigned:
            return None

        def key_fn(v):
            return (len(self.domains[v]), -len(self.crossword.neighbors(v)))

        return min(unassigned, key=key_fn)

    def backtrack(self, assignment):
        """
        Backtracking search for complete assignment. Returns complete assignment or None.
        """
        # If complete, return assignment
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            # Try assignment
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                # Inference: backup domains and temporarily reduce domain
                saved_domains = copy.deepcopy(self.domains)
                self.domains[var] = {value}

                # Propagate constraints with AC3 for extra pruning
                if self.ac3():
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result

                # restore domains if failure
                self.domains = saved_domains

        return None

    def solve(self):
        """
        High-level solve: enforce node consistency, run AC3, then backtrack.
        Returns assignment dict or None.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


# If run as a script, provide a simple CLI to solve a puzzle and print result
def main():
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output_image]")

    structure = sys.argv[1]
    words = sys.argv[2]

    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    if assignment is None:
        print("No solution.")
    else:
        # Print the solved crossword in a readable grid
        letters = [[" " for _ in range(crossword.width)] for __ in range(crossword.height)]
        for var, word in assignment.items():
            i, j = var.i, var.j
            if var.direction == Variable.ACROSS:
                for k, ch in enumerate(word):
                    letters[i][j + k] = ch
            else:
                for k, ch in enumerate(word):
                    letters[i + k][j] = ch

        for row in letters:
            print("".join(ch if crossword.structure[letters.index(row)][row.index(ch)] else "#" for ch in row))

        # Optionally save image if third arg provided
        if len(sys.argv) == 4:
            output = sys.argv[3]
            # rely on crossword.save or similar if available in provided files
            try:
                creator.crossword.save(assignment, output)
                print(f"Saved image to {output}")
            except Exception as e:
                print(f"Could not save image: {e}")


if __name__ == "__main__":
    main()
