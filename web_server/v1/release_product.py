
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
import json, re

from functions import (CONFIG, dbconMaster)


def updateReleaseProduct(post_data = {}):
  ts_start = time.time()
  xt = 0

  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    sq = "select * from %s.%s where ID='%s' and (role='admin' or 'installer')" \
          %(post_data['db_name'], CONFIG['MYSQL']['tables']['user'], post_data['installer_id'])
    print (sq)
    cur.execute(sq)
    if not cur.rowcount:
      return {"code": 1004, "description": "no_user_id"}
    
    row = cur.fetchone()
    if not post_data['db_name']:
      post_data['db_name'] = row['db_name']    

    sq_device = []  # table device
    arr_exist=[]

    sq = "select device_uid as usn from " + CONFIG['MYSQL']['tables']['device'] + " where %s" %(" or ".join(["device_uid='%s'" %usn  for usn in post_data['usnList']]))
    print (sq)
    cur.execute(sq)
    for row in cur.fetchall():
      if row['usn'] in post_data['usnList']:
        post_data['usnList'].remove(row['usn'])
        arr_exist.append(row['usn'])

    print ('exist:', arr_exist)
    print(post_data['usnList'])
    for usn in post_data['usnList']:
      sq_device.append("('%s', '%s', '%s', '%s', '%s', 'n')" %(usn,  post_data['release_date'], post_data['installer_id'], post_data['db_name'], post_data['comment']))

    if (sq_device):
      sq =  "insert into " + CONFIG['MYSQL']['tables']['device'] + "(device_uid, release_date,  installer_id, db_name, comment, flag) values%s"   %(",".join(sq_device))
      print (sq)
      xt = cur.execute(sq)
      dbCon.commit()
      if (xt):
        xt = 200
    
  return {"code": xt, "elaspe_time": round(time.time()-ts_start, 2), "data":{'exist':arr_exist, 'added': post_data['usnList']}  }