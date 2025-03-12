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

def procLogin(db_name='gas_demo', post_data= {}):
  if not post_data.get('id'):
    return {"code": 1002, "description": "no_id"}
  if not post_data.get('password'):
    return {"code": 1003, "description": "no_password"}
  
  sq = "select * from " + MYSQL['common_users'] + " where ID='" + post_data.get('id').strip() + "'"
  # print (sq)
  dbCon = dbconMaster()

  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq)
    if not cur.rowcount:
      return {"code": 1004, "description": "no_user_id"}
    
    row = cur.fetchone()
    # if row['passwd'] != post_data['password']:
    if hashlib.sha256(post_data['password'].encode('utf-8')).hexdigest() != row['passwd']:
      return {"code": 1005, "description": "password_not_match"}
    if row['flag'] == 'n':
      return {"code": 1006, "description": "id_expired"}
    del(row['passwd'])

    for r in row:
      if isinstance(row[r], datetime.datetime):
        row[r] = str(row[r])
    
    row['userseq'] = hashlib.md5((row['ID'] + 'hanskim').encode()).hexdigest()
    
    # if db_name != 'none':
    #   sq = "select name, name_eng, name_chi, language from " + row['db_name'] + "." + MYSQL['customUsers'] + "  where code='" + row['code'] + "'"
    #   cur.execute(sq)
    #   row_custom = cur.fetchone()
    #   if row_custom:
    #     row['name'] = row_custom['name']
    #     row['name_eng'] = row_custom['name_eng']
    #     row['name_chi'] = row_custom['name_chi']
    #     row['language'] = row_custom['language']
        

    return {"code": 1000, "description": row }