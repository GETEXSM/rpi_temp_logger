#!/usr/bin/env python

import sqlite3
import sys
import re
import os
import cgi
import glob
import cgitb
cgitb.enable()
import tempsettings
# global variables
os.environ['TZ'] = 'Europe/Stockholm'
from tempsettings import Debugg, MainTableName, dbname, speriod
Timegraphspan = "24"



def get_active_dev():
	VarArrayDeviceId = []
	# enable kernel modules
	os.system('sudo modprobe w1-gpio')
	os.system('sudo modprobe w1-therm')
	# search for a device file that starts with 28
	devicelist = glob.glob('/sys/bus/w1/devices/28*')
	if devicelist=='':
		return None
	else:
		for DeviceIDES in devicelist:
			VarArrayDeviceId.append(str(convert_dev_to_columns(DeviceIDES[20:])))
	if Debugg: print "All the Devices: " + str(VarArrayDeviceId)
	return str(VarArrayDeviceId)



def print_graph_script():
	#columnlist is where we store all the titels of the columns
	columnlist = []
	rowstr = ""
	chart_table=""
	#Fetch the active devices right now, so we dont show dead devices.
	activedevsstr = re.sub("[\[\]\']","",get_active_dev())
	#dont i need GSUB here ? might find out later on ^^

	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	if Timegraphspan == None:
		curs.execute("select timestamp, " + activedevsstr + " FROM " + MainTableName )
	else:
		curs.execute("select timestamp, " + activedevsstr + " FROM " + MainTableName + " WHERE timestamp>datetime('now','-" + Timegraphspan  + " hours')")
	rows=curs.fetchall()
	conn.close()
	#print rows
	columns = curs.description
	#Mark the difference between singular and plural
	for column in columns:
		columnlist.append(convert_columns_to_dev(str(column[0])))

	#Mark the difference between singular and plural
	for row in rows:
		#removing some nasty shit and making it simple to translate from Python list to a javascript list
		tempstr	= re.sub('[\'\[\]\(\)\{\}<>u]','',str(list(row[1:])))
		rowstr+= "['" + str(row[0]).replace("u","") + "'," + tempstr	 + "],\n"

	chart_table = str(columnlist) + ",\n" + rowstr
	# google chart snippet
	chart_code="""
	<script type="text/javascript" src="https://www.google.com/jsapi"></script>
	<script type="text/javascript">
	  google.load("visualization", "1", {packages:["corechart"]});
	  google.setOnLoadCallback(drawChart);
	  function drawChart() {
		var data = google.visualization.arrayToDataTable([ %s ]);
		var options = { title: 'Temperature' ,
          curveType: 'function',
          legend: { position: 'right' }
		  };

		var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
	  	function selectHandler() {
	      var selectedItem = chart.getSelection()[0];
	      if (selectedItem) {
	        //var value = data.getValue(selectedItem.row, selectedItem.column);
			//var row = table.getSelection()[0].;
	        //alert('The user selected ' + table.getSelection()[0] );
	      }
	    }
		google.visualization.events.addListener(chart, 'select', selectHandler);
		chart.draw(data, options);
		}

	</script>"""
	print chart_code % (chart_table)


def convert_columns_to_dev(uglyin):
	return uglyin.replace("dev28_","28-")

def convert_dev_to_columns(deviceidin):
	deviceidin = "dev" + str(deviceidin).replace("-","_")
	deviceidin = re.sub(r'[^\w]', ' ', deviceidin)
	return deviceidin


# main function
# This is where the program starts
def main():
	print "Content-type: text/html\n\n"
	# start printing the page
	print "<html>"
	# print the head section including the table
	# used by the javascript for the chart
	print "<head>"
	print "    <title>"
	print "GT RPI Logger"
	print "    </title>"
	print_graph_script()
	print "</head>"
	# print the page body
	print "<body>"
	print "<h1>Raspberry Pi Temperature Logger</h1>"
	print "<hr>"
	print '<div id="chart_div" style="width: 1200px; height: 700px;"></div>'
	print "</body>"
	print "</html>"
	sys.stdout.flush()

if __name__=="__main__":
	main()
