# Copyright (c) 2024, Hans kim(hanskimvz@gmail.com)

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



from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse,   uses_params
import os, sys, time
import json, hashlib

from functions import CONFIG
HTTP_HOST = CONFIG['HTTP_SERVER']['host']
HTTP_PORT = CONFIG['HTTP_SERVER']['port']


VERSION = "3.0.0"


# from functions import (HTTP_HOST, HTTP_PORT)
if VERSION.startswith("1."):
  from web_server.proc_api_v1 import proc_api
elif VERSION.startswith("2."):
  from web_server.proc_api_v2 import proc_api
elif VERSION.startswith("3."):
  from web_server.proc_api_v3 import proc_api


# document_root = '../vue_codes/dist/'

def proc_web(url_parts):
    path =  url_parts.path
    if url_parts.path == '/':
        path = '/index.html'
    
    ext = path.split(".")[-1]
    if ext == 'html' or ext == 'htm':
        type_t = 'text/html'
    elif ext == 'js':
        type_t = 'text/javascript'
    elif ext =='css':
        type_t = 'text/css'
    elif ext == 'ico':
        type_t = 'image/x-icon'
    elif ext == 'png':
        type_t = 'image/png'
    elif ext == 'jpg':
        type_t = 'image/jpeg'
    elif ext == 'json':
        type_t = 'text/json'
    else :
        type_t = 'text/html'
        path = '/index.html'
        print ('Unknown', path)

    with open(path[1:], "rb") as f:
        body = f.read()

    return type_t, body


def checkUserAuth(post_data):
  """
  POST 데이터를 통한 사용자 인증을 처리합니다.
  모든 인증은 POST 데이터의 login_id와 userseq 필드를 통해 이루어집니다.
  """
  if not post_data or not isinstance(post_data, dict):
    return False
    
  # 로그인 API 또는 회원가입 API는 인증 없이 접근 가능
  if post_data.get('action') == 'login' or post_data.get('action') == 'register':
    return True
    
  # login_id와 userseq로 인증
  if post_data.get('login_id') and post_data.get('userseq'):
    login_id = post_data['login_id']
    userseq = post_data['userseq']
    # 인증 로직: userseq가 login_id와 비밀 키의 해시값과 일치하는지 확인
    if userseq == hashlib.md5((login_id + 'hanskim').encode()).hexdigest():
      return True
      
  return False

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
  def do_OPTIONS(self):
    """Preflight 요청 (CORS 문제 해결을 위한 옵션 요청)"""
    self.send_response(200)
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    self.end_headers()

  def do_GET(self):
    url = self.path
    for i in range(5):
        url = url.replace("//","/")
    url_parts = urlparse(url)
    print('get', url_parts)    

    try:
      if url_parts.path.startswith("/api"):
        # GET 요청으로는 로그인 API만 접근 가능
        if url_parts.path.startswith("/api/login"):
          type_t, body = proc_api(url_parts)
          self.send_response(200)
        else:
          # 인증이 필요한 API는 POST 요청으로만 접근 가능하다는 메시지 반환
          type_t = 'text/json'
          body = json.dumps({
            'code': 405, 
            'message': 'API requires POST method with login_id and userseq in the request body'
          }).encode()
          self.send_response(405)  # Method Not Allowed
      else:
        try:
          type_t, body = proc_web(url_parts)
          self.send_response(200)
        except FileNotFoundError:
          type_t = 'text/html'
          body = json.dumps({'code': 404, 'message': 'File not found'}).encode()
          self.send_response(404)
        except PermissionError:
          type_t = 'text/html'
          body = json.dumps({'code': 403, 'message': 'Permission denied'}).encode()
          self.send_response(403)
        except Exception as e:
          type_t = 'text/html'
          body = json.dumps({'code': 500, 'message': str(e)}).encode()
          self.send_response(500)
    except Exception as e:
      type_t = 'text/html'
      body = json.dumps({'code': 500, 'message': str(e)}).encode()
      self.send_response(500)

    self.send_header('Content-Type', type_t)
    self.send_header("Access-Control-Allow-Origin", "*")  # CORS 허용
    self.end_headers()
    self.wfile.write(body)
        
  def do_POST(self):
    url = self.path
    for i in range(5):
        url = url.replace("//","/")
    url_parts = urlparse(url)
    print('post', url_parts)
    body = b''

    try:
      content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
      post_data = self.rfile.read(content_length) # <--- Gets the data itself
      print (post_data)
      arr_post = json.loads(post_data)

      if not url_parts.path.startswith("/api"):
        type_t = 'text/json'
        body = json.dumps({'code': 404, 'message':'Not found'}).encode()
        self.send_response(404)  # 경로를 찾을 수 없으면 404 Not Found
        return

      if url_parts.path.startswith("/api/login") or url_parts.path.startswith("/api/logout") or url_parts.path.startswith("/api/register"):
        auth_result = True # 로그인 API는 인증 없이 접근 가능
      else:
        auth_result = checkUserAuth(arr_post)

      if not auth_result:
        type_t = 'text/json'
        body = json.dumps({'code': 403, 'message':'Unauthorized'}).encode()
        self.send_response(403) # 인증 실패는 403 Forbidden
      
      else:
        type_t, body = proc_api(url_parts, arr_post)
        # API 응답에서 코드 확인
        try:
          response_data = json.loads(body)
          if isinstance(response_data, dict) and 'code' in response_data:
            if response_data['code'] == 403:
              self.send_response(403)
            elif response_data['code'] == 404:
              self.send_response(404)
            else:
              self.send_response(200)
          else:
            self.send_response(200)
        except:
          self.send_response(200)

    except json.JSONDecodeError:
      type_t = 'text/json'
      body = json.dumps({'code': 400, 'message': 'Invalid JSON'}).encode()
      self.send_response(400)  # 잘못된 JSON 형식은 400 Bad Request

    # except Exception as e:
    #   type_t = 'text/json'
    #   body = json.dumps({'code': 500, 'message': str(e)}).encode()
    #   self.send_response(500)  # 서버 오류는 500 Internal Server Error

    self.send_header('Content-Type', type_t)
    self.send_header("Access-Control-Allow-Origin", "*")  # CORS 허용
    self.end_headers()
    # print ('final body', body)
    self.wfile.write(body)


# print ("rootdir", _ROOT_DIR)

# web_dir = os.path.join(os.path.dirname(__file__), document_root)
# os.chdir(web_dir)
httpd = HTTPServer((HTTP_HOST, HTTP_PORT), SimpleHTTPRequestHandler)
print(f'Server running on port:{HTTP_PORT}, document_root:', os.getcwd())
httpd.serve_forever()