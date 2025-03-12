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


import os, time, sys
import datetime
import pymysql
import json, re, hashlib
# from functions_s import (loadSettings, dbconMaster, log, TZ_OFFSET)
from functions import (MYSQL, TZ_OFFSET, dbconMaster)

# MYSQL = loadSettings('db_table')

import configparser

# config_object = configparser.ConfigParser()
# with open ('config.ini', 'r') as f:
#   config_object.read_file(f)
# output_dict = dict()
# sections=config_object.sections()
# for section in sections:
#     items=config_object.items(section)
#     output_dict[section]=dict(items)
# print(output_dict)
# MYSQL = output_dict['MYSQL']
# TZ_OFFSET = int(output_dict['TIMEZONE']['tz_offset'])
# del(output_dict)

# sys.exit()


# def dbconMaster(host = '', user = '', password = '', db = '', charset ='', port=0): #Mysql
# 	if not host :
# 		host = str(MYSQL['host'])
# 	if not user:
# 		user = str(MYSQL['user'])
# 	if not password :
# 		password = str(MYSQL['password'])
# 	if not db:
# 		db = str(MYSQL['db'])
# 	if not charset:
# 		charset = str(MYSQL['charset'])
# 	if not port:
# 		port = int(MYSQL['port'])


# 	try:
# 		dbcon = pymysql.connect(host=host, user=str(user), password=str(password),  charset=charset, port=int(port))
# 	# except pymysql.err.OperationalError as e :
# 	except Exception as e :
# 		print ('dbconerr', str(e))
# 		return None
	
# 	return dbcon




def procLogin(db_name='gas_demo', post_data= {}):
  if not post_data.get('id'):
    return {"code": 1002, "description": "no_id"}
  if not post_data.get('password'):
    return {"code": 1003, "description": "no_password"}
  
  sq = "select * from " + MYSQL['common_users'] + " where ID='" + post_data.get('id').strip() + "'"
  # print (sq)
  dbCon = dbconMaster()

  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq)
    if not cur.rowcount:
      return {"code": 1004, "description": "no_user_id"}
    
    row = cur.fetchone()
    if row['passwd'] != post_data['password']:
      return {"code": 1005, "description": "password_not_match"}
    if row['flag'] == 'n':
      return {"code": 1006, "description": "id_expired"}
    del(row['passwd'])

    for r in row:
      if isinstance(row[r], datetime.datetime):
        row[r] = str(row[r])
    
    row['userseq'] = hashlib.md5((row['ID'] + 'hanskim').encode()).hexdigest()
    
    # if db_name != 'none':
    #   sq = "select name, name_eng, name_chi, language from " + row['db_name'] + "." + MYSQL['customUsers'] + "  where code='" + row['code'] + "'"
    #   cur.execute(sq)
    #   row_custom = cur.fetchone()
    #   if row_custom:
    #     row['name'] = row_custom['name']
    #     row['name_eng'] = row_custom['name_eng']
    #     row['name_chi'] = row_custom['name_chi']
    #     row['language'] = row_custom['language']
        

    return {"code": 1000, "description": row }


def getLanguagePack(db_name='cnt_demo', action='pack'):
  arr_rs = {
    "eng":{},
    "kor":{},
    "chi":{},
    # "fre":{},
  }
  sq = "select * from " + db_name + "." + MYSQL['customLanguage'] + " "
  sq_pack = "select * from " + db_name + "." + MYSQL['customLanguage'] + " where flag='y' "
  print (sq)
  dbCon = dbconMaster()
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    if action == 'pack':
      cur.execute(sq_pack)
      rows = cur.fetchall()
      for row in rows:
        arr_rs['kor'][row['varstr']] = row['kor']
        arr_rs['eng'][row['varstr']] = row['eng']
        arr_rs['chi'][row['varstr']] = row['chi']
        # arr_rs['chi'][row['varstr'].lower().replace(" ","_")] = row['chi']
    elif action=='list' :
      cur.execute(sq)
      rows = cur.fetchall()
      for row in rows:
        for r in row:
          if isinstance(row[r], datetime.datetime):
            row[r] = str(row[r])
          elif isinstance(row[r], bytes):
            row[r] = str(row[r].decode())
      arr_rs = rows
    else:
      print ('dict', action)
  return arr_rs

def getPlaceData(db_name='cnt_demo'):
  dbCon = dbconMaster()
  sq = "select A.code as square_code, A.name as square_name, B.code as store_code, B.name as store_name from " + db_name + "." + MYSQL['customSquare']+" as A inner join " + db_name + "." + MYSQL['customStore'] + " as B on A.code=B.square_code order by A.code asc; "
  arr = dict()
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq)
    rows = cur.fetchall()
    
    for row in rows:
      if not row['square_code'] in arr:
        arr[row['square_code']] = {"code":row['square_code'], "name": row['square_name'], "store":[]}
      arr[row['square_code']]['store'].append({"code": row['store_code'], "name":row['store_name']})

  # print (arr)
  # return arr
  arr_data = [arr[r] for r in arr]
  return arr_data

def getWebConfig(db_name='gas_demo', page = 'main'):
  # CREATE TABLE `web_config` (
  #   `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  #   `page` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  #   `body` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  #   `flag` enum('y','n') COLLATE utf8mb4_unicode_ci DEFAULT 'n',
  #   PRIMARY KEY (`pk`)
  #   ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ;
  ex_page = page.split(":")
  sq = "select page, body from " + db_name + "." + MYSQL['custom_webconfig']; 
  if ex_page[0] == 'main' or ex_page[0] == 'admin':
    sq += " where (page='" + ex_page[0] + "' or page='logo') and flag='y'"
  else:
    sq += " where page='" + ex_page[0] + "' and flag='y'"

  # print (sq)
  dbCon = dbconMaster()
  arr = {}
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq)
    rows = cur.fetchall()
    for row in rows:
      # print (row)
      if row['page'] == 'logo':
        arr['logo'] = row['body']
      else:
        arr['body'] = json.loads(row['body'])
  
  # print (arr)
  if len(ex_page) >1:
    for p in arr['body']:
      if p['page'] == ex_page[1]:
        return p

  return arr

# def getWebpageConfig(db_name='cnt_demo', page='main'):
#   s_page = page.split(":")
#   sq = "select body from " + db_name + "." + "webpage_config " + " where page='" + s_page[0] + "'"
#   if len(s_page) > 1:
#     sq += " and frame='" + s_page[1] + "'"
#   if len(s_page) > 2:
#     sq += " and depth='" + s_page[2] + "'"
#   # print (sq)
#   # dbCon = dbconMaster()
#   dbCon = dbconMaster(host = '192.168.1.250', user = 'rt_user', password = '13579', db = 'cnt_demo', charset ='utf8', port=3306)
#   arr = []
#   with dbCon:
#     cur = dbCon.cursor(pymysql.cursors.DictCursor)
#     cur.execute(sq)
#     rows = cur.fetchall()
    
#     for row in rows:
#       arr.append(json.loads(row['body']))
      
#   if len(arr) == 1:
#     return arr[0]
#   return arr


def getParamByViewBy(view_by = 'hourly', date_from='', date_to=''):
  _tz_offset = int(time.mktime(time.localtime()) -time.mktime(time.gmtime()))
  if not view_by in ['tenmin', 'hourly', 'daily', 'weekly', 'monthly','yearly']:
    return False
  
  ts = time.time()
  if not date_to:
    date_to = time.strftime("%Y-%m-%d", time.gmtime(ts))
  if not date_from:
    date_from = time.strftime("%Y-%m-%d", time.gmtime(ts-3600*24))
  
  s_date_from = date_from.split("-")
  s_date_to = date_to.split("-")

  param = {
    'hourly':{
      'group' : "year, month, day, hour, counter_label",
      'interval' : 3600,
      'date_format' : "%Y-%m-%d %H:%M",
      'js_tooltip_format' : "yyyy/MM/dd HH:mm",
      'q_datetime': "concat(year, '-', lpad(month,2,0), '-', lpad(day,2,0), ' ', lpad(hour,2,0), ':00')"
    },
    'daily':{
      'group': "year, month, day, counter_label",
      'interval' : 3600*24,
      'date_format' : "%Y-%m-%d 00:00",
      'js_tooltip_format' : "yyyy/MM/dd",
      'q_datetime' : "concat(year, '-', lpad(month,2,0), '-', lpad(day,2,0), ' ', '00:00')"
    },
    'monthly':{
      'group': "year, month, counter_label",
      'interval' : 3600*24*29,
      'date_format' : "%Y-%m",
      'js_tooltip_format' : "yyyy/MM",
      'q_datetime' : "concat(year, '-', lpad(month,2,0) )"
    },
    'tenmin':{
      'group' : "year, month, day, hour, min, counter_label",
      'interval' : 600,
      'date_format' : "%Y-%m-%d %H:%M",
      'js_tooltip_format' : "yyyy/MM/dd HH:mm",
      'q_datetime' : "concat(year, '-', lpad(month,2,0), '-', lpad(day,2,0), ' ', lpad(hour,2,0), ':',lpad(min,2,0))"
    },
    'weekly':{
      'group' : "year, week, counter_label",
      'interval' : 3600*24*7,
      'date_format' : "%Y-%m-%d",
      'js_tooltip_format' : "yyyy/MM/dd",
      'q_datetime' : "concat(year, '-', lpad(month,2,0), '-', lpad(day,2,0))"
    },
    'yearly':{
      'group' : "year, counter_label",
      'interval' : 3600*24*365,
      'date_format' : "%Y",
      'js_tooltip_format' : "yyyy",
      'q_datetime': "year"
    }
  }
  if view_by == 'monthly':
    date_from = s_date_from[0] + '-' + s_date_from[1] + '-01'
    date_to = str( datetime.date(int(s_date_to[0]) + int(int(s_date_to[1])/12), int(s_date_to[1])%12+1, 1) - datetime.timedelta(days=1) )
  
  xaxis_category = []
  ts_s = time.mktime(time.strptime(date_from, "%Y-%m-%d")) + _tz_offset
  ts_e = time.mktime(time.strptime(date_to,   "%Y-%m-%d")) + _tz_offset + 3600*24

  for ts in range (int(ts_s), int(ts_e), param[view_by]['interval']):
    tss = time.gmtime(ts)
    datetime_tag = time.strftime(param[view_by]['date_format'], tss)
    if not datetime_tag in  xaxis_category:
      xaxis_category.append(datetime_tag)
  
  param[view_by]['where_timstamp'] = "(year >= %d or year <=%d) and timestamp >=%d and timestamp <%d" %(int(s_date_from[0]), int(s_date_to[0]), ts_s, ts_e)
  param[view_by]['xaxis'] = xaxis_category
  del(param[view_by]['interval'])
  # del(param[view_by]['date_format'])
  
  return param[view_by]

def getCountData(post_data):
  print(post_data)
  ts_start = time.time()
  
  arr_where = list()
  sfilter = list()
  for sq_code in post_data['sq']:
    if not sq_code or sq_code =='0':
      continue
    sfilter.append("square_code='" + sq_code + "'")
  for st_code in post_data['st']:
    if not st_code or st_code == '0':
      continue
    sfilter.append("store_code='" + st_code + "'")
  
  arr_label = getWebConfig(post_data['db_name'], post_data['page'])['labels']
  arr = []
  for l in arr_label:
    arr.append("counter_label='" + l + "'")
  if arr:    
    sfilter.append("(" + " or ".join(arr) + ")")
  # sfilter.append(["(" + " or ".join(f"counter_label='{label}'" for label in arr_label) + ")"]  )

  if sfilter:
    arr_where.append("(" + " and ".join(sfilter) + ")")

  params =  getParamByViewBy(post_data['view_by'], post_data['date_from'], post_data['date_to'])

  arr_rs = {
    'series': [],
    'xaxis':{
      'labels': {
        'show': True,
        'datetimeFormatter': {
          'year': 'yyyy',
          'month': "yyyy MM",
          'day': 'MM/dd',
          'hour': 'HH:mm',
        },
      },
      'type': "datetime",
      'categories': params['xaxis']
    },
    'yaxis': {'show': True },
    'tooltip': {
      'x': { 'format': params['js_tooltip_format'] }
    }
  }

  arr_data = dict()
  for xaxis in params['xaxis']:
    arr_data[xaxis] = dict()

  if params['where_timstamp']:
    arr_where.append("(" + params['where_timstamp'] +")")

  sq = "select " + params['q_datetime'] + " as datetime, counter_label as label, sum(counter_val) as value from " + post_data['db_name'] + "." + MYSQL['customCount'] + ""
  sq += " where " + " and ".join(arr_where)
  if params['group']:
    sq += " group by " + params['group']
  
  print (sq)
  
  # dbCon = dbconMaster()
  dbCon = dbconMaster(host = '192.168.1.250', user = 'rt_user', password = '13579', db = 'cnt_demo', charset ='utf8', port=3306)
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq)
    rows = cur.fetchall()
    
    for row in rows:
      arr_data[row['datetime']][row['label']]= row['value']

  ts_now = time.time()
  for label in arr_label:
    arr = []
    for dt in  arr_data:
      dts = int(time.mktime(time.strptime(dt, params['date_format'])))
      if label in arr_data[dt]:
        arr.append(int(arr_data[dt][label]))
      elif dts < ts_now:
        arr.append(0)
      else : # if dt > now => None
        arr.append(None)

    arr_rs['series'].append({"name": label, "data":arr})
  

  ts_end = time.time()
  arr_rs['elaspe_time'] = round(ts_end-ts_start, 2)
  return arr_rs

def getTrafficData(post_data):
  arr = getCountData(post_data)
  arrx = []
  for series in arr['series']:
    # print (series)
    for i in range(0, len(series['data']), 24):
      arrx.append({"name": arr['xaxis']['categories'][i].split(" ")[0],  "data":series['data'][i:(i+24)]})


  arr_rs = {
    'series': arrx,
    'xaxis':{
      'labels': {
        'show': True,
        'datetimeFormatter': {
          'year': 'yyyy',
          'month': "yyyy MM",
          'day': 'MM/dd',
          'hour': 'HH:mm',
        },
      },
      'type': "datetime",
      'categories': arr['xaxis']['categories'][0:24]
    },
    'yaxis': {'show': True },
    'tooltip': {
      'x': { 'format': "HH:mm" }
    }
  }
  return arr_rs


def getZone(param):
  regex = re.compile(r"VCA.Ch0.Zn(\d+).(\w+)=(.+)", re.IGNORECASE)
  arr = dict()
  lines = param.splitlines()
  for line in lines:
    m = regex.search(line)
    if m:
      # print (m.group(1), m.group(2), m.group(3))
      if not m.group(1) in arr:
        arr[m.group(1)] = {}
      arr[m.group(1)][m.group(2)] = m.group(3)
  
  zone = [ arr[r] for r in arr]
  return zone

def getCounters(param):
  # VCA.Ch0.Ct0.name=Counter 0
  regex = re.compile(r"VCA.Ch0.Ct(\d+).(\w+)=(.+)", re.IGNORECASE)
  arr = dict()
  lines = param.splitlines()
  for line in lines:
    m = regex.search(line)
    if m:
      # print (m.group(1), m.group(2), m.group(3))
      if not m.group(1) in arr:
        arr[m.group(1)] = {}
      arr[m.group(1)][m.group(2)] = m.group(3)
  
  counter = [ arr[r] for r in arr]
  return counter

def listDevices(post_data={}):
  ts_start = time.time()
  sfilter = list()
  if post_data.get('sq'):
    for sq_code in post_data['sq']:
      if not sq_code or sq_code =='0':
        continue
      sfilter.append("square_code='" + sq_code + "'")
  if post_data.get('st'):      
    for st_code in post_data['st']:
      if not st_code or st_code == '0':
        continue
      sfilter.append("store_code='" + st_code + "'")
    
  if post_data.get('cam'):
    for cam_code in post_data['cam']:
      if not cam_code or cam_code == '0':
        continue
      sfilter.append("code='" + cam_code + "'")

  sq = "select A.code, A.usn, A.product_id, A.name, A.store_code, A.comment, A.enable_countingline, A.enable_heatmap, A.enable_snapshot, A.enable_face_det, A.enable_macsniff, A.flag, A.device_info, B.last_access, B.lic_pro, B.lic_surv, B.lic_count, B.face_det, B.heatmap, B.countrpt, B.macsniff, B.initial_access, B.param, B.url as ip from " + post_data['db_name'] + "." + MYSQL['customCamera'] + " as A inner join " + MYSQL['commonParam'] + " as B on A.device_info = B.device_info "
  if sfilter:
    sq += " where " + " and ".join(sfilter)
  sq +=  " order by B.last_access desc "
  print (sq)
  arr_rs = {
    'device': [],
    'elaspe_time':0
  }
  dbCon = dbconMaster()
  # dbCon = dbconMaster(host = '192.168.1.250', user = 'rt_user', password = '13579', db = 'cnt_demo', charset ='utf8', port=3306)
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq)
    rows = cur.fetchall()

    for row in rows:
      if not row['device_info']:
        continue

      lic = []
      if row['lic_pro'] == 'y': 
        lic.append('PRO')
      if row['lic_surv'] == 'y':
        lic.append('SURV')
      if row['lic_count'] == 'y':
        lic.append('COUNT')

      arr = {
        'device_info': row['device_info'],
        'usn': row['usn'],
        'product_id': row['product_id'],
        'square_code': '',
        'square_name': '',
        'store_code': row['store_code'],
        'store_name': '',
        'camera_code': row['code'],
        'camera_name' : row['name'],
        'license': "/".join(lic),
        'functions': {
          'face_det': True if row['face_det'] == 'y' else False,
          'heatmap':  True if row['heatmap']  == 'y' else False,
          'countrpt': True if row['countrpt'] == 'y' else False,
          'macsniff': True if row['macsniff'] == 'y' else False,
        },
        'features':{
          'enable_countingline': True if row['enable_countingline'] == 'y' else False,
          'enable_heatmap':      True if row['enable_heatmap'] == 'y'      else False,
          'enable_snapshot':     True if row['enable_snapshot'] == 'y'     else False,
          'enable_face_det':     True if row['enable_face_det'] == 'y'     else False,
          'enable_macsniff':     True if row['enable_macsniff'] == 'y'     else False,
        },
        'snapshot': {
          'date': '',
          'body': ''
        },
        'initial_access': str(row['initial_access']),
        'last_access': str(row['last_access']),
        'zone_info': getZone(row['param']),
        'counters': getCounters(row['param']),
        'ip': row['ip'],
        'flag':True if row['flag'] == 'y' else False
      }

      sq = "select regdate, body from " + MYSQL['commonSnapshot'] + " where device_info='" + row['device_info'] + "' order by regdate desc limit 1"
      cur.execute(sq)
      rs_snapshot = cur.fetchone()
      if rs_snapshot:
        arr['snapshot']['date'] = str(rs_snapshot['regdate'])
        arr['snapshot']['body'] = str(rs_snapshot['body'].decode())     

      sq = "select A.code as store_code, A.name as store_name, B.code as square_code, B.name as square_name from " + post_data['db_name'] + "." + MYSQL['customStore'] + " as A inner join " + post_data['db_name'] + "." + MYSQL['customSquare'] + " as B on A.square_code = B.code where A.code='" + row['store_code'] + "'"
      cur.execute(sq)
      rs_place = cur.fetchone()
      if rs_place:
        arr['store_code']  = rs_place['store_code']
        arr['store_name']  = rs_place['store_name']
        arr['square_code'] = rs_place['square_code']
        arr['square_name'] = rs_place['square_name']

      arr_rs['device'].append(arr)

  ts_end = time.time()
  arr_rs['elaspe_time'] = round(ts_end-ts_start, 2)  
  return arr_rs

def siteMap(post_data={}):
  arr_rs = list()
  dbCon = dbconMaster()
  # dbCon = dbconMaster(host = '192.168.1.250', user = 'rt_user', password = '13579', db = 'cnt_demo', charset ='utf8', port=3306)
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)

    sq = "select code, name from " + post_data['db_name'] + "." + MYSQL['customSquare']
    cur.execute(sq)
    rows_square = cur.fetchall()
    for i, row_sq in enumerate(rows_square):
      # print (row_sq)
      arr_rs.append({"code":row_sq['code'],"name": row_sq['name'], "store":[]})
      sq = "select code, name from "+ post_data['db_name'] + "." + MYSQL['customStore'] + " where square_code='" + row_sq['code'] +"'"
      cur.execute(sq)
      rows_store = cur.fetchall()
      for j, row_st in enumerate(rows_store):
        # print (row_st)
        arr_rs[i]['store'].append({"code": row_st['code'], "name":row_st['name'], "camera":[]})
        sq = "select code, name, enable_countingline, enable_heatmap, enable_face_det, enable_macsniff, device_info from " + post_data['db_name'] + "." + MYSQL['customCamera'] + " where store_code='" + row_st['code'] +"'"
        cur.execute(sq)
        rows_camera = cur.fetchall()
        for k, row_cam in enumerate(rows_camera):
          sq = "select body, regdate from " + MYSQL['commonSnapshot'] + " where device_info='" + row_cam['device_info'] +"' order by regdate desc limit 1"
          cur.execute(sq)
          # print (cur.rowcount)
          row_snapshot =  cur.fetchone()

          arr_rs[i]['store'][j]['camera'].append({
            "code": row_cam['code'], 
            "name":row_cam['name'],
            "enable_countingline": row_cam['enable_countingline'],
            "enable_heatmap": row_cam['enable_heatmap'],
            "enable_face_det": row_cam['enable_face_det'],
            "enable_macsniff": row_cam['enable_macsniff'],
            "last_access": str(row_snapshot['regdate']) if cur.rowcount else '',
            "snapshot": row_snapshot['body'].decode() if cur.rowcount else '',
          })
  return arr_rs

def queryDatabase(post_data): # using post data
  ts_start = time.time()
  arr_rs = {"total_records":0, "fields": [], "data":[]}
  sq_t = "select count(*) as total from " + post_data['db'] + "." + post_data['table'] + " "

  if post_data.get('fields'):
    sq = "select " + ",".join(post_data['fields']) + " from " +  post_data['db'] + "." +  post_data['table'] + " "
  else:
    sq = "select *  from " + post_data['db']  + "." + post_data['table'] + " "
    
  if post_data.get('search'):
    sq += " where " + post_data['search']

  if not post_data.get('page_max'):
    post_data['page_max'] = 20
  if not post_data.get('page_no'):
    post_data['page_no'] = 1
  offset = (post_data['page_no'] -1 ) * post_data['page_max']

  if post_data.get('groupby'):
    sq += " group by " + post_data['groupby']

  if post_data.get('orderby'):
    sq += " order by " + post_data['orderby']

  sq += " limit %d, %d"  %(offset, post_data['page_max'])

  print (sq)
  dbCon = dbconMaster()
  
  with dbCon:
    cur = dbCon.cursor(pymysql.cursors.DictCursor)
    cur.execute(sq_t)
    arr_rs['total_records'] = cur.fetchone()['total']

    cur.execute(sq)
    rows = cur.fetchall()
    for row in rows:
      arr = []

      for r in row:
        print (row[r], type(row[r]))
        if isinstance(row[r], datetime.datetime) or  isinstance(row[r],datetime.timedelta):
          row[r] = str(row[r])
        elif isinstance(row[r], bytes):
          row[r] = str(row[r].decode())

      arr_rs['data'].append(row)

    if rows:
      arr_rs['fields']  = [x  for x in rows[0]]
  ts_end = time.time()
  arr_rs['elaspe_time'] = round(ts_end-ts_start, 2)  
  return arr_rs



if __name__ == '__main__':
  pass
