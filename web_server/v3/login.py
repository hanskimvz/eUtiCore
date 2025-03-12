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

import time
import hashlib, datetime
from functions import (CONFIG, connect_to_mongodb)


def proc_login(post_data= {}):
    print ("function login")
    level = {
        'admin':16, 
        'operator':8, 
        'installer':4, 
        'user':2, 
        'guest':1
    }
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
    c_user['level'] = level[c_user['role']]
    
    c_user = {k: v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime.datetime) else v for k, v in c_user.items()}
    
    return {"code": 200, "data": c_user}

def proc_logout(post_data):
    """
    로그아웃 처리
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 로그아웃 결과
    """
    login_id = post_data.get('login_id')
    session_token = post_data.get('session_token')
    
    if not login_id or not session_token:
        return {
            "code": 400,
            "message": "로그인 ID와 세션 토큰이 필요합니다."
        }
    
    # 실제 구현에서는 세션 토큰을 무효화합니다.
    
    return {
        "code": 200,
        "data": {
            "logout_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

def proc_register(post_data):
    # 'data': {'ID': 'user1', 'name': 'User One', 'email': 'user1@example.com', 'password': '123456', 'role': 'user', 'lang': 'kor', 'flag': False}
    
    if not post_data.data.get('ID') or not post_data.data.get('name') or not post_data.data.get('email') or not post_data.data.get('password'):
        return {
            "code": 400,
            "message": "로그인 ID, 비밀번호, 이름, 이메일이 필요합니다."
        }
    client = connect_to_mongodb()
    floating_user = client[CONFIG['MONGODB']['db']][CONFIG['MONGODB']['tables']['floating_user']]
    e = floating_user.find_one({'ID': post_data.data.get('ID')})
    if e:
        return {
            "code": 409,
            "message": "이미 사용 중인 로그인 ID입니다."
        }
    e = floating_user.find_one({'email': post_data.data.get('email')})
    if e:
        return {
            "code": 409,
            "message": "이미 사용 중인 이메일입니다."
        }
    
    # 비밀번호 해시 생성
    hashed_password = hashlib.sha256(post_data.data.get('password').encode()).hexdigest()
    post_data.data['passwd'] = hashed_password
    post_data.data['flag'] = False
    post_data.data['level'] = 2
    post_data.data['userseq'] = hashlib.md5((post_data.data.get('ID') + 'hanskim').encode()).hexdigest()
    post_data.data['regdate'] = time.strftime("%Y-%m-%d %H:%M:%S")
    post_data.data['regdate'] = time.strftime("%Y-%m-%d %H:%M:%S")
   

    
    client.close()
    # 회원가입 성공
    return {
        "code": 200,
        "data": {
            "login_id": login_id,
            "name": name,
            "email": email,
            "phone": phone,
            "role": "user",
            "register_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "approved": False,
            "message": "회원가입이 완료되었습니다. 관리자 승인 후 로그인이 가능합니다."
        }
    } 