from termcolor import colored

class Var:
    def __init__(self, pos, neighbours):
        self.domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        self.pos = pos
        self.neighbours = set(neighbours)

class Sudoku:
    def __init__(self, filename):
        self.variables = []
        self.var_len = 0
        self.filename = filename
        self.sudoku = []
        self.un_constraints = set()
        self.bin_constraints = set()
        self.assignment = dict()
        self.solution = False
        self.empty = []
        self.exploring = 0
        self.degree = {}

    def sudoku_checker(self):
        if len(self.sudoku) != 9:
            raise Exception("Invalid Layout given")

        for i in self.sudoku:
            if len(i) != 9:
                raise Exception("Invalid Layout given")

    def sudoku_read(self):
        with open(self.filename) as file:
            content = file.readlines()

        for i in content:
            sub_con = []
            for con in i:
                if con.isdigit():
                    sub_con.append(int(con))
                else:
                    sub_con.append(con)
            if "\n" in sub_con:
                sub_con.remove("\n")
            self.sudoku.append(sub_con)

        self.sudoku_checker()

        return self.sudoku

    def set_coordinates(self):
        sudoku = self.sudoku_read()
        for i in range(len(sudoku)):
            for j in range(len(sudoku[i])):
                if sudoku[i][j] == "_":
                    self.empty.append((i, j))
                else:
                    self.un_constraints.add(((i, j), sudoku[i][j]))

    @staticmethod
    def neighbour_assign(mty):
        neighbours = set()
        i, j = mty

        for k in range(9):
            if k != i:
                neighbours.add((k, j))
            if k != j:
                neighbours.add((i, k))

        box_i, box_j = 3 * (i // 3), 3 * (j // 3)
        for di in range(3):
            for dj in range(3):
                ni, nj = box_i + di, box_j + dj
                if (ni, nj) != (i, j):
                    neighbours.add((ni, nj))

        if mty in neighbours:
            neighbours.remove(mty)

        return neighbours

    def neighbours(self):
        self.set_coordinates()
        neighbour = []

        for mty in self.empty:
            neighbours = self.neighbour_assign(mty)
            neighbours = [k for k in neighbours if k not in [i for i, _ in self.un_constraints]]
            neighbour.append(neighbours)

        return neighbour

    def node_consistency(self, var):
        for pos, val in self.un_constraints:
            for i in var.neighbours:
                if i == pos:
                    var.domain.discard(val)

    def consistency_mid(self, var, val):
        for neighbor in var.neighbours:
            for variable in self.variables:
                if variable.pos == neighbor:
                    variable.domain.discard(val)

    def consistency_end(self, var, val):
        for neighbor in var.neighbours:
            for variable in self.variables:
                if variable.pos == neighbor:
                    variable.domain.add(val)

    def constraint(self):
        neighbour = self.neighbours()
        for i in range(len(neighbour)):
            for j in neighbour[i]:
                if (j, i) in self.bin_constraints:
                    continue
                else:
                    self.bin_constraints.add((self.empty[i], j))

        for i in self.empty:
            self.degree[i] = sum(i in constraint for constraint in self.bin_constraints)

    def select_unassigned_var(self, assignment):
        for i in self.variables:
            if i.pos not in assignment:
                return i
        return None

    def consistent(self, assignment):
        for (x, y) in self.bin_constraints:

            if x not in assignment or y not in assignment:
                continue

            if assignment[x] == assignment[y]:
                return False

        return True

    def backtrack(self, assignment):
        if len(assignment) == self.var_len:
            return assignment

        var = self.select_unassigned_var(assignment)

        if var is not None:
            original_domain = var.domain.copy()
            for value in original_domain:
                new_assignment = assignment.copy()
                new_assignment[var.pos] = value
                self.exploring += 1

                if self.consistent(new_assignment):
                    self.consistency_mid(var, value)
                    result = self.backtrack(new_assignment)

                    if result is not None:
                        return result

                self.consistency_end(var, value)

        return None

    def res_display(self):
        for pos in self.assignment:
            i, j = pos
            self.sudoku[i][j] = self.assignment[pos]

        print("+-------+-------+-------+")
        for i in range(len(self.sudoku)):
            print("| ", end="")
            for j in range(len(self.sudoku[i])):
                if (i, j) in self.empty:
                    if j in [2, 5]:
                        print(colored(self.sudoku[i][j], 'red'), end = " | ")
                    else:
                        print(colored(self.sudoku[i][j], 'red'), end = " ")
                else:
                    if j in [2, 5]:
                        print(self.sudoku[i][j], end=" | ")
                    else:
                        print(self.sudoku[i][j], end=" ")
            print("|")

            if i in [2, 5]:
                print("+-------+-------+-------+")
        print("+-------+-------+-------+")

    def solve(self):
        self.constraint()

        for pos in self.empty:
            self.variables.append(Var(pos, self.neighbour_assign(pos)))
            self.var_len += 1

        for var in self.variables:
            self.node_consistency(var)

        self.assignment = self.backtrack(self.assignment)

        self.solution = self.assignment is not None

        return self.solution
