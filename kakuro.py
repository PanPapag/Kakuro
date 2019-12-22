from csp import *
from search import *
from puzzles import *
from utils import *

class Kakuro(CSP):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.size = len(puzzle)
        self.variables = self.get_variables()
        self.domain = self.get_domain()
        self.neighbors = self.get_neighbors()
        self.constraints = self.get_constraints()
        #CSP.__init__(self, self.variables, self.domain, self.neighbors, self.constraints)

    def get_variables(self):
        variables = []
        for i, line in enumerate(self.puzzle):
            for j, cell in enumerate(line):
                if cell == 'W':
                    variables.append('x' + str(i) + str(j))

        return variables

    def get_domain(self):
        domain = {}
        for variable in self.variables:
            domain[variable] = []
            for i in range(1,10):
                domain[variable].append(i)
        return domain

    def get_neighbors(self):
        neighbors = {}
        for variable in self.variables:
            variable_neighbors = []
            for i in range(self.size):
                if i != int(variable[2]):
                    variable_neighbors.append('x' + variable[1] + str(i))
                if i != int(variable[1]):
                    variable_neighbors.append('x' + str(i) + variable[2])
            neighbors[variable] = variable_neighbors
        return neighbors

    def get_constraints(self):
        pass

if __name__ == "__main__":
    kakuro = Kakuro(easy_5x5)
