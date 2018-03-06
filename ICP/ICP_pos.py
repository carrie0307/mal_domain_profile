# -*- coding: utf-8 -*-

"""
icp地理位置定位
"""
import pickle
import sys
reload(sys)
sys.setdefaultencoding('utf8')

with open('icp_locate_map.pkl', 'rb') as f:
    icp_locate_map = pickle.load(f)

def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

def enable_locate(icp):

    if len(icp)<3:
        return None
    else:
        icp = icp.decode('utf8')
        icp_locate = icp[:1]
        if is_chinese(icp_locate):
            return icp_locate
        else:
            return None

def get_icp_pos(icp):
    icp_locate = enable_locate(icp)
    if icp_locate:
        if icp_locate.encode('utf8') in icp_locate_map.keys():
            icp_locate = icp_locate_map[icp_locate.encode('utf8')]['province'].replace('省', '').replace('市', ''). \
                replace('自治区', '').replace('回族自治区', '').replace('维吾尔自治区', '').replace('壮族自治区', '').replace('特别行政区','')
    return icp_locate

if __name__ == "__main__":
    icp = '粤ICP备07045392号-1'
    print get_icp_pos(icp)
