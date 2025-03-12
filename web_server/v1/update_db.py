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
import json, re
# from functions_s import (configVars, dbconMaster, log, TZ_OFFSET)

from functions import (MYSQL, TZ_OFFSET)

# MYSQL = { 
#     "commonParam": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.param'),
#     "commonSnapshot": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.snapshot'),
#     "commonCount": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.counting'),
#     "commonHeatmap": configVars('software.mysql.db') +"." + configVars('software.mysql.db_common.table.heatmap'),
#     "commonCountEvent": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.count_event'),
#     "commonFace": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.face'),
#     "customCount": configVars('software.mysql.db_custom.table.count'),
#     "customHeatmap": configVars('software.mysql.db_custom.table.heatmap'),
#     "customAgeGender": configVars('software.mysql.db_custom.table.age_gender'),
#     "customSquare": configVars('software.mysql.db_custom.table.square'),
#     "customStore": configVars('software.mysql.db_custom.table.store'),
#     "customCamera": configVars('software.mysql.db_custom.table.camera'),
#     "customCounterLabel": configVars('software.mysql.db_custom.table.counter_label'),
#     "customRtCount": "realtime_counting",
# }
# MYSQL['customCount'] = 'count_tenmin_p'
# MYSQL['customLanguage'] = 'language'
# MYSQL['web_config'] = 'web_config'
# _selected_language = "eng"


# import configparser

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

def updateLanguage(post_data = {}):
  print (post_data)
  arr= []
  if post_data.get('eng'):
    arr.append("eng=\"%s\"" %post_data['eng'])
  if post_data.get('kor'):
    arr.append("kor=\"%s\"" %post_data['kor'])
  if post_data.get('chi'):
    arr.append("chi=\"%s\"" %post_data['chi'])
  if post_data.get('page'):
    arr.append("page=\"%s\"" %post_data['page'])

  if post_data.get('pk'):
    arr.append("varstr=\"%s\"" %post_data['varstr'])
    arr.append("flag=\"%s\"" %post_data['flag'])

    sq = "update " + post_data['db_name'] + "." + MYSQL['customLanguage'] + " set " + ",".join(arr) + " where pk=%d" %(post_data['pk'])
  
  else :
    arr.append("flag=\"%s\"" %post_data['flag'])
    sq = "update " + post_data['db_name'] + "." + MYSQL['customLanguage'] + " set " + ",".join(arr) + " where varstr=\"%s\"" %(post_data['varstr'])

  print (sq)
  dbCon = dbconMaster()
  with dbCon:
    cur = dbCon.cursor()
    xt = cur.execute(sq)
    dbCon.commit()

  return {"code": xt}

def updateWebConfig(db_name='cnt_demo', page='main', body=[]):
  if not isinstance(body, str):
    body = json.dumps(body, ensure_ascii=False)

  dbCon = dbconMaster()
  with dbCon:
    cur = dbCon.cursor()
    sq = "select pk from  " + db_name + "." + MYSQL['web_config'] + " where page='"+page+"'"
    cur.execute(sq)

    if cur.rowcount:
      row = cur.fetchone()
      sq = "update " + db_name + "." + MYSQL['web_config'] + " set body=\'%s\' where pk=%d" %(body, int(row[0]))
    else :
      sq = "insert into "+ db_name + "." + MYSQL['web_config'] + "(page, body, flag) values(\'%s\',\'%s\', 'y')" %(page, body)
    print (sq)

    xt = cur.execute(sq)
    dbCon.commit()

  return {"code": xt}

def updateDatabase(post_data): # using post data
  ts_start = time.time()
  print (post_data)
  # sets (key, val) ==> key =val
  sets_string = ",".join([str(k) + "=\"" + str(v) + "\"" if isinstance(v, str) else str(k) + "=" + str(v)  for (k,v) in post_data['sets']])
  sq = "select " +  post_data['db'] + "." +  post_data['table'] + " set " + sets_string + " where " + post_data['condition']
  print (sq)
    
  # if post_data.get('search'):
  #   sq += " where "

  # if not post_data.get('page_max'):
  #   post_data['page_max'] = 20
  # if not post_data.get('page_no'):
  #   post_data['page_no'] = 1
  # offset = (post_data['page_no'] -1 ) * post_data['page_max']

  # if post_data.get('groupby'):
  #   sq += " group by " + post_data['groupby']

  # if post_data.get('orderby'):
  #   sq += " order by " + post_data['orderby']

  # sq += " limit %d, %d"  %(offset, post_data['page_max'])

  # print (sq)
  # dbCon = dbconMaster(host = '192.168.1.250', user = 'rt_user', password = '13579', db = 'cnt_demo', charset ='utf8', port=3306)
  
  # with dbCon:
  #   cur = dbCon.cursor(pymysql.cursors.DictCursor)
  #   cur.execute(sq_t)
  #   arr_rs['total_records'] = cur.fetchone()['total']

  #   cur.execute(sq)
  #   rows = cur.fetchall()
  #   for row in rows:
  #     arr = []

  #     for r in row:
  #       if isinstance(row[r], datetime.datetime):
  #         row[r] = str(row[r])
  #       elif isinstance(row[r], bytes):
  #         row[r] = str(row[r].decode())

  #     arr_rs['data'].append(row)

  # arr_rs['fields']  = [x  for x in rows[0]]
  # ts_end = time.time()
  # arr_rs['elaspe_time'] = round(ts_end-ts_start, 2)  
  # return arr_rs

    # xt = cur.execute(sq)
    # dbCon.commit()
  xt=0
  ts_end = time.time()
  return {"code": xt, 'elaspe_time': round(ts_end-ts_start, 2)  }