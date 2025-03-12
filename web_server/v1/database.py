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
from functions import (MYSQL, TZ_OFFSET, dbconMaster)

def queryDatabase(post_data): # using post data
  ts_start = time.time()
  arr_rs = {"total_records":0, "fields": [], "data":[]}
  sq_t = "select count(*) as total from " + post_data['db'] + "." + post_data['table'] + " "

  if post_data.get('fields'):
    sq = "select " + ",".join(post_data['fields']) + " from " +  post_data['db'] + "." +  post_data['table'] + " "
  else:
    sq = "select *  from " + post_data['db']  + "." + post_data['table'] + " "
    
  if post_data.get('search'):
    sq += " where " + post_data['search']

  if not post_data.get('page_max'):
    post_data['page_max'] = 20
  if not post_data.get('page_no'):
    post_data['page_no'] = 1
  offset = (post_data['page_no'] -1 ) * post_data['page_max']

  if post_data.get('groupby'):
    sq += " group by " + post_data['groupby']

  if post_data.get('orderby'):
    sq += " order by " + post_data['orderby']

  sq += " limit %d, %d"  %(offset, post_data['page_max'])

  print (sq)
  dbCon = dbconMaster()
  
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq_t)
    arr_rs['total_records'] = cur.fetchone()['total']

    cur.execute(sq)
    rows = cur.fetchall()
    for row in rows:
      arr = []

      for r in row:
        print (row[r], type(row[r]))
        if isinstance(row[r], datetime.datetime) or  isinstance(row[r],datetime.timedelta):
          row[r] = str(row[r])
        elif isinstance(row[r], bytes):
          row[r] = str(row[r].decode())

      arr_rs['data'].append(row)

    if rows:
      arr_rs['fields']  = [x  for x in rows[0]]
  ts_end = time.time()
  arr_rs['elaspe_time'] = round(ts_end-ts_start, 2)  
  return arr_rs
