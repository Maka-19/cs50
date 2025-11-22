    def enforce_node_consistency(self):
        """
        Remove any values from domains that are inconsistent with
        the variable's unary constraints (word length).
        """
        for var in self.domains:
            to_remove = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    to_remove.add(word)
            self.domains[var] -= to_remove


    def revise(self, x, y):
        """
        Make variable x arc consistent with y.
        Remove any value in x's domain that has
        no corresponding value in y's domain.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        # If no overlap, no constraints
        if overlap is None:
            return False

        i, j = overlap
        to_remove = set()

        for word_x in self.domains[x]:
            # Check if there exists at least one word_y
            # that satisfies the overlap constraint
            satisfies = False
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    satisfies = True
                    break
            if not satisfies:
                to_remove.add(word_x)

        if to_remove:
            self.domains[x] -= to_remove
            revised = True

        return revised


    def ac3(self, arcs=None):
        """
        AC3 algorithm to enforce arc consistency.
        """
        if arcs is None:
            queue = [(x, y) for x in self.domains for y in self.domains if x != y]
        else:
            queue = list(arcs)

        while queue:
            x, y = queue.pop(0)

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False

                # Add all arcs (z, x) where z is neighbor of x except y
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))

        return True


    def assignment_complete(self, assignment):
        """
        Check if assignment is complete:
        every variable has a value.
        """
        return len(assignment) == len(self.crossword.variables)


    def consistent(self, assignment):
        """
        Check if assignment satisfies:
        - All values are distinct
        - All values have correct length
        - No conflicts between neighbors
        """
        # Check distinctness
        if len(set(assignment.values())) != len(assignment):
            return False

        for var, value in assignment.items():
            # Check length
            if len(value) != var.length:
                return False

            # Check overlaps
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    i, j = overlap
                    if value[i] != assignment[neighbor][j]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return domain values for var ordered by least-constraining-value (LCV).
        """
        def conflicts(word):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap is None:
                        continue

                    i, j = overlap
                    # Count how many neighbor words this word eliminates
                    for w in self.domains[neighbor]:
                        if word[i] != w[j]:
                            count += 1
            return count

        return sorted(self.domains[var], key=conflicts)


    def select_unassigned_variable(self, assignment):
        """
        Select unassigned variable using MRV, then degree heuristic.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # Sort by: (domain size asc, degree desc)
        return sorted(
            unassigned,
            key=lambda v: (len(self.domains[v]), -len(self.crossword.neighbors(v)))
        )[0]


    def backtrack(self, assignment):
        """
        Backtracking search for a complete assignment.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                # Inference: optional, can run AC3 for speed
                saved_domains = copy.deepcopy(self.domains)

                # Reduce domain temporarily
                self.domains[var] = {value}

                if self.ac3():
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result

                # Restore domains on failure
                self.domains = saved_domains

        return None
