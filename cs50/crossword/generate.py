import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:  # Looping through every variable in domains
            # Making a copy of the list of words so as to not change the size of the set
            word_list = self.domains[variable].copy()
            for word in word_list:  # Looping through each word
                # Checking to see if the word length is not consistent with the length of the variable
                if len(word) != variable.length:
                    self.domains[variable].remove(word)  # Removing the word if not consistent

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False  # exists outside the loop because we return revised if at least one change was made
        # using the overlap function to return the coords (i,j) of overlap
        overlap = self.crossword.overlaps[x, y]

        if overlap is not None:
            i, j = overlap  # unpacking the indicies of the overlap
            x_words = list(self.domains[x])
            y_words = list(self.domains[y])
            for x_word in x_words:  # looping through every word in x's domain
                match = False  # initative match found variable, we need to reset for each new x_word thus it's inside the loop
                for y_word in y_words:  # looping through every word in y's domain
                    if x_word[i] == y_word[j]:  # if x_words's i position letter matches that in y_words's j position letter
                        match = True  # we have a match and can stop searching through y_words's and move onto the next x_word
                        break  # we can then exit the loop
                if not match:
                    # if no match then we must remove word_x from x's domain
                    self.domains[x].remove(x_word)
                    revised = True  # setting revised to true, if there is at least one revision

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If `arcs` is None, begin with initial list of all arcs in the problem.
        if arcs is None:
            queue = []
            for domain in self.domains:
                for neighbor in self.crossword.neighbors(domain):
                    queue.append((domain, neighbor))
        else:
            queue = list(arcs)

        while queue:
            # Looking at first pair in queue
            x, y = queue.pop(0)
            # Call revise function from above, if it returns true then it means we've just deleted some words from x because they didn't work with y
            if self.revise(x, y):
                # If, in the process of enforcing arc consistency, you remove all of the remaining values from a domain
                if len(self.domains[x]) == 0:
                    return False  # Return False
                # Because x now has fewer words, we must now look at x's neighbors once again
                for z in self.crossword.neighbors(x):
                    # We skip because we have just checked the relation between (x,y) checking again would be redundant
                    if z != y:
                        # We will add (z,x) back into the queue
                        # Adding (z,x) because we know that x has just changed so we need to see if z is still okay
                        queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        is_complete = True

        # Check to ensure the number of variables in assignment matches that in the actual assignment
        if len(assignment) != len(self.crossword.variables):
            is_complete = False

        # Check if each variable has a value
        for variable in self.crossword.variables:
            if variable not in assignment:
                is_complete = False

        return is_complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Extracting the values aka words from the assignment
        words = assignment.values()
        # Taking the unique set of words from words, if there is are duplicates these lengths will not match
        unique_words = set(words)

        if len(words) != len(unique_words):
            return False  # If the lengths do not match, not all values are distinct

        for variable1, word1 in assignment.items():
            # Unary constraints
            if len(word1) != variable1.length:  # Checking to see if the values are the correct length
                return False

            # Checking overlap with neighbors
            for variable2 in self.crossword.neighbors(variable1):
                # If variable2 not in assignment then we don't care about it
                if variable2 in assignment:
                    # Pulling the actual word value from the assignment[variable]
                    word2 = assignment[variable2]
                    # Extracting the coordinates of the overlap
                    i, j = self.crossword.overlaps[variable1, variable2]
                    # Checking to see if the character of overlap is the same in both words
                    # If they differ then something is wrong and the assignment is not consistent
                    if word1[i] != word2[j]:
                        return False

        # If the code makes it this far, then no rules were broken and thus the assignment is consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        scores = {}  # Initalizing scoring dictionary
        for value in self.domains[var]:  # Looping through all the values in the domain of 'var'
            n = 0  # Initializing counter for number of values ruled out
            neighbors = self.crossword.neighbors(var)  # Finding the neighbors of var
            for neighbor in neighbors:  # For each neighbor of var
                if neighbor not in assignment:  # Ignoring any variable already present in assignment
                    # Find overlapping indicies between var and neighbor
                    i, j = self.crossword.overlaps[var, neighbor]
                    # Looping through all the value in the domain of 'neighbor'
                    for neighbor_word in self.domains[neighbor]:
                        if value[i] != neighbor_word[j]:  # If letter's don't match we can rule out a word
                            n = n + 1  # adding 1 to our ruled out count

            scores[value] = n

        scores = sorted(self.domains[var], key=lambda word: scores[word])

        return scores

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [
            # Find all unassigned variables not already in assignment
            v for v in self.crossword.variables if v not in assignment]

        scores = {}  # Initalizing scoring dictionary

        for value in unassigned:  # Looping through all the values in unassigned
            mrv = len(self.domains[value])  # Find the current domain size of the value
            n_degree = 0
            for neighbor in self.crossword.neighbors(value):  # For each neighbor of value
                if neighbor not in assignment:  # Ignoring any variable already present in assignment
                    n_degree = n_degree + 1  # Counting unassigned neighbors

            # For mrv low is best, thus we negate n_degree to utilize min() most effectively
            scores[value] = (mrv, -n_degree)

        # min() with a tuple sorts by the first value and then the second, so any ties in mrv will come down to which has the best n_degree or the most negative number of neighbors since we negated it
        best_variable = min(scores, key=lambda value: scores[value])

        return best_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Check if assignment is complete using assignment_complete function defined earlier
        # Return completed assignment
        if self.assignment_complete(assignment):
            return assignment

        # If assignment incomplete find all unassigned variable
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # Looping through all the unassigned variables
        for variable in unassigned:
            # Find the values (words) assocaited with each variable
            for value in self.domains[variable]:
                new_assignment = assignment.copy()  # Make a copy of the original assignment to save
                # Add the variable, value combo to the new copied assignment
                new_assignment[variable] = value
                # Ensure the new assignment is consistent with the newly added variable, value
                if self.consistent(new_assignment):
                    result = self.backtrack(new_assignment)  # If consistent then rerun backtracking
                    if result is not None:  # Copied from backtrack() function in slides
                        return result  # Return result if not a failure

        # If no assignment return None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
