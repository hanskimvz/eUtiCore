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
import os
import sys

# 모듈 가져오기
from login import process_login
from user import process_users
from device import process_devices
from data_process import process_data, process_usage
from event import process_events
from subscriber import process_subscribers

def proc_api(environ, start_response):
    """
    API 요청을 처리하는 메인 함수
    
    Args:
        environ (dict): WSGI 환경 변수
        start_response (callable): WSGI 응답 시작 함수
        
    Returns:
        list: 응답 데이터
    """
    # 요청 경로 분석
    path_info = environ.get('PATH_INFO', '')
    script_name = path_info.strip('/').split('/')[0] if path_info.strip('/') else ''
    
    # 요청 메소드 확인
    request_method = environ.get('REQUEST_METHOD', '')
    
    # 요청 데이터 파싱
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    
    request_body = environ['wsgi.input'].read(request_body_size)
    post_data = {}
    
    if request_body:
        try:
            post_data = json.loads(request_body.decode('utf-8'))
        except json.JSONDecodeError:
            # JSON 파싱 오류 처리
            response_data = {
                "code": 400,
                "message": "잘못된 JSON 형식입니다."
            }
            return send_response(start_response, response_data, 400)
    
    # 쿼리 스트링 파싱
    query_string = environ.get('QUERY_STRING', '')
    query_params = {}
    
    if query_string:
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                query_params[key] = value
    
    # 요청 처리
    if request_method == 'POST':
        # 스크립트 이름에 따라 적절한 처리 함수 호출
        if script_name == 'login':
            response_data = process_login(post_data)
        elif script_name == 'user':
            response_data = process_users(post_data)
        elif script_name == 'device':
            response_data = process_devices(post_data)
        elif script_name == 'data':
            response_data = process_data(post_data)
        elif script_name == 'usage':
            response_data = process_usage(post_data)
        elif script_name == 'event':
            response_data = process_events(post_data)
        elif script_name == 'subscriber':
            response_data = process_subscribers(post_data)
        else:
            # 지원하지 않는 API 경로
            response_data = {
                "code": 404,
                "message": f"지원하지 않는 API 경로: {script_name}"
            }
            return send_response(start_response, response_data, 404)
    else:
        # POST 이외의 메소드는 지원하지 않음
        response_data = {
            "code": 405,
            "message": f"지원하지 않는 메소드: {request_method}"
        }
        return send_response(start_response, response_data, 405)
    
    # 응답 코드 결정
    status_code = response_data.get('code', 200)
    
    # 응답 반환
    return send_response(start_response, response_data, status_code)

def send_response(start_response, response_data, status_code):
    """
    WSGI 응답을 생성하고 반환하는 함수
    
    Args:
        start_response (callable): WSGI 응답 시작 함수
        response_data (dict): 응답 데이터
        status_code (int): HTTP 상태 코드
        
    Returns:
        list: 응답 데이터
    """
    # 상태 코드에 따른 상태 메시지 매핑
    status_messages = {
        200: 'OK',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        500: 'Internal Server Error'
    }
    
    # 상태 문자열 생성
    status = f"{status_code} {status_messages.get(status_code, 'Unknown')}"
    
    # 응답 헤더 설정
    response_headers = [
        ('Content-Type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]
    
    # 응답 시작
    start_response(status, response_headers)
    
    # 응답 데이터 JSON 직렬화
    response_json = json.dumps(response_data, ensure_ascii=False)
    
    # 응답 반환
    return [response_json.encode('utf-8')]

# WSGI 애플리케이션 진입점
def application(environ, start_response):
    """
    WSGI 애플리케이션 진입점
    
    Args:
        environ (dict): WSGI 환경 변수
        start_response (callable): WSGI 응답 시작 함수
        
    Returns:
        list: 응답 데이터
    """
    try:
        return proc_api(environ, start_response)
    except Exception as e:
        # 예외 처리
        response_data = {
            "code": 500,
            "message": f"서버 내부 오류: {str(e)}"
        }
        return send_response(start_response, response_data, 500)

# 직접 실행 시 테스트 서버 실행
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    # 테스트 서버 설정
    host = '0.0.0.0'
    port = 8000
    
    # 서버 생성 및 실행
    httpd = make_server(host, port, application)
    print(f"서버가 {host}:{port}에서 실행 중입니다...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("서버가 종료되었습니다.") 