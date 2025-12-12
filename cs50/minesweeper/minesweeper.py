import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return set(self.cells)
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1, 2 Adding cell as move made and marking cell as safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Collecting all surrounding neighbors (max 9) from selected cell
        neighbors = set()
        i, j = cell
        for ii in [-1, 0, 1]:
            for jj in [-1, 0, 1]:
                if ii == 0 and jj == 0:  # Ignoring the selected cell
                    continue
                ni = i + ii
                nj = j + jj

                # Ensuring that the neighbors falls within the bounds of the game
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.add((ni, nj))

        # Counting neighbors that are already known mines
        known_mine_neighbors = len([n for n in neighbors if n in self.mines])

        # Removing already known mines and safes from neighbor list
        neighbors = neighbors - self.safes - self.mines

        # Subtracting already known mines from mine count
        count -= known_mine_neighbors

        # 3 Creating new Sentence with neighbors and adjusted count, appending to knowledge
        if neighbors:
            new_sentence = Sentence(neighbors, count)
            self.knowledge.append(new_sentence)

        # 4 Checking knowledge for obvious safes and mines
        changes_made = True

        # Using a while loop because any new information added could further deduce more information
        while changes_made:
            changes_made = False
            for sentence in self.knowledge:
                cells = sentence.cells.copy()
                count = sentence.count

                # If count == number of unknown cells then all cells are mines
                if count == len(cells) and count != 0:
                    for cell in cells:
                        if cell not in self.mines:
                            self.mark_mine(cell)
                            changes_made = True

                # If count == 0 then all cells are safes
                if count == 0:
                    for cell in cells:
                        if cell not in self.safes:
                            self.mark_safe(cell)
                            changes_made = True

        new_inferred = []

        # 5 Using new knowledge acquired derive new knowledge
        for s1 in self.knowledge:  # Comparing every item in knowledge
            for s2 in self.knowledge:  # To every other item in knowledge
                if s1 == s2:  # Skipping comparing a sentence to itself
                    continue

                # If S1 is a subset of S2, calculate the difference between the S2 and S1
                if s1.cells.issubset(s2.cells):
                    cells_diff = s2.cells - s1.cells
                    count_diff = s2.count - s1.count

                    if cells_diff and count_diff >= 0:
                        new_sentence = Sentence(cells_diff, count_diff)

                        # Add new sentence to knowledge as long as it is not already known nor inferred via this portion of the code before
                        if new_sentence not in self.knowledge and new_sentence not in new_inferred:
                            new_inferred.append(new_sentence)

        self.knowledge.extend(new_inferred)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # From the set of safe values remove all previously made moves
        candidates = self.safes - self.moves_made

        if candidates:
            return random.choice(list(candidates))  # Return any safe move from list
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        all_cells = set()

        # Make a set of every possible combination of moves in the entire board
        for i in range(self.height):
            for j in range(self.width):
                all_cells.add((i, j))

        # Remove all prior moves and anything that we know is a mine
        candidates = all_cells - self.moves_made - self.mines

        if candidates:
            return random.choice(list(candidates))  # Choose random move from list of possible moves
        return None
