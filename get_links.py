# encoding:utf-8
"""
    获取页面内外链代码
"""
from bs4 import BeautifulSoup
from urllib2 import HTTPError,URLError
from urlparse import urljoin,urlparse
from mongo_operation import MongoConn
import tldextract
import urllib2
import re
import chardet

class Get_links(object):

    def __init__(self,*args,**kwargs):
        """port
        initialize database connection
        :param sqlcon: dbconnect instance
        :param domains: domain set
        """
        self.url_mode = re.compile(r'((http|ftp|https)://)([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]\.){1,4}[a-zA-Z]{2,6}')
        self.filter_url_mode = re.compile(r'(.jpg)|(.png)|(.gif)|(.js)|(.css)|(.ico)|(.exe)|(.apk)')
        self.domain_mode = re.compile(r'([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]\.){1,4}[a-zA-Z]{2,6}')
        self.info = {}
        self.count = 0


    def send_request(self,cur_domain):
        """
        send http request
        :param cur_domain: visit domain
        :return: response
        """
        response = None
        current_url = 'http://www.'+tldextract.extract(cur_domain).registered_domain
        try:
            response = urllib2.urlopen(current_url,timeout=30)
            self.info['http_code'] = response.getcode()
        except HTTPError,e:
            self.info['http_code'] = e.code
            print '{0}:{1}'.format('httperror-1',e)
        except URLError,e:
            print '{0}:{1}'.format('urlerror-2', e)
            self.info['error'] =  e.reason
            if str(e).find('timed out')!=-1:
                self.info['timeout_flag'] = 1
            else:
                self.info['timeout_flag'] = 2
        except Exception,e:
            self.info['error'] = e
        else:
            domain = tldextract.extract(response.url).registered_domain
            if domain!=cur_domain:
                self.info['redirect_domain'] = domain
                self.info['redirect_flag'] = 1
        return response


    def decode_str(self,response):
        """
        对获取到的信息进行解码
        """
        try:
            page_source = response.read()
            # print page_source
        except Exception,e:
            print '{0}:{1}'.format('parse error',e)
            return None
        information = response.info()
        encode_type = information.getheader('Content-Encoding')
        if encode_type == 'gzip':
            buf = StringIO(page_source)
            gf = gzip.GzipFile(fileobj=buf)
            page_source = gf.read()
        else:
            encode_type = chardet.detect(page_source)['encoding']
            if encode_type:
                self.info['encode_type'] = encode_type
                decode_type = self.select_decode_type(encode_type)
                page_source = page_source.decode(decode_type, 'ignore')

        return page_source


    def select_decode_type(self,encode_type):

        if encode_type.find('utf-8')!=-1 or encode_type.find('UTF-8')!=-1 :
            decode_type = 'utf-8'
        elif encode_type.find('UTF-16')!=-1 :
            decode_type = 'utf-16'
        elif encode_type in ['GB2312','gb2312','gbk','GBK','GB18030','gb18030']:
            decode_type = 'gb18030'
        else:
            decode_type = encode_type

        return decode_type


    def deal_response(self,response):
        """
        返回soup
        """
        page_source = self.decode_str(response)
        if page_source is not None:
            soup = BeautifulSoup(page_source,'lxml')
        else:
            soup = None
        return soup


    def divide_urls(self,links, domain):
        """
        正则匹配出规范的内外链及域名
        :param links: 所有可能的连接
        :return: 内链，外链，外链域名(关联域名)
        """
        if len(links) == 0: return ([], [])
        base_url = "http://www." + domain
        inter_urls = set()
        outer_urls = set()
        for link in links:
            filtered_gp = re.search(self.filter_url_mode, link)
            if filtered_gp: continue
            if link.find('javascript') != -1:
                gp = re.search(self.url_mode, link)
                if gp:
                    link = gp.group()
            try:
                a = urlparse(link).path
            except Exception,e:
                print "{0}:{1}".format("urlparse error",e)
                continue
            if a == '':
                link = link + '/'
            try:
                url = urljoin(base_url, link)
            except:
                print link
                continue
            gp = re.search(self.url_mode, url)
            if gp:
                cur_domain = tldextract.extract(url).registered_domain
                if cur_domain == '':
                    continue
                elif cur_domain == domain:
                    inter_urls.add(url)
                else:
                    outer_urls.add(url)

        return inter_urls, outer_urls

    def get_outer_domains(self,urls, texts, domain):

        outer_domains = set()

        while len(texts) != 0:
            gp = re.search(self.domain_mode, texts)
            if gp:
                outer_domain = tldextract.extract(gp.group()).registered_domain
                if outer_domain!='' and outer_domain != domain:
                    outer_domains.add(outer_domain.lower())
                texts = texts[gp.end() + 1:]
            else:
                break

        for url in urls:
            gp = re.search(self.domain_mode, url)
            if gp:
                outer_domain = tldextract.extract(gp.group()).registered_domain
                if outer_domain!='' and outer_domain != domain:
                    outer_domains.add(outer_domain.lower())

        return outer_domains


    def extract_associnfo(self,soup, domain):
        """
        param: soup:当前域名进行http请求所得响应进行soup处理后结果
        param: domain: 当前域名
        return: 内链数量，外链数量，外链域名，外链域名数量
        """

        href1_lst = soup.find_all(attrs={'href': re.compile(r'.*')})
        # print href1_lst
        href2_lst = soup.find_all(attrs={'src': re.compile(r'.*')})
        # print href2_lst
        href_lst = href2_lst + href1_lst
        hrefs = []
        src_lst = soup.find_all(attrs={'src': self.domain_mode})
        # print src_lst
        if len(href_lst) != 0:
            for s in href_lst:
                if isinstance(s, str):
                    hrefs.append(s)
                else:
                    if s.has_attr('href'):
                        hrefs.append(s.attrs['href'])
                    else:
                        hrefs.append(s.attrs['src'])
        if len(src_lst) != 0:
            src_lst = [s.attrs['src'] for s in src_lst]
        text = ''
        for a in soup.strings:
            if a is not None:
                text = text + a.string

        links = set(hrefs)
        inter_urls, outer_urls = self.divide_urls(links, domain)
        urls = set(outer_urls) | set(src_lst)
        outer_domains = self.get_outer_domains(urls, text, domain)
        self.info['inter_urls_ct'] = len(inter_urls)
        self.info['outer_urls_ct'] = len(outer_urls)
        self.info['outer_domains_ct'] = len(outer_domains)

        self.info['inter_urls'] = list(inter_urls)
        self.info['outer_urls'] = list(outer_urls)
        self.info['outer_domains'] = list(outer_domains)

        res = (self.info['inter_urls_ct'],self.info['outer_urls_ct'],self.info['outer_domains'],self.info['outer_domains_ct'])
        """
        return: 内链数量，外链数量，外链域名，外链域名数量
        """
        return res



    def run(self,cur_domain):
        """
        param:cur_domain
        return: 内链数量，外链数量，外链域名，外链域名数量
        """
        response = self.send_request(cur_domain)
        soup = self.deal_response(response)
        res = self.extract_associnfo(soup,cur_domain)
        return res


def save_mongo_ope(mongo_conn,cur_domain,res):
    """

    """
    document = dict(domain = cur_domain,
                    inter_urls_ct = res[0],
                    outer_urls_ct = res[1],
                    outer_domains = res[2],
                    outer_domains_ct = res[3])
    mongo_conn.mongo_insert('domain_links',document)
    mongo_conn.mongo_update('domain_index',{'domain':domain},{'links_info':1},True)





if __name__ == '__main__':
    # mongo_conn = MongoConn('172.29.152.152')
    links_handler = Get_links()
    res = links_handler.run('0033y9.com')
    print res
