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

def procLogin(post_data= {}):
  if not post_data.get('id'):
    return {"code": 102, "description": "no_id"}
  if not post_data.get('password'):
    return {"code": 103, "description": "no_password"}
  
  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    sq = "select * from " + CONFIG['MYSQL']['tables']['common_user'] + " where ID='%s'" %(post_data.get('id').strip())
    print (sq)
    cur.execute(sq)
    if not cur.rowcount:
      return {"code": 104, "description": "no_user_id"}
    
    row = cur.fetchone()
    # if row['flag'] == 'n':
    #   return {"code": 105, "description": "id_expired"}
    
    db_name = row['db_name']
    if db_name == 'none':
      return {"code": 107, "description": "no_db_name"}
    
    sq = "select * from " + db_name + "." + CONFIG['MYSQL']['tables']['user'] + " where ID='%s'" %(post_data.get('id').strip())
    print (sq)
    cur.execute(sq)
    if not cur.rowcount:
      return {"code": 108, "description": "no_user_id"}
    
    row = cur.fetchone()

    if hashlib.sha256(post_data['password'].encode('utf-8')).hexdigest() != row['passwd']:
      return {"code": 109, "description": "password_not_match"}
    
    if row['flag'] == 'n':
      return {"code": 106, "description": "id_expired"}
    del(row['passwd'])

    for r in row:
      if isinstance(row[r], datetime.datetime):
        row[r] = str(row[r])
    
    row['userseq'] = hashlib.md5((row['ID'] + 'hanskim').encode()).hexdigest()
    row['db_name'] = db_name


    return {"code": 200, "description": row }


def listUsers(post_data={}):
  print (post_data)
  ts_start = time.time()

  fields = (", ".join(post_data['fields']))  if post_data['fields'] else "*"
  
  if post_data.get('action') == 'list_floating_users':
    sq = "SELECT %s FROM %s " %(fields, CONFIG['MYSQL']['tables']['floating_user'])  
    if post_data.get('only_floating'):
      sq += " where flag='n'"

  else:
    sq = "SELECT %s FROM %s.%s" %(fields, post_data['db_name'], CONFIG['MYSQL']['tables']['user'])


  if post_data['role'] != 'admin' or post_data.get('user_id'):
    sq += " WHERE ID='%s'" %post_data['user_id']

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
      if not row['ID']:
        continue

      for r in row:
        if isinstance(row[r], datetime.datetime):
          row[r] = str(row[r])

      arr_rs['data'].append(row)

  arr_rs['total_record'] = len(arr_rs['data'])
  arr_rs['elaspe_time'] = round(time.time()-ts_start, 2)
  return arr_rs


def updateFloatingUser(post_data={}):
  print (post_data)
  # {'page': 'users', 'action': 'update_floating_user', 'format': 'json', 'ID': 'jay', 'db_name': 'gas_demo', 'user_id': 'hanskim', 'role': 'admin'}
  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    # check db_name is valid
    # sq = "select * from %s where db_name='%s'" %(CONFIG['MYSQL']['tables']['common_user'], post_data['db_name'])
    # print (sq)
    # cur.execute(sq)
    # row = cur.fetchone()
    # if not row:
    if post_data['db_name'] not in ['gas_demo', 'gas_samchully']:
      return {'data': [], 'elaspe_time':0, 'code': 400, 'message': 'db_name_not_found'}

    # check if the user exists in the floating_user table
    sq = "select * from %s where ID='%s'" %(CONFIG['MYSQL']['tables']['floating_user'], post_data['ID'])
    print (sq)
    cur.execute(sq)
    row = cur.fetchone()
    if not row:
      return {'data': [], 'elaspe_time':0, 'code': 400, 'message': 'user_not_found'}
    
    post_data['email']    = row['email']
    post_data['name']     = row['name']
    post_data['category'] = row['category']
    post_data['comment']  = row['comment']
    post_data['passwd']   = row['passwd']
    post_data['lang']     = row['lang']

    # check if the user exists in the common_user table
    sq = "select * from %s where ID='%s'" %(CONFIG['MYSQL']['tables']['common_user'], post_data['ID'])
    print (sq)
    cur.execute(sq)
    row = cur.fetchone()
    if row:
      return {'data': [], 'elaspe_time':0, 'code': 401, 'message': 'user_already_exists'}

    # check if the user exists in the users table
    sq = "select * from %s.%s where ID='%s'" %(post_data['db_name'], CONFIG['MYSQL']['tables']['user'], post_data['ID'])
    print (sq)
    cur.execute(sq)
    row = cur.fetchone()
    if row:
      return {'data': [], 'elaspe_time':0, 'code': 402, 'message': 'user_already_exists'}
  
    arr_sq = []
    arr_sq.append("insert into %s (ID, db_name) values ('%s', '%s')" %(CONFIG['MYSQL']['tables']['common_user'], post_data['ID'], post_data['db_name']))

    # insert the user into the users table
    code = 'U'+ time.strftime('%y%m%d%H%M%S') + str(random.randint(10, 99))
    
    role = 'user' if post_data['category'] == 'company' else 'viewer'
    arr_sq.append("insert into %s.%s (regdate, code, ID, email, name, passwd, comment, lang, flag, role) values (now(), '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" %(post_data['db_name'], CONFIG['MYSQL']['tables']['user'], code, post_data['ID'], post_data['email'], post_data['name'], post_data['passwd'],  post_data['comment'], post_data['lang'], 'y', role))
  

    arr_sq.append("update %s set flag='y' where ID='%s'" %(CONFIG['MYSQL']['tables']['floating_user'], post_data['ID']))

    for sq in arr_sq:
      print (sq)
      cur.execute(sq)
    dbCon.commit()

  return {'data': [], 'elaspe_time':0, 'code': 200}

def updateUser(post_data={}):
  print (post_data)
  ts_start = time.time()

  if post_data.get('action') == 'update_floating_user':
    return updateFloatingUser(post_data)


  arr_rs = {
    'data': [],
    'elaspe_time':0,
    'code': 0
  }

  arr = []
  if post_data.get('currentPassword') and post_data.get('newPassword'):
    post_data['currentPassword'] = hashlib.sha256(post_data['currentPassword'].encode('utf-8')).hexdigest()
    post_data['newPassword'] = hashlib.sha256(post_data['newPassword'].encode('utf-8')).hexdigest()
    dbCon = dbconMaster()
    with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
      cur.execute("SELECT passwd FROM %s.%s WHERE ID='%s'" %(post_data['db_name'], CONFIG['MYSQL']['tables']['user'], post_data['user_id']))
      row = cur.fetchone()
      if row['passwd'] != post_data['currentPassword']:
        arr_rs['code'] = 400
        arr_rs['message'] = "Current password is incorrect"
        return arr_rs

    fields_to_set = "passwd='%s'" %post_data['newPassword']

  else:
    for field in post_data['fields']:
      # print (key, value)
      if  isinstance(post_data[field], int):
        arr.append("%s=%s" %(field, post_data[field]) )
      else :
        arr.append("%s='%s'" %(field, post_data[field]) )
  
    fields_to_set =  ", ".join(arr)

  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    sq = "update %s.%s set %s where ID='%s'" %(post_data['db_name'], CONFIG['MYSQL']['tables']['user'], fields_to_set, post_data['user_id'])
    print (sq)
    cur.execute(sq)
    dbCon.commit()
    arr_rs['code'] = 200

  arr_rs['total_record'] = len(arr_rs['data'])
  arr_rs['elaspe_time'] = round(time.time()-ts_start, 2)
  return arr_rs



def registerUser(post_data={}):
  print (post_data) 
  
  dbCon = dbconMaster()
  with dbCon.cursor(pymysql.cursors.DictCursor) as cur:
    sq = "select * from %s where ID='%s'" %(CONFIG['MYSQL']['tables']['floating_user'], post_data['ID'])
    print (sq) 
    cur.execute(sq)
    if cur.rowcount:
      return {'code': 400, 'message': 'user_already_exists'}

    sq = "select * from %s where ID='%s'" %(CONFIG['MYSQL']['tables']['common_user'], post_data['ID'])
    print (sq)
    cur.execute(sq)
    if cur.rowcount:
      return {'code': 401, 'message': 'user_already_exists'}
    
    # sq = "select max(pk) as pk from %s" %CONFIG['MYSQL']['tables']['users']
    # cur.execute(sq)
    # row = cur.fetchone()
    # code = "U%06d" %(int(row['pk']) + 1)
    passwd = hashlib.sha256(post_data['password'].encode('utf-8')).hexdigest()

    sq="insert into %s (regdate, ID, email, name, passwd, category, comment) values (now(), '%s', '%s', '%s', '%s', '%s', '%s')" %(CONFIG['MYSQL']['tables']['floating_user'], post_data['ID'], post_data['email'], post_data['name'], passwd, post_data['category'], post_data['comment'])
    print (sq)
    cur.execute(sq)
    dbCon.commit()
    if cur.rowcount == 1:
      return {'code': 200, 'message': 'user_registered'}  
    else:
      return {'code': 400, 'message': 'user_registration_failed'}  

  return {} 



