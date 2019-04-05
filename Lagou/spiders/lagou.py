# -*- coding: utf-8 -*-


import logging
import pickle
import re
import time
from datetime import datetime

import scrapy
from Lagou.items import LagouJobItem, LagouJobItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from Lagou.utils.common import get_md5

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']
    login_url = "https://passport.lagou.com/login/login.html"
    rules = (
        # Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsii/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.lagou.com',
        'Referer': 'https://www.lagou.com/',
        'X-Anit-Forge-Code': '0',
        'X-Anit-Forge-Token': 'None',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest'
    }

    cookie = {'JSESSIONID': 'ABAAABAAAHAAAFD8DAE0CD2E746F43F737F035650B6E7EF',
              'ticketGrantingTicketId': '_CAS_TGT_TGT-cfa8b888370445b5b755364bfbb804cf-20180730225005-_CAS_TGT_',
              'user_trace_token': '20180730225004-a4d90eec-e01f-4a00-9f5c-2645eda28272',
              'LG_LOGIN_USER_ID': '2da6d20b2b5356d5198633f97505a8223f09a663fe92f78f64936c31a3bfd73c'}

    def start_requests(self):
        browser = webdriver.Chrome(executable_path="c:\chromedriver.exe")
        browser.get(self.login_url)
        # browser.find_element_by_css_selector("div:nth-child(2) > form > div:nth-child(1) > input").send_keys(
        #     "自己的账号")
        # browser.find_element_by_css_selector("div:nth-child(2) > form > div:nth-child(2) > input").send_keys(
        #     "自己的账号密码")
        username ='18##########85'
        passwd = 'qwe123456'
        browser.find_element_by_css_selector("div:nth-child(2) > form > div:nth-child(1) > input").send_keys(
            username)
        browser.find_element_by_css_selector("div:nth-child(2) > form > div:nth-child(2) > input").send_keys(
            passwd)
        browser.find_element_by_css_selector(
            "div:nth-child(2) > form > div.input_item.btn_group.clearfix > input").click()
        import time
        time.sleep(10)
        cookies = browser.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        with open('cookies_dict.lagou', 'wb') as wf:
            pickle.dump(cookie_dict, wf)
        logging.info('--------lagou cookies---------')
        print(cookie_dict)
        return [scrapy.Request(self.start_urls[0], cookies=cookie_dict)]
        # yield scrapy.Request(url='https://www.lagou.com', headers=self.headers, cookies=self.cookie, dont_filter=True)

    def parse_job(self, response):

        title = response.css(".job-name::attr(title)").extract()[0]
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        list_type = []
        flag = True
        # flag = False
        # m = re.search("java", title, re.IGNORECASE)
        # if m:
        #     flag = True
        #     list_type.append("java")

        # if re.search("python", title, re.IGNORECASE):
        #     flag = True
        #     list_type.append("python")

        # if re.search("人工智能", title, re.IGNORECASE):
        #     flag = True
        #     list_type.append("人工智能")
        # if re.search("算法", title, re.IGNORECASE):
        #     flag = True
        #     list_type.append("算法")
        # if re.search("大数据", title, re.IGNORECASE):
        #     flag = True
        #     list_type.append("大数据")
        # if re.search("C\+\+", title, re.IGNORECASE):
        #     flag = True
        #     list_type.append("C++")
        # if re.search("go", title, re.IGNORECASE):
        #     flag = True
        #     list_type.append("go")
        if flag:
            # 解析拉勾网的职位
            item_loader.add_value("type", list_type)
            item_loader.add_css("title", ".job-name::attr(title)")
            item_loader.add_value("url", response.url)
            item_loader.add_value("url_obj_id", get_md5(response.url) + str(int(time.time())))
            str_salary = response.xpath("//span[@class='salary']/text()").extract_first("")
            if 'k' in str_salary:
                try:
                    list_str = str_salary.split("-")
                    salary_min = float(list_str[0].strip().split("k")[0].strip()) * 1000
                    salary_max = float(list_str[1].strip().split("k")[0].strip()) * 1000
                    item_loader.add_value("salary_min", salary_min)
                    item_loader.add_value("salary_max", salary_max)
                except Exception as e:
                    print('error str_salary', str_salary)
                    print(e)

            else:
                print('str_salary error', str_salary)
                item_loader.add_value("salary_min", 0)
                item_loader.add_value("salary_max", 0)
            # item_loader.add_css("salary", ".job_request .salary::text")
            item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
            item_loader.add_xpath("experience_year", "//*[@class='job_request']/p/span[3]/text()")
            item_loader.add_xpath("education_need", "//*[@class='job_request']/p/span[4]/text()")
            item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")
            try:
                item_loader.add_css("job_classification", '.position-label li::text')
            except Exception as e:
                print("job_classification error")
                print(e)
                item_loader.add_value("job_classification", '.job-name::attr(title)')
            item_loader.add_css("publish_date", ".publish_time::text")
            item_loader.add_css("job_advantage_tags", ".job-advantage p::text")
            item_loader.add_css("position_info", ".job_bt div")
            item_loader.add_css("job_addr", ".work_addr")
            item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
            item_loader.add_css("company_url", "#job_company dt a::attr(href)")
            item_loader.add_value("crawl_time", datetime.now())

            job_item = item_loader.load_item()

            return job_item
