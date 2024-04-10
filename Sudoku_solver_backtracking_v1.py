#Sudoku solver with back tracking

#NO OOPS CONCEPT HERE

import numpy as np
import sys

global grid
grid =np.array([[6,0,7,0,4,2,0,1,0],
                     [2,5,0,1,0,7,0,0,0],
                     [0,1,3,5,6,0,0,0,0],
                     [0,0,1,0,7,3,2,0,0],
                     [0,0,6,8,5,0,0,0,0],
                     [3,0,5,9,0,6,8,0,0],
                     [0,7,0,0,0,0,1,3,2],
                     [1,0,0,7,3,0,5,0,0],
                     [0,3,0,2,0,0,0,0,0]])




class CustomError(Exception):
    def __init__(self,msg="Break out"):
        self.msg=msg
    def __str__(self):
        return str(self.msg)



#print initialized cell_grid
"""
for i in cell_grid:
    for j in i:
       print(j,end=" ")
    print()
"""
def squ_index(row,col):
    r_mod=row//3
    c_mod=col//3
    return r_mod*3 + c_mod


def dict_initialize(grid):
    for i,rows in enumerate(grid):
        for j,val in enumerate(rows):
            #print(f"Curr Value at [{i}][{j}]={val}")
            row_dict[i].discard(val)
            #print(row_dict)
            #print()
            col_dict[j].discard(val)
            squ_dict[squ_index(i,j)].discard(val)
            
           


def possible_val(row,col):
    if grid[row][col] ==0:
        return row_dict[row] & col_dict[col] & squ_dict[squ_index(row,col)]
    return set()

#Not used in Code Yet
def ispossible(row,col,num):

    #Check if num already exists in row
    for i in range(9):
        if grid[row][i]==num:
            return False

    #Check if num already exists in col
    for i in range(9):
        if grid[i][col]==num:
            return False
    #These should now contain the row and col index
    #off the top left cell of whichever square they belong to
    row_mod=(row//3)*3
    col_mod=(col//3)*3
    #Check if num already exists in square
    for i in range(row_mod,row_mod+3):
        for j in range(col_mod,col_mod+3):
            if grid[i][j]==num:
                return False
    #assigning num to that grid location        
    #grid[row][col]=num
    return True



def solve():
    """ A recursive function that backtracks if a entered num is not possible
till it finds a solution"""
    global total
    
    for i in range(9):
        for j in range(9):
            if grid[i][j] ==0:        
                for num in possible_val(i,j):
 
                    if ispossible(i,j,num):
                        grid[i][j]=num
                        row_dict[i].discard(num)
                        col_dict[j].discard(num)
                        squ_dict[squ_index(i,j)].discard(num)

                        solve()
                        
                        grid[i][j]=0
                        row_dict[i].add(num)
                        col_dict[j].add(num)
                        squ_dict[squ_index(i,j)].add(num)


                        

                return
    print(grid)
    total+=1
    choice=input("Continue? [q/quit]")
    print()
    try:
        if choice.lower() in ['q','quit']:
            raise CustomError()
    except CustomError as e:
        print("Therefore number of Possible solutions so far:",total)
        
        sys.exit()
    return


#print initialized cell_grid

"""Checking if dictionaries got initialized
dict_initialize()


for i in grid:
    for j in i:
       print(j,end=" ")
    print()

print(row_dict)
"""


def main():
    #initializing dictionay for each row,col and square
    #With the key being their respective row/col/square index
    #and Value is a set of all possible values it could take
    #ie at the beginning all of them
    global row_dict,col_dict,squ_dict,total
    total=0
    row_dict={}
    col_dict={}
    squ_dict={}

    #Working way of initilizing
    num_set={1,2,3,4,5,6,7,8,9}


    for i in range(9):
        row_dict[i]=num_set.copy()
        col_dict[i]=num_set.copy()
        squ_dict[i]=num_set.copy()
            

    dict_initialize(grid)
    print("Solutions:\n")
    solve()
    print("Therefore Total number of Possible solutions:",total)


if (__name__ == "__main__"):
    main()




    
