#!/usr/bin/env python
import os
import sys
import urllib2 as request
import json
import datetime
import sys
#
# Define Functions Used
#
def GetEventList(START,END):
	# Create file name; ereyesterday
	#string containing our base query (hardcoded magnitude, order, and format parameters)
	BASE = 'http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=%s&endtime=%s&minmag=5.0&maxmag=9.9&orderby=time-asc'
#	#create datetime objects for the initial start and end dates
	start = START
	stop = False
	EventID = []
	while not stop:
	       	#add 365 days to current start
	        end = start + datetime.timedelta(days=365)
	       	if end > END:
	            end = END
	       	    stop = True  #stop if we're at today
	        #format the start/end times into a format Comcat API likes
	        startstr = start.strftime('%Y-%m-%dT%H:%M:%S')
	        endstr = end.strftime('%Y-%m-%dT%H:%M:%S')
	        #create a search url for this time period
	       	url = BASE % (startstr,endstr)
	#	print url
	        #open the url as a file-like object, read the data, decode as ASCII
	       	fh = request.urlopen(url)
	        data = fh.read().decode('utf-8')
	       	fh.close()
	        #turn json string into data structure
	       	jdict = json.loads(data)
	       	#loop over earthquakes, grab ID, print to stdout
	        for feature in jdict['features']:
		    EventID.append(feature['id'])
	        start = end
	return EventID
#################################################
# File Paths
#
DayConducted = datetime.date.today()
Yesterday = DayConducted - datetime.timedelta(days=1)
# Get file path and name from yesterday's QC
# This is where yesterday's count of 3 days ago and today's count of 2 days ago will go
YDay_fpath = '/Users/mrperry/autoComCatQC/EventIDQC/OUTPUT/'+Yesterday.strftime('%Y%m%d')+'/'
# This is where today count of 2 days ago will go
TDay_fpath = '/Users/mrperry/autoComCatQC/EventIDQC/OUTPUT/'+DayConducted.strftime('%Y%m%d')+'/'
#################################################
# Standard Variables
START=datetime.date(1900,1,1)
ReCountEnd = datetime.date.today() - datetime.timedelta(days=3)
NewCountEnd = datetime.date.today() - datetime.timedelta(days=2)
orig_stdout = sys.stdout
#################################################
# Get -3 days ago file name
#
Old_data = datetime.date.today() - datetime.timedelta(days=3)
old_file = YDay_fpath+Old_data.strftime('%Y%m%d')+'_1.eventID'
with open(old_file) as f:
	OldEventIDs = f.readlines()
# Remove EOL
OldEventIDs = map(lambda s: s.strip(), OldEventIDs)
###################################################
# Redo the -3 days ago Event List
#
EventID = GetEventList(START,ReCountEnd)
#
# Events Missing
#
New_Event = [New for New in EventID if New not in OldEventIDs]
Missing_Event = [Miss for Miss in OldEventIDs if Miss not in EventID]
###################################################
# Get the New Event List
NewEventID = GetEventList(START,NewCountEnd)
#################################################
# Print and Save output
#
# Save count from 3 days ago in the directory from yesterday
#
f = file(YDay_fpath+Old_data.strftime('%Y%m%d')+'_2.eventID','w')
sys.stdout = f
for ii in range(len(EventID)):
	print(EventID[ii])
sys.stdout = orig_stdout
f.close()
#
# Creat new directory and save today's count
#
if not os.path.exists(TDay_fpath):
	os.makedirs(TDay_fpath)
	f = file(TDay_fpath+NewCountEnd.strftime('%Y%m%d')+'_1.eventID','w')
	sys.stdout = f
	for ii in range(len(NewEventID)):
		print(NewEventID[ii])
	sys.stdout = orig_stdout
	f.close()
#
# Print Log
#
print(' --- Difference in Event Lists as of %s ---'%datetime.date.today())
if len(New_Event)>0:
	print(' --- Added Events --- ')
	for ii in range(len(New_Event)):
		print('%s'%New_Event[ii])
	print('\n')
if len(Missing_Event)>0:
	print(' --- Missing Events --- ')
	for ii in range(len(Missing_Event)):
		print('%s'%Missing_Event[ii])
if (len(New_Event)==0) & (len(Missing_Event)==0):
	print('No Change Detected')
