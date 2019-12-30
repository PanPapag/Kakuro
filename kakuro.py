import os
import re
import sys
import time
import puzzles

from csp import *
from search import *
from utils import *

class Kakuro(CSP):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.rows_size = len(puzzle)
        self.cols_size = len(puzzle[0])
        self.variables = self.get_variables()
        self.domain = self.get_domain()
        self.neighbors = self.get_neighbors()
        self.sums = self.get_sums()
        self.constraints = self.get_constraints
        CSP.__init__(self, self.variables, self.domain, self.neighbors, self.constraints)

    def get_variables(self):
        variables = []
        for i, row in enumerate(self.puzzle):
            for j, cell in enumerate(row):
                if cell == 'W':
                    variables.append('x' + '_' + str(i) + '_' + str(j))

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
            neighbors[variable] = []
            # Get row and col of current variable
            row = int(re.search('_(.*)_', variable).group(1))
            col = int(variable.rsplit('_', 1)[-1])
            # Check same row for neighbors
            for i in range(self.cols_size):
                if i < col - 1 or i > col + 1:
                    continue
                if isinstance(self.puzzle[row][i], str):
                    if self.puzzle[row][i] == 'W':
                        neighbor_variable = 'x' + '_' + str(row) + '_' + str(i)
                        if neighbor_variable in self.variables and neighbor_variable != variable:
                            neighbors[variable].append(neighbor_variable)
            # Check same col for neighbors
            for i in range(self.rows_size):
                if i < row -1 or i > row + 1:
                    continue
                if isinstance(self.puzzle[i][col], str):
                    if self.puzzle[i][col] == 'W':
                        neighbor_variable = 'x' + '_' + str(i) + '_' + str(col)
                        if neighbor_variable in self.variables and neighbor_variable != variable:
                            neighbors[variable].append(neighbor_variable)

        return neighbors

    def get_constraints(self, A, a, B, b):
        # if two neighbors have the same value constraints are not satisfied
        if a == b:
            return False
        # store assignments that have been made so far
        assignment = self.infer_assignment()
        # In this step check if a is equal to any other A's neighbor variable assigned value. In this case
        # the constraints are not being satisfied
        for var in self.neighbors[A]:
            if var in assignment:
                if assignment[var] == a:
                    return False
        # Similarly to B
        for var in self.neighbors[B]:
            if var in assignment:
                if assignment[var] == b:
                    return False
        # Check if neighbors A and B satisfy their common constraints
        for sum in self.sums:
            if (A in sum[1]) and (B in sum[1]):
                sum_of_neighbors = 0
                assigned_neighbors = 0
                for var in sum[1]:
                    if var in assignment:
                        if (var != A) and (var != B):
                            sum_of_neighbors += assignment[var]
                            assigned_neighbors += 1
                sum_of_neighbors += a + b
                assigned_neighbors += 2
                if (len(sum[1]) > assigned_neighbors) and (sum_of_neighbors >= sum[0]):
                    return False
                if (len(sum[1]) == assigned_neighbors) and (sum_of_neighbors != sum[0]):
                    return False

        # Check if A's constraints are being satisfied
        for sum in self.sums:
            if (A in sum[1]) and (B not in sum[1]):
                sum_of_neighbors = 0
                assigned_neighbors = 0
                for variable in sum[1]:
                    if variable in assignment:
                        if variable != A:
                            sum_of_neighbors += assignment[variable]
                            assigned_neighbors += 1
                sum_of_neighbors += a
                assigned_neighbors += 1
                if (len(sum[1]) > assigned_neighbors) and (sum_of_neighbors >= sum[0]):
                    return False
                if (len(sum[1]) == assigned_neighbors) and (sum_of_neighbors != sum[0]):
                    return False

        # Check if B's constraints are being satisfied
        for sum in self.sums:
            if (A not in sum[1]) and (B in sum[1]):
                sum_of_neighbors = 0
                assigned_neighbors = 0
                for variable in sum[1]:
                    if variable in assignment:
                        if variable != B:
                            sum_of_neighbors += assignment[variable]
                            assigned_neighbors += 1
                sum_of_neighbors += b
                assigned_neighbors += 1
                if (len(sum[1]) > assigned_neighbors) and (sum_of_neighbors >= sum[0]):
                    return False
                if (len(sum[1]) == assigned_neighbors) and (sum_of_neighbors != sum[0]):
                    return False
        # Everthing ok, constraints are being satisfied so return True
        return True

    def get_sums(self):
        sums = []
        for i, row in enumerate(self.puzzle):
            for j, cell in enumerate(row):
                if (cell != 'W' and cell != 'B'):
                    # down - column
                    if (cell[0] != ''):
                        x = []
                        for k in range(i + 1, self.rows_size):
                            if (self.puzzle[k][j] != 'W'):
                                break
                            x.append('x' + '_' + str(k) + '_' + str(j))
                        sums.append((cell[0], x))
                    # right - row
                    if (cell[1] != ''):
                        x = []
                        for k in range(j + 1, len(self.puzzle[i])):
                            if (self.puzzle[i][k] != 'W'):
                                break
                            x.append('x' + '_' + str(i) + '_' + str(k))
                        sums.append((cell[1], x))
        return sums

    def BT(self):
        start = time.time()
        result = backtracking_search(self)
        end = time.time()
        return (result, end - start)

    def BT_MRV(self):
        start = time.time()
        result = backtracking_search(self, select_unassigned_variable=mrv)
        end = time.time()
        return (result, end - start)

    def FC(self):
        start = time.time()
        result = (backtracking_search(self, inference=forward_checking))
        end = time.time()
        return (result, end - start)

    def FC_MRV(self):
        start = time.time()
        result = (backtracking_search(self, select_unassigned_variable=mrv, inference=forward_checking))
        end = time.time()
        return (result, end - start)

    def MAC(self):
        start = time.time()
        result = (backtracking_search(self, select_unassigned_variable=mrv, inference=mac))
        end = time.time()
        return (result, end - start)

    def display_grid(self, grid):
        for i in range(self.rows_size):
            for j in range(self.cols_size):
                if isinstance(self.puzzle[i][j], list):
                    if grid[i][j][0] == '':
                        print('B\{}'.format(grid[i][j][1]).ljust(4), end='\t')
                    elif grid[i][j][1] == '':
                        print('{}\B'.format(grid[i][j][0]).ljust(4), end='\t')
                    else:
                        print('{}\{}'.format(grid[i][j][0], grid[i][j][1]).ljust(4), end='\t')
                else:
                    print(grid[i][j].ljust(4), end='\t')
            print()

    def display_solution(self, grid, solution, time_elapsed, assigns):
        if solution != None:
            for variable in self.variables:
                # Get row and col of current variable
                row = int(re.search('_(.*)_', variable).group(1))
                col = int(variable.rsplit('_', 1)[-1])
                # Get value
                value = solution[variable]
                # Assign value of the variable to the grid
                grid[row][col] = str(value)
            # display assigned grid
            self.display_grid(grid)
            print("Number of assigns: {}".format(assigns))
            print("Total time elapsed: {:.4f} seconds".format(time_elapsed))
        else:
            print("No solution found!")



if __name__ == "__main__":
    # Get all puzzles from puzzle.py
    kakuro_puzzles = []
    for item in vars(puzzles).keys():
        if not item.startswith("__"):
            kakuro_puzzles.append((item,vars(puzzles)[item]))

    for puzzle_name, puzzle in kakuro_puzzles:
        print("\n----------------------------- {} Kakuro puzzle -----------------------------".format(puzzle_name))
        kakuro = Kakuro(puzzle)
        kakuro.display_grid(kakuro.puzzle)
        # BT algorithm
        print("\n> Solution using BT algorithm")
        kakuro.display_solution(kakuro.puzzle, *kakuro.BT(), kakuro.nassigns)
        # BT + MRV algorithm
        print("\n> Solution using BT and MRV algorithm")
        kakuro.display_solution(kakuro.puzzle, *kakuro.BT_MRV(), kakuro.nassigns)
        # FC algorithm
        print("\n> Solution using FC algorithm")
        kakuro.display_solution(kakuro.puzzle, *kakuro.FC(), kakuro.nassigns)
        # FC + MRV algorithm
        print("\n> Solution using FC and MRV algorithm")
        kakuro.display_solution(kakuro.puzzle, *kakuro.FC_MRV(), kakuro.nassigns)
        # MAC algorithm
        print("\n> Solution using MAC algorithm")
        kakuro.display_solution(kakuro.puzzle, *kakuro.MAC(), kakuro.nassigns)
        # print an empty line for better output
        print()
