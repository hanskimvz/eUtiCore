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
import random
import json, re, hashlib
from functions import (CONFIG, connect_to_mongodb)

def procLogin(post_data= {}):
  if not post_data.get('id'):
    return {"code": 102, "description": "no_id"}
  if not post_data.get('password'):
    return {"code": 103, "description": "no_password"}

  client = connect_to_mongodb()
  db_common = client[CONFIG['MONGODB']['db']]
  r_users = db_common[CONFIG['MONGODB']['tables']['common_user']]
  r_user = r_users.find_one({'ID': post_data['id']})
  if not r_user:
    return {"code": 104, "description": "no_user_id"}
  
  db_custom = client[r_user['db_name']]
  c_users = db_custom[CONFIG['MONGODB']['tables']['user']]  

  c_user = c_users.find_one({'ID': post_data['id']})
  if not c_user:
    return {"code": 105, "description": "no_user_id"}
  
  if hashlib.sha256(post_data['password'].encode('utf-8')).hexdigest() != c_user['passwd']:
    return {"code": 106, "description": "password_not_match"}

  if c_user['flag'] == False:
    return {"code": 107, "description": "id_expired"}

  del(c_user['passwd'], c_user['_id'])

  c_user['db_name'] = r_user['db_name']
  c_user['userseq'] = hashlib.md5((c_user['ID'] + 'hanskim').encode()).hexdigest()
  
  for r in c_user:
    if isinstance(c_user[r], datetime.datetime):
      c_user[r] = c_user[r].strftime('%Y-%m-%d %H:%M:%S')
  
  return {"code": 200, "data": c_user}

def listUsers(post_data={}):
  print (post_data)
  ts_start = time.time()
  arr_rs = {
    'data': [],
    'elasped_time': 0,
    'code': 0
  }

  client = connect_to_mongodb()

  if post_data.get('action') == 'list_floating_users':
    db = client[CONFIG['MONGODB']['db']]
    f_users = db[CONFIG['MONGODB']['tables']['floating_user']]
    rows = f_users.find({'flag': False})
  
  elif post_data.get('db_name'):
    users = client[post_data['db_name']][CONFIG['MONGODB']['tables']['user']]
    if post_data.get('user_id'):
      rows = users.find({'ID': post_data['user_id']})

    else:
      rows = users.find({})

  for row in list(rows):
    new_row = {k: None for k in post_data['fields']}
    for r in row:
      if not r in post_data['fields']:
        continue
      if isinstance(row[r], datetime.datetime):
        row[r] = row[r].strftime('%Y-%m-%d %H:%M:%S')
      new_row[r] = row[r]

    arr_rs['data'].append(new_row)  
  
  arr_rs['code'] = 200

  client.close()
  arr_rs['elasped_time'] = round(time.time()-ts_start, 2)
  arr_rs['total_records'] = len(arr_rs['data'])
  print ('rs', arr_rs)
  return arr_rs


def updateFloatingUser(post_data={}):
  print (post_data)
  client = connect_to_mongodb()
  db_common = client[CONFIG['MONGODB']['db']]
  db_custom = client[post_data['db_name']]
  f_users = db_common[CONFIG['MONGODB']['tables']['floating_user']]
  r_users = db_common[CONFIG['MONGODB']['tables']['common_user']]
  c_users = db_custom[CONFIG['MONGODB']['tables']['user']]

  f_user = f_users.find_one({'ID': post_data['ID']})
  if not f_user:
    return {'data': [], 'elasped_time':0, 'code': 400, 'message': 'user_not_found'}

  rs_r = r_users.update_one(
    {"ID": f_user['ID']},  # filter
    {
      "$set": {
        "ID": f_user['ID'],
        "db_name": post_data['db_name'],
      }
    },
    upsert=True  # This enables upsert
  )
  rs_c = c_users.update_one(
    {'ID': f_user['ID']},
    {
      "$set": {
        'regdate': datetime.datetime.utcnow(),
        'code': 'U'+ time.strftime('%y%m%d%H%M%S') + str(random.randint(10, 99)),
        'ID': f_user['ID'],
        'passwd': f_user['passwd'],
        'name': f_user['name'],
        'email': f_user['email'],
        'lang': f_user['lang'],
        'role': 'user' if f_user['category'] == 'company' else 'viewer',
        'flag': True
      }
    },
    upsert=True  # This enables upsert
  )

  rs_f = f_users.update_one({ 'ID': post_data['ID'] }, { '$set': {'flag': True} })

  client.close()
  return {'data': [], 'elasped_time':0, 'code': 200}


def updateUser(post_data={}):
  print (post_data)
  ts_start = time.time()

  if post_data.get('action') == 'update_floating_user':
    return updateFloatingUser(post_data)

  client = connect_to_mongodb()
  db_custom = client[post_data['db_name']]
  users = db_custom[CONFIG['MONGODB']['tables']['user']]

  arr_rs = {
    'data': [],
    'elasped_time':0,
    'code': 0
  }
  user = users.find_one({'ID': post_data['user_id']})
  if not user:
    arr_rs['code'] = 400
    arr_rs['message'] = "User not found"
    return arr_rs

  if post_data.get('currentPassword') and post_data.get('newPassword'):
    post_data['currentPassword'] = hashlib.sha256(post_data['currentPassword'].encode('utf-8')).hexdigest()
    post_data['newPassword'] = hashlib.sha256(post_data['newPassword'].encode('utf-8')).hexdigest()
    
    if user['passwd'] != post_data['currentPassword']:
      arr_rs['code'] = 400
      arr_rs['message'] = "Current password is incorrect"
      return arr_rs
    
    rs = users.update_one(
      {'ID': post_data['ID']}, 
      {'$set':{
         'passwd': post_data['newPassword'],
      }},
    )    

  else:
    rs = users.update_one(
      {'ID': post_data['ID']}, 
      {'$set':{
         'name': post_data['name'],
         'email': post_data['email'],
         'lang': post_data['lang'],
         'role': post_data['role'],
      }},
    )
  
  if not rs:
    arr_rs['code'] = 400
    arr_rs['message'] = "Failed to update user"
    return arr_rs
    
  arr_rs['code'] = 200
  arr_rs['message'] = "User updated"
  arr_rs['elasped_time'] = round(time.time()-ts_start, 2)
  client.close()
  return arr_rs


def registerUser(post_data={}):
  # print (post_data) 
  client = connect_to_mongodb()
  db = client[CONFIG['MONGODB']['db']]

  users = db[CONFIG['MONGODB']['tables']['common_user']]
  if users.find_one({'ID': post_data['ID']}):
    return {'code': 400, 'message': 'user_already_exists'}

  users = db[CONFIG['MONGODB']['tables']['floating_user']]
  if users.find_one({'ID': post_data['ID']}):
    return {'code': 400, 'message': 'user_already_exists'}  
  
  rs = users.insert_one({
    'regdate': datetime.datetime.utcnow(),
    'ID': post_data['ID'],
    'email': post_data['email'],
    'name': post_data['name'],
    'passwd': hashlib.sha256(post_data['password'].encode('utf-8')).hexdigest(),
    'lang': post_data['language'],
    'category': post_data['category'],
    'comment': post_data['comment'],
    'flag': False
  })
  
  client.close()
  if rs.inserted_id:
    return {'code': 200, 'message': 'user_registered'}  
  else:
    return {'code': 400, 'message': 'user_registration_failed'}  



