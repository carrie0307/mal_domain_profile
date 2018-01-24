# encoding:utf-8
"""
    功能：初始化导入空数据和表结构
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')

[u'0000.tv', u'000-973.com', u'000-m47.com', u'00-91.com', u'000-webhost.com', u'000000.in', u'0000008.com', u'00-3.com', u'000000.com', u'000-078-japan.com']

def diff_list(list1,list2):
    '''
    功能：求两个列表差集(list1有但list2没有的元素)
    '''
    retD = list(set(list1).difference(set(list2)))
    return retD


sql = "SELECT domain FROM domain_index;"
fetch_data = mysql_conn.exec_readsql(sql)
all_domains = []
for item in fetch_data:
    all_domains.append(item[0])

has_domains = []
fetch_data = mongo_conn.mongo_read('domain_conn_dm_test',{},{'source_domain':True,'_id':False,},limit_num=None)
for item in fetch_data:
    has_domains.append(item['source_domain'])


new_domains = diff_list(all_domains,has_domains)
print new_domains
print len(new_domains)
documents = []
for domain in new_domains:
    single_document = {'source_domain':domain,
    'ip_domains':{'domains':[],'reg_info':[]},
    'cname_domains':{'domains':[],'reg_info':[]},
    'reg_email_domainn':{'conn':'','domains':[],'reg_info':[]},
    'reg_phone_domainn':{'conn':'','domains':[],'reg_info':[]},
    'reg_name_domainn':{'conn':'','domains':[],'reg_info':[]},
    'links_domains':{'domains':[],'reg_info':[]},
    'visit_times':0
    }
    documents.append(single_document)
#
#
mongo_conn.mongo_insert('domain_conn_dm_test',documents)
