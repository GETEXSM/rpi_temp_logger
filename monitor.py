#!/usr/bin/env python

import sqlite3

import os
import time
import glob
import re
import sys
import tempsettings

from tempsettings import Debugg, MainTableName, dbname, speriod
#Example of readback from a 28*Sensor, here its -1.625 C
#e6 ff 4b 46 7f ff 0a 10 84 : crc=84 YES
#e6 ff 4b 46 7f ff 0a 10 84 t=-1625



# display the contents of the database
def display_data():
	print "Displaying headers:"
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("SELECT * FROM temps")
	result = curs.fetchall()
	columns = curs.description
	print "All data" + str(result)
	for rhader in columns:
		print "Columns: " + str(rhader[0])
	print "Done"
	conn.close()


#Create the Main Database, if its not there.
#and proceed with adding colomns for all the devices
def create_tempdatabase():
	if Debugg: print "Searching for :"
	if Debugg: print "Database file: " + dbname
	if Debugg: print "Table:" + MainTableName
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;""", (MainTableName, ))
	exists = bool(curs.fetchone())
	if exists:
		if Debugg: print "Found!"
		# there is a table named "tableName"
	else:
		if Debugg: print "Did not Found, Instead Creating."
		try:
			curs.execute("CREATE TABLE temps (timestamp DATETIME PRIMARY KEY);")
			if Debugg: print "Success on creating."
		except:
			if Debugg: print "Failed to create."
	#commit the changes
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


# main function
# This is where the program starts collecting all temps
def main():
	VarArrayTemp = []
	VarArrayDeviceId = []
	SQLnumberIns = []
	# enable kernel modules
	os.system('sudo modprobe w1-gpio')
	os.system('sudo modprobe w1-therm')
	create_tempdatabase()
	# search for a device file that starts with 28
	devicelist = glob.glob('/sys/bus/w1/devices/28*')
	if devicelist=='':
		return None
	else:
		if Debugg: print "Getting all Devices Temps:"
		for DeviceIDES in devicelist:
			# append /w1slave to the device file
			w1devicefile = DeviceIDES + '/w1_slave'
			# get the temperature from the device file
			temperature = get_temp(w1devicefile)
			if temperature != None:
				if Debugg: print DeviceIDES[20:] + " = "+str(temperature)
			else:
				# Sometimes reads fail on the first attempt
				# so we need to retry
				temperature = get_temp(w1devicefile)
				if Debugg: print DeviceIDES[20:] + " = "+str(temperature)
			#Create a LIST of temp and deviceid
			VarArrayDeviceId.append(str(convert_dev_to_columns(DeviceIDES[20:])))
			VarArrayTemp.append(temperature)
			#these one is for in case of we need to create all these colomns, usually only the first time
			SQLnumberIns.append("?")
	#make string and remove jidder
	SQLStringnumberIns =  str(SQLnumberIns)[1:-1]
	SQLStringnumberIns = SQLStringnumberIns.replace("'",'')
	#Debugging
	if Debugg: print "All the Devices: " + str(VarArrayDeviceId)
	if Debugg: print "All the Values: " + str(VarArrayTemp)
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	try:
		if Debugg: print "About to start storing all the values"
		tempsql = "INSERT INTO " + MainTableName + " (timestamp, " + str(VarArrayDeviceId)[1:-1] + ") VALUES (datetime('now')," + SQLStringnumberIns + ");"
		if Debugg: print "Using SQL: execute(" + tempsql + "," + str(VarArrayTemp)[1:-1] + ")"
		curs.execute(tempsql, (VarArrayTemp) )
		if Debugg: print "Success on storing all temps"
	except:
		if Debugg: print "Couldt store the temps in the database, might need to create columns for the devices."
		for newCol in VarArrayDeviceId:
			try:
				if Debugg: print "Adding device: " + newCol
				tempsql = "ALTER TABLE " + MainTableName + " ADD '" + newCol + "' TEXT;"
				if Debugg: print "using SQL: " + tempsql
				curs.execute(tempsql)
				if Debugg: print "Success"
			except:
				if Debugg: print "Failed, guessing Already there"
				pass # handle the error
		try:
			if Debugg: print "Testing Storing Again:"
			tempsql = "INSERT INTO " + MainTableName + " (timestamp, " + str(VarArrayDeviceId)[1:-1] + ") VALUES (datetime('now')," + SQLStringnumberIns + ");"
			if Debugg: print "Using SQL: execute(" + tempsql + "," + str(VarArrayTemp)[1:-1] + ")"
			curs.execute(tempsql, (VarArrayTemp))
			if Debugg: print "Success on storing all temps"
		except:
			if Debugg: print "Not this time, will try again next time"

	conn.commit()
	conn.close()

# display the contents of the database
# display_data()
#time.sleep(speriod)

#stop exe from happenning when importing this file elsewhere
if __name__=="__main__":
	main()
