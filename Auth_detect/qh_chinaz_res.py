# encoding:utf-8
"""
    通过站长之家获得奇虎360对网站的检测结果
"""
import requests
from selenium import webdriver
import ip
import re
import time
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

def request_res(domain,proxy):
    global headers
    url = 'http://tool.chinaz.com/webscan?host=' + domain
    # page_html = urllib2.urlopen(url).read()
    page_html = requests.get(url,proxies=proxy,timeout=5).content
    return page_html
    # print page_html


def get_auth_res(page_html):
    """
    从页面中提取原始的结果记录
    """
    if "excessive number of calls" in page_html:
        return "访问过多"
    elif "被屏蔽的域名" in page_html:
        return "被屏蔽的域名"
    else:
        js_res = re.compile(r'var str = ({"state":1,.+?});').findall(page_html)
        if js_res:
            auth_res = js_res[0]
            auth_res_dict = eval(auth_res.replace('null',"'NULL'"))
            return auth_res_dict
        else:
            print '----'


def get_detect_deteil(auth_res_dict):
    if not isinstance(auth_res_dict,dict):
        return auth_res_dict
    else:
        auth_detect_res = ''
        if auth_res_dict['webstate'] == '0':
            # 安全的情况
            auth_detect_res = unicode2zh(auth_res_dict['msg'])
        else:
            # 不安全的情况
            detail_res = '-'
            auth_detect_res = unicode2zh(auth_res_dict['msg'])
            for key in auth_res_dict['data']:
                # ['guama','pangzhu','cuangai','xujia','violation','google','loudong','score']
                # 获取具体的恶意评价
                if key == 'loudong':
                    # TODO：这里是NULL还是0要再看看一下
                    if auth_res_dict['data']['loudong']['high'] != 'NULL':
                        detail_res += '高危漏洞'
                        break
                    elif auth_res_dict['data']['loudong']['mid'] != 'NULL':
                        detail_res += '中危漏洞'
                        break
                    elif auth_res_dict['data']['loudong']['low'] != 'NULL':
                        detail_res += '低危漏洞'
                        break
                elif key != 'score' and auth_res_dict['data'][key]['level'] == 1:
                    if key == 'guama':
                        detail_res += '挂马'
                        break
                    elif key == 'pangzhu':
                        detail_res += '旁注'
                        break
                    elif key == 'cuangai':
                        detail_res += '篡改'
                        break
                    elif key == 'xujia':
                        detail_res += '虚假'
                        break
                    elif key == 'violation':
                        detail_res += '违规'
                        break
                    elif key == 'google':
                        detail_res += 'Google屏蔽'
                        break
        if detail_res != '-':
            auth_detect_res += detail_res
        return auth_detect_res



def unicode2zh(unicode_str):
    return unicode_str.decode('unicode_escape')



if __name__ == '__main__':
    # ip.run_Getter()
    # time.sleep(20) # 这个时间很关键，这段时间用来从各平台上获取代理ip
    # ip.ip_Verify() # ip可用性验证
    # time.sleep(60) # 验证以获得足够的IP
    # watcher = threading.Thread(target=ip.ip_watcher) # 可用ip数量监测
    # watcher.setDaemon(True)
    # watcher.start()
    # # #
    # domains = ['baidu.com','taobao.com','1688.com','sohu.com','520820.com','bqmr.info','ked3.com','0-360c.com']
    # # domains = ['qq.com']
    # for domain in domains:
    #     proxy = ip.available_IP_q.get()
    #     print proxy
    #     try:
    #         probe = requests.get('http://myip.ipip.net',proxies=proxy,timeout=5).content
    #         print probe.strip()
    #         page_html = request_res(domain,proxy)
    #         auth_res_dict = get_auth_res(page_html)
    #         domain_res = get_detect_deteil(auth_res_dict)
    #         print domain,domain_res
    #     except:
    #        pass

        # driver = webdriver.PhantomJS(executable_path="/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
        # url = 'http://tool.chinaz.com/webscan?host=' + domain
        # driver.get(url)
        # page = driver.page_source
        # with open('test.txt','w') as f:
        #     f.write(page)
        # with open('copy.txt','r') as f:
        #     page = f.read()
        # auth_res_dict = get_auth_res(page)
        # domain_res = get_detect_deteil(auth_res_dict)
        # print domain,domain_res

        # if not auth_res_dict:
        #     print domain,'被屏蔽的域名'
        #     continue
        # auth_detect_res = ''
        # if auth_res_dict['webstate'] == '0':
        #     # 安全的情况
        #     auth_detect_res = unicode2zh(auth_res_dict['msg'])
        # else:
        #     # 不安全的情况
        #     detail_res = '-'
        #     auth_detect_res = unicode2zh(auth_res['msg'])
        #     for key in auth_res_dict['data']:
        #         # ['guama','pangzhu','cuangai','xujia','violation','google','loudong','score']
        #         # 获取具体的恶意评价
        #         if key == 'loudong':
        #             if auth_res_dict['data']['loudong']['high'] != '0':
        #                 detail_res = '高危漏洞'
        #             elif auth_res_dict['data']['loudong']['mid'] != '0':
        #                 detail_res += '中危漏洞'
        #             elif auth_res_dict['data']['loudong']['low'] != '0':
        #                 detail_res += '低危漏洞'
        #         elif auth_res_dict['data'][key]['level'] == 1 and key != 'score':
        #             if key == 'guama':
        #                 detail_res += '挂马'
        #             elif key == 'pangzhu':
        #                 detail_res += '旁注'
        #             elif key == 'cuangai':
        #                 detail_res += '篡改'
        #             elif key == 'xujia':
        #                 detail_res += '虚假'
        #             elif key == 'violation':
        #                 detail_res += '违规'
        #             elif key == 'google':
        #                 detail_res += 'Google屏蔽'
        #         else:
        #             detail_res = ''
        # auth_detect_res += detail_res
        # print domain,auth_detect_res




    # for domain in domains:
    #     url = 'http://tool.chinaz.com/webscan?host=' + domain
    #     driver = webdriver.PhantomJS(executable_path="/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
    #     driver.get(url)
    #     page = driver.page_source
    #     if '被屏蔽的域名' in page:
    #         print domain,'被屏蔽的域名'
    #     if 'var str' in page:
    #         print domain, 'normal...'
    # driver.close()
    # driver.quit()
