# coding:utf-8
import requests
from selenium import webdriver
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


domain = 'baidu.com'
driver = webdriver.PhantomJS(executable_path="/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
url = 'https://guanjia.qq.com/online_server/result.html?url' + domain
# url = 'http://webscan.360.cn/index/checkwebsite?url=' + domain
driver.get(url)
page = driver.page_source
with open('qq_res_phan.txt','w') as f:
    f.write(page)
driver.close()
driver.quit()

# 360
# <div class="jg_conlist" style="display: block;">
#     <dl>
#      <dt>安全级别<span id="jg_tips" class="jg_dangerous">高危</span></dt>
#     </dl>
#     <div class="jg_tb"><img id="query" src="/img/zhiming.png?v=1"></div>
# </div>
