import pandas as pd
import copy
import datetime
import itertools
import os
import re
import cx_Oracle
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
    filename='./info.log',
    filemode='a'
)

# 支持中文
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 记录GAME_NO
if 'i.txt' not in os.listdir('.'):
    with open('./i.txt', 'w') as f:
        f.write('1')
with open('./i.txt', 'r') as f:
    num = int(f.read())

logging.info('读取UNIQUE_ID成功,开始拆分小票.(beginning)')


class MoneyAward(object):
    def __init__(self):
        self.result = list()
        self.mapping = {'7_120': 'M_7_1,M_6_1,M_5_1,M_4_1,M_3_1,M_2_1', '8_56': 'M_5_1', '8_9': 'M_8_1,M_7_1',
                        '3_3': 'M_2_1', '4_5': 'M_4_1,M_3_1', '5_5': 'M_4_1', '4_4': 'M_3_1', '7_21': 'M_5_1',
                        '6_35': 'M_3_1,M_2_1', '6_6': 'M_5_1', '6_50': 'M_4_1,M_3_1,M_2_1', '8_28': 'M_6_1',
                        '3_4': 'M_3_1,M_2_1', '7_8': 'M_7_1,M_6_1', '8_70': 'M_4_1',
                        '8_247': 'M_8_1,M_7_1,M_6_1,M_5_1,M_4_1,M_3_1,M_2_1', '7_35': 'M_4_1', '5_10': 'M_2_1',
                        '4_6': 'M_2_1', '7_7': 'M_6_1', '6_42': 'M_6_1,M_5_1,M_4_1,M_3_1', '5_16': 'M_5_1,M_4_1,M_3_1',
                        '6_20': 'M_3_1', '5_6': 'M_5_1,M_4_1', '4_11': 'M_4_1,M_3_1,M_2_1', '6_7': 'M_6_1,M_5_1',
                        '6_57': 'M_6_1,M_5_1,M_4_1,M_3_1,M_2_1', '5_20': 'M_3_1,M_2_1', '6_15': 'M_2_1',
                        '6_22': 'M_6_1,M_5_1,M_4_1', '5_26': 'M_5_1,M_4_1,M_3_1,M_2_1', '8_8': 'M_7_1'}

        # self.conn = cx_Oracle.connect('dw_user/dw_useroranew@192.168.67.203:1521/rb3bak')  # 线上
        self.conn = cx_Oracle.connect('lt_draw_base_ch/lt_draw_base_ch@10.0.0.91:1521/dev')
        self.orcl_cursor = self.conn.cursor()

    def read_oracle(self):
        """
        从oracle读取数据
        :return:列表
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        old_time = (datetime.datetime.now()+datetime.timedelta(minutes=-(60*240))).strftime("%Y-%m-%d %H:%M:%S")

        sql = """select
       ORDER_NO,DRAW_RESULT,MIX_TYPE,MULTIPLE,ISSUE_NO,LOTTERY_TYPE,LOTTERY_SUB_TYPE
      from  LTDR_PRINT_TICKET
      where
         DRAW_STATUS = 'DRAW_FINISH'
        and MIX_TYPE is not null and DRAW_RESULT is not null
        and ORDER_NO in (
          select  ORDER_NO
          from LTDR_PRINT_TICKET where ((gmt_create>=to_date('%s', 'yyyy-mm-dd HH24:mi:ss')
         and gmt_create<to_date('%s', 'yyyy-mm-dd HH24:mi:ss'))
          or (gmt_modified >= to_date('%s', 'yyyy-mm-dd HH24:mi:ss')
         and gmt_modified < to_date('%s', 'yyyy-mm-dd HH24:mi:ss')))
          and  DRAW_STATUS = 'DRAW_FINISH' and MIX_TYPE is not null and DRAW_RESULT is not null
          group by ORDER_NO
          )""" % (old_time, current_time, old_time, current_time)

        logging.info(sql)

        try:
            self.orcl_cursor.execute(sql)

            columns = [column[0] for column in self.orcl_cursor.description]
            for row in self.orcl_cursor.fetchall():
                self.result.append(dict(zip(columns, row)))

        except Exception as e:
            logging.error(e)
        finally:
            self.orcl_cursor.close()
            self.conn.close()

    def split_mix_type(self):
        """
        拆分mix_type多选类型
        :return: 多选串关拆分成单选
        """
        split_mix_type_result = []
        for i in self.result:
            try:
                i['MIX_TYPE'] = i['MIX_TYPE'].split(',')
                for j in i['MIX_TYPE']:
                    i['MIX_TYPE'] = j
                    split_mix_type_result.append(copy.deepcopy(i))
            except Exception as e:
                logging.error(e)

        return split_mix_type_result

    def match_count(self, split_mix_type_result):
        """
        计算所选比赛数量
        :return: 字典添加一个字段match_count
        """
        match_count_result = []

        for i in split_mix_type_result:
            try:
                i['MATCH_COUNT'] = len(i['DRAW_RESULT'].split('|'))
                i['DRAW_RESULT'] = i['DRAW_RESULT'].split('|')
            except Exception as e:
                logging.error(e)

            match_count_result.append(i)

        return match_count_result

    def split_by_match_count(self, match_count_result):
        """
        根据串关数和比赛数拆分  组合
        :return:组合后的结果 split_mix_type_result  []
        """
        new_list = []

        for i in match_count_result:
            # 判断比赛场次和串关的大小
            # 比赛场次大于串关m*n,进行组合操作,并且比赛场次改为m
            if i['MATCH_COUNT'] > int(i['MIX_TYPE'].split('_')[1]):
                for j in itertools.combinations(i['DRAW_RESULT'], int(i['MIX_TYPE'].split('_')[1])):
                    # print(j)

                    i['MATCH_COUNT'] = int(i['MIX_TYPE'].split('_')[1])
                    i['DRAW_RESULT'] = list(j)
                    new_list.append(copy.deepcopy(i))

            # 如果比赛场次等于串关m,需要找到映射关系
            elif i['MATCH_COUNT'] == int(i['MIX_TYPE'].split('_')[1]) and int(i['MIX_TYPE'].split('_')[2]) != 1:
                map_key = i['MIX_TYPE'].split('M_')[1]
                map_value = self.mapping[map_key]
                # print(map_value)

                i['MIX_TYPE'] = map_value
                new_list.append(copy.deepcopy(i))

            else:
                # m*1 直接添加
                new_list.append(copy.deepcopy(i))

        # TODO 根据映射关系再次拆分MIX_TYPE,目前拆分一次  OK
        split_mix_type_result = []
        for i in new_list:
            i['MIX_TYPE'] = i['MIX_TYPE'].split(',')
            for j in i['MIX_TYPE']:
                i['MIX_TYPE'] = j
                split_mix_type_result.append(copy.deepcopy(i))

        return split_mix_type_result

    def split_draw_result_multiple_choose(self, split_by_match_count_list):
        """
        拆分胜负平多选de比赛
        :return:split_list []
        """
        my_list = []
        for split_dict in split_by_match_count_list:
            split_list = []
            # {'MULTIPLE': 10, 'DRAW_RESULT': ['20190103$周四306=(SF_LOST@1.46,SF_WIN@2.16)', '20190103$周四307=(SF_LOST@3.4,SF_WIN@1.17)'], 'TICKET_NO': '10004003239466431500620980159033', 'MIX_TYPE': 'M_2_1', 'match_count': 2}

            for result_str in split_dict['DRAW_RESULT']:
                new_list = []
                # result_str = '20190103$周四306=(SF_LOST@1.46,SF_WIN@2.16)'
                # 如果单场比赛有多选
                if re.search(r',', result_str):
                    # split_dict['DRAW_RESULT'].remove(result_str)
                    b = re.sub(r'\(|\)', '', re.search(r'\((.*?)\)', result_str).group()).split(',')

                    # print('b---:', b)
                    c = result_str.split('(')[0]
                    # c = 20190103$周四306=
                    for i in b:
                        # print(c + '(' + i + ')')
                        # 20190103$周四306=(SF_LOST@1.46)  20190103$周四306=(SF_WIN@2.16)
                        new_list.append(c + '(' + i + ')')

                    # print('new_list:', new_list)

                else:
                    # 单场比赛没有多选
                    new_list.append(result_str)

                split_list.append(new_list)

            # 构造字典
            split_dict['DRAW_RESULT'] = split_list

            my_list.append(split_dict)

        split_list = []

        for each_dict in my_list:
            a = each_dict['DRAW_RESULT']

            b = a[0]
            c = []
            for i in b:
                d = []
                d.append(i)
                c.append(d)

            pre_arr = c
            a.pop(0)
            for arr in a:
                pre_arr = self.sort_(pre_arr, arr)

            # print(pre_arr)

            for i in range(len(pre_arr)):
                each_dict['DRAW_RESULT'] = pre_arr[i]
                # print(each_dict)
                split_list.append(copy.deepcopy(each_dict))

        return split_list

    def sort_(self, pre_arr, arr):
        arr_list = []

        new_pre_arr = pre_arr

        for pre_arr1 in new_pre_arr:
            for a in arr:
                pre_arr2 = pre_arr1.copy()
                pre_arr2.append(a)
                arr_list.append(pre_arr2)
        return arr_list

    def delete_data(self, split_list):
        """
        用户下单倍数>50时,order_no是一样的 需要合并 并且倍数相加
        :param split_list:
        :return: new_split_list []
        """
        # print(split_list)
        # print(len(split_list))

        for i in split_list:
            if len(i['DRAW_RESULT']) < int(i['MIX_TYPE'].split('_')[1]):
                split_list.remove(i)

            i['DRAW_RESULT'] = ', '.join(i['DRAW_RESULT'])

        a = []
        print(split_list[:5])
        df = pd.DataFrame(split_list)

        # print(df.columns)
        link = df.groupby(by=['LOTTERY_TYPE','LOTTERY_SUB_TYPE','DRAW_RESULT','ORDER_NO','MIX_TYPE','MATCH_COUNT','ISSUE_NO'])['MULTIPLE'].sum().reset_index()
        # print(link.head())

        kk = link.T.to_dict()
        for i in range(0, len(kk)):
            # print(kk[i])
            a.append(kk[i])

        return a

    def increase_fields(self, data):
        """
        增加字段,便于计算 GAME_NO, GAME_RESULT, STATUS
        :param data:
        :return:
        """
        split_last_list = []
        global num
        for each_dict in data:
            each_dict['UNIQUE_ID'] = num
            each_dict['GAME_RESULT_SP'] = -1
            each_dict['UNIQUE_STATUS'] = 'INIT'

            num += 1
            try:
                result_list = each_dict['DRAW_RESULT'].split(', ')
                for i in result_list:
                    each_dict['GAME_NO'] = re.search(r'\$(.*?)=', i).group(1)
                    # print(each_dict)
                    split_last_list.append(copy.deepcopy(each_dict))
            except Exception as e:
                logging.error(e)
        with open('./i.txt', 'w') as f:
            f.write(str(num))
        # print(split_last_list)
        return split_last_list

    def save_2_oracle(self, split_last_list):
        """
        保存数据到oracle
        :param split_last_list: 列表嵌套字典，拆分完以后的数据
        :return:
        """
        try:
            db = cx_Oracle.connect('bd_warehouse/v5gaoo5c2uc1u4ye@10.0.12.29:1521/jczjtest')  # 线上
            # db = cx_Oracle.connect('bd_warehouse/bd_warehouse@10.0.12.2:1521/dev')
            cursor = db.cursor()

            in_data=[]
            up_data=[]
            # print(split_last_list)

            for item in split_last_list:
                item['DRAW_RESULT'] = item['DRAW_RESULT'].replace(', ', '|')
                item['GMT_CREATE'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item['GMT_MODIFIED'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                sql = """select ORDER_NO,ISSUE_NO,DRAW_RESULT,LOTTERY_SUB_TYPE from  PRIZE_TICKET_SPLIT
            where ORDER_NO='%s' and DRAW_RESULT='%s' and GAME_NO='%s' and LOTTERY_SUB_TYPE='%s'""" % (
                item['ORDER_NO'], item['DRAW_RESULT'], item['GAME_NO'], item['LOTTERY_SUB_TYPE'])
                cursor.execute(sql)
                ret = cursor.fetchall()

                # 判断是否有重复数据
                if not ret:
                    in_data.append((item['ORDER_NO'], item['DRAW_RESULT'], item['MIX_TYPE'], item['MULTIPLE'],
                                    item['GMT_CREATE'], item['MATCH_COUNT'], item['UNIQUE_ID'], item['GAME_RESULT_SP'],
                                    item['UNIQUE_STATUS'], item['GAME_NO'], item['ISSUE_NO'], item['LOTTERY_TYPE'],
                                    item['LOTTERY_SUB_TYPE'], item['GMT_MODIFIED']))

                else:
                    # 有重复数据
                    up_data.append((item['MULTIPLE'], item['GMT_CREATE'], item['GMT_MODIFIED'], item['ORDER_NO'],
                                    item['DRAW_RESULT'], item['GAME_NO'], item['MULTIPLE'], item['LOTTERY_SUB_TYPE']))

            sql = """INSERT INTO PRIZE_TICKET_SPLIT (id, ORDER_NO, DRAW_RESULT, MIX_TYPE, MULTIPLE, GMT_CREATE, MATCH_COUNT, UNIQUE_ID, GAME_RESULT_SP, UNIQUE_STATUS, GAME_NO,ISSUE_NO,LOTTERY_TYPE,LOTTERY_SUB_TYPE,GMT_MODIFIED) 
	    VALUES (SEQ_PRIZE_TICKET_SPLIT.nextval, :v2, :v3, :v4, :v5,to_date(:v6,'yyyy-mm-dd hh24:mi:ss') ,:v7, :v8, :v9, :v10, :v11, :v12,:v13,:v14,to_date(:v15,'yyyy-mm-dd hh24:mi:ss'))"""

            up_sql = """update PRIZE_TICKET_SPLIT set MULTIPLE=:v1,GMT_CREATE=to_date(:v2,'yyyy-mm-dd hh24:mi:ss'), GMT_MODIFIED=to_date(:v3,'yyyy-mm-dd hh24:mi:ss') where 
	    ORDER_NO=:v4 and DRAW_RESULT=:v5 and GAME_NO = :v6 and MULTIPLE < :v7 and LOTTERY_SUB_TYPE=:v8"""

            if len(up_data)>0:
                print('开始更新数据')
                cursor.executemany(up_sql, up_data)
                db.commit()
                print('%d条数据更新Successful' % len(up_data))
                logging.info('%d条数据更新Successful' % len(up_data))

            if len(in_data) > 0:
                print('开始插入数据')
                cursor.executemany(sql,in_data)
                db.commit()
                print('%d条数据插入Successful'%len(in_data))
                logging.info('%d条数据插入Successful'%len(in_data))

            db.close()

        except Exception as e:
            logging.error(e)


    def run(self):  # 入口函数
        # 1. 读取数据
        self.read_oracle()
        logging.info('读取oracle数据成功')

        # 2. 根据mix_type拆分成单选
        split_mix_type_result = self.split_mix_type()

        # 3.计算比赛场次
        match_count_result = self.match_count(split_mix_type_result)

        # 4.计算组合方式
        split_by_match_count_list = self.split_by_match_count(match_count_result)

        loop_times = 0
        while True:

            if loop_times >= 3:
                break

            # print(len(split_by_match_count_list))

            split_by_match_count_list = self.split_by_match_count(split_by_match_count_list)

            loop_times += 1

        # 5.根据购买单场比赛 结果 拆分
        split_list = self.split_draw_result_multiple_choose(split_by_match_count_list)

        if len(split_list)==0:
            logging.info('当前时间段无数据,程序结束。len=%d' % len(split_list))
            return

        # 6.删除错误数据
        new_split_list = self.delete_data(split_list)
        # print('new_split_list:', new_split_list)
        # print(len(new_split_list))

        # 7.添加字段
        split_last_list = self.increase_fields(new_split_list)
        # print('split_last_list:',split_last_list)
        print(len(split_last_list))
        logging.info('%d条小票拆分完成' % len(split_last_list))

        # 8.保存数据
        # self.save_2_oracle(split_last_list)
        logging.info('保存结果到oracle成功')


if __name__ == '__main__':
    money_award = MoneyAward()
    money_award.run()

---------------------------------------------------------------------------------------------------------------------------

"""
自定义多线程类,获取子线程返回值
"""
import threading


class MyThread(threading.Thread):
    def __init__(self, target=None, args=(), **kwargs):
        super(MyThread, self).__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):
        if self._target == None:
            return
        self.__result__ = self._target(*self._args, **self._kwargs)

    def get_result(self):
        # 当需要取得结果值的时候阻塞等待子线程完成
        self.join()

        return self.__result__

---------------------------------------------------------------------------------------------------------------------------

import re

from info.modules.search_person.search_script_conf import es


def search_person_indistinct(keyword):
    """
    模糊匹配
    :param keyword:
    :return:
    """
    if len(keyword) > 1:
        if re.match(r'^[a-zA-Z\d]+$', keyword):
            # fuzzy “fuzziness”为“编辑距离”,相似度,“prefix_length”前缀相同长度。
            body = {
                "query": {
                    "fuzzy": {
                        "loginName": {
                            "value": keyword,
                            "fuzziness": 2,
                            "prefix_length": 3
                        }
                    }
                },
                'from': 0,
                'size': 20000,  # ES默认显示10条数据

            }
        else:
            body = {
                'query': {
                    'multi_match': {
                        'query': keyword,
                        'fields': ['loginName'],
                        'fuzziness': 'AUTO',
                        # 'fuzziness': 2,
                    }
                },
                'from': 0,
                'size': 100000,  # ES默认显示10条数据

            }
    else:
        # 单个字搜索
        body = {
            "query": {
                "wildcard": {
                    "loginName": "*" + keyword + "*",
                }
            },
            'from': 0,
            'size': 20000,
        }
    ret_people = es.search(index='user', doc_type='cif_user', body=body)
    return ret_people


def search_person_exact(keyword):
    """
    精确匹配, name字段不分词
    :param keyword:
    :return:
    """
    body = {
        "query": {
            "constant_score": {
                "filter": {
                    "term": {
                        "loginName.facet": keyword
                    }
                }
            }
        },
        # 'sort': [  # manito_score字段排序  manito_score相同使用score排序
        #     {
        #         'manito_score.sort': {'order': 'desc'},
        #         '_score': {"order": "desc"}
        #     }
        # ]
    }
    exact_people = es.search(index='user', doc_type='cif_user', body=body)
    return exact_people

import re

from info.modules.search_person.search_script_conf import es


def search_content_index(keyword, page, limit):
    if len(keyword) > 1:
        if re.match(r'^[a-zA-Z0-9]+$', keyword):
            # fuzzy “fuzziness”为“编辑距离”,相似度,“prefix_length”前缀相同长度。
            body = {

                "query": {
                    "bool": {
                        "must":{
                            "bool":{
                                "should": [
                                    {
                                        "fuzzy": {
                                            "title": {
                                                "value": keyword,
                                                "fuzziness": 1,
                                                "prefix_length": 2
                                            }
                                        }

                                    },
                                    {
                                        "fuzzy": {
                                            "content": {
                                                "value": keyword,
                                                "fuzziness": 1,
                                                "prefix_length": 2
                                            }
                                        }
                                    }
                                ]
                            }

                        },
                        "filter": {
                            "bool":{
                                "must": [
                                    {"term": {"deleted": "0"}},
                                    {"term": {"status": "published"}}
                                ],
                            }
                        }
                    }
                },
                'from': (int(page) - 1) * int(limit),
                'size': int(limit),  # ES默认显示10条数据
            }
        else:
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "multi_match": {
                                'query': keyword,
                                'fields': ['title', 'content', 'longContent'],
                                'fuzziness': 'AUTO',
                            }
                        },
                        "filter": {
                            "bool":{
                                "must": [
                                    {"term": {"deleted": "0"}},
                                    {"term": {"status": "published"}}
                                ],
                            }
                        }
                    }
                },
                'from': (int(page) - 1) * int(limit),
                'size': int(limit)
            }

    else:
        # 单个字搜索
        body = {
            "query": {

                "bool": {
                    "must": {
                        "bool": {
                            "should": [{
                                "wildcard": {
                                    "title": "*" + keyword + "*",
                                }
                            }, {
                                "wildcard": {
                                    "content": "*" + keyword + "*",
                                }
                            }, {
                                "wildcard": {
                                    "longContent": "*" + keyword + "*",
                                }
                            }]
                        }
                    },
                    "filter": {
                        "bool":{
                            "must": [
                                {"term": {"deleted": "0"}},
                                {"term": {"status": "published"}}
                            ],
                        }
                    }
                }
            },
            'from': (int(page) - 1) * int(limit),
            'size': int(limit),
        }

    ret_content = es.search(index='subject', doc_type='wbc_subject', body=body)
    return ret_content
-----------------------------------------------------------------------------------------------------------------------------------
"""
协同过滤
"""
# -*-coding:utf-8 -*-
# @author  : 草上飞
import json
import math
import numpy as np
import pandas as pd

from pyhive import hive

from config import redis_cluster, ENV, HIVE_IP
from loggers import *

from operator import itemgetter


class UserCF(object):
    def __init__(self):
        # redis连接
        self.redis = redis_cluster(ENV)

        # hive连接
        self.hive = hive.Connection(host=HIVE_IP, port=10000, username='caoshangfei', database='dw')
        # self.hive = hive.Connection(host='10.4.231.2', port=10000, username='caoshangfei', database='dw')
        print('connect hive successful')

        # 获取所有用户点击历史redis
        self.click_hist = self.redis.keys(pattern='*-click-hist')
        print('redis_key_length: ', len(self.click_hist))
        # print(self.click_hist)
        # debug('redis_click_hist：{}'.format(str(self.click_hist)))

        # 用户和点击历史
        self.user_click_hist_redis = {}
        self.user_click_hist_all = {}

        # 用户相似度矩阵
        self.user_sim_matrix = {}

        # 话题点击人数
        self.subject_click_num = {}

        # 相似度前10的用户
        self.n_sim_users = 10

        # 话题只被一个人点击
        self.one_user_click_subject=set()

    # 切割redis键名，获取userId,redis中有效的用户点击历史
    def split_user_subject(self):

        for i in self.click_hist:
            subject = self.redis.smembers(i)
            self.user_click_hist_redis[i.split('-')[0]] = subject

        # 计算人数
        self.calculate_cell_num()

    def calculate_cell_num(self,sql_user=None):
        # 计算人数
        cursor = self.hive.cursor()

        if sql_user is not None:
            cursor.execute(
                """select count(distinct a.cell) from dw.bl_user_info b join 
        (select cell from dw.bl_user_info where user_id in {}) a 
    on b.cell=a.cell""".format(tuple(sql_user))
            )
        else:
            cursor.execute(
                """select count(distinct a.cell) from dw.bl_user_info b join 
        (select cell from dw.bl_user_info where user_id in {}) a 
    on b.cell=a.cell""".format(tuple(self.user_click_hist_redis.keys()))
            )
        count_cell = cursor.fetchall()
        print('cell数量', count_cell)
        cursor.close()

    # 获取用户长期点击历史，与有效期内的点击历史相加
    def get_old_click_hist(self):
        cursor = self.hive.cursor()
        cursor.execute(
            """select user_id,id from tempon.ml_qiongjiu_api_log_detail 
                    where partition_date BETWEEN  date_sub(current_date,7) and  date_sub(current_date,1) 
                    and action = 'view' 
                    and module = 'list'
                    and page_name = 'home'
                    and user_id regexp '[0-9]{32}'"""
        )
        click_old_list = cursor.fetchall()
        df1 = pd.DataFrame(click_old_list, columns=['user_id', 'id'])

        # 分组
        df2 = df1.groupby(['user_id'])['id']

        # hive近7天点击历史
        click_old_dict = {}
        for k, v in df2:
            click_old_dict[k] = set(v.to_list())

        # 点击历史hive+redis合并
        for user_id,subject in click_old_dict.items():
            for k,v in self.user_click_hist_redis.items():
                if user_id == k:
                    self.user_click_hist_all[user_id] = subject | v
                else:
                    self.user_click_hist_all[k] = v

            else:
                self.user_click_hist_all[user_id] = subject


        print('用户历史点击与有效期内点击合并成功。',len(self.user_click_hist_all.keys()))

        cursor.close()

    # 计算所有话题点击人数
    def calculate_subject_click_num(self):
        subject_list = []
        for user,subjects in self.user_click_hist_all.items():
            subject_list.extend(list(subjects))

        subject_set = set(subject_list)
        for i in subject_set:
            self.subject_click_num[i] = subject_list.count(i)

            # 判断点击次数只有一次的
            if subject_list.count(i)==1:
                self.one_user_click_subject.add(i)

        # print(self.subject_click_num)

    # 计算用户相似度
    def user_sim(self):
        #  建立话题-用户倒排表
        subject_user = {}
        for user, subjects in self.user_click_hist_all.items():

            for subject in subjects:
                subject_user.setdefault(subject, set())
                subject_user[subject].add(user)

        # print(subject_user)

        # 计算相似度矩阵
        for subject, users in subject_user.items():
            for u in users:
                for index, v in enumerate(users):
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    # self.user_sim_matrix[u][v] = self.user_sim_matrix[u][v] + 1*(1/math.log(1+self.subject_click_num[subject]))
                    self.user_sim_matrix[u][v] += 1

                    # 判断循环最后一轮
                    if index==len(users)-1:
                        self.user_sim_matrix[u][v] = self.user_sim_matrix[u][v] * (1/math.log(1+self.subject_click_num[subject]))

        print('===========')
        # print(self.user_sim_matrix)

        for u, related_users in self.user_sim_matrix.items():
            for v, count in related_users.items():
                n_u = len(self.user_click_hist_all[u])
                n_v = len(self.user_click_hist_all[v])
                self.user_sim_matrix[u][v] = count / math.sqrt(n_u * n_v)

        # print(self.user_sim_matrix)
        print('用户相似度计算完成')

    # 推荐内容
    def recommend(self, user_id):
        recmd = {}

        try:
            # 用户有效期内点击历史
            user_click_hist = self.user_click_hist_redis[user_id]
            # print(user_id + ' user_click_hist: ', user_click_hist)

            # 排名前n的相似用户
            sim_users = sorted(self.user_sim_matrix[user_id].items(), key=itemgetter(1), reverse=True)
            # print(self.user_sim_matrix['10064003938164827700050010029946'])


            # 删除相似度1.0的用户
            df1 = pd.DataFrame(sim_users, columns=['user', 'score'])
            df2 = df1[df1.score != 1.0]
            df2 = df2[df2.score >= 0.5]
            # print(df1[df1.score == 1.0])

            n_sim_users = np.array(df2).tolist()[:self.n_sim_users]
            # print('n_sim_users: ',n_sim_users)

            # 推荐用户没有点击过的内容
            for user, score in n_sim_users:
                for subject in self.user_click_hist_redis[user]:
                    if subject not in user_click_hist:
                        recmd.setdefault(subject, 0)
                        recmd[subject] += score * float(1)
            # print(recmd)
            if len(recmd.keys()) != 0:
                return {user_id: recmd}

        except Exception as e:
            # print(e)
            pass

    # 获取user_id
    def get_user_id(self):
        cursor = self.hive.cursor()
        # 执行查询
        cursor.execute(
            """select  distinct user_id from dw.bl_recommend_api_log_detail 
where partition_date between date_sub(current_date,3) and  date_sub(current_date,1) 
    and user_id regexp '[0-9]{32}' and app_id='kk' and page_name='HOT_RECOMMEND'"""
        )

        ret = cursor.fetchall()
        print('select hive successful')

        hive_user_id_list = [''.join(i) for i in ret]
        redis_user_id_list = self.user_click_hist_redis.keys()

        # hive近5天user_id+redis时效内的user_id
        user_id = set(hive_user_id_list) | set(redis_user_id_list)

        print('hive user id length:',len(user_id))

        return user_id

    # 开始程序
    def run(self):
        pl = self.redis.pipeline()
        self.split_user_subject()

        self.get_old_click_hist()

        self.calculate_subject_click_num()

        # user_id_list = ['10064004617789424900290970012126']

        user_id_list = self.get_user_id()

        self.user_sim()
        s = 0
        r = 0
        sql_user = []
        for user_id in user_id_list:
            ret = self.recommend(user_id)
            if ret is not None:
                sql_user.append(user_id)
                # print('ret:', ret)
                temp_set = set(ret[user_id].keys())-self.one_user_click_subject
                if len(temp_set)>0:

                    pl.sadd(user_id + '_sim_user_recmd', *temp_set)
                    s += 1
                if len(temp_set) >= 2:
                    r += 1

        pl.execute()
        print('可推荐用户：', s)
        print('推荐内容数量大于2篇的用户：', r)

        # 计算人数
        self.calculate_cell_num(sql_user=sql_user)

        self.hive.close()


if __name__ == '__main__':
    user_cf = UserCF()
    user_cf.run()
	
"""
kmeans用户聚类
"""
# -*-coding:utf-8 -*-
# @author  : 草上飞
import math

import numpy as np
import pandas as pd
from pyhive import hive

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from config import redis_cluster, ENV, HIVE_IP


class UserLabel:
    def __init__(self):
        self.conn = hive.Connection(host=HIVE_IP, port=10000, username='caoshangfei', database='dm')
        self.cursor = self.conn.cursor()
        self.redis = redis_cluster(env=ENV)

    def select_data(self):
        sql = """select a.user_id,a.lottery_type,a.sp_perf_7d,a.rank_perf_7d,a.manito_preference,a.kk_customer_activity,a.advertisement_7day_scorce,a.entertainment_7day_scorce,a.information_7day_scorce,a.promote_7day_scorce
 from
(select * from dm.customer_preference_label where partition_date = date_sub(current_date,1) and if_customer_active='1.0') a join 
(select user_id from dw.bl_bury_point_detail where partition_date between date_sub(current_date,7) and date_sub(current_date,1) and app_id ='kk' group by user_id) b 
on a.user_id=b.user_id"""
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        print('查询hive成功。')

        df1 = pd.DataFrame(data, columns=['user_id','lottery_type','sp_perf_7d','rank_perf_7d','manito_preference','kk_customer_activity','advertisement_7day_scorce','entertainment_7day_scorce','information_7day_scorce','promote_7day_scorce'])
        df2 = df1[(df1['user_id'] != '-') & (df1['user_id'] != '')]


        # df2 = df1.replace('-', '')

        # 显示所有列
        # pd.set_option('display.max_columns', None)

        # df1['manito_preference'].replace({'-':None})
        df2['manito_preference'] = df2['manito_preference'].replace('-', '')

        df2['manito_preference_list'] = df2['manito_preference'].str.split(',')
        tmp_set = set()
        for lst in df2['manito_preference_list']:
            for i in lst:
                tmp_set.add(i)
        main_col = 'manito_preference'

        for sub_type in tmp_set:
            df2[main_col + '_' + sub_type] = df2[main_col].str.contains(sub_type).astype(int)

        # 删除多余列表
        df2 = df2.drop(['manito_preference', 'manito_preference_list'], axis=1)

        df3 = df2.set_index('user_id')

        df4 = pd.get_dummies(df3[['lottery_type', 'sp_perf_7d', 'rank_perf_7d','kk_customer_activity']])

        # 合并
        pd_merge = pd.merge(df3, df4, how='outer', right_index=True, left_index=True)
        pd_merge = pd_merge.drop(['lottery_type', 'sp_perf_7d', 'rank_perf_7d','kk_customer_activity'], axis=1)
        pd_merge[['advertisement_7day_scorce', 'entertainment_7day_scorce', 'information_7day_scorce',
                  'promote_7day_scorce']] = pd_merge[
            ['advertisement_7day_scorce', 'entertainment_7day_scorce', 'information_7day_scorce',
             'promote_7day_scorce']].astype(float)


        kmeans_model = KMeans(n_clusters=10, n_jobs=3, random_state=100)
        kmeans_model.fit(pd_merge.values)

        # 聚类结果标签
        pd_merge['cluster'] = kmeans_model.labels_

        # 质心
        kc = kmeans_model.cluster_centers_
        # print(kc)

        kc_1 = []
        for i in kc:
            # print(i)
            s = self.normalization(i)
            kc_1.append(s)
        # print(kc_1)

        # np.savetxt('/home/admin/test/user_cf/kc.csv', kc, fmt="%.6f")
        print(kc.shape)

        # 统计各个类别的数目
        count = pd.Series(kmeans_model.labels_).value_counts()
        print(count)

        df5 = pd_merge.sort_values(by=['cluster'])
        # np.savetxt('/home/admin/test/user_cf/columns.csv', np.array(df5.columns), fmt="%s", encoding='utf-8')

        # 获取每组的用户
        user_group = {}
        for k, v in df5.groupby(by=['cluster']):
            user_group[k] = v.index.to_list()

        # 计算每组内话题点击次数
        for group, users in user_group.items():
            print(group)
            pl = self.redis.pipeline()
            for user in users:
                pl.smembers(user + '-click-hist')
            ret = pl.execute()  # 点击

            # TODO 计算点击率 再对热度文章惩罚
            for user in users:
                pl.smembers(user + '-expose-hist')
            ret2 = pl.execute()  # 曝光

            click_user = self.calculate_count(ret=ret, k='click')

            expose_user = self.calculate_count(ret=ret2, k='expose')

            # 计算话题点击率
            click_rate = {}
            for subject_id,user_count in click_user.items():
                click_rate[subject_id] = user_count/expose_user[subject_id] * (1/math.log(1+user_count))

            print(dict(sorted(click_rate.items(), key=lambda x:x[1], reverse=True)[:10]))



    # 归一化处理
    def normalization(self, rank_list):
        score_min = min(rank_list)
        score_max = max(rank_list)
        score_list = []
        for i in rank_list:
            v = (i - score_min) / (score_max - score_min)
            score_list.append(v)
        return score_list

    # 计算
    def calculate_count(self,ret,k):
        new_list = []
        for i in ret:
            if len(i) > 0:
                new_list.extend(list(i))
        # 计算人数
        click_set = set(new_list)
        click_count = {}
        for subject in click_set:
            click_count[subject]=new_list.count(subject)
        print(dict(sorted(click_count.items(), key=lambda x:x[1], reverse=True)[:10]))

        return click_count


if __name__ == '__main__':
    # main()
    user_label = UserLabel()
    user_label.select_data()

-------------------------------------------------------------------------------------------------------------------------------
"""
杀死进程
"""
import os, signal
import sys
import subprocess


# 命令行传参
port = sys.argv[1]
print(port)

out = os.popen("lsof -i:{}".format(port)).read()
#print('进程',out)


def kill(pid):
    try:
        a = os.kill(pid, signal.SIGKILL)
        print('已杀死pid为%s的进程,　返回值是:%s' % (pid, a))

    except OSError:
        print('没有此进程!!!')


for line in out.splitlines():
    print(line)
    if "PID" in line:
        pass
    else:
        pid = int(line.split(' ')[1])
        print(pid)
        # os.kill(pid,signal.SIGKILL)
        kill(pid)
---------------------------------------------------------------------------------------------------------------------------

# -*-coding:utf-8 -*-
# @author  : 草上飞
07-文本相似度.py

import pkuseg

from gensim import corpora,models, similarities


doc0 = "我不喜欢上海"
doc1 = "上海是一个好地方"
doc2 = "北京是一个好地方"
doc3 = "上海好吃的在哪里"
doc4 = "上海好玩的在哪里"
doc5 = "上海是好地方"
doc6 = "上海路和上海人"
doc7 = "喜欢小吃"
doc_test="我喜欢上海的小吃"

all_doc = []
all_doc.append(doc0)
all_doc.append(doc1)
all_doc.append(doc2)
all_doc.append(doc3)
all_doc.append(doc4)
all_doc.append(doc5)
all_doc.append(doc6)
all_doc.append(doc7)

seg = pkuseg.pkuseg()  # 加载默认模型

all_doc_list = []

for doc in all_doc:
    doc_list = [word for word in seg.cut(doc)]
    all_doc_list.append(doc_list)

print("all_doc_list:", all_doc_list)

# 测试文档
doc_test_list = [word for word in seg.cut(doc_test)]
print(doc_test_list)

"""
# 可以加载停用词stop words
# 进行分词
text = seg.cut(content)


#停用词
stopwords = []
with open('stopwords.txt',encoding='utf-8') as f:
    stopwords = f.read()

new_text = []
for w in text:
    if w not in stopwords:
        new_text.append(w)
        print(new_text)
"""


# 制作语料库
# 使用dictionary方法获取词袋
dictionary = corpora.Dictionary(all_doc_list)

# 词袋数字编号
print(dictionary.keys())

# 编号与词之间的对应关系
print(dictionary.token2id)
print("="*50)

# 使用doc2bow制作语料库
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]

# 语料库是一组向量，向量中的元素是一个二元组（编号、频次数），对应分词后的文档中的每一个词
print("corpus:",corpus)

# 把测试文档也转换为二元组的向量
doc_test_vec = dictionary.doc2bow(doc_test_list)
print("doc_test_vec:",doc_test_vec)

# 相似度分析
# 使用TF-IDF模型对语料库建模
tfidf = models.TfidfModel(corpus)
print(tfidf)

print(tfidf[doc_test_vec])  # 测试文档中每个词的tf-idf值

# 分析测试文档的相似度
index = similarities.SparseMatrixSimilarity(tfidf[corpus],num_features=len(dictionary.keys()))

sim = index[tfidf[doc_test_vec]]

print('sim:',sim)
# 根据相似度排序
ret = sorted(enumerate(sim), key=lambda item:-item[1])
print('ret:',ret)
# 测试文档与doc7相似度最高，其次是doc0，与doc2的相似度为零


------------------------------------------------------------------------------------------------------------
{
html，
css，
js
}

index.html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>JS百度搜索框联想词提示代码</title>

<link rel="stylesheet" type="text/css" href="css/my.css" />

</head>
<body>

<div id="out">
	<div id="ser_box">
		<input type="search" id="ipt" /><span><input id="su" value="搜索" class="bg s_btn" type="submit"></span>
	</div>

	<div id="bot_box">
		<ul id="oul"></ul>
	</div>
</div>

<script src="js/my.js" type="text/javascript" charset="utf-8"></script>

<div style="text-align:center;margin:50px 0; font:normal 14px/24px 'MicroSoft YaHei';">
<p>适用浏览器：360、FireFox、Chrome、Safari、Opera、傲游、搜狗、世界之窗. 不支持IE8及以下浏览器。</p>
<p>来源：<a href="http://sc.chinaz.com/" target="_blank">站长素材</a></p>
</div>
</body>
</html>

my.css

*{
	margin: 0;
	padding: 0;
}
#out{
	width:500px;
	height:140px;
	margin: 160px 350px;
}
#ser_box{
	width:500px;
	height:32px;
	border: 1px solid red;
	text-align: center;
}
#ipt{
	width:480px;
	height: 26px;
	margin-top: 2px;
	border: 0;
	outline: 0;
	font-family: "微软雅黑";
	font-size: 16px;
}

#bot_box{
	width:500px;
	border: 1px solid #4C9ED9;
	border-top: none;
	display: none;
	}
	
#bot_box ul li{
		list-style: none;
		line-height: 25px;
		padding-left: 10px;
		}
#bot_box ul li:hover{
		background: #BCBCBC;
		}		
.s_btn {
	position:relative;
	left:300px;
	top:-31px;
    width: 100px;
    height: 36px;
    color: #fff;
    font-size: 15px;
    letter-spacing: 1px;
    background: red;
    border-bottom: 1px solid #2d78f4;
    outline: medium;
}
  
.sel{
	background:#BCBCBC;
}


my.js
function $(id) {
	return document.getElementById(id);
}

var ipt = $("ipt");
var ser = $("ser_box");
var bot = $("bot_box");
var oul = $("oul");


ipt.oninput = function() {
	var ss = ipt.value;
	// var url = "http://suggestion.baidu.com/su?cb=queryList&wd=" + ss;
	var url = "http://192.168.191.1:8000/api/search/person/su?cb=queryList&wd=" + ss;
	addScript(url);
}

ipt.onfocus = function() {
	var ss = ipt.value;
	// var url = "http://suggestion.baidu.com/su?cb=queryList&wd=" + ss;
	var url = "http://192.168.191.1:8000/api/search/person/su?cb=queryList&wd=" + ss;
	addScript(url);

}

function queryList(data) {
	ss=document.getElementsByTagName("script")[0];
	document.body.removeChild(ss)
	
	var arr = data.s;
	oul.innerHTML = "";
	if(arr.length == 0) {
		bot.style.display = "none";
	} else {
		bot.style.display = "block";
	}

	for(var i = 0; i < arr.length; i++) {
		li = document.createElement("li");
		li.innerHTML = arr[i];
		li.onclick = function() {
			oul.innerHTML = "";
			ipt.value = this.innerHTML;
			bot.style.display = "none";
		}
		oul.appendChild(li);
	}
}

function addScript(url) {
	var s = document.createElement("script");
	s.src = url;
	s.type = "text/javascript";
	document.body.appendChild(s);
}

/*取li*/

lis = document.getElementsByTagName("li");

/*按键*/
var i = 0;

document.onkeydown = function(ev) {

	if(bot.style.display == "block") {
		

		if(ev.keyCode == 40) {
			for(var j = 0; j < lis.length; j++) {
				if(lis[j].className == "sel") {
					lis[j].className = "";
				}
			}

			if(i < lis.length) {
				lis[i].className = "sel";
				i++;
				if(i == lis.length) {
					i = 0;
				}
			}
		}

		if(ev.keyCode == 38) {
			m = 0
			for(; m < lis.length; m++) {
				if(lis[m].className == "sel") {
					lis[m].className = "";
					break;
				}
			}
			i = m;
			if(m > 0) {
				lis[m - 1].className = "sel";
			} else {
				lis[lis.length - 1].className = "sel";
			}
		}

		
		
		
		if(ev.keyCode == 13) {
			for(var n = 0; n < lis.length; n++) {
				if(lis[n].className == "sel") {
					ipt.value = lis[n].innerHTML;
				}
			}
			bot.style.display = "none";
		}
	} else {
		i = 0;
		m = 0;
	}
}


flask_api
@search_person_blu.route('/su/')
def index():
    """
    搜索提示功能
    根据输入的值自动联想,支持中文,英文,英文首字母
    :return: response
    """
    global num
    num += 1
    if num % 100 == 0:
        reload(search_script_conf)
        print(search_script_conf.sug)

    wd = request.args.get('wd')

    if not wd:
        return make_response("""queryList({"q":"","p":false,"bs":"","csor":"0","status":770,"s":[]});""")

    # 搜索词(支持中文，英文，英文首字母)
    s = wd

    result = search_script_conf.get_tips_word(search_script_conf.sug, search_script_conf.data, s)[:10]

    response = make_response(
        """queryList({'q':'""" + wd + """','p':false,'s':""" + str(result) + """});""")

    response.headers['Content-Type'] = 'text/javascript; charset=utf-8'

    # 记录日志
    ret = dict()
    ret['code'] = 200
    ret['msg'] = "ok"
    ret['search_word'] = wd
    ret['search_result'] = result
    ret['search_type'] = 'search_tips'
    ret['gmt_created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    ret['user_id'] = ''
    ret['platformCode'] = ''
    info(json.dumps(ret, ensure_ascii=False))
    return response

-------------------------------------------------------------------------------------------------
import pymysql

db = pymysql.connect(host='127.0.0.1', user='root', password='mysql123', port=3306)
cursor = db.cursor()
cursor.execute("CREATE DATABASE maoyan DEFAULT CHARACTER SET utf8mb4")
db.close()

db = pymysql.connect(host='127.0.0.1', user='root', password='mysql123', port=3306, db='maoyan')
cursor = db.cursor()
sql = 'CREATE TABLE IF NOT EXISTS films (name VARCHAR(255) NOT NULL, type VARCHAR(255) NOT NULL, country VARCHAR(255) NOT NULL, 
length VARCHAR(255) NOT NULL, released VARCHAR(255) NOT NULL, score VARCHAR(255) NOT NULL, people INT NOT NULL, 
box_office BIGINT NOT NULL, PRIMARY KEY (name))'
cursor.execute(sql)
db.close()

def to_mysql(data):
    """
    信息写入mysql
    """
    table = 'films'
    keys = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    db = pymysql.connect(host='localhost', user='root', password='774110919', port=3306, db='maoyan')
    cursor = db.cursor()
    sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("Successful")
            db.commit()
    except:
        print('Failed')
        db.rollback()
    db.close()

-------------------------------------------------------------------------------------------------
gunicorn_config.py
"""
不用，需要的话再放到manage目录下使用
"""
# 为了更好的管理gunicorn，在项目目录下创建gunicorn_conf.py文件，内容如下
import os
import multiprocessing

# 获取当前该配置文件的绝对路径。gunicorn的配置文件是python文件,所以可以直接写python代码

path_of_current_file = os.path.abspath(__file__)

path_of_current_dir = os.path.split(path_of_current_file)[0]

chdir = path_of_current_dir

#workers = multiprocessing.cpu_count() * 2 + 1  # 可以理解为进程数，会自动分配到你机器上的多CPU，完成简单并行化

workers = 2  # 进程数量

worker_class = 'sync'  # 默认的worker的类型，如何选择见：[http://docs](http://docs).[gunicorn.org/en/stable/design.html#choosing-a-worker-type](http://gunicorn.org/en/stable/design.html#choosing-a-worker-type)

bind = '0.0.0.0:8000'  # 服务使用的端口

pidfile = '%s/gunicorn.pid' % path_of_current_dir  # 存放Gunicorn进程pid的位置，便于跟踪

accesslog = '%s/logs/00_gunicorn_access.log' % path_of_current_dir  # 存放访问日志的位置，注意首先需要存在logs文件夹，Gunicorn才可自动创建log文件

errorlog = '%s/logs/00_gunicorn_access.log' % path_of_current_dir  # 存放错误日志的位置，可与访问日志相同

reload = True  # 如果应用的代码有变动，work将会自动重启，适用于开发阶段

daemon = True # 是否后台运行

debug = False

timeout = 5   # server端的请求超时秒数

loglevel = 'error'

# 开启服务  gunicorn -b 10.4.212.3:8000 manage:app -c ./gunicorn_conf.py
# 查看进程  ps -aux | grep gunicorn / gunicorn.pid
# kill -9 pid

--------------------------------------------------------------------------------------------------------
search.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
    <style>
        * {
            padding: 0;
            margin: 0;
        }
        li{
            list-style: none;
        }
        li:hover{
            background: #ccc;
        }
        .wrapper {
            position: absolute;
            margin-left: -260px;
            left: 50%;
            top: 30%;
        }
        #btn {
            width: 560px;
            padding: 10px 10px;
            border: 1px solid rgb(45, 129, 240);
        }
        #ul{
            border: 1px solid #ddd;
            border-top: 0;
        }
        a{
            display: inline-block;
            width: 100%;
            text-decoration: none;
            color: rgba(0,0,0,0.8) ;
            outline: none;
            height: 30px;
            line-height: 30px;
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <input type="text " id="btn">
        <ul id="ul">
        </ul>
    </div>

    <script>
        var input = document.getElementById('btn')
        var oUl = document.getElementById('ul')
        input.onkeyup = function () {
            var value = this.value;
            var oScript = document.createElement('script');
            oScript.src = 'https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?wd=' + value + '&cb=aa'
            document.body.appendChild(oScript)
        }
        function aa(data) {
            oUl.style.display = 'block';
            var list = data.s;
            var str = '';
            if (list.length > 0) {
                list.forEach(function (ele, index) {
                    str += '<li><a href ="https://www.baidu.com/s?wd=' + ele + '">' + ele + '</li>';
                })
                oUl.innerHTML = str;
            } else {
                oUl.style.display = 'none';
            }
        }
    </script>
</body>
</html>



