import sys
from SudokuAlgorithm import *

sudoku = Sudoku(sys.argv[1])

if sudoku.solve():
    sudoku.res_display()
else:
    print("No Solution")
