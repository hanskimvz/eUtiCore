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


from urllib.parse import urlparse, urlsplit, parse_qsl, uses_params
import os, sys, time
import json

from web_server.v3 import proc_login, proc_register, proc_logout
from web_server.v3 import process_users, process_floating_user
# from web_server.v3.auth import process_auth
from web_server.v3 import process_devices
from web_server.v3 import process_subscribers
from web_server.v3 import process_data, process_usage
from web_server.v3 import process_events
from web_server.v3 import process_database


def getJsonFromFile(filename, cat = "systemlog"):
  ts_start = time.time()
  with open (filename, 'r')  as f:
    body = f.read()

  if cat == "systemlog":
    arr_rs = {"total_records":0, "fields":['no', 'levelname', 'asctime', 'module', 'funcName', 'lineno',  'threadName', 'message'], "data":[]}
    for i, line in enumerate(body.splitlines()):
      # arr_rs['total_records'] += 1
      lx = line[34:].split(" ")
      arr_rs['data'].append({
        'no':i+1,
        'level':line[0:8], 
        'date':line[10:29], 
        'module': lx[0], 
        'function':lx[1], 
        'line':lx[2], 
        'thread': lx[-1], 
        'message': " ".join(lx[3:-1])
      })
    arr_rs['total_records'] = i
  else:
    lines = body.splilines()
    arr_rs = {
      "total_records":len(lines), 
      "fields":[], 
      "data":lines
    }

  ts_end = time.time()
  arr_rs['elaspe_time'] = round(ts_end-ts_start, 2)  
  return arr_rs


def script_v2(script_name, post_data):

  #already v3 script
  if script_name in ['device', 'user', 'database', 'login', 'usage', 'event', 'subscriber']:
    return script_name, post_data

  #v2 script
  action_org = post_data.get('action')
  if script_name == 'query':
    post_data['action'] = 'list'
  
  elif script_name == 'update':
    post_data['action'] = 'modify'


  
  if post_data.get('page') == 'device_info':
      script_name = 'device'

  elif post_data.get('page') == 'users':
    script_name = 'user'
  
  elif post_data.get('page') == 'database':
    if action_org == 'get_db_tree':
      script_name = 'database'
      post_data['action'] = 'list'
    elif action_org == 'get_db_data':
      script_name = 'database'
      post_data['action'] = 'view'
    elif  post_data.get('table') == 'subscriber':
      script_name = 'subscriber'

    

  elif post_data.get('page') == 'usage_data':
    script_name = 'usage'

  elif post_data.get('page') == 'event_data':
    script_name = 'event'

  elif post_data.get('page') == 'subscriber_data':
    script_name = 'subscriber'

  elif post_data.get('page') == 'floating_user':
    script_name = 'floating_user'
  
  elif post_data.get('page') == 'usage_info':
    script_name = 'usage'

  elif post_data.get('page') == 'install_device_info' and post_data.get('action') == 'modify':
    script_name = 'device'
    post_data['action'] = 'bind'
  



  print ('--------------------------------')
  print ('script_name: %s, post_data_action: %s, action_org: %s' % (script_name, post_data.get('action'), action_org))
  print ('--------------------------------')

  return script_name, post_data


def proc_api(url_parts, post_data = {}):
    script_name = url_parts.path.split("/")[-1]
    # query = dict(parse_qsl(urlsplit(url_parts.query).path))
    # print('query:', query)
    print('script_name:', script_name)
    print('post_data:', post_data)
    arr= {}

    # 버전 2 스크립트 변환
    script_name, post_data = script_v2(script_name, post_data)

    if script_name == 'login': # post
      arr = proc_login(post_data)
    elif script_name == 'register':
      arr = proc_register(post_data)
    elif script_name == 'logout':
      arr = proc_logout(post_data)

    elif script_name == 'device':
        arr = process_devices(post_data)

    elif script_name == 'user':
        arr = process_users(post_data)
    
    elif script_name == 'floating_user':
        arr = process_floating_user(post_data)

    elif script_name == "database":
        arr = process_database(post_data)

    elif script_name == "data":
        arr = process_data(post_data)

    elif script_name == "usage":
        arr = process_usage(post_data)

    elif script_name == "event":
        arr = process_events(post_data)

    elif script_name == "subscriber":
        arr = process_subscribers(post_data)

    if post_data.get('format') == 'json':
      body = json.dumps(arr)
      return 'text/json', body.encode()
    
    elif isinstance(arr, str):
      return 'text/json', arr.encode()

