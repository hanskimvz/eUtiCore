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


# from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, urlsplit, parse_qsl, uses_params
import os, sys, time
import json

# DB_STRUCTURE = "MYSQL"
DB_STRUCTURE = "MONGO"

if DB_STRUCTURE == "MYSQL":
  from web_server.v1.users import procLogin, listUsers, updateUser, registerUser
  from web_server.v1.devices import  listDevices, updateDeviceInfo, updateReleaseProduct
  from web_server.v1.query_db import getCountData, getPlaceData, getTrafficData, siteMap, queryDatabase, getLanguagePack, getWebConfig
  from web_server.v1.update_db import updateLanguage, updateWebConfig, updateDatabase
  from web_server.v1.web_config import getWebConfig, updateWebConfig

elif DB_STRUCTURE == "MONGO":
  from web_server.v2.users import procLogin, listUsers, updateUser, registerUser
  from web_server.v2.devices import  listDevices, updateDeviceInfo, updateReleaseProduct, updateInstallDeviceInfo
  from web_server.v2.recv_data import getRecvData, getUsageData
  from web_server.v2.database import getDatabase, insertDatabase, upsertDatabase

def getJsonFromFile(filename, cat = "systemlog"):
  ts_start = time.time()
  with open (filename, 'r')  as f:
    body = f.read()

  if cat == "systemlog":
    arr_rs = {"total_records":0, "fields":['no', 'levelname', 'asctime', 'module', 'funcName', 'lineno',  'threadName', 'message'], "data":[]}
    for i, line in enumerate(body.splitlines()):
      # arr_rs['total_records'] += 1
      lx = line[34:].split(" ")
      arr_rs['data'].append({
        'no':i+1, 
        'level':line[0:8], 
        'date':line[10:29], 
        'module': lx[0], 
        'function':lx[1], 
        'line':lx[2], 
        'thread': lx[-1], 
        'message': " ".join(lx[3:-1])
      })
    arr_rs['total_records'] = i
  else:
    lines = body.splilines()
    arr_rs = {
      "total_records":len(lines), 
      "fields":[], 
      "data":lines
    }

  ts_end = time.time()
  arr_rs['elaspe_time'] = round(ts_end-ts_start, 2)  
  return arr_rs


def proc_api(url_parts, post_data = {}):
    script_name = url_parts.path.split("/")[-1]
    query = dict(parse_qsl(urlsplit(url_parts.query).path))
    print('query:', query, "script_name:", script_name)
    print('post_data:', post_data)
    arr= {}
    # if not query.get('db_name'):
    #   query['db_name'] = 'gas_demo'

    if script_name == 'login': # post
      arr = procLogin(post_data)

    elif script_name == 'query':
      if post_data['page'] == "device_info":
        arr = listDevices(post_data)

      elif post_data['page'] == "users":
        arr = listUsers(post_data)

      elif post_data['page'] == "database":
        arr = getDatabase(post_data)

      # elif post_data['page'] == "recv_uid_list":
      #   arr = listDevices(post_data)

      elif post_data['page'] == "recv_data":
        arr = getRecvData(post_data)

      elif post_data['page'] == "usage_data":
        arr = getUsageData(post_data)

      elif post_data['page'] == "webconfig":
        arr = getWebConfig(post_data)


      elif query['data'] == 'language': # get
        if not query.get('action'):
          query['action'] = 'pack'

        arr = getLanguagePack(query['db_name'], query['action'])

      elif query['data'] == 'place': # get
        arr = getPlaceData(query['db_name'])

      elif query['data'] == 'webconfig': # get
        arr = getWebConfig(query['db_name'], query['page'])

      elif query['data'] == 'jsonfromfile': # get
        arr = getJsonFromFile(query['filename'], query['cat'])


      elif query['data'] == 'count': # post
        arr = getCountData(post_data)
      
      elif query['data']=='trafficdistribution': # post
        arr = getTrafficData(post_data)

      elif query['data'] == 'listdevice': # post
        arr = listDevices(post_data)

      elif query['data'] == 'sitemap': # post
        arr = siteMap(post_data)

      elif query['data'] == 'querydb': # post
        arr = queryDatabase(post_data)


    elif script_name == 'update':
      if post_data['page'] == "releaseproduct":
        arr = updateReleaseProduct(post_data)

      elif post_data['page'] == "device_info":
          arr = updateDeviceInfo(post_data)

      elif post_data['page'] == "install_device_info":
          arr = updateInstallDeviceInfo(post_data)          

      elif post_data['page'] == "users":
        arr = updateUser(post_data)

      elif post_data['page'] == "webconfig":
        arr = updateWebConfig(post_data)




      elif query['data'] == 'language':
        arr = updateLanguage(post_data)
      
      elif query['data'] == 'webconfig':
        # print (post_data)
        updateWebConfig(db_name=query['db_name'], page=query['page'], body=post_data['data'])

      elif query['data'] == 'updatedb':
        arr = updateDatabase(post_data)

    elif script_name == 'insert':
      arr = insertDatabase(post_data)
    elif script_name == 'register':
      if post_data['page'] == "users":
        arr = registerUser(post_data)
        print("arr:", arr)



    if query.get('fmt') == 'json' or post_data.get('format') == 'json':
      body = json.dumps(arr)
      # print (body)
      return 'text/json', body.encode()
    
    elif isinstance(arr, str):
      return 'text/json', arr.encode()

