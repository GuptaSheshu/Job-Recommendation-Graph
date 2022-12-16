from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import JobPosting
from selenium.webdriver.chrome.service import Service
from contextlib import closing
from webdriver_manager.chrome import ChromeDriverManager

class AmazonScrape():
    """Main class for of the scrapping application
    """

    def get_job_listing(self, soup):
        job_info_list = []
        job_list = []
        
        total_info = soup.findAll('div', {'class': 'info first col-12 col-md-8'})
        for info in total_info:
            job_list.append(info)
        
        print(job_list)            
        for job in job_list:
            job_title = job.find_all(re.compile("h"))[0].string
            location_jobid = job.find(re.compile("p")).string.split('|')
            location = location_jobid[0]
            job_id = location_jobid[1]
            
            info_dict = {'job_title': job_title, 'company_name':'Amazon','location':location, 
                         'job_url': 'https://www.amazon.jobs/en/jobs/' + str(job_id.split(": ")[1]),
                         'desc':'','basic_qual':'', 'pref_qual':''}
            
            job_info_list.append(info_dict)
            
        return job_info_list
    
    def get_job_description(self, job_info_list, browser_options):
        for idx, job in enumerate(job_info_list):
            # webpage.get(job['job_url'])
            
            with closing(webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)) as browser:
                browser.get(job['job_url'])
                page_source = browser.page_source

            sp = BeautifulSoup(page_source, features="html.parser")
            info = sp.findAll("h2")
            for val in info:
                try:
                    if(val.string == 'DESCRIPTION'):
                        job_info_list[idx]['desc'] = val.next_sibling.text
                    elif(val.string == 'BASIC QUALIFICATIONS'):
                        job_info_list[idx]['basic_qual'] = val.next_sibling.text
                    elif(val.string == 'PREFERRED QUALIFICATIONS'):
                        job_info_list[idx]['pref_qual'] = val.next_sibling.text
                except:
                    job_info_list[idx]['desc'] = 'NOT FOUND'
                    job_info_list[idx]['basic_qual'] = 'NOT FOUND'
                    job_info_list[idx]['pref_qual'] = 'NOT FOUND'
        return job_info_list
    
    def get_Postlist(self, job_info_list):
        PostList = []
        for job in job_info_list:
            temp = JobPosting(job_title=job['job_title'], company_name = job['company_name'], location=job['location'],
                                    job_url=job['job_url'], job_description=job['desc'],
                                    basic_qualificaiton=job['basic_qual'], preferred_qualification=job['pref_qual'])
            PostList.append(temp)
        return PostList


def amazon_main():
    browser_options = Options()
    browser_options.add_argument('--no-sandbox')
    browser_options.add_argument('--headless')
    browser_options.add_argument('--disable-setuid-sandbox')
    browser_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
    num_pages = 4
    job_info_list = []
    Scarper = AmazonScrape()
    
    for nn in range(num_pages):
        URL = 'https://www.amazon.jobs/en/search?offset='+str(10*nn)+'&result_limit=10&sort=relevant&category%5B%5D=machine-learning-science&category%5B%5D=software-development&category%5B%5D=research-science&category%5B%5D=data-science&country%5B%5D=USA&country%5B%5D=CAN&country%5B%5D=GBR&country%5B%5D=IND&country%5B%5D=JPN&country%5B%5D=AUS&country%5B%5D=ESP&distanceType=Mi&radius=24km&latitude=&longitude=&loc_group_id=&loc_query=&base_query=applied%20science&city=&country=&region=&county=&query_options=&'
        with closing(webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)) as browser:
            browser.get(URL)
            page_source = browser.page_source

        soup = BeautifulSoup(page_source, features="html.parser")
        print("Scrapping from page number:{} from Amazon".format(nn))
        info_list = Scarper.get_job_listing(soup)
        info_list = Scarper.get_job_description(info_list, browser_options)
        print(len(info_list))
        job_info_list += info_list
    
    return job_info_list

if(__name__=='__main__'):
    amazon_main()

    