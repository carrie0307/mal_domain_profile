# encoding:utf-8
from selenium import webdriver
from lxml import etree
import time


domain = '520820.com'
try:
    driver = webdriver.PhantomJS(executable_path="/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
    url = 'http://bsb.baidu.com'
    driver.get(url)

    driver.find_element_by_id('url').clear()
    driver.find_element_by_id("url").send_keys(domain)

    driver.find_element_by_xpath('/html/body/div/div[1]/div/div/form/button').click()
    time.sleep(2)


    page = driver.page_source
    page = etree.HTML(page)
    res = page.xpath('/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div/@class')
    if res:
        print domain,res[0]
    driver.quit()
except:
    driver.quit()
