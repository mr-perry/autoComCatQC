#!/Users/mrperry/anaconda/bin/python
# This code will create an event count table for PROD01
#
import sys
import datetime as dt
import time
import os
import math
import numpy as np
import urllib2 as urll
import pandas
import smtplib
#
# Define Paths
#
st = time.time()
path_FormatOutput = '/Users/mrperry/autoComCatQC/OUTPUT/PROD01/FormatOutput/'
path_RawCounts = '/Users/mrperry/autoComCatQC/OUTPUT/PROD01/RawCounts/'
path_RawDiff = '/Users/mrperry/autoComCatQC/OUTPUT/PROD01/RawDiff/'
path_WorkSpace = '/Users/mrperry/autoComCatQC/'
#
# Declare constants
#
firstYear = 1900
lastYear = 2015 #dt.date.today().year
stepYear = 1
binsYear = (lastYear - firstYear)+1
sizeYears = binsYear
firstMag = 0.0
lastMag = 9.0
stepMag = 0.9
binsMag = ((lastMag - firstMag)+1);
sizeMags = binsMag*2
sizeCounts = binsYear*binsMag
#
# Contstruct File name
#
TD = dt.date.today()
YR = str(TD.year)
MN = str(TD.month)
DY = str(TD.day)
ED = str('.csv')
fname = YR+MN+DY+ED
#
# Get file name from yesterday
#
YD = TD - dt.timedelta(days=1)
YYR = str(YD.year)
YMN = str(YD.month)
YDY = str(YD.day)
y_fname = path_RawCounts+YYR+YMN+YDY+ED
if (os.path.isfile(y_fname)):
	y_Counts = np.genfromtxt(y_fname, delimiter=',')
#
#
# Initialize Array Sizes
#
Years = np.arange(sizeYears)
Mags = np.arange(sizeMags).reshape(binsMag,2)
Counts = np.arange(sizeCounts).reshape(binsMag,binsYear)
stringYears = [None]*int(binsYear) 
stringMags = [None]*int(binsMag)
#
# Create year vector 
#
countYear = 0
startYear = firstYear
while ( startYear <= lastYear ):
	Years[countYear] = startYear
	stringYears[countYear] = "%d" % (Years[countYear])
	startYear = startYear + 1
	countYear = countYear + 1
#
# Create Magnitude Vector
#
countMag = 0
startMag = firstMag
while ( startMag <= lastMag ):
	endMag = startMag + stepMag
	if ( endMag > lastMag ):
		endMag = 0
	Mags[countMag,0] = startMag
	Mags[countMag,1] = endMag
	if ( endMag != 0 ):
		stringMags[countMag] = "%d-%1.1f" % (Mags[countMag,0], Mags[countMag,1])
	else:
		stringMags[countMag] = "> %d" % (Mags[countMag,0])
	startMag = startMag + 1
	countMag = countMag + 1
#
# Back counters up by one and flip Mags
#
countMag = countMag - 1
countYear = countYear - 1
Mags = np.flipud(Mags)
stringMags = stringMags[::-1]
#
# Get Counts
#
ii = 0
while ( ii <= countYear ):
	jj = 0 
	while ( jj <= countMag ):
		if ( jj != 0 ):
			query="http://prod01-earthquake.cr.usgs.gov/fdsnws/event/1/count?starttime=%d-01-01T00:00:00&endtime=%d-12-31T23:59:59&minmagnitude=%1.1f&maxmagnitude=%1.1f"\
					% (Years[ii], Years[ii],Mags[jj,0],Mags[jj,1])
#			print query
		else:
			query="http://prod01-earthquake.cr.usgs.gov/fdsnws/event/1/count?starttime=%d-01-01T00:00:00&endtime=%d-12-31T23:59:59&minmagnitude=%1.1f"\
					% (Years[ii], Years[ii],Mags[jj,0])
#			print query
		req = urll.Request(query)
		response = urll.urlopen(req)
		the_page = response.read()
		Counts[jj,ii] = int(the_page)
		jj = jj + 1
	ii = ii + 1
#
# Load count information from yesterday
#
if 'y_Counts' in locals(): 
	if (np.size(Counts) == np.size(y_Counts)):
		diff_Counts = np.subtract(Counts,y_Counts)
		if ( np.any(np.absolute(diff_Counts) >= 1) ):
			print "A change has been detected"
			change_loc = np.where(np.absolute(diff_Counts) >= 1)
			output_str = []
			for ii in range(len(change_loc[0])):
				output_str.append('The event count for M%s in %s has changed by %d' %
					(stringMags[change_loc[0][ii]], Years[change_loc[1][ii]], diff_Counts[change_loc[0][ii],change_loc[1][ii]]))	
				print output_str[ii]
		else:
			print "No change detected"
		DOP = pandas.DataFrame(diff_Counts, stringMags, stringYears)
		#
		# Today's Count
		np.savetxt(path_WorkSpace+fname,Counts, delimiter=',') # Raw Counts
		os.rename(path_WorkSpace+fname,path_RawCounts+fname)
		#
		# Formatted Data Frame with Labels
		OP = pandas.DataFrame(Counts, stringMags, stringYears)
		tname = fname[:-4]+'output.csv'
		OP.to_csv(path_WorkSpace+tname,sep=',')
		os.rename(path_WorkSpace+tname,path_FormatOutput+tname)
		#
		# Move Difference File
		#
		dname = fname[:-4]+'diff.csv'
		DOP.to_csv(path_WorkSpace+dname,sep=',')
		os.rename(path_WorkSpace+dname,path_RawDiff+dname)
	else:
		print "Something changed and arrays are different sizes"
		np.savetxt(path_WorkSpace+fname,Counts, delimiter=',') # Raw Counts
		os.rename(path_WorkSpace+fname,path_RawCounts+fname)
		#
		# Formatted Data Frame with Labels
		#
		OP = pandas.DataFrame(Counts, stringMags, stringYears)
		tname = fname[:-4]+'output.csv'
		OP.to_csv(path_WorkSpace+tname,sep=',')
		os.rename(path_WorkSpace+tname,path_FormatOutput+tname)
		print "Exiting..."
		sys.exit()
else:
	#
	# Produce outputs and move them
	#
	# Today's Count
	np.savetxt(path_WorkSpace+fname,Counts, delimiter=',') # Raw Counts
	os.rename(path_WorkSpace+fname,path_RawCounts+fname)
	#
	# Formatted Data Frame with Labels
	OP = pandas.DataFrame(Counts, stringMags, stringYears)
	tname = fname[:-4]+'output.csv'
	OP.to_csv(path_WorkSpace+tname,sep=',')
	os.rename(path_WorkSpace+tname,path_FormatOutput+tname)
et=time.time()
print et-st
sys.exit()
