#
#  Get  Location Daily Temperatures Data from weatherapi.com  servers 
#
#  Create two files per day.  One with hourly temperature data and one file with daily min,max.

import requests
from datetime import datetime, timedelta
import json
import os

#   http://api.weatherapi.com/v1/history.json?key=xxxxx&q=99999&dt=2023-04-01

ApiKey             = "782391abr19533902233783429a125" # REPLACE with your key
ZipCode            = "95974"                          # REPLACE with your area ID

#  weather data per day

weather_url  = "http://api.weatherapi.com/v1/history.json"
weather_url += "?key=" + ApiKey
weather_url += "&q="   + ZipCode

# JSON returned
"""
{
   "location": {
      "name": "town",
      "region": "state",
      "country": "USA",
      "tz_id": "America/Los_Angeles",
      "localtime_epoch": 1622351568,
      "localtime": "2023-04-02 19:32"
   },
   "forecast": {
      "forecastday": [
      {
         "date": "2023-04-01",
         "date_epoch": 1622019600,
         "day": {
            "maxtemp_c": 20.5,
            "maxtemp_f": 73.9,
            "mintemp_c": 10.1,
            "mintemp_f": 51.6,
            ... 
         }
      }
      ...
   }
}

"""

# start x days ago
numDays=10
Day = datetime.now() - timedelta(days=numDays)

DayHeaderTags = '#  DateTime, MaxTemp, MinTemp, AvgTemp, Precip, DayLightHrs  \n'
HrHeaderTags  = '#  DateTime, tempF, Humidity  \n'


#-----------------------------------------------------
#-----------------------------------------------------
def dumpDayTemps( fName, tDat, fileDate, hTags ):

   # create file with name "YYYY_MM_DD_xxxxxData"
   fHandle = open( fName, 'w' )
   if ( fHandle == False ):         # ouch ERROR 
      return;

   fHandle.write( hTags )    # header info in data file
  
#  'day': {'maxtemp_c': 32.1, 'maxtemp_f': 89.8, 'mintemp_c': 15.8, 'mintemp_f': 60.4, 
#          'avgtemp_c': 22.4, 'avgtemp_f': 72.3, 'maxwind_mph': 14.5, 'maxwind_kph': 23.4, 
#          'totalprecip_mm': 0.0, 'totalprecip_in': 0.0, 'avgvis_km': 10.0, 'avgvis_miles': 6.0, 
#          'avghumidity': 39.0, 'uv': 8.0, 
#          'condition': {'text': 'Sunny', 'icon': '...113.png', 'code': 1000}, 

   td    = tDat['forecast']['forecastday'][0]['day']

#  'astro': {'sunrise': '05:40 AM', 'sunset': '08:32 PM', 'moonrise': '05:44 AM', 
#            'moonset': '09:37 PM', 'moon_phase': 'New Moon', 'moon_illumination': '0'}, 
   aformat = '%H:%M %p'
   astro = tDat['forecast']['forecastday'][0]['astro']
   dayHrs = ((datetime.strptime( astro['sunset' ], aformat) + timedelta(hours=12)) - \
              datetime.strptime( astro['sunrise'], aformat)).total_seconds() / 3600

   ts = fileDate + ' 13:00:00'

   fHandle.write( ts + ', ' + \
       str( td['maxtemp_f'])      + ', ' + \
       str( td['mintemp_f'])      + ', ' + \
       str( td['avgtemp_f'])      + ', ' + \
       str( td['totalprecip_in']) + ', ' + \
          ( "%.2f " % (dayHrs) )  + '\n' )

   fHandle.close()


#-----------------------------------------------------
#-----------------------------------------------------
def dumpHrTemps( fName, tDat, hTags ):

   # create file with name "YYYY_MM_DD_xxxxxData"
   fHandle = open( fName, 'w' )
   if ( fHandle == False ):         # ouch ERROR 
      return;

   fHandle.write( hTags )    # header info in data file

#  "hour": [ { "time_epoch": 1688713200, "time": "2023-07-07 00:00", "temp_c": 15.9, 
#              "temp_f": 60.6, "wind_mph": 8.3, "humidity": 67, ... },  ... ]

   for hr in tDat['forecast']['forecastday'][0]['hour']:
      ts0 = datetime.strptime(hr['time'], '%Y-%m-%d %H:%M')
      ts = ts0.strftime('%m-%d-%Y_%H:%M:00')     

      fHandle.write( ts     + ', ' + \
       str( hr['temp_f'])   + ', ' + \
       str( hr['humidity']) + '\n' )

   fHandle.close()




#-----------------------------------------------------
#  Main 
#-----------------------------------------------------
for i in range(numDays):

   dayStr   = Day.strftime("%Y_%m_%d")
   solStr   = Day.strftime("%Y-%m-%d")
   fileDate = Day.strftime("%m-%d-%Y")
   Day += timedelta(days=1)

   fName = "data/" + dayStr + '_TempData'
   if ( os.path.exists( fName )):
      print( "'" + fName + "' already exists; skipping data write" )
      continue

   url  = weather_url + ( '&dt=%s' % (solStr) )

   print( 'Getting data for %s ...' % solStr )

   r = requests.get( url )
   if ( r.status_code != 200 ):
      print( 'ERROR url failed: %s' % url )
      continue

#   Dump JSON received
#   print  ( r.content.decode("utf-8") )

   # convert weatherapi JSON to python Dictionary format.
   tDat = json.loads( r.content.decode("utf-8") )

   dumpDayTemps ( fName, tDat, fileDate, DayHeaderTags )

   fName = "data/" + dayStr + '_HrTempData' 
   dumpHrTemps( fName, tDat, HrHeaderTags )


