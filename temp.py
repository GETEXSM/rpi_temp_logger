#!/usr/bin/env python

import sqlite3
import sys
import cgi
import cgitb
cgitb.enable()
import tempsettings
# global variables
from tempsettings import Debugg, MainTableName, dbname, speriod
CGIform = None


# print the HTTP header
def printHTTPheader():
	print "Content-type: text/html\n\n"



# print the HTML head section
# arguments are the page title and the table for the chart
def printHTMLHead(title, table):
	print "<head>"
	print "    <title>"
	print title
	print "    </title>"

	print_graph_script(table)

	print "</head>"


# get data from the database
# if an interval is passed,
# return a list of records from the database
def get_data(interval):
	#print "Debugg: Interval=" + interval
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()

	if interval == None:
		curs.execute("SELECT * FROM " + MainTableName )
	else:
		curs.execute("SELECT * FROM " + MainTableName + " WHERE timestamp>datetime('now','-" + interval  + " hours')")

	rows=curs.fetchall()

	conn.close()

	return rows


# convert rows from database into a javascript table
def create_table(rows):
	chart_table=""
	for row in rows[:-1]:
		rowstr="['{0}', {1}],\n".format(str(row[0]),str(row[3]))
		chart_table+=rowstr

	row=rows[-1]
	rowstr="['{0}', {1}]\n".format(str(row[0]),str(row[3]))
	chart_table+=rowstr
	return chart_table


# print the javascript to generate the chart
# pass the table generated from the database info
def print_graph_script(table):

	# google chart snippet
	chart_code="""
	<script type="text/javascript" src="https://www.google.com/jsapi"></script>
	<script type="text/javascript">
	  google.load("visualization", "1", {packages:["corechart"]});
	  google.setOnLoadCallback(drawChart);
	  function drawChart() {
		var data = google.visualization.arrayToDataTable([
		  ['Time', 'Temperature'],
%s
		]);

		var options = {
		  title: 'Temperature'
		};

		var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
		chart.draw(data, options);
	  }
	</script>"""

	print chart_code % (table)




# print the div that contains the graph
def show_graph():
	print "<h2>Temperature Chart</h2>"
	print '<div id="chart_div" style="width: 900px; height: 500px;"></div>'



# connect to the db and show some stats
# argument option is the number of hours
def show_stats(option):

	conn=sqlite3.connect(dbname)
	curs=conn.cursor()

	if option is None:
		option = str(24)

 	curs.execute("SELECT timestamp,max(dev28_0000072e4aad) FROM " + MainTableName + " WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
	rowmax=curs.fetchone()
	rowstrmax="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmax[0]),str(rowmax[1]))
	curs.execute("SELECT timestamp,min(dev28_0000072e4aad) FROM " + MainTableName + " WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)

	rowmin=curs.fetchone()
	rowstrmin="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmin[0]),str(rowmin[1]))

	curs.execute("SELECT avg(dev28_0000072e4aad) FROM " + MainTableName + " WHERE timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
	rowavg=curs.fetchone()


	print "<hr>"


	print "<h2>Minumum temperature&nbsp</h2>"
	print rowstrmin
	print "<h2>Maximum temperature</h2>"
	print rowstrmax
	print "<h2>Average temperature</h2>"
	print "%.3f" % rowavg+"C"

	print "<hr>"

	print "<h2>In the last hour:</h2>"
	print "<table>"
	print "<tr><td><strong>Date/Time</strong></td><td><strong>Temperature</strong></td></tr>"

	rows=curs.execute("SELECT * FROM " + MainTableName + " WHERE timestamp>datetime('now','-1 hour') AND timestamp<=datetime('now')")

	for row in rows:
		rowstr="<tr><td>{0}&emsp;&emsp;</td><td>{1}C</td></tr>".format(str(row[0]),str(row[3]))
		print rowstr
	print "</table>"

	print "<hr>"

	conn.close()

def Table_to_device_Text(uglyin):
	return uglyin.replace("dev28_","28-")

def print_devid_selector(devid):
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("select * from " + MainTableName)
	columns = curs.description
	print """<form action="/cgi-bin/temp.py" method="POST">
		Select Device to show
		<select name="formdeviceid">"""

	if "formdeviceid" in CGIform: devid = str(CGIform.getvalue("formdeviceid"))

	
	print CGIform
	for rhader in columns:
		if (str(rhader[0]) != "temp") and (str(rhader[0]) != "timestamp"):
			tempid = Table_to_device_Text(str(rhader[0]))
			print "comparing: " + tempid + " and " + str(devid)
			if str(devid) == tempid:
				print '<option value="' + tempid + '" selected="selected">' + tempid + '</option>'
			else:
				print '<option value="' + tempid + '">' + tempid + '</option>'
	print """</select><input type="submit" value="Select" name="formdeviceid"></form>"""


def print_time_selector(option):
	print """<form action="/cgi-bin/temp.py" method="POST">
		Show the temperature logs for
		<select name="timeinterval">"""
	if option is not None:
		if option == "6":
			print "<option value=\"6\" selected=\"selected\">the last 6 hours</option>"
		else:
			print "<option value=\"6\">the last 6 hours</option>"
		if option == "12":
			print "<option value=\"12\" selected=\"selected\">the last 12 hours</option>"
		else:
			print "<option value=\"12\">the last 12 hours</option>"
		if option == "24":
			print "<option value=\"24\" selected=\"selected\">the last 24 hours</option>"
		else:
			print "<option value=\"24\">the last 24 hours</option>"
	else:
		print """<option value="6">the last 6 hours</option>
			<option value="12">the last 12 hours</option>
			<option value="24" selected="selected">the last 24 hours</option>"""

	print """        </select>
		<input type="submit" value="Display" name="timeinterval">
	</form>"""


# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
	# check that the option string represents a number
	if option_str.isalnum():
		# check that the option is within a specific range
		if int(option_str) > 0 and int(option_str) <= 24:
			return option_str
		else:
			return None
	else:
		return None


# main function
# This is where the program starts
def main():

	cgitb.enable()
	CGIform=cgi.FieldStorage()
	# get options that may have been passed to this script

	if "option" in CGIform:
		option=validate_input (CGIform["option"].value)
	else:
		option = None
	if "option" in CGIform: print CGIform["option"].value

	if option is None:
		option = str(24)

	# get data from the database
	records=get_data(option)

	# print the HTTP header
	printHTTPheader()

	if len(records) != 0:
		# convert the data into a table
		table=create_table(records)
	else:
		print "No data found"
		return

	# start printing the page
	print "<html>"
	# print the head section including the table
	# used by the javascript for the chart
	printHTMLHead("Raspberry Pi Temperature Logger", table)

	# print the page body
	print "<body>"
	print "<h1>Raspberry Pi Temperature Logger</h1>"
	print "<hr>"
	print_devid_selector(None)
	print_time_selector(option)
	show_graph()
	show_stats(option)
	print "</body>"
	print "</html>"

	sys.stdout.flush()

if __name__=="__main__":
	main()
