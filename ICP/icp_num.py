# coding=utf-8
import re
'''
    功能： icp格式转化函数
'''


def get_icp_num(icp):
    '''
    将icp转化为形如港030577（省份 + 主编号）
    '''
    if u'ICP证' in icp:
        icp_num = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u8bc1]([\d]+)').findall(icp)
    else:
        icp_num = re.compile(u'([\u4e00-\u9fa5]{0,1})ICP[\u5907]([\d]+)[\u53f7]*-*[\d]*').findall(icp)
    if icp_num != []:#除cmp列出特殊的几个，ICP匹配完毕
        icp = ''.join(list(icp_num[0])) #形如港030577（省份 + 主编号）
        return icp
    else:
        # 先匹配营业号 粤B2-20090059-111
        icp_num = re.compile(u'([\u4e00-\u9fa5]{0,1})[A-B][1-2]-([\d]{6,8})-*[\d]*').findall(icp)
        if icp_num != []:
            icp = ''.join(list(icp_num[0]))
            return icp
        else:
            return icp #提取失败的，返回原icp


if __name__ == '__main__':
    print get_icp_num(u'京ICP证030247号')
