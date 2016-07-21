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
path_PROD01_RawCounts = '/Users/mrperry/autoComCatQC/OUTPUT/PROD01/RawCounts/'
path_PROD02_RawCounts = '/Users/mrperry/autoComCatQC/OUTPUT/PROD02/RawCounts/'
path_RawDiff = '/Users/mrperry/autoComCatQC/OUTPUT/'
path_WorkSpace = '/Users/mrperry/autoComCatQC/'
#
# Declare constants
#
firstYear = 1900
lastYear = 2015 #dt.date.today().year
stepYear = 1
Years = np.arange(firstYear, lastYear+1,1) 
firstMag = 0.0
lastMag = 9.0
stepMag = 0.9
Mags = np.arange(firstMag, lastMag+1,1)
#
# Get PROD Count Files from today
#
TD = dt.date.today()
YR = str(TD.year)
MN = str(TD.month)
DY = str(TD.day)
ED = str('.csv')
fname = YR+MN+DY+ED
#
# Get other PROD-files from today name from yesterday
#
PROD01_fname = path_PROD01_RawCounts+fname
if (os.path.isfile(PROD01_fname)):
	PROD01_Counts = np.genfromtxt(PROD01_fname, delimiter=',')
	PROD01_Counts = np.array(PROD01_Counts)
PROD02_fname = path_PROD02_RawCounts+fname
if (os.path.isfile(PROD02_fname)):
	PROD02_Counts = np.genfromtxt(PROD02_fname, delimiter=',')
	PROD02_Counts = np.array(PROD02_Counts)
#
# Get Difference Between two production systems
if (np.size(PROD01_Counts) == np.size(PROD02_Counts)):
	diff_Counts = np.subtract(PROD01_Counts,PROD02_Counts)
	if ( np.any(np.absolute(diff_Counts) >= 1) ):
		print "A change has been detected"
		change_loc = np.where(np.absolute(diff_Counts) >= 1)
		output_str = []
		for ii in range(len(change_loc[0])):
			output_str.append('The event count for M%s in %s is different between PROD01 and PROD02 by %d' %
				(Mags[change_loc[0][ii]], Years[change_loc[0][ii]], diff_Counts[change_loc[0][ii],change_loc[1][ii]]))	
			print output_str[ii]
	else:
		print "No change detected"
	DOP = pandas.DataFrame(diff_Counts,Mags,Years)
	dname = fname[:-4]+'diff.csv'
	DOP.to_csv(path_WorkSpace+dname,sep=',')
else:
	print "Something changed and arrays are different sizes"
	sys.exit()
et=time.time()
print et-st
sys.exit()
