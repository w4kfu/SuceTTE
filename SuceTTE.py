import os
import sys

TEMPLATE="page.html"
OUT_DIR="out/"

def ProcessRootFolder(folder):
	if os.path.isdir(folder) == True:
		for root, subFolders, files in os.walk(folder):
			print "subFolders : ", subFolders
	else:
		print "Not a folder"

def main():
    if len(sys.argv) == 1:
        print "usage: SuceTTE <folder>"
    else:    
	print "Processing ", sys.argv[1], "..."
	ProcessRootFolder(sys.argv[1])

if __name__ == '__main__':
    if os.path.isfile("customize.py"):
        execfile("customize.py")
    main()
