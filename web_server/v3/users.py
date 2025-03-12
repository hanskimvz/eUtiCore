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
import json
import hashlib

def process_users(post_data):
    """
    사용자 관리 관련 요청을 처리하는 함수
    
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
        return list_users(post_data)
    elif action == 'view':
        return view_user(post_data)
    elif action == 'modify':
        return modify_user(post_data)
    elif action == 'delete':
        return delete_user(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def list_users(post_data):
    """
    사용자 목록 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 사용자 목록
    """
    db_name = post_data.get('db_name')
    fields = post_data.get('fields', [])
    filter_data = post_data.get('filter', {})
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 사용자 목록을 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    users = [
        {
            "user_id": "hanskim",
            "name": "김한수",
            "email": "hans.kim@example.com",
            "role": "admin",
            "regdate": "2025-01-01 00:00:00"
        },
        {
            "user_id": "johndoe",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "user",
            "regdate": "2025-01-02 00:00:00"
        }
    ]
    
    # 필드 필터링
    if fields:
        filtered_users = []
        for user in users:
            filtered_user = {}
            for field in fields:
                if field in user:
                    filtered_user[field] = user[field]
            filtered_users.append(filtered_user)
        users = filtered_users
    
    return {
        "code": 200,
        "data": users,
        "total_records": len(users)
    }

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
        "user_id": user_id,
        "name": "김한수",
        "email": "hans.kim@example.com",
        "role": "admin",
        "regdate": "2025-01-01 00:00:00",
        "last_login": "2025-03-15 12:34:56"
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
        "data": user,
        "total_records": 1
    }

def modify_user(post_data):
    """
    사용자 정보 수정
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 수정 결과
    """
    db_name = post_data.get('db_name')
    user_id = post_data.get('user_id')
    data = post_data.get('data', {})
    
    if not db_name or not user_id or not data:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 사용자 ID, 수정할 데이터가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 사용자 정보를 수정합니다.
    
    return {
        "code": 200,
        "data": {
            "modified_count": 1
        }
    }

def delete_user(post_data):
    """
    사용자 삭제
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 삭제 결과
    """
    db_name = post_data.get('db_name')
    user_id = post_data.get('user_id')
    
    if not db_name or not user_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 사용자 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 사용자를 삭제합니다.
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 1
        }
    } 