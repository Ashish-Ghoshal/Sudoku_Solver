# Sudoku Solver



import numpy as np
import time

# Some helper lists to iterate through houses
#################################################

# return columns' lists of cells
all_columns = [[(i, j) for j in range(9)] for i in range(9)]

# same for rows
all_rows = [[(i, j) for i in range(9)] for j in range(9)]

# same for blocks
# this list comprehension is unreadable, but quite cool!
all_blocks = [[((i//3) * 3 + j//3, (i % 3)*3+j % 3)
               for j in range(9)] for i in range(9)]

# combine three
all_houses = all_columns+all_rows+all_blocks


# Some helper functions
#################################################
# returns list [(0,0), (0,1) .. (a-1,b-1)]
# kind of like "range" but for 2d array
def range2(a, b):
    permutations = []
    for j in range(b):
        for i in range(a):
            permutations.append((i, j))
    return permutations


# Adding candidates instead of zeros
def pencil_in_numbers(puzzle):
    sudoku = np.empty((9, 9), dtype=object)
    for (j, i) in range2(9, 9):
        if puzzle[i, j] != 0:
            sudoku[i][j] = [puzzle[i, j], ]
        else:
            sudoku[i][j] = [i for i in range(1, 10)]
    return sudoku


# Count solved cells
def n_solved(sudoku):
    solved = 0
    for (i, j) in range2(9, 9):
        if len(sudoku[i, j]) == 1:
            solved += 1
    return solved


# Count remaining unsolved candidates to remove
def n_to_remove(sudoku):
    to_remove = 0
    for (i, j) in range2(9, 9):
        to_remove += len(sudoku[i, j])-1
    return to_remove


# Print full sudoku, with all candidates (rather messy)
def print_sudoku(sudoku):
    for j in range(9):
        out_string = "|"
        out_string2 = " " * 10 + "|"
        for i in range(9):
            if len(sudoku[i, j]) == 1:
                out_string2 += str(sudoku[i, j][0])+" "
            else:
                out_string2 += "  "

            for k in range(len(sudoku[i, j])):
                out_string += str(sudoku[i, j][k])
            for k in range(10 - len(sudoku[i, j])):
                out_string += " "
            if (i + 1) % 3 == 0:
                out_string += " | "
                out_string2 += "|"

        if (j) % 3 == 0:
            print ("-" * 99, " " * 10, "-" * 22)
        print (out_string, out_string2)
    print ("-" * 99,  " " * 10, "-" * 22)



# 0. Simple Elimination
# If there is one number in cell - remove it from the house
###################################
def simple_elimination(sudoku):
    count = 0
    for group in all_houses:
        for cell in group:
            if len(sudoku[cell]) == 1:
                for cell2 in group:
                    if sudoku[cell][0] in sudoku[cell2] and cell2 != cell:
                        sudoku[cell2].remove(sudoku[cell][0])
                        count += 1
    return count




# 1. Backtracking
# a.k.a. Brute Force
#####################

# Helper: list of houses of each cell
# To optimize checking for broken puzzle
def cellInHouse():
    out = {(-1, -1):[]}
    for (i, j) in range2(9, 9):
        out[(i,j)] = []
        for h in all_houses:
            if (i, j) in h:
                out[(i, j)].append(h)
    return out

def get_next_cell_to_force(s):
    for (i, j) in range2(9, 9):
        if len(s[i, j])>1:
            return (i, j)


def brute_force(s, verbose):
    solution = []
    t = time.time()
    iter_counter = 0

    cellHouse = cellInHouse()
    
    def is_broken(s, last_cell):
        for house in cellHouse[last_cell]:
            house_data = []
            for cell in house:
                if len(s[cell]) == 1:
                    house_data.append(s[cell][0])
            #Checking for duplicate in row or col or square
            if len(house_data) != len(set(house_data)):
                return True
        return False

    def iteration(s, last_cell=(-1,-1)):
        nonlocal solution
        nonlocal iter_counter

        iter_counter += 1
        if iter_counter%100000 == 0 and verbose:
            print ("Iteration", iter_counter)

        # is broken - return fail
        if is_broken(s, last_cell):
            return -1

        # is solved - return success
        if n_to_remove(s) == 0:
            #print ("Solved")
            solution = s
            return 1

        # find next unsolved cell
        next_cell = get_next_cell_to_force(s)

        # apply all options recursively
        for n in s[next_cell]:
            scopy = s.copy()
            scopy[next_cell] = [n]
            result = iteration(scopy, next_cell)
            if result == 1:
                return

    iteration(s)

    if len(solution)>0:
        if verbose:
            print ("Backtracking took:", time.time()-t, "seconds, with", iter_counter, "attempts made")
        return solution

    # this is only if puzzle is broken and couldn't be forced
    print ("The puzzle appears to be broken")
    return s


# Main Solver
#############
def solve(original_puzzle, verbose):

    report = [0]*2

    puzzle = pencil_in_numbers(original_puzzle)
    solved = n_solved(puzzle)
    to_remove = n_to_remove(puzzle)
    if verbose:
        print ("Initial puzzle: complete cells", solved, "/81. Candidates to remove:", to_remove)

    t = time.time()

    # Control how solver goes thorugh metods:
    # False - go back to previous method if the next one yeld results
    # True - try all methods one by one and then go back
    all_at_once = False

    while to_remove != 0:
        r_step = 0
        r0 = simple_elimination(puzzle)
        report[0] += r0
        r_step += r0
        


        # check state
        solved = n_solved(puzzle)
        to_remove = n_to_remove(puzzle)

        # Nothing helped, logic failed
        if r_step == 0:
            break

    #print_sudoku(puzzle)
    if verbose:
        print ("Solved with logic: number of complete cells", solved, "/81. Candidates to remove:", to_remove)
        print ("Logic part took:", time.time() - t)

    if to_remove > 0:
        for_brute = n_to_remove(puzzle)
        puzzle = brute_force(puzzle, verbose)
        report[1] += for_brute

    # Report:
    legend = [
            'Simple elimination',

            'Backtracking']
    if verbose:
        print ("Methods used:")
        for i in range(len(legend)):
            print ("\t", i, legend[i], ":", report[i])
    return puzzle


# Intereface to convert line format to internal format and back
############################################################
def line_from_solution(sol):
    out = ""
    for a in sol:
        for b in a:
            out += str(b[0])
    return out


def solve_from_line(line, verbose=False):
    s_str = ""
    raw_s = line[0:81]
    for ch in raw_s:
        s_str += ch + " "
    s_np1 = np.fromstring(s_str, dtype=int, count=-1, sep=' ')
    s_np = np.reshape(s_np1, (9, 9))
    return line_from_solution(solve(s_np, verbose))             



# Short demo solving of a puzzle
#################################
if __name__ == "__main__":

    print ("Sudoku Solver Demo")

    # Easy and Medium puzzles: courtesy of Sudoku Universe Game]
    # Difficult Named puzzles: courtesy of sudokuwiki.org


    puzzles = [

("Medium",
'100070009008096300050000020010000000940060072000000040030000080004720100200050003'
)
    ]

    for puzzleName, puzzle in puzzles:
        print ("Puzzle", puzzleName)
        print (puzzle)
        solution = solve_from_line(puzzle, verbose=True)
        print (solution)
        print ("="*80)
