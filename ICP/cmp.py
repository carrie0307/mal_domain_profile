# coding=utf-8
'''
    功能： 站长之家所得icp与页面所得icp的一致性比对

    注意： 运行时修改'collection = db.taiyuan_part_icp' 选择不同表中的域名获取

'''
from pymongo import *
import re
import icp_num

'''
最终遗留的几个特殊格式，但未影响比较结果

www.qipaishequ.com -- ICP证&nbsp;桂B2-20040022
www.ihuaerjie.com -- ICP证&nbsp;桂B2-20040022


www.zqsjbzlk.com -- 京ICP证号京ICP备号京公网安备11010702000014
www.lzljluchun.com.cn -- ICP证：粤B2-20100355

www.ihuaerjie.com ICP证 桂B2-20040022
www.ourloto.com -- ICP证 桂B2-20040022
'''


client = MongoClient('172.29.152.152', 27017)
db = client.domain_icp_analysis
collection = db.taiyuan_part_icp


def get_domain_icp():
    '''
    功能： 从数据库读取页面和权威的icp信息
    '''
    global collection
    global domain_q
    res = collection.find({'cmp':0},{'auth_icp':True, 'page_icp':True })
    return list(res)


def cmp_icp(domain_icp_list):
    '''
    功能： auth_icp.icp 与 page_icp.icp 的比对
    '''
    global collection
    cmp_res = []
    for item in domain_icp_list:
        if item['auth_icp']['icp'] == '--' and item['page_icp']['icp'] == '--':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':1}})
        elif item['auth_icp']['icp'] == '--' and item['page_icp']['icp'] != '--':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':2}})
        elif item['auth_icp']['icp'] != '--' and item['page_icp']['icp'] == '--':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':3}})
        elif item['auth_icp']['icp'] == '--' and item['page_icp']['icp'] == '-1':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':-1}})
        elif item['auth_icp']['icp'] != '--' and item['page_icp']['icp'] == '-1':
            collection.update({'_id': item['_id']}, {'$set': {'cmp':-2}})
        else:
            # 港ICP证030577号、港ICP证0188188 等转化为港030577、港0188188
            # 将“沪ICP备09091848号-1”格式类型，全部转化为沪0909184
            # 读出的字符本身就算unicode，因此不必转换
            auth_icp = icp_num.get_icp_num(item['auth_icp']['icp']) # #形如港030577（省份 + 主编号）
            page_icp = icp_num.get_icp_num(item['page_icp']['icp']) # #形如港030577（省份 + 主编号）
            if auth_icp == page_icp:
                collection.update({'_id': item['_id']}, {'$set': {'cmp':4}})
            else:
                collection.update({'_id': item['_id']}, {'$set': {'cmp':5}})




if __name__ == '__main__':
    domain_icp_list = get_domain_icp()
    cmp_icp(domain_icp_list)
    # print 'com over ...'
    # icp = u'沪ICP备09091848号-1'
    # auth_icp_1 = re.compile(u'[\u4e00-\u9fa5]{0,1}ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(icp)[0]
    # print auth_icp_1
    # www.trxqw.cn -- 京ICP证120511&#12288;京公网安备 11010802020321
    # www.dhxqw.cn -- 京ICP证120511&#12288;京公网安备 11010802020321
    # 港ICP证030577号
    # 港ICP证0188188
    # icp = u'京ICP证060962号-1'
    # page_icp = re.compile(u'ICP[\u8bc1]([\d]+)').findall(icp)[0]
    # print page_icp
