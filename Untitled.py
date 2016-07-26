#!/usr/bin/env python

import urllib2 as request
import json
from datetime import datetime,timedelta
import sys

#string containing our base query (hardcoded magnitude, order, and format parameters)
BASE = 'http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=%s&endtime=%s&minmag=6.5&maxmag=9.9&orderby=time-asc'

if __name__ == '__main__':
    #create datetime objects for the initial start and end dates
    START = datetime(1950,1,1)
    END = datetime.utcnow()
    
    start = START
    stop = False
    while not stop:
        #add 700 days to current start
        end = start + timedelta(days=700)
        if end > END:
            end = END
            stop = True  #stop if we're at today

        #format the start/end times into a format Comcat API likes
        startstr = start.strftime('%Y-%m-%dT%H:%M:%S')
        endstr = end.strftime('%Y-%m-%dT%H:%M:%S')

        #write to stderr the time period we're searching
        sys.stderr.write('Searching catalog from %s to %s...\n' % (startstr,endstr))

        #create a search url for this time period
        url = BASE % (startstr,endstr)

        #open the url as a file-like object, read the data, decode as ASCII
        fh = request.urlopen(url)
        data = fh.read().decode('utf-8')
        fh.close()

        #turn json string into data structure
        jdict = json.loads(data)

        #loop over earthquakes, grab ID, print to stdout
        for feature in jdict['features']:
            print('%s' % feature['id'])
        start = end
