# minesweeper.py
# Implementation of Sentence and MinesweeperAI for CS50 Minesweeper
# Uploaded file reference (if needed): /mnt/data/84195b3e-24fd-4110-942f-455842146da5.png

import random

class Sentence:
    """Logical statement about a Minesweeper game

    A sentence consists of a set of board cells, and a count of how many
    of those cells are mines.
    """

    def __init__(self, cells, count):
        # Store cells as a set of tuples and count as integer
        self.cells = set(cells)
        self.count = int(count)

    def __repr__(self):
        return f"Sentence({self.cells}, {self.count})"

    def known_mines(self):
        """Return the set of all cells in self.cells known to be mines.

        If the number of cells equals the count, all of them are mines.
        """
        if len(self.cells) > 0 and self.count == len(self.cells):
            return set(self.cells)
        return set()

    def known_safes(self):
        """Return the set of all cells in self.cells known to be safe.

        If the count is 0, then all cells in the sentence are safe.
        """
        if len(self.cells) > 0 and self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """Update internal knowledge representation given that a cell is a mine.

        If the cell is in the sentence, remove it and decrement the count.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """Update internal knowledge representation given that a cell is safe.

        If the cell is in the sentence, remove it (count stays the same).
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """AI player for Minesweeper that uses logical inference.

    Attributes:
        height, width: board dimensions (default values may be provided externally)
        moves_made: set of moves already taken
        mines: set of cells known to be mines
        safes: set of cells known to be safe
        knowledge: list of Sentence objects representing the AI's KB
    """

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width

        # Keep track of moves made and knowledge about mines/safes
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        """Mark a cell as a mine and update all knowledge sentences."""
        if cell in self.mines:
            return
        self.mines.add(cell)
        # Update all sentences
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """Mark a cell as safe and update all knowledge sentences."""
        if cell in self.safes:
            return
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """Called when the AI is told, for a given safe cell, how many neighboring
        cells have mines. This should:
            1) mark the cell as one of the moves made
            2) mark the cell as safe
            3) add a new Sentence to the AI's knowledge base based on the value of
               `cell` and `count` (only include cells whose state is undetermined)
            4) mark any additional cells as safe or as mines if it can be concluded
            5) add any new sentences that can be inferred from existing knowledge
        """
        # 1. Mark the move
        self.moves_made.add(cell)

        # 2. Mark the cell as safe
        self.mark_safe(cell)

        # 3. Build a new sentence for the neighbors that are not already known
        i, j = cell
        neighbors = set()
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbor = (ni, nj)
                    # Only include undetermined neighbors
                    if neighbor not in self.safes and neighbor not in self.mines:
                        neighbors.add(neighbor)
                    # If neighbor is already known to be a mine, decrement count
                    elif neighbor in self.mines:
                        count -= 1

        # Only add a sentence if there are neighbors to consider
        if len(neighbors) > 0:
            new_sentence = Sentence(neighbors, count)
            self.knowledge.append(new_sentence)

        # 4 & 5: Repeatedly infer new safe/mine cells and new sentences
        self.__infer_knowledge()

    def __infer_knowledge(self):
        """Iteratively update knowledge base with inferences until no change."""
        changed = True
        while changed:
            changed = False

            # Collect cells to be marked as mines/safes
            mines_to_mark = set()
            safes_to_mark = set()

            # 4: From each sentence, infer known mines or safes
            for sentence in self.knowledge:
                if len(sentence.cells) == 0:
                    continue
                mines = sentence.known_mines()
                safes = sentence.known_safes()
                if mines:
                    mines_to_mark |= mines
                if safes:
                    safes_to_mark |= safes

            # Mark them (these updates will modify sentences)
            for m in mines_to_mark:
                if m not in self.mines:
                    self.mark_mine(m)
                    changed = True
            for s in safes_to_mark:
                if s not in self.safes:
                    self.mark_safe(s)
                    changed = True

            # Remove empty sentences
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

            # 5: Infer new sentences by checking subset relationships
            # If sentence A is subset of B, then B - A is also a sentence with
            # count = B.count - A.count
            new_sentences = []
            n = len(self.knowledge)
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    s1 = self.knowledge[i]
                    s2 = self.knowledge[j]
                    if s1.cells and s2.cells and s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        # Only consider valid new sentence
                        if len(diff_cells) > 0:
                            candidate = Sentence(diff_cells, diff_count)
                            # Avoid adding duplicates (by equality of cells and count)
                            exists = False
                            for s in self.knowledge + new_sentences:
                                if s.cells == candidate.cells and s.count == candidate.count:
                                    exists = True
                                    break
                            if not exists:
                                new_sentences.append(candidate)
            if new_sentences:
                self.knowledge.extend(new_sentences)
                changed = True

    def make_safe_move(self):
        """Return a safe cell to choose (one that's known to be safe and not yet chosen).
        If no such move available, return None.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """Return a random move that is not known to be a mine and hasn't been made yet.
        If no such moves exist, return None.
        """
        choices = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell in self.moves_made:
                    continue
                if cell in self.mines:
                    continue
                choices.append(cell)

        if not choices:
            return None
        return random.choice(choices)
