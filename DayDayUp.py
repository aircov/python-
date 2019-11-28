
# 1.retrying模块使用

~~~python
import requests
from retrying import retry

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
           }


@retry(stop_max_attempt_number=3)
def _parse_url(url):
    print("*"*100)
    response = requests.get(url, headers=headers, timeout=3)
    return response.content.decode("utf-8")


def parse_url(url):
    try:
        html_str = _parse_url(url)
    except:
        html_str = None
    return html_str


if __name__ == '__main__':
    url = "http://www.baidu.com"
    content = parse_url(url)
    with open("content.html", "wb") as f:
        f.write(content.encode("utf-8"))
~~~

# 2.cookie字典推导式

~~~python
Cookie= "BAIDUID=2372C5B0CA576383B4BB27FAD889D1F1:FG=1; " \
        "BIDUPSID=2372C5B0CA576383B4BB27FAD889D1F1; " \
        "PSTM=1540220135; BD_UPN=12314353; " \
        "BDUSS=BFMGNqYXFNMkJnVHRIblctcGhxbllKMmRtbkhDdk1IUVRy" \
        "bnFvaURrTFZtUUJjQVFBQUFBJCQAAAAAAAAAAAEAAABh-XRYYWlyY2" \
        "92AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" \
        "AAAAAAAAAAAAAAAAAAAAANUM2VvVDNlbbV; locale=zh; BD_HOME=1; " \
        "H_PS_PSSID=27541_1464_21104_22157"

cookie_dict = {i.split("=")[0]:i.split("=")[1] for i in Cookie.split("; ")}
print(cookie_dict)

===========================================================================
login——douban
# 获取cookie
cookies = {i["name"]:i["value"] for i in driver.get_cookies()}
print(cookies)
~~~

# 3. 保存图片到本地  urlretrieve

~~~python
from urllib import request
def urlretrieve(url, filename=None, reporthook=None, data=None):
	request.urlretrieve(img_url, "images/" + img_name)  # 通过图片地址，保存图片到本地
~~~

# 4. 代理proxy的使用

* 准备一堆ip，组成ip池，随机选择一个ip使用
* 如何随机选择代理ip
  * 按照使用的次数进行排序
  * 选择使用次数少的ip，随机选择
* 检查ip可用性
  * 使用requests超时参数
  * 在线代理ip质量检测的网站

~~~python
import requests

proxies = {
    "http": "http://219.141.153.12:8080"
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
           }

response = requests.get("https://www.taobao.com", proxies=proxies, headers=headers)
print(response.status_code)
~~~

# 5.requests.utils.unqoute()

url解码


# 6. zip函数，map函数


~~~python
a = [1, 2]
b = [3, 4]
c = zip(a,b)
c = [
    (1, 3),
    (2, 4)
]

poems_list = []
        for value in zip(title_list, dynasty_list, author_list, contents):
            title, dynasty, author, content = value
            items = {
                "title": title,
                "dynasty": dynasty,
                "author": author,
                "content": content
            }
            poems_list.append(items)
        return poems_list
~~~

~~~python
# 1.有一个字典对象，d = {'a':1,'b':2}，请用尽量简洁的代码将d转换成{1: 'a', 2: 'b'}
dict(zip(d.values(), d.keys()))
~~~

~~~python
#2、匿名函数，一般用来给 filter,sorted,map,reduce 这样的函数式编程服务;
filter(lambda x: x % 3 == 0, [1, 2, 3])  结果是 [3]
sorted([1, 2, 3, 4, 5, 6, 7, 8, 9], key=lambda x: abs(5-x)) 结果是[5, 4, 6, 3, 7, 2, 8, 1, 9]
map(lambda x: x+1, [1, 2, 3])  结果是[2,3,4]
reduce(lambda a, b: '{}, {}'.format(a, b), [1, 2, 3, 4, 5, 6, 7, 8, 9]) 结果是'1, 2, 3, 4, 5, 6, 7, 8, 9'
~~~

~~~python
info_list = dl.xpath(".//p[@class='tel_shop']/text()").getall()
info_list = list(map(lambda x: re.sub(r"\s", "", x), info_list))
# print(info_list)  # ['4室2厅', '133.84㎡', '高层（共16层）', '南北向', '2003年建', '']
~~~

# 7. splitext 按照文件扩展名切割

~~~python
import os,re
img_url = img.get("data-original")
alt = img.get("alt")
alt = re.sub(r"[\?？。\.,，！!\*]", "", alt)
# 获取图片后缀('https://ws4.sinaimg.cn/bmiddle/9150e4e5gy1fxd0c5j6flg204m04o4bk', '.gif')
suffix = os.path.splitext(img_url)[1]    # 得到后缀.gif
img_name = alt + suffix
~~~

# 8.多线程、协程池爬虫

多线程

~~~python
import json
import random
import threading
import requests
from queue import Queue   # 线程队列
# from multiprocessing import JoinableQueue as Queue  # 进程队列 后续操作跟线程一样
from fake_useragent import UserAgent
from lxml import etree
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
    filename='./info.log',
    filemode='a'
)


class DianyingtiantangSpider(object):
    def __init__(self):
        self.start_url = "https://www.dy2018.com/html/gndy/dyzz/index.html"
        self.url_temp = "https://www.dy2018.com/html/gndy/dyzz/index_{}.html"
        self.ua = UserAgent().random
        self.headers = {
            # "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            # "user-agent": random.choice(self.ua)
        }
        self.url_queue = Queue()
        self.html_queue = Queue()
        self.detail_page_url_queue = Queue()
        self.movie_queue = Queue()

    def get_url_list(self):  # 构造url列表
        self.url_queue.put(self.start_url)
        for i in range(2, 300):
            self.url_queue.put(self.url_temp.format(i))

    def parse_url(self):  # 发送请求，获取响应
        while True:
            url = self.url_queue.get()
            self.headers['user-agent'] = self.ua
            response = requests.get(url, headers=self.headers)
            # 电影天堂网站编码格式为charset=gb2312，查看网页源代码
            self.html_queue.put(response.content.decode("gbk"))
            self.url_queue.task_done()

    def get_content_list(self):  # 提取电影详情页的url
        while True:
            html_str = self.html_queue.get()
            html = etree.HTML(html_str)
            detail_url_list = html.xpath("//table[@class='tbspan']//a/@href")
            content_list = []
            for detail_url_temp in detail_url_list:
                detail_url = "https://www.dy2018.com" + detail_url_temp
                content_list.append(detail_url)
            self.detail_page_url_queue.put(content_list)
            self.html_queue.task_done()

    def parse_detail_url(self):  # 请求详情页数据

            while True:
                detail_page_url_list = self.detail_page_url_queue.get()
                pass
                self.movie_queue.put(movie_list)
                self.detail_page_url_queue.task_done()


    def save_movies(self):
        while True:
            movies = self.movie_queue.get()
            with open("./电影天堂.json", "a", encoding="utf-8") as f:
                for movie in movies:
                    f.write(json.dumps(movie, ensure_ascii=False) + "\n")
            self.movie_queue.task_done()

    def run(self):  # 实现主要逻辑
        thread_list = []
        # 1.构造url列表
        t1 = threading.Thread(target=self.get_url_list)
        thread_list.append(t1)

        # 2.遍历列表，发送请求，获取响应
        for i in range(5):
            t2 = threading.Thread(target=self.parse_url)
            thread_list.append(t2)

        # 3.提取数据
        t3 = threading.Thread(target=self.get_content_list)
        thread_list.append(t3)

        # 4.请求所有详情页数据
        for i in range(5):
            t4 = threading.Thread(target=self.parse_detail_url)
            thread_list.append(t4)

        # 5.保存数据
        for i in range(2):
            t5 = threading.Thread(target=self.save_movies)
            thread_list.append(t5)

        # 把子线程设置为守护线程，主线程结束，子线程结束
        # 开启线程
        for t in thread_list:
            t.setDaemon(True)
            t.start()

        # 让主线程等待阻塞，等待队列的任务完成之后再完成
        # 队列阻塞，队列的计数器为0的时候，解阻塞
        for q in [self.url_queue, self.html_queue, self.detail_page_url_queue, self.movie_queue]:
            q.join()

        print("主线程结束")  # 多线程实现：高内聚，低耦合


if __name__ == '__main__':
    dianyingtiantangspider = DianyingtiantangSpider()
    dianyingtiantangspider.run()
~~~

协程池

~~~python
import time
from gevent import monkey
from gevent.pool import Pool
from lxml import etree

monkey.patch_all()

import requests
from queue import Queue


class QiushiSpider(object):
    def __init__(self):
        self.temp_url = 'https://www.qiushibaike.com/hot/page/{}'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
        }
        self.url_queue = Queue()
        self.pool = Pool()
        self.response_mum = 0
        self.request_mum = 0
        self.count = 0

    def run(self):
        start_time = time.time()
        self.async_start()
        end_time = time.time()

        print("耗时:{}".format((end_time - start_time)))
        print("总数:{}".format(self.count))

    def async_start(self):
        """异步请求"""
        self.get_url()

        # 执行异步请求
        for i in range(5):
            self.pool.apply_async(self.start, callback=self._callback)

        while True:
            time.sleep(0.001)
            if self.response_mum >= self.request_mum:
                break

    def get_url(self):
        """获取url,保存到队列"""
        for i in range(1, 14):
            url = self.temp_url.format(i)
            self.url_queue.put(url)
            self.request_mum += 1

    def start(self):
        # 1.获取url
        url = self.url_queue.get()
        print(url)
        data = self.send_request(url)
        self.analysis_data(data)
        #     保存

    def _callback(self, item):
        """回调函数,必须传item形参"""
        self.pool.apply_async(self.start, callback=self._callback)

    def send_request(self, url):
        """发送请求"""
        response = requests.get(url, headers=self.headers)
        print(response.url)
        data = response.content
        self.response_mum += 1
        return data

    def analysis_data(self, data):
        """解析数据"""
        html_data = etree.HTML(data)

        # 1.获取25个帖子
        div_list = html_data.xpath('//div[@id="content-left"]/div')

        # 2. 遍历每一个帖子 取出 昵称
        for div in div_list:
            nick_name = div.xpath('.//h2/text()')[0]
            print(nick_name.strip())
            self.count += 1


if __name__ == '__main__':
    qiushi = QiushiSpider()
    qiushi.run()
~~~



~~~
 # 遍历列表得到 索引，内容
 for index, info in enumerate(infos) 
~~~

13_face_spider_v2.py

# 9. selenium

~~~python
from selenium import webdriver
import time
import requests
from dama import identify

# 实例化driver
driver = webdriver.Chrome()
driver.get("https://www.douban.com/")

driver.find_element_by_id("form_email").send_keys("aircov@163.com")
driver.find_element_by_id("form_password").send_keys("douban123456")

# 识别验证码
try:
    captcha_image_url = driver.find_element_by_id("captcha_image").get_attribute("src")  # 验证码的地址
except:
    # 登录
    driver.find_element_by_class_name("bn-submit").click()
else:
    captcha_content = requests.get(captcha_image_url).content   # 请求验证码地址 获取响应
    captcha_code = identify(captcha_content)  # 调用打码平台
    print("验证码的识别结果为：%s" % captcha_code)
    # 输入验证码
    driver.find_element_by_id("captcha_field").send_keys(captcha_code)
    # 登录
    driver.find_element_by_class_name("bn-submit").click()

# 获取cookie
cookies = {i["name"]:i["value"] for i in driver.get_cookies()}
print(cookies)

time.sleep(5)

# driver.quit()
~~~



selenium 爬取拉勾网

```
新窗口打开页面：self.driver.execute_script("window.open('%s')" % link)
切换到新标签页中：self.driver.switch_to.window(self.driver.window_handles[1])
关闭当前这个详情页：self.driver.close()
继续切换回职位列表页：self.driver.switch_to.window(self.driver.window_handles[0])
```

js代码  滚动到最后

~~~python
code_js = "window.scrollTo(0,document.body.scrollHeight)"
self.driver.execute_script(code_js)
~~~



# 10. scrapy 基本使用

scrapy genspider  -t  crawl  spider_name  allow_domain

~~~python
# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re


class CfSpider(CrawlSpider):
    name = 'cf'
    allowed_domains = ['circ.gov.cn']
    start_urls = ['http://bxjg.circ.gov.cn/web/site0/tab5240/module14430/page1.htm']

    # 定义提取url地址规则
    rules = (
        # LinkExtractor 链接提取器，提取url地址
        # callback，提取出来的url地址的response会交给callback处理
        # follow 当前url地址的响应是否重新经过rules提取url地址，
        Rule(LinkExtractor(allow=r'/web/site0/tab5240/info\d+\.htm'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'/web/site0/tab5240/module14430/page\d+\.htm'), follow=True),
    )

    # parse函数有特殊功能，请求链接提取器的url，不能定义
    def parse_item(self, response):
        item = {}
        item["title"] = re.findall(r"<!--TitleStart-->(.*?)<!--TitleEnd-->", response.body.decode("utf-8"))[0]
        item["publish_date"] = re.findall(r"发布时间：(20\d{2}-\d{2}-\d{2})", response.body.decode("utf-8"))[0]
        print(item)
    #     yield scrapy.Request(
    #         url,
    #         callback=self.parse_detail,
    #         meta={"item":item}
    #     )
    #
    # def parse_detail(self,response):
    #     item = response.meta("item")
    #     item["price"] = "///"
    #     yield item

~~~

spider.py  

~~~python
# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy import log
from fangtianxia.items import NewHouseItem, ESFHouseItem, RentHouseItem


class SfwSpider(RedisSpider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = 'fangtianxia'   # lpush fangtianxia https://www.fang.com/SoufunFamily.htm

    def parse(self, response):
        tr_list = response.xpath("//div[@class='outCont']//tr")

        province = None
        for tr in tr_list:
            # 没有class属性的td
            td_list = tr.xpath("./td[not(@class)]")
            province_td = td_list[0]
            province_text = province_td.xpath(".//text()").get()
            province_text = re.sub(r"\s", "", province_text)

            # 如果有province_text，保存起来
            if province_text:
                province = province_text

            # 不爬取海外信息
            if province == "其它":
                continue

            city_td = td_list[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                # 城市名
                city = city_link.xpath(".//text()").get()
                # 城市名对应的url
                city_url = city_link.xpath(".//@href").get()
                # print("省份", province)
                # print("城市", city)
                # print("城市链接", city_url)

                # 北京新房、二手房url、租房例外
                if "bj" in city_url:
                    newhouse_url = "https://newhouse.fang.com/house/s/"
                    esf_url = "https://esf.fang.com/"
                    rent_url = "https://zu.fang.com/"
                else:
                    # 构建新房的url链接
                    newhouse_url = city_url.split(".")[0] + ".newhouse.fang.com/house/s/"
                    # 构建二手房的url链接
                    esf_url = city_url.split(".")[0] + ".esf.fang.com/"
                    # 构建租房url链接
                    rent_url = city_url.split(".")[0] + ".zu.fang.com/"

                # print("新房", newhouse_url)
                # print("二手房", esf_url)

                yield scrapy.Request(
                    url=newhouse_url,
                    callback=self.parse_newhouse,
                    meta={"item": (province, city)}
                )

                yield scrapy.Request(
                    url=esf_url,
                    callback=self.parse_esf,
                    meta={"item": (province, city)}
                )

                yield scrapy.Request(
                    url=rent_url,
                     callback=self.parse_rent,
                    meta={'item':(province, city)}
                )

    # 解析新房列表页 
    def parse_newhouse(self, response):
        print(response.request.headers['User-Agent'])
        province, city = response.meta.get("item")
        li_list = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        try:
            for li in li_list:
                name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
                if name is not None:  # 页面有广告
                    name = name.strip()

                    house_tpye_list = li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()
                    rooms = list(map(lambda x: re.sub(r"\s|/|－", "", x), house_tpye_list))
                    rooms = "".join(rooms)

                    area = "".join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall())  # 列表转化字符串
                    area = re.sub(r"\s|/|－", "", area)

                    district_text = "".join(li.xpath(".//div[@class='address']/a//text()").getall())
                    district = re.search(r".*\[(.+)\].*", district_text)
                    if district is not None:
                        district = district.group(1)

                    address = li.xpath(".//div[@class='address']/a/@title").get()

                    sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()

                    price = "".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
                    price = re.sub(r"\s|广告", "", price)

                    origin_url = "http:" + li.xpath(".//div[@class='nlcd_name']/a/@href").get()

                    tel = "".join(li.xpath(".//div[@class='tel']//text()").getall()).strip()

                    item = NewHouseItem(province=province, city=city, name=name, rooms=rooms,
                                        area=area, district=district, address=address, sale=sale,
                                        price=price, origin_url=origin_url, tel=tel)
                    yield item
        except Exception as e:
            log.ERROR(e)

        # 下一页
        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
        yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_newhouse,
                             meta={"item": (province, city)})

    # 解析二手房列表页
    def parse_esf(self, response):
        print(response.request.headers['User-Agent'])
        province, city = response.meta.get("item")
        dl_list = response.xpath("//div[contains(@class,'shop_list')]/dl")
        try:
            for dl in dl_list:
                item = ESFHouseItem(province=province, city=city)
                name = dl.xpath(".//p[@class='add_shop']/a/@title").get()
                item['name'] = name
                if name is not None:  # 页面有广告
                    info_list = dl.xpath(".//p[@class='tel_shop']/text()").getall()
                    info_list = list(map(lambda x: re.sub(r"\s", "", x), info_list))
                    # print(info_list)  # ['4室2厅', '133.84㎡', '高层（共16层）', '南北向', '2003年建', '']
                    for info in info_list:
                        if "厅" in info:
                            item['rooms'] = info
                        elif "㎡" in info:
                            item['area'] = info
                        elif "层" in info:
                            item["floor"] = info
                        elif "向" in info:
                            item['toward'] = info
                        elif "建" in info:
                            item["year"] = info
                    item['address'] = ''.join(dl.xpath(".//p[@class='add_shop']/span/text()").getall())

                    price = dl.xpath(".//dd[@class='price_right']/span//text()").getall()
                    # 总价
                    item['price'] = price[0] + price[1]
                    # 单价
                    item['unit'] = price[-1]
                    origin_url = dl.xpath(".//h4[@class='clearfix']/a/@href").get()
                    # /chushou/3_244089396.htm
                    item['origin_url'] = response.urljoin(origin_url)

                    # 获取详情页电话
                    yield scrapy.Request(url=item['origin_url'], callback=self.parse_esf_detail, meta={'item': item})
        except Exception as e:
            log.ERROR(e)

        # 下一页
        next_url = response.xpath("//a[text()='下一页']/@href").get()
        if next_url is not None:
            yield scrapy.Request(
                url=response.urljoin(next_url),
                callback=self.parse_esf,
                meta={"item": (province, city)}
            )

    # 解析二手房详情页
    def parse_esf_detail(self, response):
        item = response.meta.get('item')
        item['tel'] = response.xpath("//span[@id='mobilecode']/text()").get()

        yield item

    # 解析租房列表
    def parse_rent(self, response):
        print(response.request.headers['User-Agent'])
        province, city = response.meta.get("item")
        rent_detail_url_list = response.xpath("//p[@class='title']/a/@href").getall()
        rent_detail_url_list = list(map(lambda x: response.urljoin(x), rent_detail_url_list))
        for rent_detail_url in rent_detail_url_list:
            yield scrapy.Request(
                url=rent_detail_url,
                callback=self.parse_rent_detail,
                meta={"item": (province, city)}
            )

        # 下一页
        next_url = response.xpath("//a[text()='下一页']/@href").get()
        if next_url is not None:
            yield scrapy.Request(url=response.urljoin(next_url),
                callback=self.parse_esf,
                meta={"item": (province, city)}
            )

    # 解析租房详情页
    def parse_rent_detail(self, response):
        province, city = response.meta.get("item")
        item = RentHouseItem(province=province, city=city)

        try:
            price = response.xpath("//div[contains(@class,'trl-item sty1')]//text()").getall()
            item['price'] = ''.join(list(map(lambda x:re.sub(r'\s', '', x), price)))

            rent_toward_list = response.xpath("//div[@class='trl-item1 w146']/div[@class='tt']/text()").getall()
            item['rent_method'] = rent_toward_list[0] if len(rent_toward_list)>0 else None
            item['toward'] = rent_toward_list[1] if len(rent_toward_list)>1 else None

            rooms_floor_list = response.xpath("//div[@class='trl-item1 w182']/div[@class='tt']/text()").getall()
            item['rooms'] = rooms_floor_list[0] if len(rooms_floor_list)>0 else None
            item['floor'] = rooms_floor_list[1] if len(rooms_floor_list)>1 else None

            area_decoration_list = response.xpath("//div[@class='trl-item1 w132']/div[@class='tt']/text()").getall()
            item['area'] = area_decoration_list[0] if len(area_decoration_list)>0 else None
            item['decoration'] = area_decoration_list[1] if len(area_decoration_list)>1 else None

            address_list = response.xpath("//div[contains(@class,'rcont')]//text()").getall()
            item['address'] = ''.join(list(map(lambda x:re.sub(r'\s', '', x), address_list)))

            item['origin_url'] = response.url

            # tel = response.xpath("//div[@class='tjcont-jjr-line2 clearfix']/text()").get()
            # if tel:
            #     item['tel'] = tel.strip()
            # else:
            #     item['tel'] = tel
            tel = response.xpath("//div[@class='trlcont rel']//text()").getall()
            item['tel'] = None
            for i in tel:
                if re.findall(r'\d{11}', i):
                    item['tel'] = i.strip()

            # print(item)
            yield item
        except Exception as e:
            log.ERROR(e)
~~~



pipeline.py 保存json文件

~~~python
import re
from scrapy.exporters import JsonLinesItemExporter


class YangguangPipeline(object):
    def __init__(self):
        self.fp = open("yangguang.json", "wb")  # start_exporting() 是以二进制方式写入的write(b"[")
        self.exporter = JsonLinesItemExporter(self.fp, ensure_ascii=False, encoding="utf-8")

    def open_spider(self, spider):  # 当爬虫被打开的是时候执行
        print("这是爬虫开始了...")

    def process_item(self, item, spider):  # 当爬虫有item传过来的时候会被调用
        item["content"] = self.process_content(item["content"])
        print(item)
        self.exporter.export_item(item)
        return item

    def process_content(self, content):
        content = [re.sub(r"\xa0|\s", "", i) for i in content]
        content = [i for i in content if len(i) > 0]  # 去除列表中的空字符串
        return content

    def close_spider(self, spider):  # 当爬虫关闭的时候执行
        self.fp.close()
        print("这是爬虫结束了。。。")
~~~

pipeline.py 分表存储，twisted异步保存到数据库

~~~python
from datetime import datetime
from fangtianxia.items import NewHouseItem, ESFHouseItem, RentHouseItem
from pymysql import cursors
from twisted.enterprise import adbapi


class FangtianxiaTwistedPipeline(object):
    """异步保存到数据库"""
    def __init__(self):
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'mysql123',
            'database': 'fangtianxia',
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        self._sql = None

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
            insert into newhouse(id,province,city,name,rooms,area,price,address,district,sale,origin_url,tel,crawl_time)
            values (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            return self._sql
        return self._sql

    def process_item(self, item, spider):
        """分表保存"""
        if isinstance(item, NewHouseItem):
            # runInteraction将同步转化为异步处理
            defer = self.dbpool.runInteraction(self.insert_item_newhouse, item)
            # 错误处理
            defer.addErrback(self.handle_error, item, spider)

        if isinstance(item, ESFHouseItem):
            defer = self.dbpool.runInteraction(self.insert_item_esfhouse, item)
            defer.addErrback(self.handle_error, item, spider)

        if isinstance(item, RentHouseItem):
            defer = self.dbpool.runInteraction(self.insert_item_renthouse, item)
            defer.addErrback(self.handle_error, item, spider)

    def insert_item_newhouse(self, cursor, item):
        """保存新房数据到MySQL"""
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            self.sql,
            (item.get('province'), item.get('city'), item.get('name'), item.get('rooms'),
             item.get('area'), item.get('price'), item.get('address'), item.get('district'),
             item.get('sale'), item.get('origin_url'), item.get('tel'), crawl_time)
        )

    def insert_item_esfhouse(self, cursor, item):
        """保存二手房数据到MySQL"""
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql_esfhouse = "insert into esfhouse(id,province,city,name,rooms,floor,toward,year,address,area,price,unit,origin_url,tel,crawl_time) values (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(
            sql_esfhouse,
            (item.get('province'), item.get('city'), item.get('name'), item.get('rooms'),
             item.get('floor'), item.get('toward'), item.get('year'), item.get('address'),
             item.get('area'), item.get('price'), item.get('unit'), item.get('origin_url'),
             item.get('tel'), crawl_time)
        )

    def insert_item_renthouse(self, cursor, item):
        """保存租房数据到MySQL"""
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql_renthouse = "insert into renthouse(id, province, city, decoration, floor, price, area, rent_method, address, rooms, toward, origin_url, tel, crawl_time) value (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(
            sql_renthouse,
            (item.get('province'), item.get('city'), item.get('decoration'), item.get('floor'),
             item.get('price'), item.get('area'), item.get('rent_method'), item.get('address'),
             item.get('rooms'), item.get('toward'), item.get('origin_url'),
             item.get('tel'), crawl_time)
        )

    def handle_error(self, error, item, spider):
        print("=" * 20 + "error" + "=" * 20)
        print(error)
        print("=" * 20 + "error" + "=" * 20)
~~~

middleware.py  处理useragent和proxy

~~~python
import redis
import requests
from scrapy import signals
from fake_useragent import UserAgent

class RandomUserAgent(object):
    """随机useragent"""
    def process_request(self, request, spider):
        user_agent = UserAgent()
        request.headers['User-Agent'] = user_agent.random


class IPProxyMiddleware(object):
    """获取随机代理"""
    def process_request(self, request, spider):
        if 'proxy' not in request.meta:
            proxy = self.get_proxy_from_redis()
            print(f"this is request ip:{proxy}")

    def process_response(self, request, response, spider):
        if response.status != 200:
            proxy = self.get_proxy_from_redis()
            print(f"this is response ip:{proxy}")
            request.meta['proxy'] = 'https://' + proxy
            return request
        return response

    def get_proxy(self):
        """随机从代理池中读取proxy"""
        PROXY_POOL_URL = 'http://localhost:5555/random'
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print('Proxy_pool connect filed',e)
            return None

    def get_proxy_from_redis(self):
        """从redis中读取随机代理"""
        redis_connection = redis.Redis(host='localhost',port=6379,db=0)
        try:
            proxy = redis_connection.srandmember('proxy_pool')
            # print(proxy)
            return proxy.decode()
        except Exception as e:
            print('Proxy_pool connect filed', e)
            return None
~~~

settings.py  基本设置

~~~python
ROBOTSTXT_OBEY = False


LOG_LEVER = "WARNING"
LOG_FILE = "info.log"

# 确保所有爬虫共享相同的去重指纹
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 确保request存储到redis中
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 在redis中保持scrapy-redis用到的队列，不会清理redis中的队列，从而可以实现暂停和恢复的功能
SCHEDULER_PERSIST = True
# 设置链接redis信息
REDIS_URL = "redis://127.0.0.1:6379/0"

#  scrapy-redis-bloomfilter
# DUPEFILTER_CLASS =”scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
# 散列函数的个数，默认为6，可以自行修改
BLOOMFILTER_HASH_NUMBER = 6
# Bloom Filter的bit参数，默认30，占用128MB空间，去重量级1亿
BLOOMFILTER_BIT = 30

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
}

DOWNLOADER_MIDDLEWARES = {
   # 'fangtianxia.middlewares.FangtianxiaDownloaderMiddleware': 543,
   'fangtianxia.middlewares.RandomUserAgent': 540,
   'fangtianxia.middlewares.IPProxyMiddleware': 541,
}

ITEM_PIPELINES = {
   'fangtianxia.pipelines.FangtianxiaTwistedPipeline': 300,
}
~~~



# 11. scrapy_login

~~~python
# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import request
from PIL import Image
from yundama import identify
import requests


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['https://accounts.douban.com/login']
    login_url = 'https://accounts.douban.com/login'
    profile_url = 'https://www.douban.com/people/187541834/'
    edit_signature_url = 'https://www.douban.com/j/people/187541834/edit_signature'

    def parse(self, response):
        formdata = {
            'source': 'None',
            'redir': 'https://www.douban.com/',
            'form_email': 'aircov@163.com',
            'form_password': 'douban123456',
            'remember': 'on',
            'login': '登录'
        }

        # 验证码url
        captcha_url = response.xpath("//img[@id='captcha_image']/@src").get()
        # print("*"*50)
        # print(captcha_img)
        if captcha_url:
            captcha = self.recognize_captcha(captcha_url)
            formdata["captcha-solution"] = captcha
            captcha_id = response.xpath("//input[@name='captcha-id']/@value").get()
            formdata["captcha-id"] = captcha_id

        print(formdata)

        yield scrapy.FormRequest(
            url=self.login_url,
            formdata=formdata,
            callback=self.after_login
        )

    # 登录成功，豆瓣主页面
    def after_login(self, response):
        if response.url == 'https://www.douban.com/':
            print("登录成功!")
            yield scrapy.Request(
                self.profile_url,
                callback=self.parse_profile
            )
        else:
            print("登录失败!")

        print(re.findall(r"这是我自己修改的", response.body.decode("utf-8")))

    # 个人主页
    def parse_profile(self,response):
        if response.url == 'https://www.douban.com/people/187541834/':
            print("进入到了个人主页!")
            
            # <input type="hidden" name="ck" value="Xdd_" disabled="">
            ck = response.xpath("//input[@name='ck']/@value").get()

            # 构造form表单，发送请求，修改签名
            formdata = {
                "ck":ck,
                "signature":"我就是我，不一样的烟火~~"
            }
            yield scrapy.FormRequest(
                self.edit_signature_url,
                callback=self.parse_none,
                formdata=formdata
            )
            print("修改签名成功。。。")

        else:
            print("没有进入个人主页!")

    # 发送请求没有加上callback=  会自动执行这个def parse(self, response):函数
    def parse_none(self,response):
        pass

    # 调用打码平台识别验证码
    def recognize_captcha(self, img_url):
        request.urlretrieve(img_url, "captcha.png")  # 保存图片到本地
        captcha_content = requests.get(img_url).content  # 请求验证码地址 获取响应
        captcha_code = identify(captcha_content)  # 调用打码平台
        print("验证码的识别结果为：%s" % captcha_code)
        return captcha_code

~~~



next_url = urllib.parse.urljoin(response.url, next_url)   自动补全url地址

```
yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_newhouse,
                     meta={"item": (province, city)})
```

~~~python
# -*- coding: utf-8 -*-
import scrapy
import urllib
import requests
from tieba.items import TiebaItem
import re


class TbSpider(scrapy.Spider):
    name = 'tb'
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/f?ie=utf-8&kw=%E6%9D%8E%E6%AF%85&fr=search&pn=0&']

    def parse(self, response):
        # 根据帖子进行分组
        div_list = response.xpath("//div[contains(@class, 'i')]")
        for div in div_list:
            item = TiebaItem()
            item["href"] = div.xpath("./a/@href").get()
            item["title"] = div.xpath("./a/text()").get()
            item["img_list"] = []
            if item["href"] is not None:
                # 自动将url地址补充完整
                item["href"] = urllib.parse.urljoin(response.url, item["href"])
                # print(item)
                yield scrapy.Request(
                    item["href"],
                    callback=self.parse_detail_url,
                    meta={"item": item}
                )

        # 列表页de翻页
        next_url = response.xpath("//a[text()='下一页']/@href").get()
        if next_url is not None:
            next_url = urllib.parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
            )

    def parse_detail_url(self,response):  # 处理详情页
        item = response.meta["item"]
        # if "img_list" not in item:
        #     item["img_list"] = re.findall(r'<a href="(http://c\.hiphotos\.baidu\.com/forum/.*?)">.*?</a>',response.body.decode("utf-8"))
        # else:
            # <a href="http://c.hiphotos.baidu.com/forum/w%3D400%3Bq%3D80%3Bg%3D0/sign=f5e39e97...c.jpg">图</a>
        try:
            item["img_list"].extend(re.findall(r'<a href="(http://c\.hiphotos\.baidu\.com/forum/.*?)">.*?</a>',response.body.decode("utf-8")))
        except Exception as e:
            print("%s:%s" % (e,response.url))

        next_url = response.xpath("//a[text()='下一页']/@href").get()
        if next_url is not None:  # 表示有下一页
            next_url = urllib.parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_detail_url,
                meta={"item": item}
            )
        else:
            # URL地址解码requests.utils.unquote(i)
            item["img_list"] = [requests.utils.unquote(i).split("src=")[-1].strip() for i in item["img_list"]]
            # print(item)
            yield item

~~~

# 12. xpath总结

`//div[@class='xxx']/ul/li[not(@clsas)]/span/a/text()`没有class属性的li标签

`//div[contains(@class,'xxx')]/span[last()]/a/text()`class中包含‘xxx’的div下的最后一个span

`//a[text()='下一页']/@href` 文本等于“下一页”的a标签

# 13.python时间序列处理

```python
crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

# 14 redis 实现增量爬取，断点续爬

scrapy  setting.py中设置

```python
# 确保所有爬虫共享相同的去重指纹
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 确保request存储到redis中
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 在redis中保持scrapy-redis用到的队列，不会清理redis中的队列，从而可以实现暂停和恢复的功能
SCHEDULER_PERSIST = True
# 设置链接redis信息
REDIS_URL = "redis://47.102.99.199:6379/2"
```

# 15 随机user-agent设置

middleware.py中设置

```python
class KuanspiderDownloaderMiddleware(object):
    ......
    def process_request(self, request, spider):
        """设置随机请求头"""
        ua = UserAgent()
        request.headers['User-Agent'] = ua.random
```

查看user-agent

```python
class KuanSpider(scrapy.Spider):
    ......
	def parse(self, response):
   		print(response.request.headers["User-Agent"])
```

# 16 保存文件，图片

~~~python
def save_content_list(self, content_list):
        with open("douyu_anchor.json", "w", encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content, ensure_ascii=False) + "\n")
~~~

```python
import os
from urllib import request
item = {
    'title':category,
    'image':image_url
}

file_path = './img/'+item['title']
if not os.path.exists(file_path):
    os.mkdir(file_path)

if not os.path.exists(file_path+item['image']):

    request.urlretrieve(item['image'], file_path+item['image'])
```

# 17. urlencode  url地址参数补全

~~~python
def get_page_index(keyword, city_code, offset):
    data = {
        'query': keyword,
        'scity': city_code,
        'page': offset,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    }
    proxies = {
        'http': 'http://127.0.0.1:8087',
        'https': 'https://127.0.0.1:8087'
    }
    url = 'https://www.zhipin.com/job_detail/?' + urlencode(data)
    try:
        urllib3.disable_warnings()
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.text
        elif requests.get(url, headers=headers, proxies=proxies, verify=False).status_code == 200:
            res1 = requests.get(url, headers=headers, proxies=proxies, verify=False)
            return res1.text
        return None
    except RequestException:
        print('请求初始页出错')
        return None
~~~

# 18. MySQL去重操作

```mysql
--查询单个字段重复数据
select name from films group by name having count(*)>1;
--查询多个字段的重复数据，并将结果的所有字段信息返回
select * from films where(films.name,films.box_office) in (select name,box_office from films group by name,box_office having count(*)>1);
--删除 table 中重复数据.
# 1.查询出重复记录形成一个集合（临时表t2），集合里是每种重复记录的最小ID。
# 2.关联 判断重复基准的字段。
# 3.根据条件，删除原表中id大于t2中id的记录
delete films form films,(select min(id) id,name,released from films group by name,released having count(*)>1) t2 where films.name = t2.name and films.released = t2.released and films.id>t2.id;
```

# 19. logging模块使用/scrapy.log使用

```python
log_name = 'sb_spider_log.log'
logging.basicConfig(  # 日志输出信息
    filename=log_name,
    filemode='a',
    level=logging.INFO,
    datefmt='%Y-%m-%d %A %H:%M:%S')
......
logging.info('Page crawling succeeded')
logging.error()
```

~~~python
# LOG_LEVER = "INFO"
# LOG_FILE = "info.log"

from scrapy import log
......
log.error(e)
~~~

# 20. python3爬虫中文乱码之请求头 ‘Accept-Encoding’：br 的问题

‘Accept-Encoding’：是浏览器发给服务器,声明浏览器支持的编码类型。一般有gzip,deflate,br 等等。

python3中的 requests包中response.text 和 response.content

response.content #字节方式的响应体，会自动为你解码 gzip 和 deflate 压缩 类型：bytes

reponse.text #字符串方式的响应体，会自动根据响应头部的字符编码进行解码。类型：str

但是这里是默认是不支持解码br的！！！！

br 指的是 Brotli，是一种全新的数据格式，无损压缩，压缩比极高（比gzip高的）

~~~python
import brotli
# 获取网页内容，返回html数据
response = requests.get(url, headers=headers)
# 通过状态码判断是否获取成功
if response.status_code == 200:
    print(response.headers)
    print(response.encoding)
    key = 'Content-Encoding'
    if(key in response.headers and response.headers['Content-Encoding'] == 'br'):
        data = brotli.decompress(response.content)
        data1 = data.decode('utf-8')
        print(data1)
~~~

# 21. requests获取cookies

~~~python
user_id = re.search(r'"uniqueid":"(\d+)"', user_info).group(1)
print(user_id)
url = 'https://weibo.com/u/{}/home'.format(user_id)
response = self.sess.get(url)

# <class 'requests.structures.CaseInsensitiveDict'> 转化成字典
cookies = dict(response.request.headers)

with open('./cookies.txt','w') as f:
    f.write(cookies['Cookie'])
~~~

# 22. 滑动验证码破解

~~~python
import cv2
import time

import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import numpy as np

from config import username, password


class Login163(object):
    """
    使用opencv识别验证码中缺口位置，获取需要滑动距离，并使用selenium模仿人类行为破解滑动验证码
    """

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1280, 900)
        self.wait = WebDriverWait(self.driver, 20)
        self.url = 'https://dl.reg.163.com/ydzj/maildl?product=urs&curl=https://m.reg.163.com/'
        self.zoom = 1

    def get_pic(self):
        """获取图片"""
        target = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img'))).get_attribute('src')
        template = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_jigsaw'))).get_attribute('src')

        target_img = Image.open(BytesIO(requests.get(target).content))
        template_img = Image.open(BytesIO(requests.get(template).content))
        target_img.save('target.jpg')
        template_img.save('template.png')

        local_img = Image.open('target.jpg')
        size_loc = local_img.size
        self.zoom = 391 / int(size_loc[0])  # 缩放系数为391除以本地的宽度，391为目标图片在网页上的宽度
        print('self.zoom:', self.zoom)

    def match(self, target, template):
        img_rgb = cv2.imread(target)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template, 0)
        run = 1
        w, h = template.shape[::-1]
        print(w, h)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

        # 使用二分法查找阈值的精确值
        L = 0
        R = 1
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            print(threshold)
            if threshold < 0:
                print('Error')
                return None
            loc = np.where(res >= threshold)
            print(len(loc[1]))
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                print('目标区域起点x坐标为：%d' % loc[1][0])
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2

        return loc[1][0]

    def get_tracks(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        distance += 20
        print('distance:', distance)
        v = 0
        t = 0.2
        forward_tracks = []
        current = 0
        mid = distance * 3 / 5
        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3
            s = v * t + 0.5 * a * (t ** 2)
            v = v + a * t
            current += s
            forward_tracks.append(round(s))

        back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}

    def crack_slider(self):
        self.get_pic()
        target = 'target.jpg'
        template = 'template.png'
        distance = self.match(target, template)

        tracks = self.get_tracks((distance + 18) * self.zoom)  # 对位移的缩放计算   18需要自己调整
        print('tracks', tracks)
        slider = self.driver.find_element_by_class_name("yidun_slider")  # 需要滑动的元素
        ActionChains(self.driver).click_and_hold(slider).perform()  # 鼠标按住左键不放

        for track in tracks['forward_tracks']:
            ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()

        time.sleep(0.5)
        for back_tracks in tracks['back_tracks']:
            ActionChains(self.driver).move_by_offset(xoffset=back_tracks, yoffset=0).perform()

        ActionChains(self.driver).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(self.driver).move_by_offset(xoffset=3, yoffset=0).perform()
        time.sleep(1)
        ActionChains(self.driver).release().perform()  # 释放鼠标

        time.sleep(1)
        self.driver.find_element_by_xpath("//div[@class='bButton_btn ']/button").click()

        # 重试
        try:
            failure = WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'yidun_tips__text'), '向右拖动滑块填充拼图'))
            print(failure)
        except:
            failure = None

        if failure:
            self.crack_slider()

        # 错误
        try:
            error = WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'yidun_tips__text'), '失败过多，点此重试'))
            print(error)
        except:
            error = None

        if error:
            error.click()
            time.sleep(2)
            self.crack_slider()


    def run(self):
        self.driver.get(self.url)
        self.driver.find_elements_by_xpath("//div[@class='ipt_wrap large']/input")[0].send_keys(self.username)
        self.driver.find_elements_by_xpath("//div[@class='ipt_wrap large']/input")[1].send_keys(self.password)

        # 点击登录
        self.driver.find_element_by_xpath("//div[@class='u-btn c-main']/button").click()

        # 验证机器人行为
        try:
            robot = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_tips')))

            if robot:
                print("正在验证机器人行为！")
                wait = WebDriverWait(self.driver, 20).until(
                    EC.text_to_be_present_in_element((By.CLASS_NAME, 'yidun_tips__text'), '验证成功'))
                if wait:
                    self.driver.find_element_by_xpath("//div[@class='u-btn c-main']/button").click()

        except:
            pass

        # 跳转页面
        time.sleep(1)
        try:
            self.driver.find_element_by_class_name("u-icon-img").click()
            time.sleep(2)
        except:
            pass

        # 滑动验证码页面
        self.crack_slider()
        if self.driver.current_url == 'https://m.reg.163.com/#/email':

            cookies = {i["name"]: i["value"] for i in self.driver.get_cookies()}
            print(cookies)
        print(self.driver.current_url)

        # 关闭webdriver
        time.sleep(5)
        self.driver.close()


if __name__ == '__main__':
    username = username
    password = password
    login163 = Login163(username=username, password=password).run()
~~~

~~~python
def FindPic(target, template):
    """
    找出图像中最佳匹配位置
    :param target: 目标即背景图
    :param template: 模板即需要找到的图
    :return: 返回最佳匹配及其最差匹配和对应的坐标
    """
    target_rgb = cv2.imread(target)
    target_gray = cv2.cvtColor(target_rgb, cv2.COLOR_BGR2GRAY)
    template_rgb = cv2.imread(template, 0)
    res = cv2.matchTemplate(target_gray, template_rgb, cv2.TM_CCOEFF_NORMED)
    value = cv2.minMaxLoc(res)
~~~

使用cv2库，先读取背景图，然后夜视化处理（消除噪点），然后读取模板图片，使用cv2自带图片识别找到模板在背景图中的位置，使用minMaxLoc提取出最佳匹配的最大值和最小值，返回一个数组形如（-0.3， 0.95， （121,54），（45， 543））元组四个元素，分别是最小匹配概率、最大匹配概率，最小匹配概率对应坐标，最大匹配概率对应坐标。

我们需要的是最大匹配概率坐标，对应的分别是x和y坐标，但是这个不一定，有些时候可能是最小匹配概率坐标，最好是根据概率的绝对值大小来比较。

滑块验证较为核心的两步，第一步是找出缺口距离，第二步是生成轨迹并滑动，较为复杂的情况下还要考虑初始模板图片在背景图中的坐标，以及模板图片透明边缘的宽度，这些都是影响轨迹的因素。

# 23. scrapy 使用selenium

~~~python
class SeleniumDownloadMiddleware(object):
    def __init__(self):
        self.driver = webdriver.Chrome()

    def process_request(self, request, spider):
        self.driver.get(request.url)
        time.sleep(1)

        try:
            while True:
                showmore = self.driver.find_element_by_class_name('show-more')
                showmore.click()
                time.sleep(0.3)
                if not showmore:
                    break
        except:
            pass

        # 获得网页源代码，异步，需要延迟    阅读、评论、喜欢三个字段ajax请求，在网页中直接通过xpath不可
        source = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=source, request=request, encoding="utf-8")
        return response
~~~

# 24. scrapy部署

1. 在scrapy项目路径下执行`sudo scrapyd`或`scrapyd`，启动scrapyd服务；或以后台进程方式启动`nohup scrapyd > scrapyd.log 2>&1 &`
   1.   2表示标准错误输出
   2.   1表示标准信息输出
   3.   2>&1表示把错误信息一起输入到标准输出
2. 部署scrapy爬虫项目`scrapyd-deploy deployname -p myspider`
3. 启动爬虫项目中的一个爬虫`curl http://localhost:6800/schedule.json -d project=myspider -d spider=tencent`
4. 终止爬虫`curl http://localhost:6800/cancle.json -d project=myspider -d job=tencent`(kill-9  `ps-aux | grep 'myspider'| awk '{print "kill-9"$2}' | sh`)

listproject.json -- 列出项目      listjobs.json -- 列出job      listspiders.json -- 列出爬虫

# 25.selenium封杀

~~~js
window.navigator.webdriver
selenium：true
chrome：undefined
~~~

解决方法：

~~~python
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions

option = ChromeOptions()
# 设置无头浏览器方法
# options.set_headless()
# options.headless = True
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = Chrome(options=option)
~~~

此时启动的Chrome窗口，在右上角会弹出一个提示，不用管它，不要点击`停用`按钮。

# 26. crontab定时任务

1.编辑任务 crontab -e

    任务格式
    分 时 日 月 星期 命令
    m  h  d m  week command
    30 *  * *  *    ls  每月8号7点半执行ls命令 
    
    * */5 * *   *  ls  每隔3分钟执行 ls命令
    
    注意点:
        星期0;指的是星期天
        * 代表每
        */n 代表隔

2.查看任务 crontab -l

定时爬虫操作

终端命令 进入项目

1. 在爬虫项目中 创建 .sh文件
2. 在.sh文件中 写执行命令
    cd `dirname $0` || exit 1
    python ./main.py >> run.log 2>&1
3. 添加可执行权限 sudo chmod +x run.sh
4. crontab -e
5. */5 * * * * /home/ubuntu/..../myspider.sh >> /home/ubuntu/.../run2.log 2>&1


-------------------------------------------------------------------------------------------------------------


# 1、python装饰器，传参

~~~python
def set_level(level_num):
    def set_func(func):
        def call_func(*args, **kwargs):
            if level_num == 1:
                print("----权限级别1，验证----")
            elif level_num == 2:
                print("----权限级别2，验证----")
            return func()
        return call_func
    return set_func

@set_level(1)
def test1():
    print("-----test1---")
    return "ok test1"

# 计算函数耗时的装饰器
def count_time(func):
    def int_time(*args, **kwargs):
        start_time = time.time()  # 程序开始时间
        ret = func(*args, **kwargs)
        over_time = time.time()  # 程序结束时间
        total_time = (over_time - start_time)
        print('%s程序共计%.6f秒' % (func, total_time))
        return ret
    return int_time
~~~

# 2、字典按照值的大小排序

~~~js
json.dumps()--dict->str              json.loads()--str->dict
~~~



~~~python
d={'a':24,'g':52,'i':12,'k':33}
sorted(d.items(), key=lambda x:x[1])
$:[('i', 12), ('a', 24), ('k', 33), ('g', 52)]
--------------------------------------------------
# 前十10人气大神倒序排序
manito_score = sorted(result.items(), key=lambda x: float(x[1]), reverse=True)[:10]
---------------------------------------------------
# 排序  ret_json=[{'user_id'：461687615，'manito_score'：88},{'user_id'：461687614，'manito_score'：84}]
sorted_x = sorted(ret_json, key=lambda x: x['manito_score'], reverse=True)

# 排序， 根据两个字段的值倒序排序
sorted_x = dict(sorted(feature_result_list[0].items(), key=lambda x: (-(json.loads(x[1]).get('3010013') if json.loads(x[1]).get('3010013') else 0),-(json.loads(x[1]).get('3000015') if json.loads(x[1]).get('3000015') else 0))))
~~~

filter函数：

~~~python
dic = {'k1': 10, 'k2': 100, 'k3': 50, 'k4': 90}
print(list(filter(lambda x: x[1] > 50, dic.items())))  # 把值大于50的由元祖组成的键值对过滤出来。 x[1]代表value
$:[('k2', 100), ('k4', 90)]
---------------------------------------------------------
# 删除字典中值为None的元素
result_dict = dict(filter(lambda x: x[1] != None, ret.items()))
~~~



# 3、python实现冒泡排序、插入排序、快速排序

~~~python
def BubbleSort(numList):
    if not len(numList):
        return
    for i in range(len(numList)):
        for j in range(len(numList)-1):
            if numList[i] < numList[j]:
                numList[i], numList[j] = numList[j], numList[i]
    return numList
时间复杂度：O(n)  O(n2)
~~~

~~~python
def insert_sort(alist):
    # 从第二个位置，即下标为1的元素开始向前插入
    for i in range(1, len(alist)):
        # 从第i个元素开始向前比较，如果小于前一个元素，交换位置
        for j in range(i, 0, -1):
            if alist[j] < alist[j-1]:
                alist[j], alist[j-1] = alist[j-1], alist[j]

alist = [54,26,93,17,77,31,44,55,20]
insert_sort(alist)
时间复杂度：O(n)  O(n2)
~~~

~~~python
def quick_sort(alist, start, end):
    """快速排序"""

    # 递归的退出条件
    if start >= end:
        return

    # 设定起始元素为要寻找位置的基准元素
    mid = alist[start]

    # low为序列左边的由左向右移动的游标
    low = start

    # high为序列右边的由右向左移动的游标
    high = end

    while low < high:
        # 如果low与high未重合，high指向的元素不比基准元素小，则high向左移动
        while low < high and alist[high] >= mid:
            high -= 1
        # 将high指向的元素放到low的位置上
        alist[low] = alist[high]

        # 如果low与high未重合，low指向的元素比基准元素小，则low向右移动
        while low < high and alist[low] < mid:
            low += 1
        # 将low指向的元素放到high的位置上
        alist[high] = alist[low]
    # 退出循环后，low与high重合，此时所指位置为基准元素的正确位置
    # 将基准元素放到该位置
    alist[low] = mid
    # 对基准元素左边的子序列进行快速排序
    quick_sort(alist, start, low-1)
    # 对基准元素右边的子序列进行快速排序
    quick_sort(alist, low+1, end)

alist = [54,26,93,17,77,31,44,55,20]
quick_sort(alist,0,len(alist)-1)
print(alist)

时间复杂度：O(nlogn)  O(n2)
~~~



# 4、公网如何与内网通讯？

第一步：在内网服务器上，使用ssh命令建立反向隧道:

`ssh -fNR port:localhost:22 publicUserName@publicIp`

-f 表示后台执行

-N 表示不执行任何命令

-R 建立反向隧道

port 你可以指定任何端口，这个只要没有被占用即可

第二步：登录你自己的服务器，登录进去之后，使用如下命令：

`ssh localhost -p port`

-p 后面跟的port（端口）需要与第一步设置的保持一致

另外 请注意下用户名是否一致

至此，输入完密码之后，就可以远程登录了

# 5、Linux、vim命令

压缩：zip ana.zip anaconda-ks.cfg

解压：upzip fileName.zip

`lsof -i:8000`     用于查看某一端口的占用情况

`netstat -tunlp |grep 8000`   用于查看指定的端口号的进程情况

`du -sh *`  查看当前目录下所有文件大小

```shell
python@ubuntu:~/kkbuluo$ du -sh *
96K		2018电影
240K	fangtianxia
256K	proxy-pool
188K	search_proj
48M		unsplash_spider
384K	weibo_spider
```

`df -h` 查看磁盘使用量

~~~shell
root@ubuntu:~# df -h
文件系统        容量  已用  可用 已用% 挂载点
udev            1.5G     0  1.5G    0% /dev
tmpfs           300M  8.8M  291M    3% /run
/dev/sda1        21G   13G  6.7G   66% /
tmpfs           1.5G   14M  1.5G    1% /dev/shm
tmpfs           5.0M     0  5.0M    0% /run/lock
tmpfs           1.5G     0  1.5G    0% /sys/fs/cgroup
tmpfs           300M   56K  299M    1% /run/user/1000
~~~

`fdisk -l`查看磁盘使用量

~~~shell
root@ubuntu:~/kkbuluo# fdisk -l
Disk /dev/sda: 35 GiB, 37580963840 bytes, 73400320 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x39fde10b

设备       启动    Start   末尾   扇区  Size Id 类型
/dev/sda1  *        2048 64520191 64518144 30.8G 83 Linux
/dev/sda2       64520192 73400319  8880128  4.2G  5 扩展
/dev/sda5       64522240 73400319  8878080  4.2G 82 Linux 交换 / Solaris
~~~

程序后台执行：`nohup  python3  money_award.py  &`    会在当前文件夹生nohup.out(终端打印数据)

**vim将多个空格换成一个空格**  `:%s/  */ /g`

**vim查找字符串** `:/python`   N键下一个

**vim多行注释与取消注释**：<https://blog.csdn.net/suixin_123/article/details/81393397>

**多行删除**

* 1.首先在命令模式下，输入“：set nu”显示行号；
*  2.通过行号确定你要删除的行； 
* 3.命令输入“：32,65d”,回车键，32-65行就被删除了
  如果无意中删除错了，可以使用‘u’键恢复（命令模式下）

**vim提取含有所有关键词的行**：

* :let @a="" --- 使用let命令寄存器a里的内容清空 
* :g/book/y A --- 把所有包含book的行都添加到寄存器a中
* :put a --- 把寄存器a里的内容粘贴出来 ，光标所在行

# 6、Oracle数据库

* 查看时间（小时）

~~~sql
select sysdate,to_char(sysdate,'hh24')  from dual;
sysdate    to_char(sysdate,'HH24')
2019-08-26 10:07:24
~~~



* python操作oracle读取数据dict格式

~~~python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
    filename='./info.log',
    filemode='a'
)
# 支持中文
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
conn = cx_Oracle.connect('dw_user/dw_userrainbow@106.75.248.35:15210/rainbow') 
orcl_cursor = self.conn.cursor()

try:
    orcl_cursor.execute(sql)
    columns = [column[0] for column in self.orcl_cursor.description]
    for row in orcl_cursor.fetchall():
        result.append(dict(zip(columns, row)))

except Exception as e:
	logging.error(e)
finally:
	conn.close()
	orcl_cursor.close()
~~~



* 查询时间大于某个时间的记录：

~~~sql
select * from WBC_SUBJECT where GMT_CREATE > to_date('2019-04-09 12:00:00','yyyy-mm-dd hh24:mi:ss');
~~~

* 查询一个半小时之间的数据：

~~~python
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
old_time =(datetime.datetime.now()+datetime.timedelta(minutes=-90)).strftime("%Y-%m-%d %H:%M:%S")
sql = """select     TICKET_NO,ORDER_NO,DRAW_RESULT,MIX_TYPE,MULTIPLE,GMT_CREATE,ISSUE_NO,LOTTERY_TYPE,LOTTERY_SUB_TYPE,GMT_MODIFIED
        from LTDR_PRINT_TICKET
        where  ((gmt_create>=to_date('%s', 'yyyy-mm-dd HH24:mi:ss')
           and gmt_create<to_date('%s', 'yyyy-mm-dd HH24:mi:ss'))
            or (gmt_modified >= to_date('%s', 'yyyy-mm-dd HH24:mi:ss')
           and gmt_modified < to_date('%s', 'yyyy-mm-dd HH24:mi:ss')))
          and DRAW_STATUS = 'DRAW_FINISH'
          and MIX_TYPE is not null and DRAW_RESULT is not null""" % (old_time, current_time, old_time, current_time)
~~~

* 插入Oracle数据库，查询，增量更新

~~~python
try:
	db = cx_Oracle.connect('bd_warehouse/v5gaoo5c2uc1u4ye@192.168.16.16:1521/jczjtest')  # 线上
    # db = cx_Oracle.connect('bd_warehouse/bd_warehouse@10.0.12.2:1521/dev')
    cursor = db.cursor()

    in_data=[]
    up_data=[]

    for item in split_last_list:
        item['DRAW_RESULT'] = item['DRAW_RESULT'].replace(', ', '|')
        item['GMT_CREATE'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['GMT_MODIFIED'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = """select ORDER_NO,ISSUE_NO,DRAW_RESULT,LOTTERY_SUB_TYPE from  PRIZE_TICKET_SPLIT where ORDER_NO='%s' and DRAW_RESULT='%s' and GAME_NO='%s' and LOTTERY_SUB_TYPE='%s'""" % (item['ORDER_NO'], item['DRAW_RESULT'], item['GAME_NO'], item['LOTTERY_SUB_TYPE'])
        cursor.execute(sql)
        ret = cursor.fetchall()

        # 判断是否有重复数据
        if not ret:
            in_data.append((item['ORDER_NO'], item['DRAW_RESULT'], item['MIX_TYPE'], item['MULTIPLE'], item['GMT_CREATE'], item['MATCH_COUNT'], item['UNIQUE_ID'], item['GAME_RESULT_SP'], item['UNIQUE_STATUS'], item['GAME_NO'], item['ISSUE_NO'], item['LOTTERY_TYPE'], item['LOTTERY_SUB_TYPE'], item['GMT_MODIFIED']))
        else:
            # 有重复数据
            up_data.append((item['MULTIPLE'], item['GMT_CREATE'], item['GMT_MODIFIED'], item['ORDER_NO'],item['DRAW_RESULT'], item['GAME_NO'], item['MULTIPLE'], item['LOTTERY_SUB_TYPE']))

        sql = """INSERT INTO PRIZE_TICKET_SPLIT (id, ORDER_NO, DRAW_RESULT, MIX_TYPE, MULTIPLE, GMT_CREATE, MATCH_COUNT, UNIQUE_ID, GAME_RESULT_SP, UNIQUE_STATUS, GAME_NO,ISSUE_NO,LOTTERY_TYPE,LOTTERY_SUB_TYPE,GMT_MODIFIED) VALUES (SEQ_PRIZE_TICKET_SPLIT.nextval, :v2, :v3, :v4, :v5,to_date(:v6,'yyyy-mm-dd hh24:mi:ss') ,:v7, :v8, :v9, :v10, :v11, :v12,:v13,:v14,to_date(:v15,'yyyy-mm-dd hh24:mi:ss'))"""

        up_sql = """update PRIZE_TICKET_SPLIT set MULTIPLE=:v1,GMT_CREATE=to_date(:v2,'yyyy-mm-dd hh24:mi:ss'), GMT_MODIFIED=to_date(:v3,'yyyy-mm-dd hh24:mi:ss') where ORDER_NO=:v4 and DRAW_RESULT=:v5 and GAME_NO = :v6 and MULTIPLE < :v7 and LOTTERY_SUB_TYPE=:v8"""

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
~~~



# 7、crontab使用

py文件：main.py

~~~python
import datetime 

time_now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
print("现在的时间是:{}".format(time_now))
~~~

可执行文件：run.sh

~~~shell
cd `dirname $0` || exit 1   # 进入当前Shell程序的目录
python3 ./main.py >> run.log 2>&1   # 将标准错误重定向到标准输出
~~~

编辑定时任务( 如果文件不存在会自动创建)：`crontab -e`

~~~python
*/1 * * * * /home/python/Desktop/run.sh   # 每分钟执行一次run.sh
~~~

查看定时任务：`crontab -l`

删除定时任务：`crontab -r`



# 8、项目部署

linux批量杀死进程：

* `ps -ef | grep gunicorn | awk '{print $2}'|xargs kill -9`

svn到服务器：

* svn co --username=caoshangfei --password  caoshangfei123456 https://huored.gicp.net:8088/svn/bd_anti_spam/trunk/线上搜索项目/search_system_online
* svn co --username=caoshangfei --password  caoshangfei123456 https://huored.gicp.net:8088/svn/bd_python_recommend/branches/v2.0.0
* svn co --username=caoshangfei --password  caoshangfei123456 https://huored.gicp.net:8088/svn/bd_python_recommend/branches/supplement
* svn co --username=caoshangfei --password  caoshangfei123456 https://huored.gicp.net:8088/svn/bd_python_recommend/trunk
* 解决冲突：svn revert --depth=infinity .   ----->    svn update
* 回到其他版本号：svn up -r  版本号 

项目部署流程：

* 进入 root 用户  vim  /etc/supervisord.conf

* sudo -i 切换 root 用户                 root 用户 切换 hadoop 用户  su - hadoop





**hadoop005启动gunicorn：**   `/home/hadoop/.local/bin/gunicorn -b 192.168.17.25:8000 manage:app -c ./gunicorn_conf.py`

**线下推荐启动程序：**`gunicorn -b 10.4.212.3:3000 -w 3 run_app:app --log-level=debug --log-file ./log/gunicorn.log `

**supervisorctl 管理gunicorn 启动：**

~~~javascript
[program:sensitive_word]
command=/opt/anaconda3/bin/gunicorn -b 10.4.212.4:7200  sensitive_word_api:app -c  gunicorn_conf.py
directory=/home/admin/anti_spam/sensitive_word_model
startsecs=0
stopwaitsecs=0
autostart=true
autorestart=true
user=admin
environment=HOME=/home/admin
environment=NLS_LANG="Simplified Chinese_CHINA.ZHS16GBK"
stdout_logfile=/home/admin/anti_spam/sensitive_word_model/log/gunicorn.log
stderr_logfile=/home/admin/anti_spam/sensitive_word_model/log/gunicorn.err

~~~

# 9、MySQL去重操作

```mysql
--查询单个字段重复数据
select name from films group by name having count(*)>1;
--查询多个字段的重复数据，并将结果的所有字段信息返回
select * from films where(films.name,films.box_office) in (select name,box_office from films group by name,box_office having count(*)>1);
--删除 table 中重复数据.
# 1.查询出重复记录形成一个集合（临时表t2），集合里是每种重复记录的最小ID。
# 2.关联 判断重复基准的字段。
# 3.根据条件，删除原表中id大于t2中id的记录
delete films form films,(select min(id) id,name,released from films group by name,released having count(*)>1) t2 where films.name = t2.name and films.released = t2.released and films.id>t2.id;
```

乐观锁：`update tb_sku set stock=2 where id=1 and stock=7;`

# 10、Django 获取参数

1. 查询字符串query—string

```python
# /qs/?a=1&b=2&a=3
def qs(request):
    a = request.GET.get('a')
    b = request.GET.get('b')
    alist = request.GET.getlist('a')
    print(a)  # 1
    print(b)  # 2
    print(alist) # ['1','3']
    return HttpResponse("OK")
```

**重要：查询字符串不区分请求方式，即假使客户端进行POST方式的请求，依然可以通过request.GET获取请求中的查询字符串数据。**

2. 表单类型form-data

```python
def get_body(request):
    a = request.POST.get('a')
    b = request.POST.get('b')
    alist = request.POST.getlist('a')
    print(a)
    print(b)
    print(alist)
    return HttpResponse('OK')
```

**重要：request.POST只能用来获取POST方式的请求体表单数据。**

3. 非表单类型non-form-data

```python
例如要获取请求体中的如下JSON数据
{"a": 1, "b": 2}
import json

def get_body_json(request):
    json_str = request.body
    json_str = json_str.decode()  # python3.6 无需执行此步
    req_data = json.loads(json_str)
    print(req_data['a'])
    print(req_data['b'])
    return HttpResponse('OK')
```

4. 请求头

```python
def get_headers(request):
    print(request.COOKIES.get('name'))
    print(request.META['CONTENT_TYPE'])
    return HttpResponse("OK")
```

5. 常用的HttpRequest对象属性

```python
method、user、path、
```

# 11、Django Rest Framework

`request.data` 返回解析之后的请求体数据。类似于Django中标准的`request.POST`和`request.FILES`

`request.query_params`与Django标准的`request.GET`相同

set_password    check_password

# 12、使用redis有什么缺点，怎么解决？redis为什么这么快？

回答:主要是四个问题

(一)缓存和数据库双写一致性问题

- 分析：一致性问题是分布式常见问题，还可以再分为最终一致性和强一致性。数据库和缓存双写，就必然会存在不一致的问题。。答这个问题，先明白一个前提。就是如果对数据有强一致性要求，不能放缓存。我们所做的一切，只能保证最终一致性。另外，我们所做的方案其实从根本上来说，只能说降低不一致发生的概率，无法完全避免。因此，有强一致性要求的数据，不能放缓存。
- 回答:[《分布式之数据库和缓存双写一致性方案解析》](https://www.baidu.com/s?wd=%E3%80%8A%E5%88%86%E5%B8%83%E5%BC%8F%E4%B9%8B%E6%95%B0%E6%8D%AE%E5%BA%93%E5%92%8C%E7%BC%93%E5%AD%98%E5%8F%8C%E5%86%99%E4%B8%80%E8%87%B4%E6%80%A7%E6%96%B9%E6%A1%88%E8%A7%A3%E6%9E%90%E3%80%8B&tn=24004469_oem_dg&rsv_dl=gh_pl_sl_csd)给出了详细的分析，在这里简单的说一说。首先，采取正确更新策略，先更新数据库，再删缓存。其次，因为可能存在删除缓存失败的问题，提供一个补偿措施即可，例如利用消息队列。

(二)缓存雪崩问题

- 分析：缓存雪崩，即缓存同一时间大面积的失效，这个时候又来了一波请求，结果请求都怼到数据库上，从而导致数据库连接异常。
- 回答：1，给缓存的实效时间加上一个随机值，避免集体实效；2，使用互斥锁，但是该方法吞吐量明显下降；3，双缓存，我们有两个缓存，缓存A和缓存B，缓存A的实效时间20分钟，缓存B不设置实效时间，自己做缓存预热处理

(三)缓存击穿问题

- 分析：缓存穿透，即黑客故意去请求缓存中不存在的数据，导致所有的请求都怼到数据库上，从而数据库连接异常。
- 回答：1，利用互斥锁，缓存失效的时候，先去获得锁，得到锁了，再去请求数据库。没得到锁，则休眠一段时间重试；2、采用异步更新；3、提供一个能迅速判断请求是否有效的拦截机制，比如，利用布隆过滤器，内部维护一系列合法有效的key。迅速判断出，请求所携带的Key是否合法有效。如果不合法，则直接返回。

(四)缓存的并发竞争问题

- 回答:如下所示
  (1)如果对这个key操作，不要求顺序
  这种情况下，准备一个分布式锁，大家去抢锁，抢到锁就做set操作即可，比较简单。
  (2)如果对这个key操作，要求顺序
  假设有一个key1,系统A需要将key1设置为valueA,系统B需要将key1设置为valueB,系统C需要将key1设置为valueC.
  期望按照key1的value值按照 valueA-->valueB-->valueC的顺序变化。这种时候我们在数据写入数据库的时候，需要保存一个时间戳。假设时间戳如下

```
系统A key 1 {valueA  3:00}
系统B key 1 {valueB  3:05}
系统C key 1 {valueC  3:10}
```

那么，假设这会系统B先抢到锁，将key1设置为{valueB 3:05}。接下来系统A抢到锁，发现自己的valueA的时间戳早于缓存中的时间戳，那就不做set操作了。以此类推。

redis为什么这么快？

分析:这个问题其实是对redis内部机制的一个考察。其实根据博主的面试经验，很多人其实都不知道redis是单线程工作模型。所以，这个问题还是应该要复习一下的。
回答:主要是以下三点
(一)纯内存操作
(二)单线程操作，避免了频繁的上下文切换
(三)采用了非阻塞I/O多路复用机制

# 13、在ES批量插入数据超时时自动重试

学习ES基本操作：

~~~python
# 创建index    POST  http://192.168.191.1:8000/create_index?index=xxx
@app.route('/create_index', methods=['POST'])
def create_index():
    index = request.args.get('index')
    result = es.indices.create(index=index, ignore=400)

    return jsonify(result)


# 删除index   DEL   http://192.168.191.1:8000/delete_index?index=xxx
@app.route('/delete_index', methods=['DELETE'])
def delete_index():
    index = request.args.get('index')
    result = es.indices.delete(index=index, ignore=[400, 404])
    print(result)
    return jsonify(result)


# 创建mapping
@app.route('/create_mapping', methods=['POST'])
def create_mapping():
    index = request.args.get('index')
    mapping = {
        "subject": {
            "properties": {
                "title": {
                    "type": "string",
                    'analyzer': 'ik_max_word',
                    'search_analyzer': 'ik_max_word',

                },
                "group": {
                    "type": "string"
                },
                "name": {
                    "type": "keyword",
                    "index": "not_analyzed"
                },
                "shortContent": {
                    "type": "string",
                    'analyzer': 'ik_max_word',
                    'search_analyzer': 'ik_max_word'
                },
                "longContent": {
                    "type": "string",
                    'analyzer': 'ik_max_word',
                    'search_analyzer': 'ik_max_word'
                },
                'manito_score':{
                    "type": "integer",
                    "fields": {
                        "sort": {
                            "type": "float",
                            "index": "not_analyzed"
                        }
                    }
                }
            }
        }
    }
    result = es.indices.put_mapping(index=index, doc_type='subject', body=mapping)

    return jsonify(result)
~~~



使用ES批量插入数据：

~~~python
from elasticsearch import Elasticsearch, helpers

# es超时自动重试
# es = Elasticsearch([{'host':'10.7.131.4','port':9200}],timeout=60,max_retries=3,retry_on_timeout=True)
# 连接es集群
es = Elasticsearch(['10.7.131.4', '10.7.131.5', '10.7.131.6'],
                   sniff_on_connection_fail=True,  # 节点无响应时刷新节点
                   sniff_timeout=180  # 设置超时时间
                   )

def gendata():
    my_word = ['foo','bar','baz']
    for word in my_word:
        yield {
            '_index':'news2',
            '_type':'subject',
            'title':word
        }

helpers.bulk(es, gendata())
~~~

查询ES中所有数据：

~~~python
from elasticsearch import Elasticsearch, helpers

# 连接到es集群
es = Elasticsearch(['10.7.131.4', '10.7.131.5', '10.7.131.6'],
                   sniff_on_connection_fail=True,  # 节点无响应时刷新节点
                   sniff_timeout=180  # 设置超时时间
                   )


def search():
    es_search_options = set_search_optional()
    es_result = get_search_result(es_search_options)
    final_result = get_result_list(es_result)
    return final_result


def get_result_list(es_result):
    final_result = []
    for item in es_result:
        final_result.append(item['_source'])
    return final_result


def get_search_result(es_search_options, scroll='5m', index='user', doc_type='cif_user', timeout="1m"):
    es_result = helpers.scan(
        client=es,
        query=es_search_options,
        scroll=scroll,
        index=index,
        doc_type=doc_type,
        timeout=timeout
    )
    return es_result


def set_search_optional():
    # 检索选项
    es_search_options = {
        "query": {
            "match_all": {
            }
        }
    }
    return es_search_options


if __name__ == '__main__':
    final_results = search()
    # print([i.get('loginName') for i in final_results])
    print(len(final_results))
~~~

# 14、xpath语法

* xpath定位当前元素的相邻元素/兄弟元素：

~~~
前N位：
preceding-sibling::div[N]
后N位：
following-sibling::div[N]
~~~

* xpath获取内容包含`评论[`并且不包含`原文`的a标签的文本

`.//a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()`

`//div[@class='xxx']/ul/li[not(@clsas)]/span/a/text()`没有class属性的li标签

`//div[contains(@class,'xxx')]/span[last()]/a/text()`class中包含‘xxx’的div下的最后一个span

`//a[text()='下一页']/@href` 文本等于“下一页”的a标签

# 15、html特效：鼠标移动线条汇聚

~~~html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>Examples</title>
    <meta name="description" content="">
    <meta name="keywords" content="">
    <link href="" rel="stylesheet">
</head>
<body>
    <script>
!function(){function n(n,e,t){return n.getAttribute(e)||t}function e(n){return document.getElementsByTagName(n)}function t(){var t=e("script"),o=t.length,i=t[o-1];return{l:o,z:n(i,"zIndex",-1),o:n(i,"opacity",.5),c:n(i,"color","0,0,0"),n:n(i,"count",99)}}function o(){a=m.width=window.innerWidth||document.documentElement.clientWidth||document.body.clientWidth,c=m.height=window.innerHeight||document.documentElement.clientHeight||document.body.clientHeight}function i(){r.clearRect(0,0,a,c);var n,e,t,o,m,l;s.forEach(function(i,x){for(i.x+=i.xa,i.y+=i.ya,i.xa*=i.x>a||i.x<0?-1:1,i.ya*=i.y>c||i.y<0?-1:1,r.fillRect(i.x-.5,i.y-.5,1,1),e=x+1;e<u.length;e++)n=u[e],null!==n.x&&null!==n.y&&(o=i.x-n.x,m=i.y-n.y,l=o*o+m*m,l<n.max&&(n===y&&l>=n.max/2&&(i.x-=.03*o,i.y-=.03*m),t=(n.max-l)/n.max,r.beginPath(),r.lineWidth=t/2,r.strokeStyle="rgba("+d.c+","+(t+.2)+")",r.moveTo(i.x,i.y),r.lineTo(n.x,n.y),r.stroke()))}),x(i)}var a,c,u,m=document.createElement("canvas"),d=t(),l="c_n"+d.l,r=m.getContext("2d"),x=window.requestAnimationFrame||window.webkitRequestAnimationFrame||window.mozRequestAnimationFrame||window.oRequestAnimationFrame||window.msRequestAnimationFrame||function(n){window.setTimeout(n,1e3/45)},w=Math.random,y={x:null,y:null,max:2e4};m.id=l,m.style.cssText="position:fixed;top:0;left:0;z-index:"+d.z+";opacity:"+d.o,e("body")[0].appendChild(m),o(),window.onresize=o,window.onmousemove=function(n){n=n||window.event,y.x=n.clientX,y.y=n.clientY},window.onmouseout=function(){y.x=null,y.y=null};for(var s=[],f=0;d.n>f;f++){var h=w()*a,g=w()*c,v=2*w()-1,p=2*w()-1;s.push({x:h,y:g,xa:v,ya:p,max:6e3})}u=s.concat([y]),setTimeout(function(){i()},100)}();
</script>
</body>
</html>
~~~

# 16、scrapyd+scrapydweb实现 Scrapyd 集群管理

**scrapyd：**

`step1：pip install scrapyd     pip install scrapyd-client`

`step2:修改scrapyd默认配置，使scrapyd可以运行在任意ip。`

`~/.virtualenvs/spider/lib/python3.5/site-packages/scrapyd$ vim default_scrapyd.conf   bind_address = 0.0.0.0`

`step3: 修改scrapy.cfg文件`

~~~python
[settings]
default = sina.settings

[deploy:sina_spider]
url = http://192.168.191.137:6800/
project = sina
~~~

`进入爬虫项目目录，使用命令：scrapyd-deploy sina_spider -p sina 上传爬虫代码`

`step4:查看爬虫状态：curl http://192.168.191.137:6800/daemonstatus.json`

`step5：运行爬虫：curl http://192.168.191.137:6800/schedule.json -d project=sina -d spider=weibo_spider`

**scrapydweb：**

`pip install scrapydweb`

`运行：scrapydweb`

`会自动生成一个scrapydweb_settings.py 文件，修改SCRAPYDWEB_HOST=0.0.0.0`

# 17、读取redis数据库bytes转dict

~~~python
def convert(data):
    if isinstance(data, bytes):
        return data.decode('ascii')
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return map(convert, data)
    return data
~~~

# 18、一行代码

* 一行代码打印99乘法表

  ~~~python
  print('\n'.join([' '.join(['%s*%s=%-2s' % (y, x, x*y) for y in range(1, x+1)]) for x in range(1, 10)]))
  ~~~

* 一行代码输出菲波那切数列

  ~~~python
  print([x[0] for x in [(a[i][0], a.append([a[i][1], a[i][0]+a[i][1]])) for a in ([[1, 1]], ) for i in range(30)]])
  ~~~



# 19、神器

截图：Snipaste

看图：Picasa3

工具：FastStone Capture

# 20、断电下载

* 在以前版本的 HTTP 协议是不支持断点的，HTTP/1.1 开始就支持了。一般断点下载时会用到 header请求头的Range字段，这也是现在众多号称多线程下载工具（如 FlashGet、迅雷等）实现多线程下载的核心所在。
* range是请求资源的部分内容（不包括响应头的大小），单位是byte，即字节，从0开始.
  如果服务器能够正常响应的话，服务器会返回 206 Partial Content 的状态码及说明.
  如果不能处理这种Range的话，就会返回整个资源以及响应状态码为 200 OK .（这个要注意，要分段下载时，要先判断这个）

~~~python
import requests
from tqdm import tqdm
import os


def download_from_url(url, dst):
    response = requests.get(url, stream=True) # 设置stream=True参数读取大文件
    print(response.status_code)
    file_size = int(response.headers['content-length']) # 通过header的content-length属性可以获取文件的总容量。
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst) # 获取本地已经下载的部分文件的容量，方便继续下载，当然需要判断文件是否存在，如果不存在就从头开始下载
    else:
        first_byte = 0
    if first_byte >= file_size: # 本地已下载文件的总容量和网络文件的实际容量进行比较
        return file_size
    header = {"Range": f"bytes={first_byte}-{file_size}"} 
    pbar = tqdm(
                total=file_size, initial=first_byte,
                unit='B', unit_scale=True, desc=dst)
    req = requests.get(url, headers=header, stream=True) # 开始请求视频文件了
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024): #循环读取每次读取一个1024个字节
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size


if __name__ == '__main__':
	url = "https://f.us.sinaimg.cn/003JuhEelx07v8gjXeXS01041200FozD0E010.mp4?label=mp4_720p&template=1280x720.23.0&Expires=1562142855&ssig=B%2BC3%2BWo%2Bh%2F&KID=unistore,video"
	download_from_url(url, "1.mp4")
~~~

断电下载优化，使用aiohttp进行并发下载

~~~python
import aiohttp
import asyncio
import os

from tqdm import tqdm

async def fetch(session, url, dst, pbar=None, headers=None):
    if headers:
        async with session.get(url, headers=headers) as req:
            with(open(dst, 'ab')) as f:
                while True:
                    chunk = await req.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(1024)
            pbar.close()
    else:
        async with session.get(url) as req:
            return req


async def async_download_from_url(url, dst):
    '''异步'''
    async with aiohttp.connector.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            req = await fetch(session, url, dst)

            file_size = int(req.headers['content-length'])
            print(f"获取视频总长度:{file_size}")
            if os.path.exists(dst):
                first_byte = os.path.getsize(dst)
            else:
                first_byte = 0
            if first_byte >= file_size:
                return file_size
            header = {"Range": f"bytes={first_byte}-{file_size}"}
            pbar = tqdm(
                total=file_size, initial=first_byte,
                unit='B', unit_scale=True, desc=dst)
            await fetch(session, url, dst, pbar=pbar, headers=header)

url = "https://f.us.sinaimg.cn/003JuhEelx07v8gjXeXS01041200FozD0E010.mp4?label=mp4_720p&template=1280x720.23.0&Expires=1562142855&ssig=B%2BC3%2BWo%2Bh%2F&KID=unistore,video"
task = [asyncio.ensure_future(async_download_from_url(url, f"{i}.mp4")) for i in range(1, 12)]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(task))
loop.close()
~~~


# 21、Excel数据分析

**excel间隔行取数据方法：**

=OFFSET($A$1,N*(ROW(A1)-1),,)    ---只要改变N值，就能实现间隔N行提取数据。






