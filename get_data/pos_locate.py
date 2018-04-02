# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')
from Base import Base

class PosLocate(Base):
    """
    域名地理位置统计类
    """
    def __init__(self):
        Base.__init__(self)

    def get_domain_numinfo(self,source):
        """
        根据源查询各省份的域名数量，各类域名数量
        :param source: 查询源:注册人地址、注册电话地理、邮编地理、ICP地理、IP地理
        :return: {
            province_1:{
                "非法赌博":数量,
                "色情"：数量,
                "all":总的数量
            },...,province_n:{
                "非法赌博":数量,
                "色情"：数量,
                "all":总的数量
            }
        }
        """
        if source in ['reg_whois', 'reg_phone', 'reg_postal']:
            sql = "select b." + source + "_province,a.dm_type as maltype,count(*) as num from domain_general_list a join domain_locate b on a.domain = b.domain " \
                                         "  where b." + source + "_country='中国' and length(" + source + "_province)!=CHAR_LENGTH(" + source + "_province) group by b." + source + "_province,a.dm_type"
        elif source == 'icp':
            sql = "select b." + source + "_province,a.dm_type as maltype,count(*) as num from domain_general_list a join domain_locate b on a.domain = b.domain " \
                                         "  where  length(" + source + "_province)!=CHAR_LENGTH(" + source + "_province) group by b." + source + "_province,a.dm_type"
        elif source == 'ip':
            sql = "select ip_province,maltype,count(*) as num from domain_ip_relationship " \
                  " where ip_country='中国' and length(ip_province)!=CHAR_LENGTH(ip_province) group by ip_province,maltype"
        else:
            print "无该项查询"
            return []
        sql = sql+' limit 100'
        res = self.mysql_db.query(sql)
        if len(res) != 0:
            results1 = {}

            for rs in res:
                if not results1.has_key(rs[source + '_province']):
                    results1[rs[source + '_province']] = {}
                results1[rs[source + '_province']][rs['maltype']] = rs['num']

            results = []
            for key, value in results1.iteritems():
                gm_ct= value.get("非法赌博".decode('utf8')) if value.get("非法赌博".decode('utf8')) else(0)
                pn_ct = value.get("色情".decode('utf8')) if value.get("色情".decode('utf8')) else(0)
                all_ct = pn_ct + gm_ct
                row = dict(
                    pos = key,
                    porno = pn_ct,
                    gamble = gm_ct,
                    all = all_ct
                )
                results.append(row)
        else:
            results = []

        return self.add_seq_num(results,order_by='all')

    def get_general_bypos(self, source, province):
        """
        查询某源地理位置的某省的域名信息概览
        :param source: 查询源:注册人地址、注册电话地理、邮编地理、ICP地理、IP地理
        :param province: 省份
        :return: {
            num:[非法域名总量，赌博域名数量，色情域名数量],
            res:[
                {
                    domain:域名,
                    dm_type:域名类型,
                    update_time:更新时间,
                    ip :服务ip,
                    ip_geo:ip地理,
                    enter_num:链入站点数量
                },...,{
                    ...
                }
            ]
        }
        """
        if source in ['reg_whois','reg_phone','reg_postal','icp']:
            sql = "select dg.* from domain_general_list dg join domain_locate dw on dg.domain=dw.domain " \
                "where dw." + source +"_province = %s"
            sql = sql + ' limit 100'
            res = self.mysql_db.query(sql,province)
        elif source == 'ip':
            sql = "select a.* from domain_general_list a join domain_ip_relationship b on a.domain = b.domain" \
                  " where b.ip_country='中国' and b.ip_province = %s"
            sql = sql + ' limit 100'
            res = self.mysql_db.query(sql,province)
        else:
            print "无该项查询"
            res = []

        gm_count = 0
        pn_count = 0
        if len(res) != 0:
            results = []
            for rs in res:
                if rs['dm_type'] == '非法赌博'.decode('utf8'):
                    gm_count+=1
                if rs['dm_type'] == '色情'.decode('utf8'):
                    pn_count+=1
                rs =dict(
                    domain = rs['domain'],
                    dm_type = rs['dm_type'],
                    update_time = str(rs['update_time']),
                    ip = rs['IP'],
                    ip_geo = rs['IP_geo'],
                    enter_num = rs['legal_enter_num']+rs['mal_enter_num']
                )
                results.append(rs)
        else:
            results = res
        results = dict(
            res = results,
            num = [gm_count+pn_count,gm_count,pn_count]
        )

        return results

    def check_chinese(self,check_str):
        for ch in check_str.decode('utf8'):
            if not (u'\u4e00' <= ch <= u'\u9fff'):
                return False
        return True

    def get_all_pos(self,domain):
        """
                根据域名查询各个源（注册地址、注册电话地理、邮编地理、ip地理、ICP地理）的地理位置
                :param domain: 查询域名
                :return:result = {
                    reg_whois_src : {src:注册地址,pos:详细地理,province:省份},
                    reg_postal_src : {src:注册地址,pos:详细地理,province:省份},
                    reg_phone_src : {src:注册地址,pos:详细地理,province:省份},
                    auth_icp_src : {src:注册地址,pos:详细地理,province:省份},
                    page_icp_src: {src:注册地址,pos:详细地理,province:省份}
                    ip_src : [{src:注册地址,pos:详细地理,province:省份},{src:注册地址,pos:详细地理,province:省份}...]
                }
        """
        result = dict(
            reg_whois_src ={'src': '', 'pos': '', 'concrete_pos': ''},
            reg_postal_src ={'src': '', 'pos': '', 'concrete_pos': ''},
            reg_phone_src  = {'src': '', 'pos': '', 'concrete_pos': ''},
            auth_icp_src = {'src': '', 'pos': '', 'concrete_pos': ''},
            page_icp_src = {'src': '', 'pos': '', 'concrete_pos': ''},
            ip_src = []
        )
        # 获取whois地理位置信息
        sql = "select country_code,province,city,reg_whois_country,reg_whois_province,reg_whois_city," \
              " postal_code,reg_postal_country,reg_postal_province,reg_postal_city," \
              " reg_phone,reg_phone_country,reg_phone_province,reg_phone_city" \
              "  from domain_locate where domain = %s "
        res = self.mysql_db.get(sql,domain)
        # 获取icp地理位置信息
        sql = "select auth_icp,auth_icp_locate,page_icp,page_icp_locate from domain_icp where domain=%s"
        res2 = self.mysql_db.get(sql, domain)
        res['auth_icp'] = res2['auth_icp']
        res['auth_icp_province'] = res2['auth_icp_locate']
        res['page_icp'] = res2['page_icp']
        res['page_icp_province'] = res2['page_icp_locate']

        if res is not None:
            src = self.None_to_empty(res['country_code'])+'/'+self.None_to_empty(res['province'])+'/'+self.None_to_empty(res['city'])
            pos = ''
            if self.check_chinese(self.None_to_empty(res['reg_whois_country'])):
                pos=pos+self.None_to_empty(res['reg_whois_country'])
            if self.check_chinese(self.None_to_empty(res['reg_whois_province'])):
                pos=pos+self.None_to_empty(res['reg_whois_province'])
            if self.check_chinese(self.None_to_empty(res['reg_whois_city'])):
                pos=pos+self.None_to_empty(res['reg_whois_city'])
            result['reg_whois_src']['src']=src
            result['reg_whois_src']['pos'] = pos
            result['reg_whois_src']['concrete_pos'] = self.None_to_empty(res['reg_whois_province'])

            src = self.None_to_empty(res['postal_code'])
            pos = ''
            if self.check_chinese(self.None_to_empty(res['reg_postal_country'])):
                pos=pos+self.None_to_empty(res['reg_postal_country'])
            if self.check_chinese(self.None_to_empty(res['reg_postal_province'])):
                pos=pos+self.None_to_empty(res['reg_postal_province'])
            if self.check_chinese(self.None_to_empty(res['reg_postal_city'])):
                pos=pos+self.None_to_empty(res['reg_postal_city'])

            result['reg_postal_src']['src']=src
            result['reg_postal_src']['pos'] = pos
            result['reg_postal_src']['concrete_pos'] = self.None_to_empty(res['reg_postal_province'])

            src = self.None_to_empty(res['reg_phone'])
            pos = ''
            if self.check_chinese(self.None_to_empty(res['reg_phone_country'])):
                pos=pos+self.None_to_empty(res['reg_phone_country'])
            if self.check_chinese(self.None_to_empty(res['reg_phone_province'])):
                pos=pos+self.None_to_empty(res['reg_phone_province'])
            if self.check_chinese(self.None_to_empty(res['reg_phone_city'])):
                pos=pos+self.None_to_empty(res['reg_phone_city'])
            result['reg_phone_src']['src']=src
            result['reg_phone_src']['pos'] = pos
            result['reg_phone_src']['concrete_pos'] = self.None_to_empty(res['reg_phone_province'])

            # auth_icp 的处理
            result['auth_icp_src']['src']=self.None_to_empty(res['auth_icp'])
            if self.check_chinese(self.None_to_empty(res['auth_icp_province'])):
                result['auth_icp_src']['pos']=self.None_to_empty(res['auth_icp_province'])
            else:
                result['auth_icp_src']['pos'] = ''
            result['auth_icp_src']['concrete_pos'] = result['auth_icp_src']['pos']
            # page_icp 的处理
            result['page_icp_src']['src']=self.None_to_empty(res['page_icp'])
            if self.check_chinese(self.None_to_empty(res['page_icp_province'])):
                result['page_icp_src']['pos']=self.None_to_empty(res['page_icp_province'])
            else:
                result['page_icp_src']['pos'] = ''
            result['page_icp_src']['concrete_pos'] = result['page_icp_src']['pos']

        sql = "select ip,ip_country,ip_province from domain_ip_relationship where domain = %s;"
        res = self.mysql_db.query(sql,domain)
        if res:
            for item in res:
                temp_dict = {}
                temp_dict['src'] = item['ip']
                pos = ''
                if self.check_chinese(self.None_to_empty(item['ip_country'])):
                    pos=pos+self.None_to_empty(item['ip_country'])
                if self.check_chinese(self.None_to_empty(item['ip_province'])):
                     pos=pos+self.None_to_empty(item['ip_province'])
                temp_dict['pos'] = pos
                temp_dict['concrete_pos'] = self.None_to_empty(item['ip_province'])
                result['ip_src'].append(temp_dict)

        return result

if __name__ == "__main__":
    pl =PosLocate()
    # print pl.get_domain_numinfo('reg_whois')
    # print pl.get_domain_numinfo('icp')
    # print pl.get_domain_numinfo('ip')
    # print pl.get_general_bypos('reg_whois', '山东')
    # print pl.get_general_bypos('reg_whois','山东')
    # print pl.get_general_bypos('reg_phone', '山东')
    # print pl.get_general_bypos('reg_postal', '山东')
    # print pl.get_general_bypos('icp', '山东')
    # print pl.get_general_bypos('ip', '台湾')
    # print pl.get_all_pos('000000.in')
    print pl.get_all_pos('00-3.com')
    # result = []
    # mapType = [
    #     '广东', '青海', '四川', '海南', '陕西',
    #     '甘肃', '云南', '湖南', '湖北', '黑龙江',
    #     '贵州', '山东', '江西', '河南', '河北',
    #     '山西', '安徽', '福建', '浙江', '江苏',
    #     '吉林', '辽宁', '台湾',
    #     '新疆', '广西', '宁夏', '内蒙古', '西藏',
    #     '北京', '天津', '上海', '重庆',
    #     '香港', '澳门'
    # ]
    # for value in res.values():
    #     if value.has_key('concrete_pos') is True:
    #         if value['concrete_pos'] != "":
    #             if value['concrete_pos'] in mapType:
    #                 row = dict(
    #                     name=value['concrete_pos'],
    #                     value=1
    #                 )
    #                 result.append(row)
    # print "lallal"
    # print result
