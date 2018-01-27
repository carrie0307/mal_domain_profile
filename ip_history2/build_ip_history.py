# encoding:utf-8
'''
    功能：根据对域名进行轮询解析的结果，填充ip历史信息表
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..") # 回退到上一级目录
import database.mongo_operation
import database.mysql_operation
mongo_conn = database.mongo_operation.MongoConn('172.29.152.151','mal_domain_profile')
mysql_conn = database.mysql_operation.MysqlConn('172.26.253.3','root','platform','mal_domain_profile','utf8')
import time

# 先取出一个域名的所有ip记录
# 检查是否有num位（num表所ip数量，这里也用这一位来标志是否进行过历史记录比对）
# 将这一次的数据与前一次的比对，若有变化，则change+=1,并记录new,cut;
# 不论是否有变化，都根据ip数量置num的值
# for ip in new:
#     addtoset {ip:---,'cidr':---} # 如果此次新增的ip以前已经记录过其对应的ip-cidr，则addtoset会自动去重


def diff_list(list1,list2):
    '''
    功能：求两个列表差集(list1有但list2没有的元素)
    '''
    retD = list(set(list1).difference(set(list2)))
    return retD
