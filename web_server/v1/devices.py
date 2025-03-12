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
import datetime
import pymysql
import json, re, hashlib
from functions import (CONFIG, dbconMaster)


def listDevices(post_data={}):
  print (post_data)
  ts_start = time.time()

  fields = (", ".join(post_data['fields']))  if post_data['fields'] else "*"
    
  if post_data['role'] == 'admin': 
    sq = "select %s from  %s.%s " %(fields, post_data['db_name'], CONFIG['MYSQL']['tables']['device'])
    if post_data.get('uid'):
      sq += " where device_uid='%s'" %post_data['uid']
  else:
    sq = "select %s from  %s.%s where installer_id='%s' " %(fields, post_data['db_name'], CONFIG['MYSQL']['tables']['device'],  post_data['user_id'])
    if post_data.get('uid'):
      sq += " and device_uid='%s'" %post_data['uid']

  print (sq)

  arr_rs = {
    'data': [],
    'elaspe_time':0,
    'code': 0
  }

  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    cur.execute(sq)
    rows = cur.fetchall()

    for row in rows:
      if not row['device_uid']:
        continue

      for r in row:
        if isinstance(row[r], datetime.datetime):
          row[r] = str(row[r])

      arr_rs['data'].append(row)

  arr_rs['total_record'] = len(arr_rs['data'])
  arr_rs['elaspe_time'] = round(time.time()-ts_start, 2)
  return arr_rs

def updateDeviceInfo(post_data={}):
  print (post_data)
  ts_start = time.time()
  arr_rs = {
    'data': [],
    'elaspe_time':0,
    'code': 0
  }
  
  arr = []
  for field in post_data['fields']:
    # print (key, value)
    if  isinstance(post_data[field], int):
      arr.append("%s=%s" %(field, post_data[field]) )
    else :
      arr.append("%s='%s'" %(field, post_data[field]) )
  
  fields_to_set =  ", ".join(arr)
  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    sq = "update %s.%s set %s where device_uid='%s'" %(post_data['db_name'], CONFIG['MYSQL']['tables']['device'], fields_to_set, post_data['device_uid'])
    print (sq)
    cur.execute(sq)
    dbCon.commit()
    arr_rs['code'] = 200

  arr_rs['total_record'] = len(arr_rs['data'])
  arr_rs['elaspe_time'] = round(time.time()-ts_start, 2)
  return arr_rs

def updateReleaseProduct(post_data = {}):
  ts_start = time.time()
  xt = 0

  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    sq = "select * from %s where ID='%s'" %(CONFIG['MYSQL']['tables']['common_user'], post_data['installer_id'])
    print (sq)
    cur.execute(sq)
    if not cur.rowcount:
      return {"code": 1004, "description": "no_user_id"}
    
    row = cur.fetchone()
    if not post_data['db_name']:
      post_data['db_name'] = row['db_name']    

    
    arr_exist=[]

    where_exist = " or ".join(["device_uid='%s'" %usn  for usn in post_data['usnList']])

    # check exist device in common_device
    sq = "select device_uid as usn from %s where %s" \
          %(CONFIG['MYSQL']['tables']['common_device'], where_exist)
    print (sq)
    cur.execute(sq)
    arr_exist = [row['usn'] for row in cur.fetchall()]
    arr_add = []
    for usn in post_data['usnList']:
      if not usn in arr_exist:
        arr_add.append(usn)
    
    if arr_add:
      sq = "insert into %s (device_uid, db_name) values %s" \
            %(CONFIG['MYSQL']['tables']['common_device'], ",".join(["('%s', '%s')" %(usn, post_data['db_name']) for usn in arr_add]))
      print (sq)
      cur.execute(sq)
      dbCon.commit()


    # check exist device in device table of custom db
    sq = "select device_uid as usn from %s.%s where %s" %(post_data['db_name'], CONFIG['MYSQL']['tables']['device'], where_exist)
    print (sq)
    cur.execute(sq)
    arr_exist = [row['usn'] for row in cur.fetchall()]
    arr_add = []
    for usn in post_data['usnList']:
      if not usn in arr_exist:
        arr_add.append(usn)
        # sq_device.append("('%s', '%s', '%s', '%s', 'n')" %(usn,  post_data['release_date'], post_data['installer_id'], post_data['comment']))

    if arr_add:
      sq =  "insert into %s.%s (device_uid, release_date, installer_id, comment, flag) values%s" \
            %(post_data['db_name'], CONFIG['MYSQL']['tables']['device'], ",".join(["('%s', '%s', '%s', '%s', 'n')" %(usn,  post_data['release_date'], post_data['installer_id'], post_data['comment']) for usn in arr_add]))
      print (sq)
      xt = cur.execute(sq)
      dbCon.commit()
      if (xt):
        xt = 200
    
  return {"code": xt, "elaspe_time": round(time.time()-ts_start, 2), "data":{'exist':arr_exist, 'added': arr_add}  }






