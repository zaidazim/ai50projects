import itertools
import random
import copy


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
        # while len(self.mines) != mines:
        #     i = random.randrange(height)
        #     j = random.randrange(width)
        #     if not self.board[i][j]:
        #         self.mines.add((i, j))
        #         self.board[i][j] = True

        # Add fixed mine locations:
        mine_list = [ (2,4), (3,5), (4,1), (6,5), (6,7), (7,4), (7,6), (7,7) ] 
        for i,j in mine_list: 
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
        # if {A,B} = 2 the function returns A, B
        if len(self.cells) == self.count:
            return self.cells
        # else no inference could be drawn and it returns an empty set
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if {A, B, C} = 0 the function returns A, B, C
        if self.count == 0:
            return self.cells
        # else it returns an empty set
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            return None

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            return None


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
        print(f"Marked mine: {cell}") # added print statements
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        print(f"Marked safe: {cell}") # added print statements
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
        # 1
        self.moves_made.add(cell)

        # 2
        self.mark_safe(cell)

        # 3
        neighbors = set()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Check if cell in bound
                if 0 <= i < self.height and 0 <= j < self.width:

                    # Check if cell's state is undetermined
                    if (i, j) not in self.mines and (i, j) not in self.safes:
                        neighbors.add((i, j))
        
        if len(neighbors) == count:
            for neighbor in neighbors:
                self.mark_mine(neighbor)
                count -= 1
        
        if count == 0:
            for neighbor in neighbors:
                self.mark_safe(neighbor)

        # Loop to see the added neighbors
        print("Added neighbors: ")
        for neighbor in neighbors:
            print(neighbor, end=' ') 
        print()              

        new_sentence = Sentence(neighbors, count)
        if len(neighbors) != 0 and new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)
            print(f"Added sentence- {new_sentence.cells}: {new_sentence.count}")
        # 4
        kb = copy.deepcopy(self.knowledge)
        for sentence in kb:
            if len(sentence.cells) == sentence.count and sentence.count != 0:
                for cell in sentence.cells:
                    self.mark_mine(cell)
            
            if sentence.count == 0:
                for cell in sentence.cells:
                    self.mark_safe(cell)
                   

        # 5
        self.infer_new_sentence(self.knowledge)



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) != 0:
            for cell in self.safes:
                if (cell not in self.moves_made) and (cell not in self.mines):
                    print('Safe cell found: ' + str(cell))
                    return cell
        
        else:
            print('No safe cells found')

    def make_random_move(self):


        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        total_moves = self.height * self.width
        possible_moves = set()
        for row in range(self.height):
            for col in range(self.width):
                if (row, col) not in self.moves_made:
                    if (row, col) not in self.mines:
                        possible_moves.add((row, col))

        if len(possible_moves) == 0 or self.moves_made == total_moves - 8:
            return None
        else:
            return possible_moves.pop()

    def infer_new_sentence(self, knowledge):

        for i in range(len(self.knowledge)):
            for j in range(i+1, len(self.knowledge)):
                
                if knowledge[i].cells.issubset(knowledge[j].cells):
                    updated_cells = knowledge[j].cells.difference(knowledge[i].cells)
                    updated_count = knowledge[j].count - knowledge[i].count
                    new_sentence = Sentence(updated_cells, updated_count)

                    if new_sentence not in self.knowledge and len(new_sentence.cells) != 0:
                        self.knowledge.append(new_sentence)

                elif knowledge[j].cells.issubset(knowledge[i].cells):
                    updated_cells = knowledge[i].cells.difference(knowledge[j].cells)
                    updated_count = knowledge[i].count - knowledge[j].count
                    new_sentence = Sentence(updated_cells, updated_count)

                    if new_sentence not in self.knowledge and len(new_sentence.cells) != 0:
                        self.knowledge.append(new_sentence)