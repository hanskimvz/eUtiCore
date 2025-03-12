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
from functions import (CONFIG, connect_to_mongodb)


def listDevices(post_data={}):
  print (post_data)
  ts_start = time.time()
  rows = []
  arr_rs = {
    'data': [],
    'elasped_time':0,
    'code': 200
  }
  client = connect_to_mongodb()
  devices = client[post_data['db_name']][CONFIG['MONGODB']['tables']['device']]
  fields_query = {field: 1 for field in post_data['fields']} if post_data['fields'] else {}
  
  if post_data.get('device_uid'):
    filters = {'device_uid': post_data['device_uid']}
  elif post_data.get('uid'):
    filters = {'uid': post_data['uid']}    
  elif post_data.get('role') == 'admin':
    filters = {}
  elif post_data.get('role') == 'installer':
    filters = {'installer_id': post_data['user_id']}

  if post_data.get('filter'):
    filters.update(post_data['filter'])

  rows =  devices.find(filters, fields_query)
  
  for row in list(rows):
    del (row['_id'])
    new_row = {k: None for k in post_data['fields']}
    for r in row:
      new_row[r] = row[r]
      if isinstance(row[r], datetime.datetime):
        new_row[r] = str(row[r])
    # if not row.get('install_date'):
    #   new_row['install_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    arr_rs['data'].append(new_row)

  arr_rs['total_records'] = len(arr_rs['data'])
  arr_rs['elasped_time'] = round(time.time()-ts_start, 2)
  print (arr_rs)
  client.close()
  return arr_rs



def updateDeviceInfo(post_data={}):
  print (post_data)
  ts_start = time.time()
  arr_rs = {
    'data': [],
    'elasped_time':0,
    'code': 0
  }
  client = connect_to_mongodb()
  db = client[post_data['db_name']]
  devices = db[CONFIG['MONGODB']['tables']['device']]
  subscribers = db[CONFIG['MONGODB']['tables']['subscriber']]
  arr = {}
  for key in post_data:



    if key in ['db_name', 'format', 'user_id', 'role', 'page', 'meter_id_org']:
      continue
    if key in ['battery', 'last_count', 'last_timestamp', 'uptime', 'initial_count', 'maximum', 'minimum', 'ref_interval', 'server_port', 'error_count']:
      arr[key] = int(post_data[key])
    else:
      arr[key] = post_data[key]

  rs = devices.update_one(
    {'device_uid': post_data['device_uid']}, 
    {'$set': arr}
  )

  if post_data.get('meter_id_org'):
    subscribers.update_one(
      {'meter_id': post_data['meter_id_org']}, 
      {'$set': {
        'bind_device_id': None,
        'bind_date': None,
        'binded': False
        }
      }
    )
    
  subscribers.update_one(
    {'customer_no': post_data['customer_no']}, 
    {'$set': {
        'bind_device_id': post_data['device_uid'],
        'bind_date': datetime.datetime.now(),
        'binded': True
      }
    }
  )


  client.close()
  return {
    "code": 200,
    "elasped_time": round(time.time()-ts_start, 2),
    "data": {'modified_count': rs.modified_count}
  }


def updateInstallDeviceInfo(post_data = {}):
  print (post_data)
  # post_data: {'page': 'install_device_info', 'format': 'json', 'db_name': 'gas_demo', 'login_id': 'hanskim', 'role': 'admin', 'userseq': 'ca29e7325bf9825817bc185cb3435f49', 'device_uid': 'D4245A98', 'meter_id': '202465478965', 'install_date': '2025-03-06', 'initial_count': 0, 'ref_interval': 43200, 'flag': 'inactive', 'comment': '', 'customer_name': '이순신', 'customer_no': 'S12547896', 'subscriber_no': '1204365785'}
  # 설치 정보 업데이트
  ts_start = time.time()
  client = connect_to_mongodb()
  db = client[post_data['db_name']]
  devices = db[CONFIG['MONGODB']['tables']['device']]
  if post_data['flag'] == 'active' or post_data['flag'] == True:
    update_data = {
      'flag': True,
      'install_date': post_data['install_date'],
      'initial_count': int(post_data['initial_count']),
      'ref_interval': int(post_data['ref_interval']),
      'comment': post_data['comment']
    }

    subscribers = db[CONFIG['MONGODB']['tables']['subscriber']]
    rows =  subscribers.find({'meter_id': post_data['meter_id']})
    # {"customer_no":"S32649713","customer_name":"윤병일","addr_city":"서울시","addr_dist":"강남구","addr_dong":"신사동","addr_road":"638-2","addr_apt":"반도빌라","addr_detail":"반도빌라204","class":"4(G2.5)","share_house":"O","subscriber_no":"1204321613","meter_id":"365478965162","in_outdoor":"실내","category":"주택용","checked":true,"bind_date":"-","bind_device_id":"-","binded":"-"}

    print (rows)



      # subscribers.update_one(
      #   {'meter_id': row['meter_id']}, 
      #   {'$set': update_data}
      # )

  else:
    update_data = {
      'flag': False,
    }

  # rs = devices.update_one(
  #   {'device_uid': post_data['device_uid']}, 
  #   {'$set': update_data}
  # )

  client.close()
  return {
    "code": 200,
    "elasped_time": round(time.time()-ts_start, 2),
    # "data": {'modified_count': rs.modified_count}
  }

def updateReleaseProduct(post_data = {}):
    ts_start = time.time()
    client = connect_to_mongodb()
    users = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['common_user']]
    user = users.find_one({'ID': post_data['installer_id']})
    
    if not user:
        return {"code": 1004, "description": "no_user_id"}
    
    if not post_data['db_name']:
        post_data['db_name'] = user['db_name']
    
    devices_common = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['common_device']]
    devices_custom = client[post_data['db_name']][CONFIG['MONGODB']['tables']['device']]
    
    # 기존 디바이스 확인
    existing_devices = list(devices_common.find({'device_uid': {'$in': post_data['usnList']}}))
    existing_usns = [dev['device_uid'] for dev in existing_devices]
    
    # 새로 추가할 디바이스 필터링
    new_usns = [usn for usn in post_data['usnList'] if usn not in existing_usns]
    
    if new_usns:
        # common_device에 추가
        common_devices = [{'device_uid': usn, 'db_name': post_data['db_name']} for usn in new_usns]
        devices_common.insert_many(common_devices)
        
        # custom device 테이블에 추가
        custom_devices = [{
            'device_uid': usn,
            'release_date': post_data['release_date'],
            'installer_id': post_data['installer_id'],
            'comment': post_data['comment'],
            'flag': False
        } for usn in new_usns]
        result = devices_custom.insert_many(custom_devices)
        code = 200 if result.inserted_ids else 0
    else:
        code = 0
    
    client.close()
    return {
        "code": code,
        "elasped_time": round(time.time()-ts_start, 2),
        "data": {
            'exist': existing_usns,
            'added': new_usns
        }
    }






