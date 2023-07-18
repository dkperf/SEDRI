#
#  Get  Inverter Daily Total Power (Watt Hours) Data from SolarEdge  servers 
#
import requests
from datetime import datetime, timedelta
import json
import os

SE_SITE_ID         = "7423235"      # REPLACE with your  solaredge site id
SE_SITE_INVERTERID = "720131E7-BD"  # REPLACE with your  solaredge inverter serial #
ApiKey             = "AYU3X3JWHVQYVV3ANFR4347C661J2925"  # REPLACE with your solaredge API key


#  total power generated per day by inverter
power_url  = "https://monitoringapi.solaredge.com/site/"+SE_SITE_ID
power_url += "/energy?api_key="+ApiKey
power_url += "&timeUnit=DAY"

#returns 
"""
{
  "energy": {
    "timeUnit": "DAY",
    "unit": "Wh",
    "measuredBy": "INVERTER",
    "values": [
      {
        "date": "2023-04-20 00:00:00",
        "value": 26881
      }, ...

"""

# start x days ago
numDays=15
Day = datetime.now() - timedelta(days=numDays)

headerTags = '#  DateTime, Power(Wh) \n'


for i in range(numDays):

   dayStr   = Day.strftime("%Y_%m_%d")
   solStr   = Day.strftime("%Y-%m-%d")
   fileDate = Day.strftime("%m-%d-%Y")
   Day += timedelta(days=1)

   fName = "data/" + dayStr + '_PowerData'
   if ( os.path.exists( fName )):
      print( "'" + fName + "' already exists; skipping data write" )
      continue

   url  = power_url + ( '&startDate=%s&endDate=%s' % (solStr, solStr) )

   print( 'Getting data for %s ...' % solStr )

   r = requests.get( url )
   if ( r.status_code != 200 ):
      print( 'ERROR url failed: %s' % url )
      continue

   # convert solaredge JSON to python Dictionary format.
   iDat = json.loads( r.content.decode("utf-8") )

   # create file with name "YYYY_MM_DD_PowerData"
   fHandle = open( fName, 'w' )
   if ( fHandle == False ):         # ouch ERROR 
      continue

   fHandle.write( headerTags )    # header info in data file

   for p in iDat['energy']['values']:

      Power    =  float( p['value'] ) 
      timeStamp = str  ( p['date' ] )      #  'YYYY-mm-dd HH:MM:SS'

      idate = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
      ts  = idate.strftime('%m-%d-%Y')  
      ts += ' 23:00:00'

      fHandle.write( ts + ', ' + ( "%.2f " % Power ) + '\n' )

   fHandle.close()


