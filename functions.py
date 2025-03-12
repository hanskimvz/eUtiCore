# Copyright (c) 2024, Hans kim(hanskimvz@gmail.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os, time, sys
import socket
import re, base64, struct
import threading
import logging, logging.handlers

import json

try:
	import pymysql
except ImportError:
	pass

try:
	from pymongo import MongoClient
except ImportError:
	pass

CONFIG_FILE = "./gasDataServer/config.json"

def loadConfig():
  if not os.path.isfile(CONFIG_FILE):
    print(f"Error: Configuration file not found at {CONFIG_FILE}")
    return None
  
  try:
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
  except json.JSONDecodeError:
    print(f"Error: {CONFIG_FILE} is not a valid JSON file.")
    return None
  except IOError:
    print(f"Error: Unable to read {CONFIG_FILE}.")
    return None

CONFIG = loadConfig()
print(CONFIG)

def dbconMaster(host = '', user = '', password = '', db = '', charset ='', port=0): #Mysql
	if not host :
		# host = str(MYSQL['host'])
		host = str(CONFIG['MYSQL']['host'])
	if not user:
		# user = str(MYSQL['user'])
		user = str(CONFIG['MYSQL']['user'])
		
	if not password :
		# password = str(MYSQL['password'])
		password = str(CONFIG['MYSQL']['password'])
		
	if not db:
		# db = str(MYSQL['db'])
		db = str(CONFIG['MYSQL']['db'])
	if not charset:
		# charset = str(MYSQL['charset'])
		charset = str(CONFIG['MYSQL']['charset'])

	if not port:
		# port = int(MYSQL['port'])
		port = int(CONFIG['MYSQL']['port'])


	try:
		dbcon = pymysql.connect(host=host, user=str(user), password=str(password),  charset=charset, port=int(port))
	# except pymysql.err.OperationalError as e :
	except Exception as e :
		print ('dbconerr', str(e))
		return None
	
	return dbcon


def connect_to_mongodb(host = '', user = '', password = '', db = '', charset ='', port=0):
	if not host :
		host = str(CONFIG['MONGODB']['host'])
	if not user:
		user = str(CONFIG['MONGODB']['user'])
		
	if not password :
		password = str(CONFIG['MONGODB']['password'])
		
	if not db:
		db = str(CONFIG['MONGODB']['db'])
	if not port:
		port = int(CONFIG['MONGODB']['port'])

	uri ="mongodb://%s:%s@%s:%s/" %(user, password, host, port) 
	# Connect to MongoDB (default localhost:27017)
	client = MongoClient(uri, authSource='admin')
	return client
