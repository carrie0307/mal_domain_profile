# coding=utf-8
from pymongo import *
'''
将原始的domain转移到icp表中
'''


client = MongoClient('172.29.152.152', 27017)

def get_ip_domains():
    """
    从ip库中获取原始的域名
    :return: 域名列表
    """
    db = client.eds_last
    collection = db.taiyuan_all_icp
    # 通过find的第二个参数来指定返回的键
    res = collection.find({},{'domain': True, '_id':False })
    domains = [str(domain['domain']) for domain in list(res)]
    return domains


def transfer_domains(domains):
    """
    将域名和document的原始构造插入表中
    :param domains: 原始的域名列表
    :return: 域名列表
    """
    db = client.domain_icp_analysis
    collection = db.taiyuan_part_icp
    domain_documents = [{'domain':domain, 'auth_icp':{'icp':'', 'exact_unique':0, 'vague_unique':0}, 'page_icp':{'icp':'', 'exact_unique':0, 'vague_unique':0}, 'cmp':0} for domain in domains]
    collection.insert_many(domain_documents)
    print 'insert over ... '


def strip_fun(string):
    return string.strip()





if __name__ == '__main__':
    # domains = get_ip_domains()
    r_file = open('taiyuan_part.txt', 'r')
    domains = []
    content = r_file.read()
    domains = map(strip_fun,content.split('\n'))
    r_file.close()
    transfer_domains(domains)
