from os import listdir
from os.path import isfile, join

def all_lines(directory):
	onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
	indx1 = 0
	for f in onlyfiles:
		lines = [line.rstrip('\n') for line in open(f)]
		for indx2,line in enumerate(lines):
			yield '[' + str(indx1) + ']' + '[' + str(indx2) + ']' + line

for line in all_lines('/Users/ork/Workspace/geoip/test/'):
	print line