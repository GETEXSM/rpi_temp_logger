#!/usr/bin/env python

import os
import re
import sys
import tempsettings
from tempsettings import Debugg, MainTableName, dbname, speriod





def printHTMLHead(title, table):
	print "<head>"
	print "    <title>"
	print title
	print "    </title>"
	print "</head>"






    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("SELECT * FROM temps")
