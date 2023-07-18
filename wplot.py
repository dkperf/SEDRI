#
#  Plot Panel and Inverter Data 
#
from datetime import datetime, timedelta
import os
import subprocess

# start x days ago
numDays=30
startDay = datetime.now() - timedelta(days=numDays)

dataFiles=['pdata',       'idata',         'wdata',       'tdata',       'thdata'      ]
fileId =  ['_PanelData',  '_InverterData', '_PowerData',  '_TempData',   '_HrTempData' ]

# append all matching file to 'dataFile'
def createDataFile( dataFile, in_File_Post, startDay, numDays ):

   Day = startDay

   #   os.remove( dataFile )
   with open( dataFile, 'wb' ) as fd :

      print( 'Appending ', numDays, ' days of  %-16.16s data to  %s ...' % (in_File_Post, dataFile ))
      for i in range(numDays):

         dayStr = Day.strftime("%Y_%m_%d")
         Day += timedelta(days=1)

         fName = "data/" + dayStr + in_File_Post

         if ( os.path.exists( fName ) == False ):
            continue

#         print( 'Appending data from  %s ...' % fName )

         with open( fName, "rb") as fi:
            while True:
               data = fi.read( 65536 )
               if not data :
                  break
               fd.write( data )


# Main

for idx, fname in enumerate( dataFiles ):
   createDataFile( 'wplot_'+fname,  fileId[idx],  startDay, numDays )


subprocess.Popen( ['wplot', 'solar.dpt' ] )


