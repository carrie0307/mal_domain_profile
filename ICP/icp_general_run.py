# coding=utf-8

import ICP_pos
import ip
import Queue
import threading
import requests
import chardet
import urllib2
import datetime
import re
import time
import sys
sys.path.append("..") # 回退到上一级目录
import database.mysql_operation

'''同步队列'''
domain_q = Queue.Queue()
dm_page_icp_q = Queue.Queue()
res_q = Queue.Queue()


'''数据库连接'''
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

'''线程数量'''
thread_num = 10


def get_domains():
    '''
    功能:从数据库中读取未获取权威icp信息的域名，添加入域名队列
    '''
    global mysql_conn
    # sql = "SELECT domain FROM domain_icp WHERE flag = 0;"
    sql = "SELECT domain FROM domain_icp_copy WHERE flag = 1;"
    fetch_data = mysql_conn.exec_readsql(sql)
    if fetch_data == False:
        print "获取数据有误..."
        return False
    for domain in fetch_data:
        domain_q.put(domain[0])



def get_chinaz_icp_info():
    '''
    功能： 从站长之家获取包含域名icp信息的原始页面（注意由于被ban的问题，添加了获取代理），将html页面添加入队列
    '''
    global domain_q
    global dm_page_icp_q

    proxy = ip.available_IP_q.get() # 获取一个代理
    while not domain_q.empty():
        domain = domain_q.get()
        try:
            url = 'http://icp.chinaz.com/{query_domain}'.format(query_domain=domain)
            html = requests.get(url, proxies = proxy, timeout=5).text
        except Exception, e: # 其他异常
            if "Connection" in str(e):
                domain_q.put(domain) # 被ban导致的获取失败，将域名加入队列，重新获取
                proxy = ip.available_IP_q.get()
                continue
            else:
                print str(e)
                print domain + "获取html异常"
                continue
        # 进行处理获取icp内容内容
        icp = get_icp_info(html)
        if icp:
            # icp地理位置解析
            locate = ICP_pos.get_icp_pos(icp) if icp != '--' else ''
            dm_page_icp_q.put([domain,icp,locate])
        else:
            # 提取失败（可能是页面获取有误导致）的重新获取页面
            domain_q.put(domain)
    print '权威icp获取完成...'


def get_icp_info(html):
    '''
    功能： 提取chinaz页面的icp信息

    '''
    if "<h2>404" in html:
        #获取icp异常 eg. www.365bet.cd的查询结果
        icp = '--'
        return icp
    try:
        content = re.compile(r'<p><font>(.+?)</font>').findall(html)
        if content == []:
            content = re.compile(r'<p class="tc col-red fz18 YaHei pb20">([^<]+?)<a href="javascript:" class="updateByVcode">').findall(html)
        icp = content[0]
        if icp == u"未备案或者备案取消，获取最新数据请":
            icp = '--'
        return icp
    except:
        # TODO:这里加一个处理
        return ''
        print "chinaz页面提取icp异常..."


# urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
def pre_deal_html(req):
    '''
    功能：urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
    '''
    info = req.info()
    content = req.read()
    encoding = info.getheader('Content-Encoding')
    if encoding == 'gzip':
        buf = StringIO(content)
        gf = gzip.GzipFile(fileobj=buf)
        content = gf.read()
    charset = chardet.detect(content)['encoding']
    if charset != 'utf-8' and charset != None:
        content = content.decode(charset, 'ignore')
    return content


def get_page_icp_info():
    '''
    功能：获取网页源代码，添加入html队列

    注： 页面无法访问的，置icp信息为-1
    '''
    global dm_page_icp_q
    global res_q

    while True:
        try:
            domain,auth_icp,locate = dm_page_icp_q.get(timeout=200)
            url = 'http://www.' + domain
        except Queue.Empty:
            break
            print '页面icp获取完成...'
        try:
            resp = urllib2.urlopen(url,timeout=20)
            html = pre_deal_html(resp) # 处理编码
            code = resp.code
            # 从页面提取icp
            page_icp = get_page_icp(html)
        except urllib2.HTTPError, e:
            code = e.code
            page_icp = '-1'
        except Exception, e:
            code = 'ERROR'
            page_icp = '-1'
        finally:
            print domain,auth_icp,locate,page_icp,code
            res_q.put([domain,auth_icp,locate,page_icp,code])
    print 'download over ...'


def get_page_icp(html):
    '''
    功能：获取页面上的icp信息，分三种情况进行处理：
        pattern1: 备案：粤ICP备11007122号-2 (500.com)
        pattern2: 京ICP证 030247号 (icbc) 360soulou.com 豫ICP证041518号
        pattern2: 京ICP证000007 (sina) (这个可能提取会有误)
        pattern3: 粤B2-20090059-111 (qq.com) （增值营业号）
    '''
    try:
        pattern1 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u5907][\d]{6,8}[\u53f7]*-*[\d]*)').findall(html)
        if pattern1 != []:
            icp = pattern1[0]
        else:
            pattern2 = re.compile(u'([\u4e00-\u9fa5]{0,1}ICP[\u8bc1].*[\d]{6,8}[\u53f7])').findall(html)
            if pattern2 != []:
                icp = pattern2[0]
            # 增值业务营业号
            else:
                pattern3 = re.compile(u'([\u4e00-\u9fa5]{0,1}[A-B][1-2]-[\d]{6,8}-*[\d]*)').findall(html)
                if pattern3 != []:
                    icp = pattern3[0]
                else:
                    icp = '--'
        if icp == '':
            icp = '--'
        return icp
    except:
        return ''
        print domain + "get icp WRONG\n"


def mysql_save_icp():

    global res_q
    counter = 0

    while True:
        try:
            domain,auth_icp,locate,page_icp,code = res_q.get(timeout=400)
        except Queue.Empty:
            break
            print '存储结束'
        insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "UPDATE domain_icp_copy\
              SET auth_icp = '%s',icp_locate = '%s',page_icp = '%s',http_code = '%s',get_icp_time = '%s',flag = flag + 1\
              WHERE domain = '%s';" %(auth_icp,locate,page_icp,code,insert_time,domain)
        exec_res = mysql_conn.exec_cudsql(sql)
        if exec_res:
            counter += 1
            print "counter:" + str(counter)
            if counter == 100:
                mysql_conn.commit()
                counter = 0
    mysql_conn.commit()
    print "存储完成... "





if __name__ == '__main__':
    global mysql_conn
    ip.run_Getter()
    time.sleep(20) # 这个时间很关键，这段时间用来从各平台上获取代理ip
    ip.ip_Verify() # ip可用性验证
    time.sleep(90) # 验证以获得足够的IP
    watcher = threading.Thread(target=ip.ip_watcher) # 可用ip数量监测
    watcher.setDaemon(True)
    watcher.start()
    '''开始icp批量获取'''
    get_domains()
    get_chinaz_icp_td = []
    for _ in range(thread_num):
        get_chinaz_icp_td.append(threading.Thread(target=get_chinaz_icp_info))
    print '开始获取权威icp信息...'
    for td in get_chinaz_icp_td:
        td.start()
    time.sleep(10)
    get_page_icp_td = []
    for _ in range(thread_num):
        get_page_icp_td.append(threading.Thread(target=get_page_icp_info))
    print '开始获取页面icp信息...'
    for page_td in get_page_icp_td:
        page_td.start()
    print '开始存储icp信息...\n'
    save_db_td = threading.Thread(target=mysql_save_icp)
    save_db_td.start()
    save_db_td.join()
    mysql_conn.close_db()
