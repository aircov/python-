缩略图：
http://wx1.sinaimg.cn/wap180/d19c292fly1g317vqecuuj229e29e1ky.jpg
原图：
http://wx1.sinaimg.cn/large/d19c292fly1g317vqecuuj229e29e1ky.jpg


代理：https://proxy.mimvp.com/price.php#open
小号：http://www.wbxiaohao.com/       √
     http://www.xiaohao.kim/
     http://shop.91kami.com/xiaohao

13415378284----xh666666
17841044149----xh666666
------------------------------------------------------------------

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


utils.py
#!/usr/bin/env python
# encoding: utf-8
import re
import datetime


def time_fix(time_string):
    now_time = datetime.datetime.now()
    if '分钟前' in time_string:
        minutes = re.search(r'^(\d+)分钟', time_string).group(1)
        created_at = now_time - datetime.timedelta(minutes=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if '小时前' in time_string:
        minutes = re.search(r'^(\d+)小时', time_string).group(1)
        created_at = now_time - datetime.timedelta(hours=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if '今天' in time_string:
        return time_string.replace('今天', now_time.strftime('%Y-%m-%d'))

    if '月' in time_string:
        time_string = time_string.replace('月', '-').replace('日', '')
        time_string = str(now_time.year) + '-' + time_string
        return time_string

    return time_string


keyword_re = re.compile('<span class="kt">|</span>|原图|<!-- 是否进行翻译 -->|')
emoji_re = re.compile('<img alt="|" src="//h5\.sinaimg(.*?)/>')
white_space_re = re.compile('<br />')
div_re = re.compile('</div>|<div>')
image_re = re.compile('<img(.*?)/>')
url_re = re.compile('<a href=(.*?)>|</a>')


def extract_weibo_content(weibo_html):
    s = weibo_html
    if '转发理由' in s:
        s = s.split('转发理由:', maxsplit=1)[1]
    if 'class="ctt">' in s:
        s = s.split('class="ctt">', maxsplit=1)[1]
    s = s.split('赞[', maxsplit=1)[0]
    s = keyword_re.sub('', s)
    s = emoji_re.sub('', s)
    s = url_re.sub('', s)
    s = div_re.sub('', s)
    s = image_re.sub('', s)
    if '<span class="ct">' in s:
        s = s.split('<span class="ct">')[0]
    s = white_space_re.sub(' ', s)
    s = s.replace('\xa0', '')
    s = s.strip(':')
    s = s.strip()
    return s


def extract_comment_content(comment_html):
    s = comment_html
    if 'class="ctt">' in s:
        s = s.split('class="ctt">', maxsplit=1)[1]
    s = s.split('举报', maxsplit=1)[0]
    s = emoji_re.sub('', s)
    s = keyword_re.sub('', s)
    s = url_re.sub('', s)
    s = div_re.sub('', s)
    s = image_re.sub('', s)
    s = white_space_re.sub(' ', s)
    s = s.replace('\xa0', '')
    s = s.strip(':')
    s = s.strip()
    return s


weibo_spider.py
#!/usr/bin/env python
# encoding: utf-8
import re
from datetime import datetime

import requests
from lxml import etree
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider
from sina.items import BlogsItem, InformationItem, RelationshipsItem, CommentItem
from sina.spiders.utils import time_fix, extract_weibo_content, extract_comment_content
import time


class WeiboSpider(RedisSpider):
    name = "weibo_spider"
    base_url = "https://weibo.cn"
    redis_key = "weibo_spider:start_urls"

    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        "DOWNLOAD_DELAY": 0.5,
    }

    # 默认初始解析函数
    def parse(self, response):
        """ 抓取个人信息 """
        information_item = InformationItem()
        information_item['crawl_time_unix'] = int(time.time())
        information_item['crawl_time_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        selector = Selector(response)
        information_item['_id'] = re.findall('(\d+)/info', response.url)[0]
        text1 = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
        nick_name = re.findall('昵称;?[：:]?(.*?);', text1)
        gender = re.findall('性别;?[：:]?(.*?);', text1)
        place = re.findall('地区;?[：:]?(.*?);', text1)
        briefIntroduction = re.findall('简介;?[：:]?(.*?);', text1)
        birthday = re.findall('生日;?[：:]?(.*?);', text1)
        sex_orientation = re.findall('性取向;?[：:]?(.*?);', text1)
        sentiment = re.findall('感情状况;?[：:]?(.*?);', text1)
        vip_level = re.findall('会员等级;?[：:]?(.*?);', text1)
        authentication = re.findall('认证;?[：:]?(.*?);', text1)
        labels = re.findall('标签;?[：:]?(.*?)更多>>', text1)
        if nick_name and nick_name[0]:
            information_item["nick_name"] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            information_item["gender"] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            information_item["province"] = place[0]
            if len(place) > 1:
                information_item["city"] = place[1]
        if briefIntroduction and briefIntroduction[0]:
            information_item["brief_introduction"] = briefIntroduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:
            information_item['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                information_item["sex_orientation"] = "同性恋"
            else:
                information_item["sex_orientation"] = "异性恋"
        if sentiment and sentiment[0]:
            information_item["sentiment"] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            information_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            information_item["authentication"] = authentication[0].replace(u"\xa0", "")
        if labels and labels[0]:
            information_item["labels"] = labels[0].replace(u"\xa0", ",").replace(';', '').strip(',')
        request_meta = response.meta
        request_meta['item'] = information_item
        yield Request(self.base_url + '/u/{}'.format(information_item['_id']),
                      callback=self.parse_further_information,
                      meta=request_meta, dont_filter=True, priority=1)

    def parse_further_information(self, response):
        text = response.text
        information_item = response.meta['item']
        microblogs_num = re.findall('微博\[(\d+)\]', text)
        if microblogs_num:
            information_item['microblogs_num'] = int(microblogs_num[0])
        follows_num = re.findall('关注\[(\d+)\]', text)
        if follows_num:
            information_item['follows_num'] = int(follows_num[0])
        fans_num = re.findall('粉丝\[(\d+)\]', text)
        if fans_num:
            information_item['fans_num'] = int(fans_num[0])
        yield information_item

        # 获取该用户微博--原创
        # yield Request(url=self.base_url + '/{}/profile?filter=1&page=1'.format(information_item['_id']),
        #               callback=self.parse_blog,
        #               priority=1)

        # 获取该用户微博--所有
        yield Request(url=self.base_url + '/{}?page=1'.format(information_item['_id']),
                      callback=self.parse_blog,
                      priority=1)

        # 获取关注列表
        yield Request(url=self.base_url + '/{}/follow?page=1'.format(information_item['_id']),
                      callback=self.parse_follow,
                      dont_filter=True)
        # 获取粉丝列表
        yield Request(url=self.base_url + '/{}/fans?page=1'.format(information_item['_id']),
                      callback=self.parse_fans,
                      dont_filter=True)

    def parse_blog(self, response):
        print(response.request.meta['account']['_id'])
        header_str = response.request.meta['account']['cookie']
        # header_dict = {i.split('=')[0]: i.split('=')[1] for i in header_str.split('; ')}
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'cookie': header_str
        }
        # if response.url.endswith('page=1'):
        if response.url.endswith('1'):
            # 如果是第1页，一次性获取后面的所有页
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_blog, dont_filter=True, meta=response.meta)

                    # break

        """
        解析本页的数据
        """
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                blog_item = BlogsItem()
                blog_item['crawl_time_unix'] = int(time.time())
                blog_item['crawl_time_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href')[0]
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)
                blog_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_tweet_id.group(2),
                                                                          user_tweet_id.group(1))
                blog_item['user_id'] = user_tweet_id.group(2)
                blog_item['_id'] = '{}_{}'.format(user_tweet_id.group(2), user_tweet_id.group(1))
                create_time_info_node = tweet_node.xpath('.//span[@class="ct"]')[-1]
                create_time_info = create_time_info_node.xpath('string(.)')
                if "来自" in create_time_info:
                    blog_item['created_at'] = time_fix(create_time_info.split('来自')[0].strip())
                    blog_item['tool'] = create_time_info.split('来自')[1].strip()
                else:
                    blog_item['created_at'] = time_fix(create_time_info.strip())

                like_num = tweet_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
                blog_item['like_num'] = int(re.search('\d+', like_num).group())

                repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()')[-1]
                blog_item['repost_num'] = int(re.search('\d+', repost_num).group())

                comment_num = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()')[-1]
                blog_item['comment_num'] = int(re.search('\d+', comment_num).group())

                images = tweet_node.xpath('.//img[@alt="图片"]/@src')
                if len(images) > 0:
                    blog_item['image_url'] = re.sub(r'wap180', 'large', images[0])

                videos = tweet_node.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    blog_item['video_url'] = videos[0]

                map_node = tweet_node.xpath('.//a[contains(text(),"显示地图")]')
                if map_node:
                    blog_item['location'] = True

                repost_node = tweet_node.xpath('.//a[contains(text(),"原文评论[")]/@href')
                if repost_node:
                    blog_item['origin_weibo'] = repost_node[0]

                # 检测由没有阅读全文:
                all_content_link = tweet_node.xpath('.//a[text()="全文" and contains(@href,"ckAll=1")]')
                if all_content_link:
                    all_content_url = self.base_url + all_content_link[0].xpath('./@href')[0]
                    yield Request(all_content_url, callback=self.parse_all_content, meta={'item': blog_item},
                                  priority=1)

                else:
                    tweet_html = etree.tostring(tweet_node, encoding='unicode')
                    blog_item['content'] = extract_weibo_content(tweet_html)

                    # 解析发微博地点
                    if 'location' in blog_item:
                        # blog_item['location'] = tweet_node.xpath('.//span[@class="ctt"]/a[last()]/text()')[0]
                        iii = tweet_node.xpath('.//a[contains(text(),"显示地图")]/preceding-sibling::*[1]//text()')
                        location = ''.join(iii).strip().replace(' 秒拍视频 .', '').replace(' · ', '·')
                        if re.search(r'\s.*?的秒拍视频', location):
                            blog_item['location'] = location.split(' ')[-2]
                        else:
                            blog_item['location'] = location.split(' ')[-1]

                    # 发表文章
                    article = tweet_node.xpath(
                        './/span[contains(text(),"发布了头条文章") or contains(text(),"Just published the top article")]/text()')
                    if len(article) > 0:
                        a_text = re.search(r'《(.*?)》', article[0]).group(1)
                        u = tweet_node.xpath('.//a[contains(text(),"{}")]/@href'.format(a_text))
                        if len(u) > 0:
                            blog_item['article_url'] = u[0]
                            article_id = requests.get(u[0], headers=headers).text
                            ret = re.search(r'(https:\/\/weibo\.com\/ttarticle\/p\/show\?id=.*?)"', article_id).group(1)
                            # print(ret)
                            # 获取文章
                            article_text = requests.get(ret, headers=headers).text
                            html_str = etree.HTML(article_text)
                            a = html_str.xpath("//div[contains(@class,'WB_editor_iframe')]//text()")
                            article_content = re.sub(r'\\u200b|\\xa0', '', ''.join(a).strip())
                            blog_item['article_content'] = article_content.strip()

                    yield blog_item

                # 抓取该微博的评论信息
                if blog_item['comment_num'] > 0:
                    comment_url = self.base_url + '/comment/' + blog_item['weibo_url'].split('/')[-1] + '?page=1'
                    yield Request(url=comment_url, callback=self.parse_comment,dont_filter=True,
                                  meta={'weibo_url': blog_item['weibo_url']})

            except Exception as e:
                print(e, response.url)
                self.logger.error(e)

    def parse_all_content(self, response):
        # 有阅读全文的情况，获取全文
        tree_node = etree.HTML(response.body)
        blog_item = response.meta['item']
        content_node = tree_node.xpath('//*[@id="M_"]/div[1]')[0]
        tweet_html = etree.tostring(content_node, encoding='unicode')
        blog_item['content'] = extract_weibo_content(tweet_html)
        if 'location' in blog_item:
            # blog_item['location'] = content_node.xpath('.//span[@class="ctt"]/a[last()]/text()')[0]
            iii = content_node.xpath('.//a[contains(text(),"显示地图")]/preceding-sibling::*[1]//text()')
            location = ''.join(iii).strip().replace(' 秒拍视频 .', '').replace(' · ', '·')
            if re.search(r'\s.*?的秒拍视频', location):
                blog_item['location'] = location.split(' ')[-2]
            else:
                blog_item['location'] = location.split(' ')[-1]
        yield blog_item

    def parse_article(self, response):
        # 用户发表文章解析文章详情页
        tree_node = etree.HTML(response.body)
        blog_item = response.meta['item']
        a = tree_node.xpath("//div[contains(@class,'WB_editor_iframe')]//text()")
        ret = re.sub(r'\\u200b|\\xa0', '', ''.join(a).strip())
        blog_item['article_content'] = ret
        print(blog_item['article_content'])
        yield blog_item

    def parse_follow(self, response):
        """
        抓取关注列表
        """
        # 如果是第1页，一次性获取后面的所有页
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_follow, dont_filter=True, meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/follow', response.url)[0]
        for uid in uids:
            relationships_item = RelationshipsItem()
            relationships_item['crawl_time_unix'] = int(time.time())
            relationships_item['crawl_time_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            relationships_item["fan_id"] = ID
            relationships_item["followed_id"] = uid
            relationships_item["_id"] = ID + '-' + uid
            yield relationships_item

    def parse_fans(self, response):
        """
        抓取粉丝列表
        """
        # 如果是第1页，一次性获取后面的所有页
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_fans, dont_filter=True, meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="移除"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/fans', response.url)[0]
        for uid in uids:
            relationships_item = RelationshipsItem()
            relationships_item['crawl_time_unix'] = int(time.time())
            relationships_item['crawl_time_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            relationships_item["fan_id"] = uid
            relationships_item["followed_id"] = ID
            relationships_item["_id"] = uid + '-' + ID
            yield relationships_item

    def parse_comment(self, response):
        # 如果是第1页，一次性获取后面的所有页
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_comment, dont_filter=True, meta=response.meta)
        tree_node = etree.HTML(response.body)
        comment_nodes = tree_node.xpath('//div[@class="c" and contains(@id,"C_")]')
        for comment_node in comment_nodes:
            comment_user_url = comment_node.xpath('.//a[contains(@href,"/u/")]/@href')
            if not comment_user_url:
                continue
            comment_item = CommentItem()
            comment_item['crawl_time_unix'] = int(time.time())
            comment_item['crawl_time_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            comment_item['weibo_url'] = response.meta['weibo_url']
            comment_item['comment_user_id'] = re.search(r'/u/(\d+)', comment_user_url[0]).group(1)
            comment_item['content'] = extract_comment_content(etree.tostring(comment_node, encoding='unicode'))
            comment_item['_id'] = comment_node.xpath('./@id')[0]
            created_at_info = comment_node.xpath('.//span[@class="ct"]/text()')[0]
            like_num = comment_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
            comment_item['like_num'] = int(re.search('\d+', like_num).group())
            comment_item['created_at'] = time_fix(created_at_info.split('\xa0')[0])
            yield comment_item
===============================================================================================
account_build:{
				cookies,
				images,
				__init__.py,
				account.txt,
				chaojiying.py,
				WeiBoLogin_pc_m_cn.py,
				}

account.txt
a----P
17739208867----qwer123456
13415378284----xh666666
17841044149----xh666666
wijm58782@qt164.cc----HFPylv829W5
45368456162@qt164.cc----IBVfce807b0
1557516571000@qt164.cc----XZAqbd1040M
39o6273558355@qt164.cc----KACula317GC
1557600233wjfm8@qt164.cc----UWJfkz148s7
1557590916zdx@qt164.cc----YVNwrp589N0


chaojiying.py
# coding:utf-8

import requests
from hashlib import md5


class Chaojiying_Client(object):
    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


def use_cjy(filename):
    username = "nicholas"
    password = "chaojiying123456"
    app_id = "898017"  # 用户中心>>软件ID
    cjy = Chaojiying_Client(username, password, app_id)
    img = open(filename, 'rb').read()  # 本地图片文件路径
    return cjy.PostPic(img, 1005)  # 9004->验证码类型


if __name__ == '__main__':
    captcha_result = use_cjy("./images/weibo1558921523.png")
    print(captcha_result)
    print(captcha_result['pic_str'])


WeiBoLogin_pc_m_cn.py
# 微博模拟登录
# 作者: David
# Github: https://github.com/HEUDavid/WeiboSpider

import base64
import binascii
import json
import os
import random
import re
import time
from urllib.parse import quote_plus
from PIL import Image
import pymongo
import requests
import rsa
from pymongo.errors import DuplicateKeyError

from sina.account_build.chaojiying import use_cjy
from sina.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME


class WeiboLogin:

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.Session = requests.Session()
        self.Session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

        # login.php?client=ssologin.js(v1.4.19) 找到 POST 的表单数据
        self.Form_Data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '0',
            'useticket': '1',
            'pagerefer': 'https://passport.weibo.com',
            'vsnf': '1',
            'service': 'miniblog',
            'pwencode': 'rsa2',
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '243',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'TEXT'  # 这里是 TEXT, META 不可以
        }

    def get_su(self):
        '''
        对应 prelogin.php
        对 账号 先 javascript 中 encodeURIComponent
        对应 Python3 中的是 urllib.parse.quote_plus
        然后在 base64 加密后 decode
        '''
        username_quote = quote_plus(self.username)
        username_base64 = base64.b64encode(username_quote.encode('utf-8'))
        su = username_base64.decode('utf-8')
        # print('处理后的账户:', su)

        self.Form_Data['su'] = su

        return su

    def get_server_data(self, su):
        '''
        预登陆获得 servertime, nonce, pubkey, rsakv
        '''
        url_str1 = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su='
        url_str2 = '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_='
        pre_url = url_str1 + su + url_str2 + str(int(time.time() * 1000))
        pre_data_res = self.Session.get(pre_url)
        server_data = eval(pre_data_res.content.decode(
            'utf-8').replace('sinaSSOController.preloginCallBack', ''))

        self.Form_Data['servertime'] = server_data['servertime']
        self.Form_Data['nonce'] = server_data['nonce']
        self.Form_Data['rsakv'] = server_data['rsakv']

        return server_data

    def get_password(self, servertime, nonce, pubkey):
        '''
        对密码进行 rsa 加密
        '''
        rsaPublickey = int(pubkey, 16)  # 16进制 string 转化为 int
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + nonce + '\n' + self.password
        message = message.encode('utf-8')
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制
        # print('处理后的密码:', passwd)

        self.Form_Data['sp'] = passwd

        return passwd

    def get_png(self, pcid):
        '''
        获取验证码
        '''
        png_url = 'https://login.sina.com.cn/cgi/pin.php?r=' + \
            str(int(random.random() * 100000000)) + '&s=0&p=' + pcid
        png_page = self.Session.get(png_url)
        image_name = './images/weibo'+ str(int(time.time())) +'.png'
        with open(image_name, 'wb') as f:
            f.write(png_page.content)
            print('验证码下载成功, 请到目录下查看')

        # 手动输入验证码
        # fp = open(image_name, 'r')
        # im = Image.open(image_name)
        # im.show()
        # verification_code = input('请输入验证码: ')
        # fp.close()

        # 超级鹰
        captcha_result = use_cjy(image_name)
        verification_code = captcha_result['pic_str']

        return verification_code

    def get_cookie(self):
        su = self.get_su()
        '''
        {'retcode': '4049', 'reason': '为了您的帐号安全，请输入验证码'}
        {'retcode': '2093', 'reason': '抱歉！登录失败，请稍候再试'}
        {'retcode': '0', 'ticket': 'ST-NTcwNjQxMzA3Mg==-1557049968-yf-6EE75B29C64734704473DCDD74DBC755-1', 'uid': '5706413072', 'nick': '大大大卫哥'}
        '''
        try:
            # 不输入验证码
            server_data = self.get_server_data(su)
            self.get_password(
                server_data['servertime'],
                server_data['nonce'],
                server_data['pubkey'])
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_' + str(
                time.time() * 1000)

            login_page = self.Session.post(login_url, data=self.Form_Data)
            ticket_js = login_page.json()
            print('不输入验证码登录成功, 用户昵称:', ticket_js['nick'])

        except Exception as e:
            # 输入验证码
            server_data = self.get_server_data(su)  # 刷新
            self.get_password(
                server_data['servertime'],
                server_data['nonce'],
                server_data['pubkey'])
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_' + str(
                time.time() * 1000)

            self.Form_Data['door'] = self.get_png(server_data['pcid'])

            login_page = self.Session.post(login_url, data=self.Form_Data)
            ticket_js = login_page.json()

            if ticket_js['retcode'] != '0':
                print(ticket_js['reason'])
                return None
            else:
                print('输入验证码登录成功, 用户昵称:', ticket_js['nick'])

        finally:
            print('ticket_js:', ticket_js)

        ticket = ticket_js['ticket']
        ssosavestate = ticket.split('-')[2]
        # 处理跳转
        jump_ticket_params = {
            'callback': 'sinaSSOController.callbackLoginStatus',
            'ticket': ticket,
            'ssosavestate': ssosavestate,
            'client': 'ssologin.js(v1.4.19)',
            '_': str(time.time() * 1000),
        }
        jump_url = 'https://passport.weibo.com/wbsso/login'

        jump_login = self.Session.get(jump_url, params=jump_ticket_params)
        jump_login_data = json.loads(
            re.search(r'{.*}', jump_login.text).group(0))
        print('登录状态:', jump_login_data)
        if not jump_login_data['result']:
            # 登录失败 退出
            return None

        # PC 版 个人主页
        weibo_com_home = 'https://weibo.com/u/' + \
            jump_login_data['userinfo']['uniqueid']
        weibo_com_home_page = self.Session.get(weibo_com_home)
        # print('weibo_com_home_page.cookies', weibo_com_home_page.cookies)
        # print(weibo_com_home_page.text[:1500:])
        weibo_com_home_title_pat = r'<title>(.*)</title>'
        weibo_com_home_title = re.findall(
            weibo_com_home_title_pat,
            weibo_com_home_page.text)[0]
        print('PC 版个人主页:', weibo_com_home_title)  # PC 版登录成功

        # PC 版 首页
        weibo_com = 'https://weibo.com'
        weibo_com_page = self.Session.get(weibo_com)
        # print('weibo_com_page.cookies', weibo_com_page.cookies)
        # print(weibo_com_page.text[:1500:])

        # PC 版 搜索页
        s_weibo_com = 'https://s.weibo.com'
        s_weibo_com_page = self.Session.get(s_weibo_com)

        # 触屏版 m.weibo.com
        mParams = {
            'url': 'https://m.weibo.cn/',
            '_rand': str(time.time()),
            'gateway': '1',
            'service': 'sinawap',
            'entry': 'sinawap',
            'useticket': '1',
            'returntype': 'META',
            'sudaref': '',
            '_client_version': '0.6.26',
        }
        murl = 'https://login.sina.com.cn/sso/login.php'
        mhtml = self.Session.get(murl, params=mParams)

        mpa = r'replace\((.*?)\);'
        mres = re.findall(mpa, mhtml.text)[0]  # 从新浪通行证中找到跳转链接

        mlogin = self.Session.get(eval(mres))

        m_weibo_com = 'https://m.weibo.cn'
        m_weibo_com_page = self.Session.get(m_weibo_com)

        login_start = m_weibo_com_page.text.index('login:')
        uid_start = m_weibo_com_page.text.index('uid:')

        print('触屏版登录状态')
        print(m_weibo_com_page.text[login_start:login_start + 13:])
        print(m_weibo_com_page.text[uid_start:uid_start + 17:])

        # 旧版
        weibo_cn = 'https://weibo.cn'
        weibo_cn_page = self.Session.get(weibo_cn)
        # print(weibo_cn_page.text)
        print(dict(weibo_cn_page.request.headers))

        # return self.Session.cookies  # 返回PC版登陆cookie
        return dict(weibo_cn_page.request.headers)['Cookie']  # 返回旧版cookie

def save(name, data):
    path = './cookies/' + name + '.json'
    with open(path, 'w+') as f:
        json.dump(data, f)
        print(path, '保存成功')



def main():
    file_path = os.getcwd() + './account.txt'
    with open(file_path, 'r') as f:
        lines = f.readlines()
    mongo_client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
    collection = mongo_client[DB_NAME]["account"]
    for line in lines:
        try:
            line = line.strip()
            username = line.split('----')[0]
            password = line.split('----')[1]
            print('=' * 10 + username + '=' * 10)
            login = WeiboLogin(username, password)
            cookies = login.get_cookie()

            # 保存到当前文件夹
            # if cookies:
            #     data = cookies.get_dict()
            #     cookie_name = 'cookie_' + username  # 保存 cookie 的文件名称
            #     save(cookie_name, data)

            # 保存到mongodb
            try:
                collection.insert_one(
                    {"_id": username, "password": "********", "cookie": cookies, "status": "success"})
            except DuplicateKeyError as e:
                collection.find_one_and_update({'_id': username}, {'$set': {'cookie': cookies, "status": "success"}})

        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    main()




