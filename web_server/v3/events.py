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

def process_events(post_data):
    """
    이벤트 관리 관련 요청을 처리하는 함수
    
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
        return list_events(post_data)
    elif action == 'view':
        return view_event(post_data)
    elif action == 'modify':
        return modify_event(post_data)
    elif action == 'delete':
        return delete_event(post_data)
    elif action == 'bulk_delete':
        return bulk_delete_events(post_data)
    elif action == 'stats':
        return stats_events(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def list_events(post_data):
    """
    이벤트 목록 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 이벤트 목록
    """
    db_name = post_data.get('db_name')
    device_uid = post_data.get('device_uid')
    fields = post_data.get('fields', [])
    filter_data = post_data.get('filter', {})
    start_date = post_data.get('start_date')
    end_date = post_data.get('end_date')
    resolved = post_data.get('resolved')
    event_type = post_data.get('event_type')
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 이벤트 목록을 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    events = [
        {
            "event_id": "EVT20250315001",
            "device_uid": "D4245A98",
            "timestamp": 1741459200,
            "datetime": "2025-03-15 12:00:00",
            "event_type": "alarm",
            "event_message": "가스 누출 감지",
            "resolved": False
        },
        {
            "event_id": "EVT20250312002",
            "device_uid": "D4245A99",
            "timestamp": 1741200000,
            "datetime": "2025-03-12 10:00:00",
            "event_type": "alarm",
            "event_message": "배터리 부족",
            "resolved": False
        },
        {
            "event_id": "EVT20250310003",
            "device_uid": "D4245B01",
            "timestamp": 1741027200,
            "datetime": "2025-03-10 09:00:00",
            "event_type": "alarm",
            "event_message": "통신 오류",
            "resolved": False
        }
    ]
    
    # 필드 필터링
    if fields:
        filtered_events = []
        for event in events:
            filtered_event = {}
            for field in fields:
                if field in event:
                    filtered_event[field] = event[field]
            filtered_events.append(filtered_event)
        events = filtered_events
    
    return {
        "code": 200,
        "data": events,
        "total_records": len(events)
    }

def view_event(post_data):
    """
    이벤트 상세 정보 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 이벤트 정보
    """
    db_name = post_data.get('db_name')
    event_id = post_data.get('event_id')
    fields = post_data.get('fields', [])
    
    if not db_name or not event_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 이벤트 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 이벤트 정보를 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    event = {
        "event_id": event_id,
        "device_uid": "D4245A98",
        "timestamp": 1741459200,
        "datetime": "2025-03-15 12:00:00",
        "event_type": "alarm",
        "event_code": "GAS_LEAK",
        "event_message": "가스 누출 감지",
        "resolved": False,
        "resolved_timestamp": None,
        "resolved_datetime": None,
        "resolved_by": None,
        "resolution_note": None,
        "severity": 4,
        "notify": True
    }
    
    # 필드 필터링
    if fields:
        filtered_event = {}
        for field in fields:
            if field in event:
                filtered_event[field] = event[field]
        event = filtered_event
    
    return {
        "code": 200,
        "data": event,
        "total_records": 1
    }

def modify_event(post_data):
    """
    이벤트 정보 수정
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 수정 결과
    """
    db_name = post_data.get('db_name')
    event_id = post_data.get('event_id')
    data = post_data.get('data', {})
    
    if not db_name or not event_id or not data:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 이벤트 ID, 수정할 데이터가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 이벤트 정보를 수정합니다.
    
    # 이벤트 해제 처리
    if 'resolved' in data and data['resolved']:
        current_time = time.time()
        current_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
        
        if 'resolved_timestamp' not in data:
            data['resolved_timestamp'] = current_time
        
        if 'resolved_datetime' not in data:
            data['resolved_datetime'] = current_datetime
        
        if 'resolved_by' not in data:
            data['resolved_by'] = post_data.get('login_id')
    
    return {
        "code": 200,
        "data": {
            "modified_count": 1
        }
    }

def delete_event(post_data):
    """
    이벤트 삭제
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 삭제 결과
    """
    db_name = post_data.get('db_name')
    event_id = post_data.get('event_id')
    
    if not db_name or not event_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 이벤트 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 이벤트를 삭제합니다.
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 1
        }
    }

def bulk_delete_events(post_data):
    """
    이벤트 일괄 삭제
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 삭제 결과
    """
    db_name = post_data.get('db_name')
    filter_data = post_data.get('filter', {})
    
    if not db_name or not filter_data:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 필터 조건이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 이벤트를 일괄 삭제합니다.
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 5
        }
    }

def stats_events(post_data):
    """
    이벤트 통계 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 통계 정보
    """
    db_name = post_data.get('db_name')
    device_uid = post_data.get('device_uid')
    start_date = post_data.get('start_date')
    end_date = post_data.get('end_date')
    group_by = post_data.get('group_by')
    
    if not db_name or not start_date or not end_date or not group_by:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 시작 날짜, 종료 날짜, 그룹화 기준이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 통계 정보를 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    if group_by == 'event_type':
        stats = [
            {
                "event_type": "alarm",
                "count": 15,
                "resolved_count": 10,
                "unresolved_count": 5
            },
            {
                "event_type": "warning",
                "count": 25,
                "resolved_count": 20,
                "unresolved_count": 5
            },
            {
                "event_type": "info",
                "count": 50,
                "resolved_count": 50,
                "unresolved_count": 0
            },
            {
                "event_type": "error",
                "count": 5,
                "resolved_count": 3,
                "unresolved_count": 2
            }
        ]
    else:
        stats = []
    
    return {
        "code": 200,
        "data": stats,
        "total_records": len(stats)
    } 