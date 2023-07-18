#
#  Get  Inverter Data from SolarEdge  servers 
#  Gets Timestamp, total ActivePower, dc Voltage, ac Current, temperature, Mode 
#  which the Inverter sends out every few minutes.
#
import requests
from datetime import datetime, timedelta
import json 
import os

SE_SITE_ID         = "7423235"      # REPLACE with your  solaredge site id
SE_SITE_INVERTERID = "720131E7-BD"  # REPLACE with your  solaredge inverter serial #
ApiKey             = "AYU3X3JWHVQYVV3ANFR4347C661J2925"  # REPLACE with your solaredge API key

#  url to get inverter stats by minute..
inverter_url  = "https://monitoringapi.solaredge.com/equipment/"+SE_SITE_ID
inverter_url += "/" + SE_SITE_INVERTERID + "/data"

#  solaredge returns following:
"""
{
  "data": {
    "count": 167,
    "telemetries": [
      {
        "date": "2023-04-27 06:13:42",
        "totalActivePower": 0,
        "dcVoltage": 24.6349,
        "powerLimit": 0,
        "totalEnergy": 4464140,
        "temperature": 20.2829,
        "inverterMode": "THROTTLED",
        "operationMode": 0,
        "L1Data": {
          "acCurrent": 0,
          "acVoltage": 240.757,
          "acFrequency": 59.9968,
          "apparentPower": 0,
          "activePower": 0,
          "reactivePower": 0,
          "qRef": 0
        }
      }, ...
"""

# start x days ago
numDays=15
Day = datetime.now() - timedelta(days=numDays)

headerTags = '#  DateTime, totActivePower, dcVoltage, acCurrent, temp, Mode \n'

#  format and write buffer to file
def writeBuf( fh, ts, pw, volt, current, temp, mode ) :
   buf = ts + ', ' 
   buf += "%.2f, " % pw
   buf += "%.2f, " % volt
   buf += "%.2f, " % current
   buf += "%.1f, " % temp
   buf +=  mode
   buf += '\n'
   fh.write( buf )


for i in range(numDays):

   dayStr   = Day.strftime("%Y_%m_%d")
   solStr   = Day.strftime("%Y-%m-%d")
   fileDate = Day.strftime("%m-%d-%Y")
   Day += timedelta(days=1)

   fName = "data/" + dayStr + '_InverterData'
   if ( os.path.exists( fName )):
      print( "'" + fName + "' already exists; skipping data write" )
      continue

   url  = inverter_url + '?startTime=%s 03:00:00' % solStr
   url += '&endTime=%s 22:00:00&api_key=%s' % (solStr, ApiKey)

   print( 'Getting data for %s ...' % solStr )

   r = requests.get( url )
   if ( r.status_code != 200 ):
      print( 'ERROR url failed: %s' % url )
      continue

   # convert solaredge JSON to python Dictionary format.
   iDat = json.loads( (r.content.decode("utf-8")).replace( 'null', '0' ))

   # create file with name "YYYY_MM_DD_InverterData"
   fHandle = open( fName, 'w' )
   if ( fHandle == False ):         # ouch ERROR 
      continue

   fHandle.write( headerTags )    # header info in data file

   # for each 'data' 'telemetries' entry in Dictionary write an entry to data file.
   x = 0
   for p in iDat['data']['telemetries']:

      temp     = (float(p['temperature']) * 9/5) + 32
      Power    =  float( p['totalActivePower'] ) 
      DCvoltage=  float( p['dcVoltage'] ) 
      ACcurrent=  float( p['L1Data']['acCurrent'])   
      mode     =  p['inverterMode']

      timeStamp = str( p['date'] )      #  'YYYY-mm-dd HH:MM:SS'

      idate = datetime.strptime(timeStamp, '%Y-%m-%d %H:%M:%S')
      ts = idate.strftime('%m-%d-%Y %H:%M:%S')  

      if ( x == 0 ):      # add initial entry to data file with all 0's
         ts1 = (idate-timedelta(minutes=10)).strftime('%m-%d-%Y %H:%M:%S')  
         writeBuf( fHandle, ts1, 0, 0, 0, temp, mode )
         
      writeBuf( fHandle, ts, Power, DCvoltage, ACcurrent, temp, mode )
      x += 1

   # add last entry to data file with all 0's ; makes nice for graphs/plots
   ts1 = (idate+timedelta(minutes=10)).strftime('%m-%d-%Y %H:%M:%S')  
   writeBuf( fHandle, ts1, 0, 0, 0, temp, mode )
   fHandle.close()


