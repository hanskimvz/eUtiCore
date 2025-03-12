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
import random
import json, re, hashlib
from functions import (CONFIG, dbconMaster)


def getWebConfig(post_data = {}):
  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    if post_data['user_id'] == 'default':
      sq = "select userID, body from %s.%s where userID like '%%_default' and page='menu'" %(post_data['db_name'], CONFIG['MYSQL']['tables']['web_config'])
    # else:
    #   sq = "select body from %s.%s where userID='%s' and page='menu'" %(post_data['db_name'], CONFIG['MYSQL']['tables']['web_config'], post_data['user_id'])
    print (sq)
    cur.execute(sq)
    result = {}
    for row in cur.fetchall():
      result[row['userID'].replace('_default', '')] = json.loads(row['body'])  
    print (result)
    return {"code": 200, "description": "success", "data": result} if cur.rowcount > 0 else {"code": 400, "description": "failed"}

def updateWebConfig(post_data = {}):
  # print(post_data)
  arr =[]
  if post_data.get('action') == 'put_permissions':
    for route in post_data['menulist']:
      child_arr = []
      if route.get('children'):
        for child in route['children']:
          child_arr.append({'name':child['name'], 'flag': child.get('flag')})

      arr.append({'name':route['name'], 'flag': route.get('flag'), 'children': child_arr})
  
  print (arr)

  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    sq = "select pk from %s.%s where userID='%s_default' and page='menu'" %(post_data['db_name'], CONFIG['MYSQL']['tables']['web_config'], post_data['role'])
    cur.execute(sq)
    if cur.rowcount > 0:
      sq = "update  %s.%s set body = '%s' where pk=%s" %(post_data['db_name'], CONFIG['MYSQL']['tables']['web_config'], json.dumps(arr), cur.fetchone()['pk'])
    else:
      sq = "insert into %s.%s (userID, page, body) values ('%s_default', 'menu', '%s')" %(post_data['db_name'], CONFIG['MYSQL']['tables']['web_config'], post_data['role'], json.dumps(arr))

    print(sq)
    cur.execute(sq)
    dbCon.commit()
  return {"code": 200, "description": "success"}
