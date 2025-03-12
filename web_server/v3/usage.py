# Copyright (c) 2025, Hans kim(hanskimvz@gmail.com)

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

import time, datetime
from functions import (CONFIG, connect_to_mongodb)
from .device import list_devices

def process_usage(post_data):
    action = post_data.get('action', '')  
    
    if action == 'list':
        return list_customer_with_usage(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def get_first_day_of_this_month(): 
    # 현재 날짜 가져오기
    today = datetime.datetime.now()
    
    # 이번 달의 첫 날 자정(00:00:00) 구하기
    first_day_midnight = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
    
    # 원하는 형식으로 반환
    return first_day_midnight.strftime('%Y-%m-%d %H:%M:%S')

def get_count_at(collection, device_uid, ts):
    # print(collection, device_uid, ts)
    doc = collection.find_one({
        'device_uid': str(device_uid),
        'timestamp': {'$lte': ts}
    }, sort=[("timestamp", -1)])
    if not doc :
        return {
            "counter_val": 0,
            "timestamp": 0,
            "device_uid": device_uid,
            "year": 0,
            "month": 0,
            "day": 0,
            "hour": 0
        }
    
    del doc['_id']
    return doc

def list_customer_with_usage(post_data):
    # 먼저 고객 정보를 조회해서 list로 만든다.
    # 그리고 각 고객별 사용량 데이터를 조회해서 추가한다.
    # 그리고 그 데이터를 반환한다.
    post_data['filter'] = {'flag': True}
    post_data['fields'] = [
        'device_uid',
        'customer_name', 
        'customer_no', 
        'addr_prov', 'addr_city', 'addr_dist', 'addr_detail', 'addr_apt', 
        'meter_id', 'last_count','last_access'
    ]
    client = connect_to_mongodb()
    db = client[post_data['db_name']]
    devices   = db[CONFIG['MONGODB']['tables']['device']]
    countdata = db[CONFIG['MONGODB']['tables']['data']] 

    device_list = devices.find(post_data['filter'], {field: 1 for field in post_data['fields']})
    
    today = datetime.datetime.now()
    ts_firstday = int(datetime.datetime(today.year, today.month, 1, 0, 0, 0).timestamp())
    # print(ts_firstday)

    arr = []
    for d in device_list:
        count_at = get_count_at(countdata, d['device_uid'], ts_firstday)
        usage = d.get('last_count', 0) - count_at['counter_val'] if count_at['timestamp']  else 0

        arr.append({
            'customer_name': d['customer_name'], 
            'customer_no':   d['customer_no'], 
            'addr_prov':   d.get('addr_prov', ''),
            'addr_city':   d.get('addr_city', ''),
            'addr_dist':   d.get('addr_dist', ''),
            'addr_detail': d.get('addr_detail', ''),
            'addr_apt':    d.get('addr_apt', ''),
            'meter_id':      d['meter_id'], 
            'prev_count':    count_at['counter_val'] if count_at['timestamp']  else 0, 
            'current_count': d['last_count'] if d.get('last_count') else 0, 
            'read_date':     time.strftime('%Y-%m-%d', time.strptime(d['last_access'], '%Y-%m-%d %H:%M:%S')) if d.get('last_access') else "-", 
            'usage':         usage if usage > 0 else 0, 
            'cost':          usage * 100 if usage > 0 else 0
        })
    
    client.close()

    for r in arr:
        print(r)

    return {
        "code": 200,
        "data": arr,
        "total_records": len(arr)
    }
    