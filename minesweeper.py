import itertools
import random

class Sentence():
    """
    A logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of how many of those cells are mines.
    """

    def __init__(self, cells, count):
        # use a set for cells to allow subset operations and easy removal
        self.cells = set(cells)
        self.count = count

    def __repr__(self):
        return f"Sentence({self.cells}, {self.count})"

    def known_mines(self):
        """
        If the number of cells equals the count, all cells are mines.
        Return a set of those cells (or an empty set).
        """
        if len(self.cells) > 0 and len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        If count is zero, all cells in the sentence are safe.
        Return a set of those cells (or an empty set).
        """
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Update the sentence given that a cell is known to be a mine:
        remove the cell from self.cells and decrement count by 1.
        If cell not in sentence, do nothing.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            # since that cell is a mine, reduce the count
            self.count -= 1

    def mark_safe(self, cell):
        """
        Update the sentence given that a cell is known to be safe:
        remove the cell from self.cells. Count remains the same.
        If cell not in sentence, do nothing.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player (AI)
    """

    def __init__(self, height=8, width=8):
        # board dimensions
        self.height = height
        self.width = width

        # keep track of moves made, known mines, and known safes
        self.moves_made = set()
        self.mines = set()
        self.safes = set()

        # knowledge base of Sentences
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Mark a cell as a mine and update all knowledge to reflect this.
        """
        if cell in self.mines:
            return
        self.mines.add(cell)
        # update all sentences
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Mark a cell as safe and update all knowledge to reflect this.
        """
        if cell in self.safes:
            return
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the AI reveals a safe cell `cell` with `count` neighboring mines.
        1) mark the cell as a move made
        2) mark the cell as safe
        3) add a new sentence to KB based on the cell's neighbors
        4) repeatedly mark additional cells as safe/mine if possible
           and add any new inferred sentences (subset inference)
        """
        # 1) mark move made
        self.moves_made.add(cell)

        # 2) mark as safe
        self.mark_safe(cell)

        # 3) construct new sentence from neighbors (excluding known safes / known mines)
        (i, j) = cell
        neighbors = set()
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbor = (ni, nj)
                    # Skip cells we already know are safe or moves made (they're already revealed safe)
                    if neighbor in self.safes:
                        continue
                    # If neighbor is known mine, decrement count (don't include in sentence)
                    if neighbor in self.mines:
                        count -= 1
                        continue
                    # Otherwise include in sentence if not already a move made
                    if neighbor not in self.moves_made:
                        neighbors.add(neighbor)

        # Add the new sentence if it has any cells
        new_sentence = None
        if len(neighbors) > 0:
            new_sentence = Sentence(neighbors, count)
            self.knowledge.append(new_sentence)

        # 4) Repeatedly update KB: mark safes/mines from sentences and infer new sentences
        changed = True
        while changed:
            changed = False

            # Collect safes and mines known from sentences
            safes_to_mark = set()
            mines_to_mark = set()
            for sentence in self.knowledge:
                safes_to_mark |= sentence.known_safes()
                mines_to_mark |= sentence.known_mines()

            # Mark discovered safes
            for s in safes_to_mark:
                if s not in self.safes:
                    self.mark_safe(s)
                    changed = True

            # Mark discovered mines
            for m in mines_to_mark:
                if m not in self.mines:
                    self.mark_mine(m)
                    changed = True

            # Remove empty sentences
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

            # Subset inference: if sentence A's cells are subset of sentence B's cells,
            # we can infer B - A has count difference
            new_inferred = []
            for s1, s2 in itertools.permutations(self.knowledge, 2):
                if s1.cells and s2.cells and s1 != s2 and s1.cells.issubset(s2.cells):
                    inferred_cells = s2.cells - s1.cells
                    inferred_count = s2.count - s1.count
                    # Only add meaningful sentences
                    if len(inferred_cells) > 0:
                        inferred = Sentence(inferred_cells, inferred_count)
                        # avoid duplicates: comparable by cells and count
                        duplicate = False
                        for old in self.knowledge + new_inferred:
                            if old.cells == inferred.cells and old.count == inferred.count:
                                duplicate = True
                                break
                        if not duplicate:
                            new_inferred.append(inferred)

            if new_inferred:
                for s in new_inferred:
                    self.knowledge.append(s)
                changed = True

    def make_safe_move(self):
        """
        Return a known safe cell that has not yet been chosen.
        If no such moves, return None.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Return a random move (i, j) from all possible moves that are
        not known to be mines and have not already been chosen.
        If no moves are possible, return None.
        """
        all_cells = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
        ]
        choices = [
            cell for cell in all_cells
            if cell not in self.moves_made and cell not in self.mines
        ]
        if not choices:
            return None
        return random.choice(choices)
