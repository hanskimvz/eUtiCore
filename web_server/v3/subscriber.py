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

def process_subscribers(post_data):
    """
    구독자 관리 관련 요청을 처리하는 함수
    
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
        return list_subscribers(post_data)
    elif action == 'view':
        return view_subscriber(post_data)
    elif action == 'modify':
        return modify_subscriber(post_data)
    elif action == 'delete':
        return delete_subscriber(post_data)
    elif action == 'bind':
        return bind_subscriber(post_data)
    elif action == 'import':
        return import_subscribers(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def list_subscribers(post_data):

    if not post_data.get('filter'):
        post_data['filter'] = {}
    
    field_query = {}
    if post_data.get('fields'):
        field_query = {field: 1 for field in post_data['fields']} if post_data['fields'] else {}

    client = connect_to_mongodb()
    collection = client[post_data['db_name']][CONFIG['MONGODB']['tables']['subscriber']]
    total_records = collection.count_documents(post_data['filter'])

    rows = collection.find(post_data['filter'], field_query)

    arr = []

    for row in list(rows):
        del row['_id']
        for r in row:
            if isinstance(row[r], datetime.datetime):
                row[r] = str(row[r])
            elif isinstance(row[r], bytes):
                try:
                    row[r] = str(row[r].decode())
                except:
                    row[r] = row[r].hex()

        arr.append(row)

    client.close()
    return {
        "code": 200,
        "data": arr,
        "total_records": total_records
    }

def view_subscriber(post_data):
    field_query = {}
    if post_data.get('fields'):
        field_query = {field: 1 for field in post_data['fields']} if post_data['fields'] else {}

    client = connect_to_mongodb()
    collection = client[post_data['db_name']][CONFIG['MONGODB']['tables']['subscriber']]
    data = collection.find_one({'meter_id': post_data['meter_id']}, field_query)
    if data:
        for r in data:
            if isinstance(data[r], datetime.datetime):
                data[r] = str(data[r])
            elif isinstance(data[r], bytes):
                data[r] = str(data[r].decode())
        del data['_id']
    else:
        data = {}
    client.close()
    return {
        "code": 200,
        "data": data
    }

def modify_subscriber(post_data):
    """
    구독자 정보 수정
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 수정 결과
    """
    db_name = post_data.get('db_name')
    customer_no = post_data.get('customer_no')
    data = post_data.get('data', {})
    
    if not db_name or not customer_no or not data:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 고객 번호, 수정할 데이터가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 구독자 정보를 수정합니다.
    
    return {
        "code": 200,
        "data": {
            "modified_count": 1
        }
    }

def delete_subscriber(post_data):
    """
    구독자 삭제
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 삭제 결과
    """
    db_name = post_data.get('db_name')
    customer_no = post_data.get('customer_no')
    
    if not db_name or not customer_no:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 고객 번호가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 구독자를 삭제합니다.
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 1
        }
    }

def bind_subscriber(post_data):
    """
    구독자-장치 바인딩
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 바인딩 결과
    """
    db_name = post_data.get('db_name')
    customer_no = post_data.get('customer_no')
    meter_id = post_data.get('meter_id')
    device_uid = post_data.get('device_uid')
    
    if not db_name or not customer_no or not meter_id or not device_uid:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 고객 번호, 미터 ID, 장치 ID가 필요합니다."
        }
    
    # 실제 구현에서는 구독자와 장치를 바인딩합니다.
    
    bind_date = time.strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "code": 200,
        "data": {
            "bind_date": bind_date,
            "binded": True
        }
    }

def import_subscribers(post_data):
    """
    구독자 데이터 일괄 가져오기
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 가져오기 결과
    """
    db_name = post_data.get('db_name')
    data = post_data.get('data', [])
    
    if not db_name or not data:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 가져올 데이터가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에 구독자 데이터를 일괄 삽입합니다.
    
    # 가져오기 결과
    import_count = 0
    import_records = []
    duplicated_count = 0
    duplicated_records = []
    failed_count = 0
    failed_records = []
    
    # 데이터 처리
    for item in data:
        if 'customer_no' not in item:
            failed_records.append({
                "error": "필수 필드 누락: customer_no"
            })
            failed_count += 1
            continue
        
        # 예시: 중복 체크
        if item.get('customer_no') == 'S45678901':
            duplicated_records.append({
                "customer_no": item.get('customer_no'),
                "customer_name": item.get('customer_name'),
                "subscriber_no": item.get('subscriber_no'),
                "error": "중복된 고객 번호"
            })
            duplicated_count += 1
            continue
        
        # 예시: 필수 필드 체크
        if 'meter_id' not in item:
            failed_records.append({
                "customer_no": item.get('customer_no'),
                "error": "필수 필드 누락: meter_id"
            })
            failed_count += 1
            continue
        
        # 예시: 데이터 형식 체크
        if item.get('share_house') not in ['O', 'X']:
            failed_records.append({
                "customer_no": item.get('customer_no'),
                "error": "유효하지 않은 데이터 형식: share_house"
            })
            failed_count += 1
            continue
        
        # 성공적으로 가져온 레코드
        import_records.append({
            "customer_no": item.get('customer_no'),
            "customer_name": item.get('customer_name'),
            "subscriber_no": item.get('subscriber_no')
        })
        import_count += 1
    
    return {
        "code": 200,
        "data": {
            "import_count": import_count,
            "import_records": import_records,
            "duplicated_count": duplicated_count,
            "duplicated_records": duplicated_records,
            "failed_count": failed_count,
            "failed_records": failed_records
        }
    } 