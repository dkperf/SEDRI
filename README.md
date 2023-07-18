# SEDRI
# SolarEdge Data Retriever Inspector

This project has only been installed/executed on Windows OS.

There are other SolarEdge Data Retrievers on GitHub, but those require
tapping into the internet feed of the inverter and/or opening the 
inverter up to get encryption keys and such.  Also using more LAN/RS232 equipment.

This project just requires your PC and an internet connection to SolarEdge monitoring.

This mostly Python project extracts data from the solaredge servers and stores
that data locally for further inspection via plotting software.  

The plotting portion of this project expects Windows OS.
The python scripts will work on linux and create the data files.

Per day data collected from solaredge servers includes:

15 minute optimizer data ( Watts output ) for each optimizer (panel) in the system.  
 5 minute Inverter data ( Watt Hrs, dcVoltage, inverter temperature, acCurrent, inverter state )
Total Watt Hours collected once for each day.
Day temperature per hour and  max/min temps and daylight hours

Currently this project only supports reading data for one Inverter.

Since all the solar data is being extracted from the solarEdge servers and not from
the inverter directly, the data is time lagged.  I have chosen to only use
the data from days that have already completed.  So currently this project only 
extracts data that is from yesterday and previous to that.


## PURPOSE

I have a Solaredge HD 3800 inverter with 14 panels on my roof.  I wanted to be able
to inspect and compare my solaredge system data in a much faster
and easier to use process than the graphing process provided by solaredge monitoring.
I also wanted to keep an ongoing archive of my system data for future comparision.
With these tools I can view 20,30,50... days of data all at once.

This project collects the data from solaredge servers about my system and stores that 
reformated data in local hard drive files for each day.  No Database is used here.
Feel free to change for your usage.

Once the data is local, a graphing tool (wplot.exe) is used to provide an interactive 
view/inspection of that data.

A cron job is used to get and store data daily.

## Installation

Download the files in this project into your directory of choice.

For a quick sample view of the solar panel/inverter data:

     cd to 'sample_plot_data'
     you can just watch the video 'wplot.mp4' to get a feel.
     there is about one month of sample panel/inverter data here.
     type '..\wplot ..\solar.dpt' to run viewer or just type 'view'
     use ctrl+mouse_scroll to voom in/out x-axis.
     right mouse button for ledgend
     See if this is what you are looking for before doing the work of full install.
     You can change all parameters of the graph by editing solar.dpt.
     Use menu->help->usage.help  in wplot.exe for info on parameter options.


Install python on your system.
You might have to install python module pytz ( pip install pytz )

Make sure your SolarEdge Inverter is logging data to solaredge servers.

Get a login to SolarEdge monitoring system.
Get an API Access Key from SolarEdge (see other info / documentation for links).

Edit the .Data.py files to insert your own SolarEdge site ID, Inverter Serial #,
solarEdge remote access API-KEY and login id and password for solaredge monitoring system.

Check if wplot.exe software program included here is current version on sourceforge web site.
    https://sourceforge.net/projects/windows-plot/

If you want the weather data ( hr temps, max temp ... ) get a login for weatherapi.com.
Then get a weatherapi   API Key so you can access their data from your python code.
This is all in tData.py

## Usage

Once your .py files are updated with correct SolarEdge user information you can
run each .py file by itself to see if login/API data is working correctly.

The pData.py (panel Data) script has an extra step which involves determining
which SolarEdge optimizer ID_tag belongs with which panel on your roof.
Read the PanelMap section in the pData.py script.

Once the pData.py, iData.py, wData.py and tData.py scripts are running correctly
you can do the following.  

if linux do chmod +x ./getAllData.cmd

run 'getAllData.cmd'    to aquire your data; It will attempt to get past 15 days worth of data.
                        pData.py can only get 7 days of data.  Thats all solarEdge provides.

run 'wplot.py'          to plot and examine your system data.

Edit the solar.dpt file to adjust/add items on your plot.


## Acknowledgements

 Used some python session code for accessing solaredge 'playback' data from:

 - [cooldil/solaredge.py](https://gist.github.com/cooldil/0b2c5ee22befbbfcdefd06c9cf2b7a98)
 

## Other Info / Documentation

[SolarEdge Server API] (https://knowledge-center.solaredge.com/sites/kc/files/se_monitoring_api.pdf)

[SolarEdge Server API key] (https://www.solaredge.com/us/node/88689)

## Project details

When the getalldata command file is run there are 4 python scripts that are executed.

pData.py iData.py wData.py tData.py 

Each of these scripts connect to solaredge servers and extract data requested.
Once data has been received and parsed the data is reformated and stored in the \data directory.

Another command file is run 'wplot.py'.  This program collects/combines the many data files in
the data ( one for each day ) directory ( for a date range )  and combines them into a single 
datafile that the wplot.exe program uses to display the data.

The wplot.exe program uses the solar.dpt file to tell it what and how to display the data.


