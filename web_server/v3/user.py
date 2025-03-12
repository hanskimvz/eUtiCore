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
import hashlib
import random
from functions import (CONFIG, connect_to_mongodb)

def process_users(post_data):
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
        return list_users(post_data)
    elif action == 'view':
        return view_user(post_data)
    elif action == 'modify':
        return modify_user(post_data)
    elif action == 'delete':
        return delete_user(post_data)

    elif action == 'add':
        return add_user(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def process_floating_user(post_data):   
    action = post_data.get('action', '')
    if action == 'list':
        return list_floating_users(post_data)
    elif action == 'approve':
        return approve_user(post_data)    
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }
    
def list_users(post_data):
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
        del (row['_id'])
        new_row = {k: None for k in post_data['fields']}
        for r in row:
            new_row[r] = row[r]
            if isinstance(row[r], datetime.datetime):
                new_row[r] = str(row[r])
        arr_rs['data'].append(new_row)
    
    client.close()

    arr_rs['code'] = 200
    arr_rs['elasped_time'] = round(time.time()-ts_start, 2)
    arr_rs['total_records'] = len(arr_rs['data'])
    return arr_rs

def view_user(post_data):
    """
    사용자 상세 정보 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 사용자 정보
    """
    db_name = post_data.get('db_name')
    user_id = post_data.get('user_id')
    fields = post_data.get('fields', [])
    
    if not db_name or not user_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 사용자 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 사용자 정보를 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    user = {
        "userseq": 2,
        "login_id": user_id,
        "name": "홍길동",
        "email": "user1@example.com",
        "phone": "010-2345-6789",
        "role": "user",
        "created_at": "2023-01-02 00:00:00",
        "last_login": "2023-06-02 12:34:56",
        "address": "서울시 강남구",
        "company": "ABC 주식회사",
        "department": "개발팀"
    }
    
    # 필드 필터링
    if fields:
        filtered_user = {}
        for field in fields:
            if field in user:
                filtered_user[field] = user[field]
        user = filtered_user
    
    return {
        "code": 200,
        "data": user
    }

def modify_user(post_data):
    """
    사용자 정보 수정
    Args:
    post_data: {'action': 'modify', 'format': 'json', 'db_name': 'gas_demo', 'login_id': 'hanskim', 'role': 'admin', 'userseq': 'ca29e7325bf9825817bc185cb3435f49', 'data': {'code': 'U25031006262465', 'ID': 'user1', 'name': 'User One', 'email': 'user1@example.com', 'user_role': 'user', 'lang': 'kor', 'groups': '', 'flag': True, 'comment': ''}}
        
    Returns:
        dict: 수정 결과
    """
    db_name = post_data.get('db_name')
    ID = post_data['data'].get('ID')
    name = post_data['data'].get('name')
    email = post_data['data'].get('email')
    user_role = post_data['data'].get('user_role')
    lang = post_data['data'].get('lang')
    groups = post_data['data'].get('groups')
    flag = post_data['data'].get('flag')
    comment = post_data['data'].get('comment')
    
    if not db_name or not ID or not name or not email or not user_role or not lang:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 사용자 ID, 수정할 데이터가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 사용자 정보를 수정합니다.
    client = connect_to_mongodb()
    users = client[db_name][CONFIG['MONGODB']['tables']['user']]
    set_data = {
        'name': name, 
        'email': email, 
        'role': user_role, 
        'lang': lang, 
        'groups': groups if groups else '', 
        'flag': flag, 
        'comment': comment
    }
    r = users.update_one({'ID': ID}, {'$set': set_data})
    client.close()
    return {
        "code": 200,
        "data": {
            "update_result": r.raw_result
        }
    }

def delete_user(post_data):
    """
    data': {'code': '', 'ID': 'user1'}
    """
    db_name = post_data.get('db_name')
    code = post_data['data'].get('code')
    ID = post_data['data'].get('ID')

    client = connect_to_mongodb()
    users = client[db_name][CONFIG['MONGODB']['tables']['user']]
    floating_user = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['floating_user']]
    user_route = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['common_user']]

    r = floating_user.delete_one({'$or': [{'code': code}, {'ID': ID}]})
    print ('floating_user delete:', r)
    r = users.delete_one({'$or': [{'code': code}, {'ID': ID}]})
    print ('users delete:', r)
    r = user_route.delete_one({'$or': [{'code': code}, {'ID': ID}]})
    print ('user_route delete:', r)
    client.close()
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 1
        }
    }

def add_user(post_data):
    # 'data': {'ID': 'user1', 'name': 'User One', 'email': 'user1@example.com', 'password': '123456', 'role': 'user', 'lang': 'kor', 'flag': True, 'comment': ''}

    level = {
        'admin':16, 
        'operator':8, 
        'installer':4, 
        'user':2, 
        'guest':1
    }
    db_name = post_data.get('db_name')
    ID = post_data['data'].get('ID')
    name = post_data['data'].get('name')
    email = post_data['data'].get('email')
    password = post_data['data'].get('password')
    role = post_data['data'].get('role')
    lang = post_data['data'].get('lang')
    flag = post_data['data'].get('flag')
    comment = post_data['data'].get('comment')

    if not db_name or not ID or not name or not password or not email:
        return {
            "code": 400,
            "message": "database name, user id, name, password are required."
        }
    
    client = connect_to_mongodb()
    floating_user = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['floating_user']]
    user_route = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['common_user']]
    users = client[db_name][CONFIG['MONGODB']['tables']['user']]

    e = floating_user.find_one({'ID': ID})
    if e:
        return {
            "code": 400,
            "message": "user id already exists."
        }
    e = floating_user.find_one({'email': email})
    if e:
        return {
            "code": 400,
            "message": "email already exists."
        }

    # 비밀번호 해시 생성
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # 사용자 라우트 생성
    r = user_route.update_one({
        'ID': ID,
    }, {
        '$set': {
            'db_name': db_name,
        }
    }, upsert=True)

    r = floating_user.insert_one({
        'regdate': time.strftime("%Y-%m-%d %H:%M:%S"),
        'ID': ID,
        'name': name,
        'email': email,
        'flag': True,
    })

    r = users.insert_one({
        'regdate': time.strftime("%Y-%m-%d %H:%M:%S"),
        'code': 'U'+ time.strftime('%y%m%d%H%M%S') + str(random.randint(10, 99)),
        'ID': ID,
        'name': name,
        'email': email,
        'passwd': hashed_password,
        'userseq': hashlib.md5((ID + 'hanskim').encode()).hexdigest(),
        'level': level[role],
        'role': role,
        'lang': lang,
        'flag': flag,
        'comment': comment,
    })
    
    client.close()
    return {
        "code": 200,
        "data": {
            "user_id": ID,
            "user_name": name,
            "user_role": role,
            "created": True
        }
    }


def list_floating_users(post_data):
    db_name = post_data.get('db_name')
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 미승인 사용자 목록 조회
    client = connect_to_mongodb()
    floating_users = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['floating_user']]
    rows = floating_users.find({'flag': False})
    arr = []
    for row in rows:
        print (row)
        del (row['_id'])
        if isinstance(row['regdate'], datetime.datetime):
            row['regdate'] = str(row['regdate'])
        arr.append(row)
    client.close()

    return  {
        'code': 200,
        'data': arr,
        'total_records': len(arr)
    }

def approve_user(post_data):
    """
    미승인 사용자 승인
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 승인 결과
    """
    db_name = post_data.get('db_name')
    user_id = post_data.get('user_id')
    
    if not db_name or not user_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 사용자 ID가 필요합니다."
        }
    
    # 실제 구현에서는 floating_users 테이블에서 users 테이블로 사용자를 이동합니다.
    
    return {
        "code": 200,
        "data": {
            "approved": True,
            "user_id": user_id
        }
    } 