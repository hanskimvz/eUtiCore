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

import json
import time, datetime
from functions import (CONFIG, connect_to_mongodb)

def process_devices(post_data):
    print(__file__, __name__)
    """
    장치 관리 관련 요청을 처리하는 함수
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 처리 결과
    """
    # 인증 확인
    login_id = post_data.get('login_id')
    userseq = post_data.get('userseq')
    
    if not login_id or not userseq:
        return {
            "code": 401,
            "message": "인증 정보가 필요합니다."
        }
    
    # 액션에 따른 처리
    action = post_data.get('action', '')
    
    if action == 'list':
        return list_devices(post_data)
    elif action == 'view':
        return view_device(post_data)
    elif action == 'modify':
        return modify_device(post_data)
    elif action == 'delete':
        return delete_device(post_data)
    elif action == 'bind':
        return bind_device(post_data)
    elif action == 'unbind':
        return unbind_device(post_data)    
    elif action == 'release':
        return release_device(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def list_devices(post_data):
    client = connect_to_mongodb()
    devices = client[post_data['db_name']][CONFIG['MONGODB']['tables']['device']]
    fields_query = {field: 1 for field in post_data.get('fields', [])}
    
    filters = {}
    if post_data.get('role') == 'installer':
        filters = {'installer_id': post_data['user_id']}

    if post_data.get('filter'):
        filters.update(post_data['filter'])

    rows =  devices.find(filters, fields_query)
    arr = []
    for row in list(rows):
        del (row['_id'])
        for r in row:
            if isinstance(row[r], datetime.datetime):
                row[r] = str(row[r])
            elif isinstance(row[r], bytes):
                row[r] = str(row[r].decode())
        arr.append(row)
    client.close()
    return {
        "code": 200,
        "data": arr,
        'total_records': len(arr),
    }


def view_device(post_data):
    """
    post_data: {'action': 'view', 'format': 'json', 'device_uid': 'F68C057D', 'db_name': 'gas_demo', 'login_id': 'hanskim', 'role': 'admin', 'userseq': 'ca29e7325bf9825817bc185cb3435f49', 'level': '16'}
    """
    client = connect_to_mongodb()
    devices = client[post_data['db_name']][CONFIG['MONGODB']['tables']['device']]
    
    fields_query = {field: 1 for field in post_data.get('fields', [])}
    filters = {}
    if post_data.get('device_uid'):
        filters = {'device_uid': post_data.get('device_uid')}
    elif post_data.get('meter_id'):
        filters = {'meter_id': post_data.get('meter_id')}

    data = {}
    if filters:
        data = devices.find_one(filters, fields_query)
    
        if data:
            del (data['_id'])
            for r in data:
                if isinstance(data[r], datetime.datetime):
                    data[r] = str(data[r])
                elif isinstance(data[r], bytes):
                    data[r] = str(data[r].decode())
    
        client.close()  
    return {
        "code": 200,
        "data": data
    }



    """
    장치 상세 정보 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 장치 정보
    """
    db_name = post_data.get('db_name')
    device_uid = post_data.get('device_uid')
    fields = post_data.get('fields', [])
    
    if not db_name or not device_uid:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 장치 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 장치 정보를 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    device = {
        "device_uid": device_uid,
        "device_name": "가스미터 1",
        "device_type": "gas_meter",
        "firmware_version": "1.0.0",
        "hardware_version": "1.0.0",
        "status": "active",
        "last_seen": "2023-06-01 12:34:56",
        "battery_level": 85,
        "signal_strength": 75,
        "meter_id": "123456789012",
        "customer_no": "S12345678",
        "installation_date": "2023-01-15",
        "installation_location": "실내",
        "installation_note": "현관 옆 벽면",
        "installer_id": "I12345",
        "installer_name": "김설치",
        "maintenance_history": [
            {
                "date": "2023-03-10",
                "type": "battery_replacement",
                "note": "배터리 교체"
            },
            {
                "date": "2023-05-20",
                "type": "firmware_update",
                "note": "펌웨어 업데이트"
            }
        ]
    }
    
    # 필드 필터링
    if fields:
        filtered_device = {}
        for field in fields:
            if field in device:
                filtered_device[field] = device[field]
        device = filtered_device
    
    return {
        "code": 200,
        "data": device
    }

def modify_device(post_data):
    """
    장치 정보 수정
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 수정 결과
    """
    db_name = post_data.get('db_name')
    device_uid = post_data.get('device_uid')
    data = post_data.get('data', {})
    
    if not db_name or not device_uid or not data:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 장치 ID, 수정할 데이터가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 장치 정보를 수정합니다.
    
    return {
        "code": 200,
        "data": {
            "modified_count": 1
        }
    }

def delete_device(post_data):
    """
    장치 삭제
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 삭제 결과
    """
    db_name = post_data.get('db_name')
    device_uid = post_data.get('device_uid')
    
    if not db_name or not device_uid:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 장치 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 장치를 삭제합니다.
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 1
        }
    }

def bind_device(post_data):
    """
    'data': {'device_uid': 'A149490D', 'meter_id': '202465478965', 'install_date': '2025-03-10', 'initial_count': 2543, 'ref_interval': 43200, 'comment': ''},
    """
    db_name = post_data.get('db_name')
    device_uid = post_data['data'].get('device_uid')
    meter_id = post_data['data'].get('meter_id')
    
    if not db_name or not device_uid or not meter_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 장치 ID, 미터 ID가 필요합니다."
        }
    
    # 실제 구현에서는 장치와 미터를 바인딩합니다.
    
    bind_date = time.strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "code": 200,
        "data": {
            "bind_date": bind_date,
            "binded": True
        }
    }
def unbind_device(post_data):
    """
    'data': {'device_uid': 'AE4638F0', 'meter_id': '365478965122', 'install_date': '2025-03-10', 'initial_count': 35723, 'ref_interval': 43200, 'comment': ''},
    """
    db_name = post_data.get('db_name')
    device_uid = post_data['data'].get('device_uid')
    meter_id = post_data['data'].get('meter_id')
    
    if not db_name or not device_uid:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 장치 ID가 필요합니다."
        }
    
    # 실제 구현에서는 장치와 미터를 바인딩 해제합니다.
    
    return {
        "code": 200,
        "data": {
            "unbinded": True
        }
    }

def release_device(post_data):
    """
    장치 출시 관리 (설치자에게 장치 출시)
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 출시 결과
    """
    db_name = post_data.get('db_name')
    device_uids = post_data.get('device_uids', [])
    installer_id = post_data.get('installer_id')
    
    if not db_name or not device_uids or not installer_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 장치 ID 목록, 설치자 ID가 필요합니다."
        }
    
    # 실제 구현에서는 장치를 설치자에게 출시합니다.
    
    release_date = time.strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "code": 200,
        "data": {
            "release_date": release_date,
            "released_count": len(device_uids),
            "released_devices": device_uids,
            "installer_id": installer_id
        }
    } 