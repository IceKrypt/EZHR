import re

import requests
from bs4 import BeautifulSoup

import mysql.connector

# contents = page.content


mydb = mysql.connector.connect(user='matt',password='123456',database='job_schema')
cursor = mydb.cursor(prepared=True)


def extract_job_title_from_result(soup):
    jobs = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):

        for a in div.find_all(name='a', attrs={'data-tn-element': 'jobTitle'}):
            jobs.append(a['title'])

    return (jobs)


def extract_company_from_result(soup):
    companies = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):
        company = div.find_all(name="span", attrs={"class": "company"})
        if len(company) > 0:
            for b in company:
                companies.append(b.text.strip())
        else:
            sec_try = div.find_all(name="class", attrs={"class": "result-link-source"})

            for span in sec_try:
                companies.append(span.text.strip())
    return companies


def extract_location_from_result(soup):
    locations = []
    spans = soup.findAll('span', attrs={'class': 'location'})
    for span in spans:
        locations.append(span.text)
    return locations


def extract_salary_from_result(soup):
    salaries = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):
        try:
            salaries.append(div.find('nobr').text)
        except:
            try:
                div_two = div.find(name="div", attrs={"class": "paddedSummary"})
                div_three = div_two.find("div")
                salaries.append(div_three.text.strip())
            except:
                salaries.append("NONE")
    return (salaries)


def extract_summary_from_result(soup):
    summaries = []

    for div in soup.find_all(name="div", attrs={"class": "row"}):

        for a in div.find_all(name='a', attrs={'class': 'jobtitle turnstileLink'}):
            link = 'http://www.indeed.com' + a['href']
            fullsummary = summaryHelper(link)
            # print(len(summaries))
            summaries.append(fullsummary)
    return summaries


def summaryHelper(url):
    minisummaries = []
    subpage = requests.get(url)
    subsoup = BeautifulSoup(subpage.text, 'html.parser')
    JobDespTab = str(subsoup.find(attrs={"class": "jobsearch-JobComponent-description icl-u-xs-mt--md"}))
    cleanr = re.compile('<.*?>')

    clean_text = re.sub(cleanr, ' ', JobDespTab)

    # print(len(minisummaries))
    return clean_text




def scraper_customizat(pages,city,job):

    job = job.replace(' ', '+')
    customlink ='https://www.indeed.com/jobs?q='+job+'&l='+city

    for i in range(pages):
        print(customlink + '&start=' + str(i))
        page = requests.get(customlink + '&start=' + str(i))
        print(page)
        scraper_start(page)



def scraper_start(page):
    soup = BeautifulSoup(page.text, 'html.parser')


    bugstop = len(extract_summary_from_result(soup))   # called bugstop because if the for loop[ below goes beond this loop program crashes =/

    summarylist=(extract_summary_from_result(soup))
    #salaryList  = (extract_salary_from_result(soup))  #  SalaryList is out for now due to not every job having a "salary" on indeed.com
    companylist = (extract_company_from_result(soup))
    titlelist = (extract_job_title_from_result(soup))
    locationlist = (extract_location_from_result(soup))
    for i in range(bugstop-1):
        sql = "INSERT INTO job_schema.'jobs' ('job_title','job_company','job_location','job_summary') VALUES (%s,%s,%s,%s) "

        #thisSalary = salaryList[i]
        thisCompany = companylist[i]
        thisTitle = titlelist[i]
        thisLocation = locationlist[i]
        thisSummary = summarylist[i]


        insert_tuple = (thisTitle,thisCompany,thisLocation,thisSummary)
        #cursor.execute(sql,insert_tuple)
        print(insert_tuple)
        #mydb.commit()




scraper_customizat(10,'chicago','java')
