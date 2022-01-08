#!/usr/bin/python3
import sys, os

CGREEN = '\33[92m'
CNORMAL = '\33[0m'

for i in range(1, 9):
	for j in range(1, 3):
		p = "./testcase/test_data/"
		f = "0" + str(i) + "_" + str(j) + ".lsp"
		cmd = "python3 " + sys.argv[1] +" < " + p + f
		print(CGREEN, "test input ", f, CNORMAL)
		os.system(cmd)



