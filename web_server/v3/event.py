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
import time
from datetime import datetime, timedelta

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
    fields = post_data.get('fields', [])
    filter_data = post_data.get('filter', {})
    page = post_data.get('page', 1)
    page_size = post_data.get('page_size', 10)
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 이벤트 목록을 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    events = [
        {
            "event_id": "E12345",
            "device_uid": "D1234A56",
            "event_type": "gas_leak",
            "event_level": "critical",
            "event_time": "2023-06-01 12:34:56",
            "event_value": 120,
            "event_status": "active",
            "event_message": "가스 누출 감지",
            "customer_no": "S12345678"
        },
        {
            "event_id": "E12346",
            "device_uid": "D2345B67",
            "event_type": "low_battery",
            "event_level": "warning",
            "event_time": "2023-06-02 10:20:30",
            "event_value": 15,
            "event_status": "active",
            "event_message": "배터리 부족",
            "customer_no": "S23456789"
        },
        {
            "event_id": "E12347",
            "device_uid": "D3456C78",
            "event_type": "connection_lost",
            "event_level": "warning",
            "event_time": "2023-06-03 09:15:45",
            "event_value": 0,
            "event_status": "resolved",
            "event_message": "연결 끊김",
            "customer_no": "S34567890"
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
    
    # 페이지네이션
    total_records = len(events)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_events = events[start_idx:end_idx]
    
    return {
        "code": 200,
        "data": paginated_events,
        "total_records": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_records + page_size - 1) // page_size
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
        "device_uid": "D1234A56",
        "device_name": "가스미터 1",
        "event_type": "gas_leak",
        "event_level": "critical",
        "event_time": "2023-06-01 12:34:56",
        "event_value": 120,
        "event_status": "active",
        "event_message": "가스 누출 감지",
        "customer_no": "S12345678",
        "customer_name": "홍길동",
        "addr_city": "서울시",
        "addr_dist": "강남구",
        "addr_dong": "신사동",
        "addr_detail": "반도빌라204",
        "notification_sent": True,
        "notification_time": "2023-06-01 12:35:00",
        "notification_recipients": [
            {
                "type": "sms",
                "recipient": "010-1234-5678",
                "status": "sent"
            },
            {
                "type": "email",
                "recipient": "user1@example.com",
                "status": "sent"
            }
        ],
        "actions_taken": [
            {
                "action_type": "auto_shutdown",
                "action_time": "2023-06-01 12:35:05",
                "action_status": "success",
                "action_message": "가스 밸브 자동 차단"
            }
        ]
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
        "data": event
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
    
    # 실제 구현에서는 데이터베이스에서 필터 조건에 맞는 이벤트를 일괄 삭제합니다.
    
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
        dict: 이벤트 통계
    """
    db_name = post_data.get('db_name')
    start_date = post_data.get('start_date')
    end_date = post_data.get('end_date')
    group_by = post_data.get('group_by', 'event_type')
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 이벤트 통계를 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    # 예시 통계 데이터
    if group_by == 'event_type':
        stats = {
            "gas_leak": 12,
            "low_battery": 25,
            "connection_lost": 18,
            "high_usage": 8,
            "tamper_detected": 3
        }
    elif group_by == 'event_level':
        stats = {
            "critical": 15,
            "warning": 35,
            "info": 16
        }
    elif group_by == 'event_status':
        stats = {
            "active": 28,
            "resolved": 38
        }
    elif group_by == 'date':
        # 날짜별 통계 예시
        stats = {
            "2023-06-01": 15,
            "2023-06-02": 12,
            "2023-06-03": 18,
            "2023-06-04": 10,
            "2023-06-05": 8
        }
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 그룹화 기준: {group_by}"
        }
    
    return {
        "code": 200,
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "group_by": group_by,
            "stats": stats
        }
    } 