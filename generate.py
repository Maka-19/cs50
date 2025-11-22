import copy
import random

from generate import *
class CrosswordCreator:
    def __init__(self, crossword):
        """
        Make new CSP crossword generator.
        """
        self.crossword = crossword

        # Domains: a dictionary mapping variables to a set of possible words
        self.domains = {
            var: set(self.crossword.words)
            for var in self.crossword.variables
        }

        }

    def enforce_node_consistency(self):
        """Remove any values from domains that are inconsistent
        with the variable's unary constraints (word length)."""
        for var in list(self.domains.keys()):
            to_remove = {w for w in self.domains[var] if len(w) != var.length}
            if to_remove:
                self.domains[var] -= to_remove

    def revise(self, x, y):
        """Make variable x arc consistent with y.

        Remove any value in x's domain that has no corresponding
        possible value in y's domain. Return True if a revision was made."""
        revised = False
        overlap = self.crossword.overlaps[x, y]
        # No overlap => nothing to do
        if overlap is None:
            return False
        i, j = overlap
        to_remove = set()
        for vx in set(self.domains[x]):
            # check if any vy in domain[y] satisfies overlap
            has_support = False
            for vy in self.domains[y]:
                if vx[i] == vy[j]:
                    has_support = True
                    break
            if not has_support:
                to_remove.add(vx)
        if to_remove:
            self.domains[x] -= to_remove
            revised = True
        return revised

    def ac3(self, arcs=None):
        """AC3 algorithm. If arcs is None, initialize with all arcs.
        Return True if arc consistency enforced successfully; False if any
        domain becomes empty."""
        # Build initial queue of arcs
        if arcs is None:
            queue = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    queue.append((x, y))
        else:
            queue = list(arcs)

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                # add arcs (z, x) for all neighbors z of x except y
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """Return True if assignment is complete (all variables assigned)."""
        return set(assignment.keys()) == set(self.crossword.variables)

    def consistent(self, assignment):
        """Return True if assignment is consistent:
        - all words have correct length
        - all words are unique
        - all overlapping letters match
        """
        # All assigned words must be unique
        values = list(assignment.values())
        if len(values) != len(set(values)):
            return False

        for var, word in assignment.items():
            # Check length
            if len(word) != var.length:
                return False
            # Check overlaps with already assigned neighbors
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
        """Return domain values for var ordered by least-constraining-value.

        For each value, count how many values it would rule out for
        neighboring unassigned variables; sort ascending.
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
                for w in self.domains[neighbor]:
                    if value[i] != w[j]:
                        count += 1
            return count

        return sorted(self.domains[var], key=ruled_out_count)

    def select_unassigned_variable(self, assignment):
        """Select an unassigned variable using MRV, breaking ties by degree."""
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        # MRV: fewest legal values; Degree: most neighbors
        def sort_key(v):
            return (len(self.domains[v]), -len(self.crossword.neighbors(v)))
        return min(unassigned, key=sort_key)

    def backtrack(self, assignment):
        """Backtracking search to find a complete assignment or None if failure."""
        # If assignment is complete, return it
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                # Save domains and assign
                saved_domains = copy.deepcopy(self.domains)
                # Temporarily restrict domain and run inference
                self.domains[var] = {value}
                if self.ac3():
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result
                # restore domains
                self.domains = saved_domains
        return None

    # Helper / output functions (optional)
    def solve(self):
        """Solve the crossword: enforce node consistency, AC3, then backtrack."""
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())
    