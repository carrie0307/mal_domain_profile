# coding:utf-8
import requests
from selenium import webdriver
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

domain = '520820.com'
# 需要用无头浏览器
headers = { 'Host':'webscan.360.cn',
            'Connection':'keep-alive',
            'Cache-Control':'max-age=0',
            'Accept': 'text/html, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
            'Accept-Encoding': 'deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
}

# domain = '520820.com'
# url = 'http://webscan.360.cn/index/checkwebsite?url=' + domain
# page_html = requests.get(url,headers=headers).content
# with open('360 request.txt','w') as f:
#     f.write(page_html)


# domain = '1kapp.com'
# # driver = webdriver.PhantomJS(executable_path="/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
# driver = webdriver.PhantomJS(executable_path="/home/carrie/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
# url = 'https://guanjia.qq.com/online_server/result.html?url' + domain
# # url = 'http://webscan.360.cn/index/checkwebsite?url=' + domain
# driver.get(url)
# page = driver.page_source
#
# print page
# qq_judge = re.compile(r'<span class="loading_score .+?">(.+?)</span>').findall(page)
# if qq_judge: # 未提取到的可能是页面未加载完全，先不存储
#     qq_judge_res = qq_judge[0]
#     qq_judge_res.replace('&nbsp','--')
#     print qq_judge_res
#
# driver.close()
# driver.quit()

#coding=utf-8
import os

import time

from scrapy.selector import HtmlXPathSelector
from scrapy.http import HtmlResponse
from selenium.webdriver.common.proxy import ProxyType
from lxml import etree

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import warnings
warnings.filterwarnings("ignore")


PATH_PHANTOMJS='/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
browser=webdriver.PhantomJS(PATH_PHANTOMJS)

#代理ip
proxy=webdriver.Proxy()
proxy.proxy_type=ProxyType.MANUAL
proxy.http_proxy='118.193.107.92:80'
#将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
browser.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
print '---'

url = 'http://myip.ipip.net'
browser.get(url)

source_code = browser.page_source
print source_code


# url = 'http://webscan.360.cn/index/checkwebsite?url=' + domain
# browser.get(url)
# time.sleep(1)
# page = etree.HTML(source_code)
# # # print source_code
# res = page.xpath('//*[@id="jg_tips"]/text()')
# if res:
#     print domain,res[0]
# elif '访问网站方式太像一个机器人' in str(source_code):
#     print '访问网站方式太像一个机器人'
# print '===='
browser.quit()
