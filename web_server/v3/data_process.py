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
import datetime
import random
from datetime import timedelta

def process_data(post_data):
    """
    데이터 관리 관련 요청을 처리하는 함수
    
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
        return list_data(post_data)
    elif action == 'view':
        return view_data(post_data)
    elif action == 'modify':
        return modify_data(post_data)
    elif action == 'delete':
        return delete_data(post_data)
    elif action == 'bulk_delete':
        return bulk_delete_data(post_data)
    elif action == 'stats':
        return stats_data(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def list_data(post_data):
    """
    데이터 목록 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 데이터 목록
    """
    db_name = post_data.get('db_name')
    device_uids = post_data.get('device_uids', [])
    start_date = post_data.get('start_date')
    end_date = post_data.get('end_date')
    fields = post_data.get('fields', [])
    page = post_data.get('page', 1)
    page_size = post_data.get('page_size', 10)
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 데이터 목록을 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    data_list = [
        {
            "data_id": "D12345",
            "device_uid": "D1234A56",
            "timestamp": "2023-06-01 12:00:00",
            "gas_usage": 0.5,
            "gas_pressure": 2.1,
            "temperature": 22.5,
            "battery_level": 85,
            "signal_strength": 75
        },
        {
            "data_id": "D12346",
            "device_uid": "D1234A56",
            "timestamp": "2023-06-01 13:00:00",
            "gas_usage": 0.3,
            "gas_pressure": 2.0,
            "temperature": 23.0,
            "battery_level": 85,
            "signal_strength": 75
        },
        {
            "data_id": "D12347",
            "device_uid": "D2345B67",
            "timestamp": "2023-06-01 12:00:00",
            "gas_usage": 0.2,
            "gas_pressure": 2.2,
            "temperature": 21.5,
            "battery_level": 65,
            "signal_strength": 60
        }
    ]
    
    # 필드 필터링
    if fields:
        filtered_data_list = []
        for data_item in data_list:
            filtered_data = {}
            for field in fields:
                if field in data_item:
                    filtered_data[field] = data_item[field]
            filtered_data_list.append(filtered_data)
        data_list = filtered_data_list
    
    # 페이지네이션
    total_records = len(data_list)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_data = data_list[start_idx:end_idx]
    
    return {
        "code": 200,
        "data": paginated_data,
        "total_records": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_records + page_size - 1) // page_size
    }

def view_data(post_data):
    """
    데이터 상세 정보 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 데이터 정보
    """
    db_name = post_data.get('db_name')
    data_id = post_data.get('data_id')
    fields = post_data.get('fields', [])
    
    if not db_name or not data_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 데이터 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 데이터 정보를 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    data = {
        "data_id": data_id,
        "device_uid": "D1234A56",
        "device_name": "가스미터 1",
        "timestamp": "2023-06-01 12:00:00",
        "gas_usage": 0.5,
        "gas_pressure": 2.1,
        "temperature": 22.5,
        "battery_level": 85,
        "signal_strength": 75,
        "customer_no": "S12345678",
        "customer_name": "홍길동",
        "meter_id": "123456789012",
        "raw_data": "0x1A2B3C4D5E6F",
        "data_quality": "good"
    }
    
    # 필드 필터링
    if fields:
        filtered_data = {}
        for field in fields:
            if field in data:
                filtered_data[field] = data[field]
        data = filtered_data
    
    return {
        "code": 200,
        "data": data
    }

def modify_data(post_data):
    """
    데이터 정보 수정
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 수정 결과
    """
    db_name = post_data.get('db_name')
    data_id = post_data.get('data_id')
    data = post_data.get('data', {})
    
    if not db_name or not data_id or not data:
        return {
            "code": 400,
            "message": "데이터베이스 이름, 데이터 ID, 수정할 데이터가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 데이터 정보를 수정합니다.
    
    return {
        "code": 200,
        "data": {
            "modified_count": 1
        }
    }

def delete_data(post_data):
    """
    데이터 삭제
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 삭제 결과
    """
    db_name = post_data.get('db_name')
    data_id = post_data.get('data_id')
    
    if not db_name or not data_id:
        return {
            "code": 400,
            "message": "데이터베이스 이름과 데이터 ID가 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 데이터를 삭제합니다.
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 1
        }
    }

def bulk_delete_data(post_data):
    """
    데이터 일괄 삭제
    
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
    
    # 실제 구현에서는 데이터베이스에서 필터 조건에 맞는 데이터를 일괄 삭제합니다.
    
    return {
        "code": 200,
        "data": {
            "deleted_count": 15
        }
    }

def stats_data(post_data):
    """
    데이터 통계 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 데이터 통계
    """
    db_name = post_data.get('db_name')
    device_uids = post_data.get('device_uids', [])
    start_date = post_data.get('start_date')
    end_date = post_data.get('end_date')
    stat_type = post_data.get('stat_type', 'gas_usage')
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 데이터 통계를 조회합니다.
    # 여기서는 예시 데이터를 반환합니다.
    
    # 예시 통계 데이터
    if stat_type == 'gas_usage':
        stats = {
            "total": 125.5,
            "average": 4.2,
            "max": 8.7,
            "min": 0.1,
            "by_device": {
                "D1234A56": 45.2,
                "D2345B67": 38.6,
                "D3456C78": 41.7
            }
        }
    elif stat_type == 'battery_level':
        stats = {
            "average": 75.3,
            "max": 95,
            "min": 45,
            "by_device": {
                "D1234A56": 85,
                "D2345B67": 65,
                "D3456C78": 90
            }
        }
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 통계 유형: {stat_type}"
        }
    
    return {
        "code": 200,
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "stat_type": stat_type,
            "stats": stats
        }
    }

def process_usage(post_data):
    """
    사용량 관련 요청을 처리하는 함수
    
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
    
    if action == 'usage':
        return get_usage(post_data)
    else:
        return {
            "code": 400,
            "message": f"지원하지 않는 액션: {action}"
        }

def get_usage(post_data):
    """
    사용량 데이터 조회
    
    Args:
        post_data (dict): POST 요청으로 전달된 데이터
        
    Returns:
        dict: 사용량 데이터
    """
    db_name = post_data.get('db_name')
    device_uids = post_data.get('device_uids', [])
    time_unit = post_data.get('time_unit', 'day')  # day, week, month, year
    start_date = post_data.get('start_date')
    end_date = post_data.get('end_date')
    
    if not db_name:
        return {
            "code": 400,
            "message": "데이터베이스 이름이 필요합니다."
        }
    
    # 실제 구현에서는 데이터베이스에서 사용량 데이터를 조회합니다.
    # 여기서는 예시 데이터를 생성합니다.
    
    # 날짜 범위 생성
    if not start_date:
        start_date = "2023-06-01"
    if not end_date:
        end_date = "2023-06-30"
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # 시간 단위에 따른 데이터 포인트 생성
    data_points = []
    current_dt = start_dt
    
    while current_dt <= end_dt:
        if time_unit == 'day':
            time_label = current_dt.strftime("%Y-%m-%d")
            next_dt = current_dt + timedelta(days=1)
        elif time_unit == 'week':
            # 주의 시작일(월요일)로 조정
            week_start = current_dt - timedelta(days=current_dt.weekday())
            time_label = week_start.strftime("%Y-%m-%d")
            next_dt = week_start + timedelta(days=7)
        elif time_unit == 'month':
            time_label = current_dt.strftime("%Y-%m")
            # 다음 달의 1일
            if current_dt.month == 12:
                next_dt = datetime(current_dt.year + 1, 1, 1)
            else:
                next_dt = datetime(current_dt.year, current_dt.month + 1, 1)
        elif time_unit == 'year':
            time_label = current_dt.strftime("%Y")
            next_dt = datetime(current_dt.year + 1, 1, 1)
        else:
            return {
                "code": 400,
                "message": f"지원하지 않는 시간 단위: {time_unit}"
            }
        
        # 각 장치별 사용량 생성
        device_usage = {}
        for device_uid in device_uids or ["D1234A56", "D2345B67", "D3456C78"]:
            # 랜덤 사용량 생성 (실제 구현에서는 데이터베이스에서 조회)
            usage = round(random.uniform(0.1, 5.0), 2)
            device_usage[device_uid] = usage
        
        data_points.append({
            "time_label": time_label,
            "usage": device_usage
        })
        
        current_dt = next_dt
    
    # 총 사용량 계산
    total_usage = {}
    for device_uid in device_uids or ["D1234A56", "D2345B67", "D3456C78"]:
        total_usage[device_uid] = round(sum(point["usage"].get(device_uid, 0) for point in data_points), 2)
    
    return {
        "code": 200,
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "time_unit": time_unit,
            "data_points": data_points,
            "total_usage": total_usage
        }
    } 