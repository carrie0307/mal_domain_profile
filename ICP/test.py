# coding=utf-8
import requests
import re
from pymongo import *
'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.taiyuan_all_icp
# collection.update({'domain': 'www.168168cc.com'}, {'$set': {'page_icp':{'icp':'', 'exact_unique':0, 'vague_unique':0}}})
res = collection.find({'auth_icp.icp':{'$ne':'--'}},{'domain':True, 'auth_icp.icp':True})
# res = collection.distinct('auth_icp.icp')
province_dict = {}
for item in res:
    if u'晋' not in item['auth_icp']['icp']:
        try:
            province = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u5907][\d]+[\u53f7]*-*[\d]*').findall(item['auth_icp']['icp'])[0]
            province_dict[province] = province_dict.get(province, 0) + 1
            # print province
        except:
            print '--'
            print item['domain'],item['auth_icp']['icp']
province_dict = sorted(province_dict.iteritems(),key = lambda asd:asd[1],reverse = True)
print province_dict
for key in province_dict:
    print key[0], key[1]
'''

# for item in res:
    # if item['page_icp']['icp'] != '--' and item['page_icp']['icp'] != '-1' and item['page_icp']['exact_unique'] == 0:
     #    print item['domain'], item['page_icp']['icp']
'''
client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.domain_icp_info3
collection.update({'page_icp.icp':{'$ne':''}, 'page_icp.exact_unique':{'$ne':0}, 'page_icp.vague_unique':{'$ne':0}}, {'$set': {'page_icp':{'icp':'', 'exact_unique':0, 'vague_unique':0}}},multi=True)
'''
'''
res = collection.find({'page_icp':{'$ne':''}},{'page_icp':True, 'auth_icp':True, 'domain':True, '_id':False})
for item in list(res):
    # if item['page_icp'] != '--' and item['page_icp'] != '-1':
        # print item['domain'], item['auth_icp'], item['page_icp']
    # if u'ICP证' in item['page_icp'] or u'ICP证' in item['auth_icp']:
        # print item['domain'], item['auth_icp'], item['page_icp']
        # collection.update({'domain': item['domain']}, {'$set': {'page_icp':''}})
    if u'ICP证' in item['auth_icp']:
        print item['domain'], item['auth_icp'], item['page_icp']
        # collection.update({'domain': item['domain']}, {'$set': {'page_icp':''}})
'''


'''
# 港ICP证030577号、港ICP证0188188 等转化为030577、0188188
# 将“沪ICP备09091848号-1”格式类型，全部转化为0909184
icp1 = u'港ICP证030577号1'
if u'ICP证' in icp1:
    icp1 = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u8bc1]([\d]+)').findall(icp1)[0]
else:
    icp1 = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(icp1)[0]
icp1 =  ''.join(list(icp1))
icp2 = u'港ICP证030577号1'
if u'ICP证' in icp2:
    icp2 = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u8bc1]([\d]+)').findall(icp2)[0]
else:
    icp2 = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(icp2)[0]
icp2 =  ''.join(list(icp2))
if icp1 == icp2:
    print 'ok'
# if u'ICP证' in item['page_icp']:
#     page_icp = re.compile(u'ICP[\u8bc1]([\d]+)').findall(item['page_icp'])[0]
# else:
#     page_icp = re.compile(u'[\u4e00-\u9fa5]{0,1}ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(item['page_icp'])[0]
'''


pattern3 = re.compile(u'([\u4e00-\u9fa5]{0,1}[A-B][1-2]-[\d]{6,8}-*[\d]*)').findall(u'ICP证&nbsp;桂B2-20040022')
print pattern3[0]
#
pattern3 = re.compile(u'([\u4e00-\u9fa5]{0,1})[A-B][1-2]-([\d]{6,8})-*[\d]*').findall(u'ICP证&nbsp;桂B2-20040022')
print pattern3[0][0] + pattern3[0][1]
