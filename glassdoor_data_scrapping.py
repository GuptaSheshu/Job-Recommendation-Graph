from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import *
from selenium.webdriver.chrome.service import Service
from contextlib import closing
from webdriver_manager.chrome import ChromeDriverManager

class GlassdoorScrape():
    """Main class for of the scrapping application
    """

    def get_job_listing_query(self, soup):
        """ Method to extract job information such as company name, 
        job_url, job_title based on query.

        Args:
            soup (bs4.BeautifulSoup): a BeautifulSoup datatype to 
            access HTML types for extraction of certain class.

        Returns:
            List: A list of dictionary containing job information.
        """
        job_info_list = []
        job_list = []
        
        total_info = soup.findAll('div', {'class': 'd-flex flex-column pl-sm css-3g3psg css-1of6cnp e1rrn5ka4'})
        for info in total_info:
            extra_info = info.find_all("a")
            company_name = extra_info[0].string
            job_url = 'https://www.glassdoor.com'+extra_info[0]['href']
            job_title = extra_info[1].string
            
            # Location
            location_info = info.find_all("div")
            location = location_info[2].string
                        
            info_dict = {'job_title': job_title,'company_name':company_name, 'location':location, 
                         'job_url': job_url,
                         'desc':'','basic_qual':'', 'pref_qual':''}
            
            job_info_list.append(info_dict)
            
        return job_info_list
        
    def get_job_listing_company(self, soup, company_name):
        """ Method to extract job information such as 
        job_url, job_title based on company name.

        Args:
            soup (bs4.BeautifulSoup): a BeautifulSoup datatype to 
            access HTML types for extraction of certain class.
            company_name (str): A company name to use it for scrapping
            different role within the company.

        Returns:
            List: A list of dictionary containing job information.
        """
        job_info_list = []
        job_list = []
        
        total_info = soup.findAll('li', {'class': 'jobsList__JobsListStyles__newJobListItem pt-std'})
        for info in total_info:
            extra_info = info.find_all("a")
            company_name = company_name
            job_url = 'https://www.glassdoor.com'+extra_info[0]['href']
            job_title = extra_info[1].string
            
            # Location
            location = info.findAll('span','jobDetails__JobDetailsStyles__newLocationGrey')[0].text
                        
            info_dict = {'job_title': job_title,'company_name':company_name, 'location':location, 
                         'job_url': job_url,
                         'desc':'','basic_qual':'', 'pref_qual':''}
            
            job_info_list.append(info_dict)
            
        return job_info_list

    def get_job_description(self, job_info_list, browser_options):
        """Extract extra information about the job such as Job description,
        basic qualification, and preferred qualification.

        Args:
            job_info_list (List): A list of dictionary containing basic job
            information.
            browser_options (selenium.webdriver.chrome.options.Options): browser
            options for selenium to interact with browser to give HTML.

        Returns:
            job_info_list (List): A list of dictionary containing basic job
            information and advanced information such as job description etc.
        """
        for idx, job in enumerate(job_info_list):
            # webpage.get(job['job_url'])
            with closing(webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)) as browser:
                browser.get(job['job_url'])
                page_source = browser.page_source

            sp = BeautifulSoup(page_source, features="html.parser")
            info = sp.findAll('div','desc css-58vpdc ecgq1xb5')
            for val in info:
                try:
                    job_info_list[idx]['desc'] = val.text.strip()
                    job_info_list[idx]['basic_qual'] = val.text.strip()
                    job_info_list[idx]['pref_qual'] = val.text.strip()
                except:
                    job_info_list[idx]['desc'] = 'NOT FOUND'
                    job_info_list[idx]['basic_qual'] = 'NOT FOUND'
                    job_info_list[idx]['pref_qual'] = 'NOT FOUND'
        return job_info_list
        
    def get_Postlist(self, job_info_list):
        PostList = []
        for job in job_info_list:
            temp = JobPosting(job_title=job['job_title'],company_name = job['company_name'], location=job['location'],
                                    job_url=job['job_url'], job_description=job['desc'],
                                    basic_qualificaiton=job['basic_qual'], preferred_qualification=job['pref_qual'])
            PostList.append(temp)
        return PostList


def glassdoor_main():
    browser_options = Options()
    browser_options.add_argument('--no-sandbox')
    browser_options.add_argument('--headless')
    browser_options.add_argument('--disable-setuid-sandbox')
    browser_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    job_info_list = []
    Scarper = GlassdoorScrape()
    query_dict, company_dict = get_url_glassdoor()
    for key, val in query_dict.items():
        # browser = webdriver.Chrome(options=browser_options)
        # browser.implicitly_wait(10)
        URL = val
        # browser.get(url=URL)
        with closing(webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)) as browser:
            browser.get(URL)
            page_source = browser.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        print("Scrapping for query - {}".format(key))
        info_list = Scarper.get_job_listing_query(soup)
        info_list = Scarper.get_job_description(info_list, browser_options)
        job_info_list += info_list
    
    
    for key, val in company_dict.items():
        URL = val
        # browser.get(url=URL)
        with closing(webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)) as browser:
            browser.get(URL)
            page_source = browser.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        print("Scrapping for company - {}".format(key))
        info_list = Scarper.get_job_listing_company(soup, key)
        info_list = Scarper.get_job_description(info_list, browser_options)
        job_info_list += info_list
    
    return job_info_list

if(__name__=='__main__'):
    glassdoor_main()