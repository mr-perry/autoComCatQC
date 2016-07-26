#!/Users/mrperry/anaconda/bin/python
# This code will create an event count table for ComCat
#
import sys
import datetime as dt
import os
import numpy as np
import urllib2 as urll
import pandas as pd
#
# Define Paths
#
path_RawCounts = '/Users/mrperry/autoComCatQC/M6+_CountCheck/Output/RawCounts/'
path_RawDiff = '/Users/mrperry/autoComCatQC/M6+_CountCheck/Output/RawDiff/'
path_WorkSpace = '/Users/mrperry/autoComCatQC/M6+_CountCheck'
#
# Get file name from 3-days ago (yesterday's QC) 
#
three_days_ago = dt.date.today() - dt.timedelta(days=1)
YYR = str(three_days_ago.year)
YMN = str(three_days_ago.month)
YDY = str(three_days_ago.day)
y_fname = path_RawCounts+YYR+YMN+YDY+ED
if (os.path.isfile(y_fname)):
	y_Counts = pd.read_csv(y_fname, delimiter=',', index_col=0)
	y_Counts.set_index(pd.DatetimeIndex(y_Counts.index), inplace=True)
#
# Get the date from 2 days ago AKA ereyesterday
#
ereyesterday = dt.date.today() - dt.timedelta(days=2)
#
# First of the year (will have to figure out what I want to do with QC for 1 Jan though...)
# 
first_of_year = dt.date(ereyesterday.year,01,01)
# Number of days since the beginning of the year (does not include current day so add 1)
D = (ereyesterday - first_of_year).days+1
# Make date vector
Date_array = np.array([first_of_year + dt.timedelta(days=ii) for ii in xrange(D)])
zero_array = np.zeros(len(Date_array))
# Magnitude labels, numbers, and dictionary (to create pandas DF)
Mags = np.array([6.0,6.5,7.0,7.5,8.0,8.5,9.0])
Mag_labels =['M6.0','M6.5','M7.0','M7.5','M8.0','M8.5','M9.0']
Mag_array = {'M6.0': zero_array, 'M6.5': zero_array, 'M7.0': zero_array, 'M7.5': zero_array, 
		'M8.0': zero_array, 'M8.5': zero_array, 'M9.0': zero_array}
# Create Pandas DF: Rows -- Dates, Columns -- Magnitude
Count_DF = pd.DataFrame(data=Mag_array,index=Date_array)
Count_DF.set_index(pd.DatetimeIndex(Count_DF.index), inplace=True)
#
# Construct File name
#
YR = str(ereyesterday.year)
MN = str(ereyesterday.month)
DY = str(ereyesterday.day)
ED = str('.csv')
fname = YR+MN+DY+ED
#
# Get Counts
#
for ii in range(len(Count_DF)):
	for jj in range(len(Mags)):
		if Mags[jj]!=9.0:
			query = "http://earthquake.usgs.gov/fdsnws/event/1/count?starttime=%sT00:00:00&endtime=%sT23:59:59.999&minmagnitude=%1.1f&maxmagnitude=%1.1f"\
			%(Count_DF.index[ii].strftime('%Y-%m-%d'),Count_DF.index[ii].strftime('%Y-%m-%d'),Mags[jj],Mags[jj]+.4999)
		else:
			query = "http://earthquake.usgs.gov/fdsnws/event/1/count?starttime=%sT00:00:00&endtime=%sT23:59:59.999&minmagnitude=%1.1f"\
                        %(Count_DF.index[ii].strftime('%Y-%m-%d'),Count_DF.index[ii].strftime('%Y-%m-%d'),Mags[jj])
		print query
		req = urll.Request(query)
		response = urll.urlopen(req)
		the_page = response.read()
		Count_DF[Mag_labels[jj]][ii] = int(the_page)
#
# Load count information from yesterday
#
if 'y_Counts' in locals(): 
	#
	# -3 Daily count DF will be 1-row short of -2 Daily Count 
	#
	Counts = Count_DF.head(len(Count_DF)-1)
	#
	# Check their sizes, then subtract -3 daily from -2 daily
	# 
	if (np.size(Counts) == np.size(y_Counts)):
		diff_Counts = Counts - y_Counts
		if ( np.any(np.absolute(diff_Counts) > 0) ):
			print "A change has been detected"
			change_loc = np.where(np.absolute(diff_Counts) > 0)
			output_str = []
			for ii in range(len(change_loc[0])):
				output_str.append('The event count for %s on %s has changed by %d' % 
						(Mag_labels[change_loc[1][ii]],diff_Counts.index[change_loc[0][ii]].strftime('%Y-%m-%d'),diff_Counts[Mag_labels[change_loc[1][ii]]][change_loc[0][ii]]))
				print output_str[ii]
		else:
			print "No change detected"
		#
		# Today's Count
		#
		Count_DF.to_csv(fname)
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
sys.exit()
