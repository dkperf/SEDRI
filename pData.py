
#
#  Script to retrieve solar Panel data from SolarEdge servers
#

import requests
from datetime import datetime
import json, pytz
import os

SOLAREDGE_USER    = "solarid@gmail.com" # REPLACE with your solaredge web username
SOLAREDGE_PASS    = "password"          # REPLACE with your solaredge web password
SOLAREDGE_SITE_ID = "4461429"           # REPLACE with your solaredge site id

login_url  = "https://monitoring.solaredge.com/solaredge-apigw/api/login"
panels_url = "https://monitoring.solaredge.com/solaredge-web/p/playbackData"

DAILY_DATA   = "4"
WEEKLY_DATA  = "5"
MONTHLY_DATA = "6"    # returns empty sets for me

DATA_TYPE = WEEKLY_DATA

#  PanelMap is a Table for conversion from SolarEdge panel ID ("key") to Our Panel ID's
#  When the data comes from Solaredge it has "optimizer ID" and the "panel Wattage"
#  for each 15 min period.  This "optimizer ID" means nothing to us.  We would like
#  to map the "optimizer ID" to some useful identifier for a specific panel on our roof.
#  Only way I could figure to get this matchup is ( probably a better way):
#  To get this "optimizer ID" to YOUR panel key match up set 'makingPanelMap' to True.
#  Run this script, then find 12 noon ( or any time ) in the output data file.
#  Now go to the solaredge monitoring->Layout->Physical layout.
#  This assumes that you have setup your Solaredge Physical layout information.
#  "Show playback" and select "weekly" then move playback cursor to same 
#  date and time as in data file.   Now match watts in data file (number on the right)
#  to value shown on solar panel on layout screen to  get your panel # (id). 
#  Now you have the SolarEdge Panel ID ( number in the data file on the left)
#  matched to the id on the your panel optimizer label.
#  Then put those entries here in "PanelMap".  

#  Once completed set 'makingPanelMap' to False.

makingPanelMap = False;  # True

PanelMap = {
# "solaredgeID": "yourPanelName",

#  "152070423": "P01",
#  "137573352": "P02",
#  "137573478": "P03",
#  "124567884": "P04",
#  "143872151": "P05",
#  "112349835": "P06",
#  "123456789": "P07",
}

NumPanels=len( PanelMap )

_lastZeroBuf = ''
_lastTot     = 1


#-----------------------------------------------------
#-----------------------------------------------------
def dumpTimeData( timeStamp, pKeys, panelData, fHandle ):

   buf = timeStamp +  '\n';
   for pId in pKeys:
      val = float(panelData[pId])
      buf += '  "' + pId + '": "' + str(val) + '",\n';

   fHandle.write( buf )


#-----------------------------------------------------
#-----------------------------------------------------
def writePanelData( timeStamp, pKeys, panelData, fHandle ):

   global _lastTot, _lastZeroBuf  

   #  Only entries with a match in PanelMap will be in panelData[]
   if ( len( pKeys ) != NumPanels ): 
      #todo:  figure out missing panel data column and add as ""
      print( "ERROR v xi_ ", len( pKeys ), "   ", pKeys )

   tot = 0;
   buf = timeStamp

   for pId in pKeys:
      val = float(panelData[pId])
      tot += val
      buf += ', ' + str(val)

   buf += '\n'

   if ( tot == 0 ):        # this tot & zeroBuf stuff is to remove
      _lastZeroBuf = buf   # excess lines with all zeros.
                           # we want an all zero line pre and post the non-zero lines

   if ( tot != 0 and _lastTot == 0 ):
      if ( len(_lastZeroBuf) > 10 ):
         fHandle.write( _lastZeroBuf )
      _lastZeroBuf = ''

   if ( tot != 0 or ( tot == 0 and _lastTot != 0 )):
      fHandle.write( buf )

   _lastTot = tot




#-------------------------------------------------------------------
#  This function attempts to request solaredge playback
#  data in JSON format for the given time frame.
#  Playback data is used to extract per panel (optimizer) 15 minute data.
#-------------------------------------------------------------------
def requestPanelData():

   session = requests.session()

   panels = session.post(login_url, headers = {"Content-Type": "application/x-www-form-urlencoded"}, \
      data={"j_username": SOLAREDGE_USER, "j_password": SOLAREDGE_PASS})

   if panels.status_code != 200:   
      print( "SolarEdge login failed - status: " + panels.status_code )
      return {}

   panels = session.post(panels_url, headers = {"Content-Type": "application/x-www-form-urlencoded", \
      "X-CSRF-TOKEN": session.cookies["CSRF-TOKEN"]}, \
      data={"fieldId": SOLAREDGE_SITE_ID, "timeUnit": DATA_TYPE})

   # massage returned  content to our liking.

   panelJson = panels.content.decode("utf-8").replace('\'', '"').replace('fieldDataArray', \
      '"fldDataArray"').replace('key', '"key"').replace('value', '"value"')

   panelJson = panelJson.replace('timeUnit', '"timeUnit"').replace('fieldData', \
      '"fieldData"').replace('reportersData', '"reportersData"')

   # convert solaredge JSON to python Dictionary format.
   return json.loads( panelJson )




#-----------------------------------------------------
#            Main
#-----------------------------------------------------
def main():

   panelDict = requestPanelData();

   # did panel data request fail?
   if len( panelDict ) == 0:
      return 2 

   #  request returned is from a JSON similar to:
   """
   {
     "timeUnit": "WEEK",
     "fieldData": { ... }
     "fldDataArray": [...]
     "reportersData": {
       "Tue May 14 11:15:00 GMT 2022": { 
         "19AA7C": [ { "key": "167234117", "value": "2937.91" } ],  
         "0C25F3": [ 
             { "key": "123492291", "value": "199.26" },
             { "key": "123494034", "value": "199.79" },
             { "key": "134529883", "value": "205.0" },
             ...
           ] },
        ...
      }
   }
   """

   #print ( json.dumps( panelDict ))     # dump panel data dictionary as JSON string.


   #  Create a data file for each unique day there is data for in Dictionary

   # header for data file(s)
   panelTags = "# Date_Time, " + str( sorted( list( PanelMap.values()) )) + '\n'
   panelTags = panelTags.replace( '[', '' ).replace( ']', '' ).replace( "'", '' )

   now = datetime.now()
   today = now.strftime("%Y_%m_%d")

   fHandle = open( __file__ )      # we need an empty file handle
   fHandle.close()

   fmt = '%m-%d-%Y %H:%M:%S'       # format for data file timeStamp

   panelData = {}
   workDayStr = warned = ''

   # for every Time Stamp entry in "reportersData" 
   # parse time stamp and log panel data to data file.

   for date_str in panelDict["reportersData"].keys():
      date = datetime.strptime(date_str, '%a %b %d %H:%M:%S GMT %Y')
      newDate = pytz.timezone('PST8PDT').localize(date)
      dayStr = newDate.strftime('%Y_%m_%d')              # 2021_04_20

      if ( dayStr == today ):  # don't want partial days.  Could add time chk here
         continue

      if ( dayStr != workDayStr ):
         if ( warned == dayStr ):
            continue

         fName = "data/" + dayStr + '_PanelData'
         if ( makingPanelMap == False and os.path.exists( fName )):
            print( "'" + fName + "' already exists; skipping data write" )
            warned =dayStr;
            continue

         if ( fHandle.closed == False ):          # switched to new date
            fHandle.close()

         _lastZeroBuf = ''
         _lastTot = 1
         workDayStr = dayStr
      
         fHandle = open( fName, 'w' )
         if ( fHandle == False ):         # ouch ERROR 
            continue

         print( 'Saving data for %s ...' % dayStr )
         fHandle.write( panelTags )    # header info in data file

      panelData.clear()
      for sid in panelDict["reportersData"][date_str].keys():
         for entry in panelDict["reportersData"][date_str][sid]:
            pId = PanelMap.get( entry["key"], "Unk" )   # Get our panel ID for SE key
            if pId != "Unk":
                panelData[pId] = entry["value"].replace(",", "")
            elif makingPanelMap:
                panelData[entry["key"]] = entry["value"].replace(",", "")
                
      # want panel data values sorted by our panel ID's when saved in data file.
      pKeys = sorted( list( panelData.keys() ))

      timeStamp = newDate.strftime(fmt) 

      if  makingPanelMap:   # this should only be used during setup...  
         dumpTimeData( timeStamp, pKeys, panelData, fHandle )
      else:
         writePanelData( timeStamp, pKeys, panelData, fHandle )

   if ( fHandle.closed == False ):         # clean up
      fHandle.close()

   return 0



#------------------------------------------------------------
#   if standalone  execution
#------------------------------------------------------------
if __name__ == '__main__':
   import sys
   sys.exit(main())



