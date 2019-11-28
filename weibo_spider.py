WeiboSpider-senior:{
                  read_mongodb,
                  sina,
                  start.py
              }
              
start.py
from scrapy import cmdline

cmdline.execute('scrapy crawl weibo_spider'.split())

==============================================================================
read_mongodb:{
                  01_read_mongo_regex_to_excel.py
              }

01_read_mongo_regex_to_excel.py

import pymongo
import pandas as pd
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME

# 消除报警
import warnings

warnings.filterwarnings('ignore', category=Warning)

client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
collection = client[DB_NAME]['Blogs']
cursor = collection.find({'content': {'$regex': '竞彩'}})
# cursor = collection.find({'user_id': '3516672303'})
print(cursor.count())
lie = []
for i in cursor:
    # print(i)
    # print(type(i))  # <class 'dict'>
    lie.append(i)

df=pd.DataFrame(lie).set_index(['_id'])
print(df)
df.to_excel('weibo.xlsx')

===============================================================================================================
sina:{
      account_bulid,
      spiders,
      __init__.py,
      items.py,
      middlewares.py,
      pipelines.py,
      redis_init.py,
      redis_scripts.py,
      settings.py
      }

__init__.py
None

items.py
# -*- coding: utf-8 -*-
from scrapy import Item, Field


class BlogsItem(Item):
    """ 微博信息 """
    _id = Field()  # 微博id
    weibo_url = Field()  # 微博URL
    created_at = Field()  # 微博发表时间
    like_num = Field()  # 点赞数
    repost_num = Field()  # 转发数
    comment_num = Field()  # 评论数
    content = Field()  # 微博内容
    article_url = Field()  # 微博文章url
    article_content = Field()  # 微博文章内容
    user_id = Field()  # 发表该微博用户的id
    tool = Field()  # 发布微博的工具
    image_url = Field()  # 图片
    video_url = Field()  # 视频
    location = Field()  # 定位信息
    origin_weibo = Field()  # 原始微博，只有转发的微博才有这个字段
    crawl_time_unix = Field()  # 抓取时间戳
    crawl_time_date = Field()  # 抓取时间日期


class InformationItem(Item):
    """ 个人信息 """
    _id = Field()  # 用户ID
    nick_name = Field()  # 昵称
    gender = Field()  # 性别
    province = Field()  # 所在省
    city = Field()  # 所在城市
    brief_introduction = Field()  # 简介
    birthday = Field()  # 生日
    microblogs_num = Field()  # 微博数
    follows_num = Field()  # 关注数
    fans_num = Field()  # 粉丝数
    sex_orientation = Field()  # 性取向
    sentiment = Field()  # 感情状况
    vip_level = Field()  # 会员等级
    authentication = Field()  # 认证
    person_url = Field()  # 首页链接
    labels = Field()  # 标签
    crawl_time_unix = Field()  # 抓取时间戳
    crawl_time_date = Field()  # 抓取时间日期


class RelationshipsItem(Item):
    """ 用户关系，只保留与关注的关系 """
    _id = Field()
    fan_id = Field()  # 关注者,即粉丝的id
    followed_id = Field()  # 被关注者的id
    crawl_time_unix = Field()  # 抓取时间戳
    crawl_time_date = Field()  # 抓取时间日期


class CommentItem(Item):
    """
    微博评论信息
    """
    _id = Field()
    comment_user_id = Field()  # 评论用户的id
    content = Field()  # 评论的内容
    weibo_url = Field()  # 评论的微博的url
    created_at = Field()  # 评论发表时间
    like_num = Field()  # 点赞数
    crawl_time_unix = Field()  # 抓取时间戳
    crawl_time_date = Field()  # 抓取时间日期

middlewares.py
# encoding: utf-8
import random

import pymongo
import redis

from sina.settings import LOCAL_MONGO_HOST, DB_NAME, LOCAL_MONGO_PORT, REDIS_HOST, REDIS_PORT


class CookieMiddleware(object):
    """
    每次请求都随机从账号池中选择一个账号去访问
    """

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.account_collection = client[DB_NAME]['account']

    def process_request(self, request, spider):
        all_count = self.account_collection.find({'status': 'success'}).count()
        if all_count == 0:
            raise Exception('当前账号池为空')
        random_index = random.randint(0, all_count - 1)
        random_account = self.account_collection.find({'status': 'success'})[random_index]
        request.headers.setdefault('Cookie', random_account['cookie'])
        request.meta['account'] = random_account


class RedirectMiddleware(object):
    """
    检测账号是否正常
    302 / 403,说明账号cookie失效/账号被封，状态标记为error
    418,偶尔产生,需要再次请求
    """

    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.account_collection = client[DB_NAME]['account']

    def process_response(self, request, response, spider):
        http_code = response.status
        if http_code == 302 or http_code == 403:
            self.account_collection.find_one_and_update({'_id': request.meta['account']['_id']},
                                                        {'$set': {'status': 'error'}}, )
            return request
        elif http_code == 418:
            spider.logger.error('ip 被封了!!!请更换ip,或者停止程序...')

            proxy_data = self.get_proxy_from_redis()
            current_proxy = f'https://{proxy_data}'
            spider.logger.debug(f"当前代理IP:{current_proxy}")
            request.meta['proxy'] = current_proxy
            return request

        else:
            return response

    def get_proxy_from_redis(self):
        """从redis中读取随机代理"""
        redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        try:
            # proxy = redis_connection.srandmember('proxy_pool')
            proxy = redis_connection.spop('proxy_pool')
            # print(proxy)
            return proxy.decode()
        except Exception as e:
            print('Proxy_pool connect filed', e)
            return None


class IPProxyMiddleware(object):

    def fetch_proxy(self):
        """从redis中读取随机代理"""
        # 如果需要加入代理IP，请重写这个函数
        # 这个函数返回一个代理ip，'ip:port'的格式，如'12.34.1.4:9090'
        redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        try:
            # proxy = redis_connection.srandmember('proxy_pool')
            proxy = redis_connection.spop('proxy_pool')
            # print(proxy)
            return proxy.decode()
        except Exception as e:
            print('Proxy_pool connect filed', e)
            return None

    def process_request(self, request, spider):
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = f'https://{proxy_data}'
            spider.logger.debug(f"当前代理IP:{current_proxy}")
            request.meta['proxy'] = current_proxy


pipelines.py
# -*- coding: utf-8 -*-
import pymongo
from pymongo.errors import DuplicateKeyError
from sina.items import RelationshipsItem, BlogsItem, InformationItem, CommentItem
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME


class MongoDBPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        db = client[DB_NAME]
        self.Information = db['Information']
        self.Blogs = db['Blogs']
        self.Comments = db['Comments']
        self.Relationships = db['Relationships']

    def process_item(self, item, spider):
        ''' 判断item的类型，并作相应的处理，再入数据库 '''
        if isinstance(item, RelationshipsItem):
            self.insert_item(self.Relationships, item)
        elif isinstance(item, BlogsItem):
            self.insert_item_update(self.Blogs, item)
        elif isinstance(item, InformationItem):
            self.insert_item(self.Information, item)
        elif isinstance(item, CommentItem):
            self.insert_item(self.Comments, item)
        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            # 说明有重复数据

            pass

    @staticmethod
    def insert_item_update(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            # 说明有重复数据,更新
            collection.update(
                {'_id': item.get('_id')},
                {'$set':
                    {
                        'article_content': item.get('article_content'),
                        'crawl_time_unix': item.get('crawl_time_unix'),
                        'crawl_time_date': item.get('crawl_time_date'),
                        'like_num': item.get('like_num'),
                        'repost_num': item.get('repost_num'),
                        'comment_num': item.get('comment_num'),
                    }
                }
            )
            pass


class MongoDBPipeline2(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        self.db = self.client[DB_NAME]
        self.Information = self.db['Information']
        self.Blogs = self.db['Blogs']
        self.Comments = self.db['Comments']
        self.Relationships = self.db['Relationships']

    def process_item(self, item, spider):
        ''' 判断item的类型，并作相应的处理，再入数据库 '''
        if isinstance(item, RelationshipsItem):
            self.insert_item(self.Relationships, item)
        elif isinstance(item, BlogsItem):
            self.insert_item(self.Blogs, item)
        elif isinstance(item, InformationItem):
            self.insert_item(self.Information, item)
        elif isinstance(item, CommentItem):
            self.insert_item(self.Comments, item)
        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            '''
            说明有重复数据
            '''
            pass

    def close_spider(self, spider):
        self.client.close()


redis_init.py
#!/usr/bin/env python
# encoding: utf-8
import redis
import sys
import os

# from sina.settings import LOCAL_REDIS_HOST, LOCAL_REDIS_PORT
from rediscluster import StrictRedisCluster

sys.path.append(os.getcwd())

# r = redis.Redis(host=LOCAL_REDIS_HOST, port=LOCAL_REDIS_PORT)
def redis_cluster(env):
    """
    连接到redis集群
    :return: 返回一个redis连接
    """
    redis_nodes_dev = [{'host': '10.3.90.6', 'port': 7001},
                       {'host': '10.3.90.6', 'port': 7002},
                       {'host': '10.3.90.6', 'port': 7003},
                       {'host': '10.3.90.6', 'port': 7004},
                       {'host': '10.3.90.6', 'port': 7005},
                       {'host': '10.3.90.6', 'port': 7006},
                       {'host': '10.3.90.6', 'port': 7007}]

    redis_nodes_prod = [{'host': '10.3.90.1', 'port': 7000},
                        {'host': '10.3.90.1', 'port': 7001},
                        {'host': '10.3.90.2', 'port': 7000},
                        {'host': '10.3.90.2', 'port': 7001},
                        {'host': '10.3.90.3', 'port': 7000},
                        {'host': '10.3.90.3', 'port': 7001},
                        {'host': '10.3.90.4', 'port': 7000},
                        {'host': '10.3.90.4', 'port': 7001},
                        {'host': '10.3.90.5', 'port': 7000},
                        {'host': '10.3.90.5', 'port': 7001},
                        {'host': '10.3.90.6', 'port': 7000},
                        {'host': '10.3.90.6', 'port': 7001}, ]

    try:
        redis_conn = None
        if env == 'dev':
            redis_conn = StrictRedisCluster(startup_nodes=redis_nodes_dev)
        else:
            redis_conn = StrictRedisCluster(startup_nodes=redis_nodes_prod)
    except Exception as e:
        # loggers.error("连接redis集群异常!{0}".format(str(e)))
        print(e)

    return redis_conn


# 连接redis
# 测试
r = redis_cluster('dev')
# 线上
# conn_redis = redis_cluster('prod')

for key in r.scan_iter("weibo_spider*"):
    r.delete(key)

start_uids = [
    '3516672303',  # 严谨
    '6380423180',  # 韩国模特
    '6014957055',  # 专业推荐足球体育
]
for uid in start_uids:
    r.lpush('weibo_spider:start_urls', "https://weibo.cn/%s/info" % uid)

print('redis初始化完毕')


redis_scripts.py
"""
添加start——redis——key，开始爬虫
"""
import redis

from sina.settings import REDIS_HOST,REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

start_uids = [
    '3738227653'
]
for uid in start_uids:
    r.lpush('weibo_spider:start_urls', "https://weibo.cn/%s/info" % uid)

print('redis_key添加成功')

settings.py
# -*- coding: utf-8 -*-

BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
}

# CONCURRENT_REQUESTS 和 DOWNLOAD_DELAY 根据账号池大小调整 目前的参数是账号池大小为200
CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 0.5


DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'sina.middlewares.CookieMiddleware': 300,
    'sina.middlewares.RedirectMiddleware': 200,
    # 'sina.middlewares.IPProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,

}

ITEM_PIPELINES = {
    'sina.pipelines.MongoDBPipeline': 300,
    # 'scrapy_redis.pipelines.RedisPipeline': None ,  # 数据保存到redis一份
}

# MongoDb 配置
LOCAL_MONGO_HOST = '10.4.180.12'
LOCAL_MONGO_PORT = 27000
DB_NAME = 'Sina'


# Redis 配置
REDIS_HOST = '192.168.191.137'
REDIS_PORT = 6379

# Ensure use this Scheduler
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"
# Ensure all spiders share same duplicates filter through redis
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
# Redis URL
REDIS_URL = 'redis://{}:{}'.format(REDIS_HOST, REDIS_PORT)
# Number of Hash Functions to use, defaults to 6
BLOOMFILTER_HASH_NUMBER = 6
# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
BLOOMFILTER_BIT = 31
# Persist
SCHEDULER_PERSIST = True



# Redis集群地址
# REDIS_MASTER_NODES = [
#     {'host': '10.3.90.6', 'port': 7001},
#     {'host': '10.3.90.6', 'port': 7002},
#     {'host': '10.3.90.6', 'port': 7003},
#     {'host': '10.3.90.6', 'port': 7004},
#     {'host': '10.3.90.6', 'port': 7005},
#     {'host': '10.3.90.6', 'port': 7006},
#     {'host': '10.3.90.6', 'port': 7007}
# ]
# # 使用的哈希函数数，默认为6
# BLOOMFILTER_HASH_NUMBER = 6
# # Bloomfilter使用的Redis内存位，30表示2 ^ 30 = 128MB，默认为22 (1MB 可去重130W URL)
# BLOOMFILTER_BIT = 22
# # 不清空redis队列
# SCHEDULER_PERSIST = True
# # 调度队列
# SCHEDULER = "scrapy_redis_cluster.scheduler.Scheduler"
# # 去重
# DUPEFILTER_CLASS = "scrapy_redis_cluster.dupefilter.RFPDupeFilter"
# # queue
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis_cluster.queue.PriorityQueue'



# IP
DOWNLOAD_TIMEOUT = 10

RETRY_TIMES = 15

=========================================================================================================================
spiders:{
          __init__.py,
          utils.py,
          weibo_spider.py
        }











