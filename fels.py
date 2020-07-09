#!/usr/bin/env python

import sqlite3

import os
import time
import glob
import re
import sys
import cgi
import cgitb


#Example of readback from a 28*Sensor, here its -1.625 C
#e6 ff 4b 46 7f ff 0a 10 84 : crc=84 YES
#e6 ff 4b 46 7f ff 0a 10 84 t=-1625


# global variables
speriod=(15*60)-1
dbname='/var/www/templog.db'
MainTableName='temps'
VarArrayTemp = []
VarArrayDeviceId = []


# display the contents of the database
def display_data():
	print "Displaying data:"
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()

	curs.execute("SELECT * FROM temps")
	result = curs.fetchall()

	print(result)
	for row in result:
		print "Rows: " + str(row[1])



	print "Done Displaying data"
	conn.close()


#Create the Main Database, if its not there.
#and proceed with adding colomns for all the devices
def create_tempdatabase():
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;""", (MainTableName, ))
	exists = bool(curs.fetchone())
	if exists:
		print "ITS THERE!"
		# there is a table named "tableName"
	else:
		print "No table"
		curs.execute("CREATE TABLE temps (timestamp DATETIME PRIMARY KEY, temp NUMERIC);")

	# commit the changes
	conn.commit()
	conn.close()


# get temerature
# returns None on error, or the temperature as a float
def get_temp(devicefile):

	try:
		fileobj = open(devicefile,'r')
		lines = fileobj.readlines()
		fileobj.close()
	except:
		return None

	# get the status from the end of line 1
	status = lines[0][-4:-1]

	# if the status is ok, get the temperature from line 2
	if status=="YES":
		m = re.match( '.*t=(-?[0-9\.]+)' ,	lines[1] )
		tempstr= m.group(1)
		tempvalue=float(tempstr)/1000
		return tempvalue
	else:
		#error in getting the value, log ? #Debugging
		return None

def convert_dev_to_columns(deviceidin):
	deviceidin = "dev" + str(deviceidin).replace("-","_")
	deviceidin = re.sub(r'[^\w]', ' ', deviceidin)
	return deviceidin


def show_table_headers():
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()


	curs.execute("select * from " + MainTableName)
	columns = curs.description
	for rhader in columns:
		print "Columns: " + str(rhader[0])

	print [member[0] for member in curs.description]


	conn.commit()
	conn.close()


# main function
# This is where the program starts collecting all temps
def main():


	form = cgi.FieldStorage()
	devid = None
	if "formdeviceid" in form: devid = 	form.getvalue("formdeviceid")
	print devid
	print form






# display the contents of the database
# display_data()
#time.sleep(speriod)

#stop ex from happenning when importing this file elsewhere
if __name__=="__main__":
	main()
