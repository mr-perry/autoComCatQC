#!/Users/mrperry/anaconda/bin/python
# This code will create an event count table for ComCat
#
import sys
import datetime as dt
#from datetime import date
import os
import math
import numpy as np
import urllib2 as urll
import pandas
import smtplib
#
# Define Paths
#
path_FormatOutput = '/Users/mrperry/autoComCatQCoutput/FormatOutput/'
path_RawCounts = '/Users/mrperry/autoComCatQCoutput/RawCounts/'
path_RawDiff = '/Users/mrperry/autoComCatQCoutput/RawDiff/'
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
fname = path_RawCounts+YR+MN+DY+ED
if (os.path.isfile(fname)):
	Counts = np.genfromtxt(fname, delimiter=',')
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
	else:
		print "Something changed and arrays are different sizes"
		print "Exiting..."
		sys.exit()
else:
	sys.exit()
