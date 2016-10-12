#!/usr/bin/env python

import qradarapi
from time import sleep
from geoip import geolite2
import datetime as DT
import argparse

aparse = argparse.ArgumentParser()
aparse.add_argument("username", help="Username to search (passed into a LIKE function)")
aparse.add_argument("sincedays", help="Number of days to search back")
args = aparse.parse_args()

cobj = qradarapi.connect()

searchstring = """SELECT * FROM events WHERE userName LIKE '{}%' AND qid = 6501068 
	ORDER BY startTime DESC LAST {} days""".format(args.username, args.sincedays)
r = cobj.start_search(searchstring)

sid = r.json()['search_id']
scomplete = False
while not(scomplete):
	r = cobj.get_search(sid)
	if r.json()['status'] == "EXECUTE":
		sleep(3)
	else:
		scomplete = True
# This is not to say that the search completed successfully, so some rudimentary checking		
if r.json()['status'] == "COMPLETED":
	r = cobj.get_search_results(sid)
	l = r.json()
	for k in l['events']:
		ts = DT.datetime.utcfromtimestamp( int(k['starttime']) / 1000 ).isoformat()
		gip = geolite2.lookup(k['sourceip'])
		if gip is not None:
			ccode = "{} {}".format(gip.country,gip.continent)
		else:
			ccode = "geoip not found"
		print "{}  {}\t{}\t{}".format(ts,k['sourceip'], ccode, k['username'])
else:
	print "Something went wrong, search {} did not complete:\n{}".format(sid,r.json['status'])
