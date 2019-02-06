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

        for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):

            link = 'http://www.indeed.com' + a['href']

            fullsummary = summaryHelper(link)

            summaries.append(fullsummary)
    return summaries

def extract_job_link(soup):
    links = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):

        for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
            link = 'http://www.indeed.com' + a['href']
            links.append(link)
    return links
def summaryHelper(url):

    subpage = requests.get(url)
    subsoup = BeautifulSoup(subpage.text, 'html.parser')
    JobDespTab = str(subsoup.find(attrs={"class": "jobsearch-JobComponent-description icl-u-xs-mt--md"}))
    cleanr = re.compile('<.*?>')

    clean_text = re.sub(cleanr, ' ', JobDespTab)


    return clean_text




def scraper_customizat(pages,city,job):

    job = job.replace(' ', '+')
    customlink ='https://www.indeed.com/jobs?q='+job+'&l='+city

    for i in range(pages):
        page = customlink + '&start=' + str(i);

        print(page)
        scraper_start(page)

def scraper_start(page):
    pagejson = requests.get(page)
    soup = BeautifulSoup(pagejson.text, 'html.parser')


    summarylist=(extract_summary_from_result(soup))
    #salaryList  = (extract_salary_from_result(soup))  #  SalaryList is out for now due to not every job having a "salary" on indeed.com
    companylist = (extract_company_from_result(soup))
    titlelist = (extract_job_title_from_result(soup))
    locationlist = (extract_location_from_result(soup))
    urlList = (extract_job_link(soup))
    for i in range(9):
        sql = "INSERT INTO jobs (job_title,job_company,job_location,job_summary,job_url) VALUES (%s,%s,%s,%s,%s)"
        thisCompany = companylist[i]
        thisTitle = titlelist[i]
        thisLocation = locationlist[i]
        thisSummary = summarylist[i]
        thisUrl = urlList[i]

        insert_tuple = (thisTitle,thisCompany,thisLocation,thisSummary,thisUrl)
        cursor.execute(sql,insert_tuple)
        print(insert_tuple)
        mydb.commit()


def db_test():

    cities = ['chicago','new york city', 'seattle','washington','Detroit','Austin','San Francisco','Dallas','orlando','Denver']

    search_jobs= ['software developer', 'artificial intelligence','web developer','Database administrator','mySQL','java', "angular","react",  'python',
                  'financial analyst','internship','cybersecurity']

    for i in range(len(search_jobs)):
        for j in range(len(cities)):
            scraper_customizat(10,cities[j],search_jobs[i])
db_test()

