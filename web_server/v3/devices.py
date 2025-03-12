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

def process_devices(post_data):
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
    elif action == 'release':
        return release_device(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def list_devices(post_data):
    print(__file__, __name__)
    """
    장치 목록 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 장치 목록
    """
    db_name = post_data.get('db_name')
    fields = post_data.get('fields', [])
    filter_data = post_data.get('filter', {})
    role = post_data.get('role', '')
    user_id = post_data.get('user_id', '')
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 장치 목록을 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    devices = [
        {
            "device_uid": "D4245A98",
            "meter_id": "202465478965",
            "install_date": "2025-03-06",
            "last_access": "2025-03-06 15:30:22",
            "last_count": 1234,
            "battery": 85,
            "flag": True
        },
        {
            "device_uid": "D4245A99",
            "meter_id": "202465478966",
            "install_date": None,
            "last_access": None,
            "last_count": None,
            "battery": None,
            "flag": False
        }
    ]
    
    # 필드 필터링
    if fields:
        filtered_devices = []
        for device in devices:
            filtered_device = {}
            for field in fields:
                if field in device:
                    filtered_device[field] = device[field]
            filtered_devices.append(filtered_device)
        devices = filtered_devices
    
    return {
        "code": 200,
        "data": devices,
        "total_records": len(devices)
    }

def view_device(post_data):
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
        "meter_id": "202465478965",
        "install_date": "2025-03-06",
        "last_access": "2025-03-06 15:30:22",
        "last_count": 1234,
        "battery": 85,
        "firmware_version": "1.0.3",
        "flag": True,
        "comment": "정기 점검 완료"
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
        "data": device,
        "total_records": 1
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
    장치 바인딩
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 바인딩 결과
    """
    db_name = post_data.get('db_name')
    device_uid = post_data.get('device_uid')
    meter_id = post_data.get('meter_id')
    
    if not db_name or not device_uid or not meter_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 장치 ID, 미터 ID가 필요합니다."
        }
    
    # 실제 구현에서는 장치와 미터를 바인딩합니다.
    
    return {
        "code": 200,
        "data": {
            "device_uid": device_uid,
            "meter_id": meter_id,
            "bind_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": "장치 바인딩 성공"
        }
    }

def release_device(post_data):
    """
    제품 출시 관리
    
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
    
    return {
        "code": 200,
        "data": {
            "released_count": len(device_uids),
            "installer_id": installer_id,
            "release_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": "제품 출시 성공"
        }
    } 