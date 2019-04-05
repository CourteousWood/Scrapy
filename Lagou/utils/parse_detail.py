import re
import time
from datetime import datetime

from JobSpiders.items import Job51Item, Job51ItemLoader

from JobSpiders.JobSpiders.utils import get_md5


def parse_detail_utils(self, response, value):
    contain_key_word = response.xpath("//div[@class='tHeader tHjob']//h1/text()").extract_first().strip()
    m = re.search(value, contain_key_word, re.IGNORECASE)
    if m:
        itemloader = Job51ItemLoader(item=Job51Item(), response=response)
        itemloader.add_value("url", response.url)
        itemloader.add_value("url_obj_id", get_md5(response.url)+str(int(time.time())))
        itemloader.add_value("title", contain_key_word)
        try:
            if response.xpath("/html/body/div[3]/div[2]/div[2]/div/div[1]/strong//text()").extract_first("") != "":
                str_salary = response.xpath("/html/body/div[3]/div[2]/div[2]/div/div[1]/strong//text()").extract_first(
                    "")
                if '千/月' in str_salary:
                    list_str = str_salary.split("-")
                    print(list_str[0])
                    print(list_str[1].strip().split("千")[0].strip())
                    salary_min = float(list_str[0]) * 1000
                    salary_max = float(list_str[1].strip().split("千")[0].strip()) * 1000
                    itemloader.add_value("salary_min", salary_min)
                    itemloader.add_value("salary_max", salary_max)
                elif '万/月' in str_salary:
                    list_str = str_salary.strip().split("-")
                    print(list_str[0])
                    print(list_str[1].strip().split("万")[0].strip())
                    salary_min = float(list_str[0]) * 10000
                    salary_max = float(list_str[1].strip().split("万")[0].strip()) * 10000
                    itemloader.add_value("salary_min", salary_min)
                    itemloader.add_value("salary_max", salary_max)
                elif '万/年' in str_salary:
                    list_str = str_salary.strip().split("-")
                    salary_min = float(list_str[0]) * 10000 / 12
                    salary_max = float(list_str[1].strip().split("万")[0].strip()) * 10000 / 12
                    itemloader.add_value("salary_min", salary_min)
                    itemloader.add_value("salary_max", salary_max)
                else:
                    itemloader.add_value("salary_min", 0)
                    itemloader.add_value("salary_max", 0)
            else:
                itemloader.add_value("salary_min", 0)
                itemloader.add_value("salary_max", 0)
        except Exception as e:
            print("str_salary error")
            print(e)
            itemloader.add_value("salary_min", 0)
            itemloader.add_value("salary_max", 0)
        info = response.xpath("//p[@class='msg ltype']/@title").extract_first()
        job_city = info.strip().split("|")[0].strip()
        experience_year = find_in_list(self, key="经验", list_name=info)

        itemloader.add_value("job_city", job_city)
        itemloader.add_value("experience_year", experience_year)
        try:
            education_need = info.strip().split("|")[2].strip()
            print(education_need)
            if '人' in education_need:
                education_need = "无"
            itemloader.add_value("education_need", education_need)
        except Exception as e:
            print("education_need error null")
            print(e)

        publish_date = find_in_list(self, key="发布", list_name=info)
        itemloader.add_value("publish_date", publish_date)
        job_advantage_tags_list = response.xpath("//div[@class='t1']//span/text()").extract()
        if len(job_advantage_tags_list) == 0:
            job_advantage_tags = " "
        else:
            job_advantage_tags = ','.join(job_advantage_tags_list)
        position_info_contains_job_request_list = response.xpath(
            "//div[@class='bmsg job_msg inbox']/p//text()").extract()
        if len(position_info_contains_job_request_list) == 0:
            position_info_contains_job_request = " "
        else:
            position_info_contains_job_request = ','.join(position_info_contains_job_request_list)
        itemloader.add_value("job_advantage_tags", job_advantage_tags)
        itemloader.add_value("position_info", position_info_contains_job_request)
        job_classification = response.xpath("//div[@class='tCompany_main']//div[@class='mt10']/p[1]//a/text()").extract_first("")
        itemloader.add_value("job_classification", job_classification)
        itemloader.add_value("crawl_time", datetime.now())
        item = itemloader.load_item()
        return item


def find_in_list(self, key, list_name):
    for i in range(0, len(list_name)):
        value = list_name.strip().split("|")[i].strip()
        if key in value:
            return value
