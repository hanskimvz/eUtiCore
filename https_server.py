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



from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
from urllib.parse import urlparse,   uses_params
import os, sys, time
import json, hashlib

# from functions import (HTTP_HOST, HTTP_PORT)
from functions import CONFIG
HTTP_HOST = CONFIG['HTTP_SERVER']['host']
HTTP_PORT = CONFIG['HTTP_SERVER']['port']
from web_server.proc_api import proc_api

port = 5100
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


def checkUserseq(headers):
# cookie: _temp=123456; _selected_language=kor; _login_id=hanskim; _db_name=cnt_demo; _role=admin; _name=Hans%20Kim; _userseq=ca29e7325bf9825817bc185cb3435f49
# accept-language: en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,zh-CN;q=0.6,zh;q=0.5
# accept-encoding: gzip, deflate
# referer: http://192.168.1.252:5173/recentdata
# user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36
# accept: application/json, text/plain, */*
# connection: close
# host: 192.168.1.252:9999

# Host: 192.168.1.252:9999
# Connection: keep-alive
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
# Accept-Encoding: gzip, deflate
# Accept-Language: en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,zh-CN;q=0.6,zh;q=0.5
# Cookie: _temp=123456

  print ('================headers================')
  print (headers)
  print ('================headers end ================')
  arr = {'host':'', 'connection': 'keep-alive', 'user-agent':'', 'cookie':'', 'cookies':{}}
  for head in headers :
    arr[head.lower()] = headers[head]
  
  print ('referer', arr['referer'])
  if arr['referer'].split("/")[-2] == 'account' and arr['referer'].split("/")[-1] == 'register':
    return True
  
  if not arr.get('cookie'):
    return False
  
  for key, val in [tuple(x.strip().split("=")) for x in arr['cookie'].split(";")]:
      arr['cookies'][key] = val
  # if headers.get('referer')  and headers['referer'].split("/")[-1] == 'login':
  #   return True
  # print (hashlib.md5((arr['cookies']['_login_id'] + 'hanskim').encode()).hexdigest() )
  # print (arr['cookies']['_userseq'])
  print (arr)
  if not arr['cookies'].get('_userseq'):
    return False
  if not arr['cookies'].get('_login_id'):
    return False
  if arr['cookies']['_userseq'] == hashlib.md5((arr['cookies']['_login_id'] + 'hanskim').encode()).hexdigest():
    return True
  return False

class MyHandler(SimpleHTTPRequestHandler):
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

    if url_parts.path.startswith("/api"):
      type_t, body = proc_api(url_parts)
    else:
      type_t, body = proc_web(url_parts)

    self.send_response(200)
    self.send_header('Content-Type', type_t)
    self.send_header("Access-Control-Allow-Origin", "*")  # CORS 허용
    self.end_headers()
    self.wfile.write(body)
        
  def do_POST(self):
    print('post, self.path', self.path)
    url = self.path
    for i in range(5):
        url = url.replace("//","/")
    url_parts = urlparse(url)
    # print('post', url_parts)
    body = b''
    chk_user = checkUserseq(self.headers)
    print("cheked user", chk_user)
    chk_user = True

    content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
    post_data = self.rfile.read(content_length) # <--- Gets the data itself
    print('post_data', post_data)
    arr_post = json.loads(post_data)


    if url_parts.path.startswith("/api/login") :
      type_t, body = proc_api(url_parts, arr_post)

    elif url_parts.path.startswith("/api"):
        if chk_user:
          type_t, body = proc_api(url_parts, arr_post)
        else :
          type_t, body = 'text/json', json.dumps({'code': 403, 'message':'Unauthorized'}).encode()
    else :
      type_t, body = 'text/json', json.dumps({'code': 404, 'message':'Not found'}).encode()

    self.send_response(200)
    self.send_header('Content-Type', type_t)
    self.send_header("Access-Control-Allow-Origin", "*")  # CORS 허용
    self.end_headers()
    self.wfile.write(body)


# print ("rootdir", _ROOT_DIR)

# web_dir = os.path.join(os.path.dirname(__file__), document_root)
# os.chdir(web_dir)
httpd = HTTPServer((HTTP_HOST, HTTP_PORT), MyHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, 
                               keyfile="key.pem", 
                               certfile="cert.pem", 
                               server_side=True)

print(f'Server running on port:{port}, document_root:', os.getcwd())
httpd.serve_forever()