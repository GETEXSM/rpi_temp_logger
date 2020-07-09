#!/usr/bin/env python

# global variables
import os
speriod=(15*60)-1
dbname="/gt/templog.db"
MainTableName="temps"
os.environ["TZ"]="Europe/Stockholm"

Debugg = 0
#Debugging = 1 if you wanna print all debugg during run
#Debugging = 0 Silent run, Still error report when Fatal
