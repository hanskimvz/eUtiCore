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

# mongosh -u gas_user -p --port 5090

import os, time, sys
import datetime
import json, re, hashlib
from functions import (CONFIG, connect_to_mongodb)

def process_database(post_data):
  if post_data.get('action') == 'list':
    return getDatabaseTree()
  elif post_data.get('action') == 'view':
    return queryDatabase(post_data)


def queryDatabase(post_data): # using post data
  ts_start = time.time()
  arr_rs = {"total_records":0, "fields": [], "data":[]}

  if not post_data.get('filter'):
    post_data['filter'] = {}
  
  field_query = {}
  if post_data.get('fields'):
    field_query = {field: 1 for field in post_data['fields']} if post_data['fields'] else {}

  limit_num = 0
  if post_data.get('limit'):
    limit_num = int(post_data.get('limit'))


  client = connect_to_mongodb()
  collection = client[post_data['db']][post_data['table']]
  arr_rs['total_records'] = collection.count_documents(post_data['filter'])

  if (limit_num == 0 and arr_rs['total_records'] > 1000):
    limit_num = 1000

  if limit_num:
    if post_data.get('orderby'):
      rows = collection.find(post_data['filter'], field_query).limit(limit_num).sort(post_data.get('orderby'))
    else:
      rows = collection.find(post_data['filter'], field_query).limit(limit_num)
  
  else :
    if post_data.get('orderby'):
      rows = collection.find(post_data['filter'], field_query).sort(post_data.get('orderby'))
    else:
      rows = collection.find(post_data['filter'], field_query)




  
  for row in list(rows):
    # row['_id'] = str(row['_id'])
    del row['_id']
    for r in row:
      if isinstance(row[r], datetime.datetime):
        row[r] = str(row[r])
      elif isinstance(row[r], bytes):
        try:
          row[r] = str(row[r].decode())
        except:
          row[r] = row[r].hex()

      if r not in arr_rs['fields']:
        arr_rs['fields'].append(r)

    arr_rs['data'].append(row)

  for i, rs in enumerate(arr_rs['data']):
    for f in arr_rs['fields']:
      if f not in [r for r in rs]:
        arr_rs['data'][i][f] = '-'

  client.close()
  
  arr_rs['elasped_time'] = round(time.time()-ts_start, 2)
  return  arr_rs


def getDatabaseTree():
  ts_start = time.time()
  client = connect_to_mongodb()
  
  # 모든 데이터베이스 목록 가져오기
  db_list = client.list_database_names()
  
  # 시스템 데이터베이스 제외 (선택사항)
  excluded_dbs = ['admin', 'config', 'local']
  db_list = [db for db in db_list if db not in excluded_dbs]

  arr = []  
  for db in db_list:
    print (db)
    dbs = client[db]
      
    # 해당 데이터베이스의 모든 컬렉션 목록 가져오기
    collection_list = dbs.list_collection_names()
      
    # 시스템 컬렉션 제외 (선택사항)
    excluded_collections = ['system.indexes', 'system.users']
    collection_list = [col for col in collection_list if col not in excluded_collections]
    arr.append({"db": db, "collections": collection_list})
  
  client.close()
  print (json.dumps(arr))
  return {
      "code": 200,
      "elasped_time": round(time.time()-ts_start, 2),
      "data": arr
  }

def insertDatabase(post_data):
  ts_start = time.time()
  client = connect_to_mongodb()
  collection = client[post_data['db']][post_data['table']]
  collection.insert_many(post_data['data'])
  client.close()
  return {
    "code": 200,
    "elasped_time": round(time.time()-ts_start, 2),  
  }



def upsertDatabase(post_data):
  ts_start = time.time()
  client = connect_to_mongodb()
  collection = client[post_data['db']][post_data['table']]
  query = {
    'device_uid': post_data['device_uid']
  }
  if post_data.get('_id'):
    query['_id'] = post_data['_id']
  collection.update_one(query, {'$set': post_data}, upsert=True)
  client.close()


  return {
    "code": 200,
    "elasped_time": round(time.time()-ts_start, 2),  
  }


if __name__ == '__main__':
  print (getDatabaseTree())

