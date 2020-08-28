import re
import hashlib
import requests
from bs4 import BeautifulSoup
from time import sleep;
import mysql.connector
import sys
import os

# @author is Matthew Blackman

host_var = os.environ['host_var']
username_var = os.environ['username_var']
password_var = os.environ['password_var']

mydb = mysql.connector.connect(host=host_var, user=username_var, password=password_var, database='ezhr')
cursor = mydb.cursor(prepared=True)


# TODO: Rewrite this scraper code to work better with Indeeds updated layout. Could also be abstracted/modularized a bit to work for other websites

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
        for a in div.find_all(name='a', attrs={'data-tn-element': 'jobTitle'}):
            link = 'http://www.indeed.com' + a['href']
            fullsummary = summaryHelper(link)
            summaries.append(fullsummary)
    return summaries


def extract_job_link(soup):
    links = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):

        for a in div.find_all(name='a', attrs={'data-tn-element': 'jobTitle'}):
            link = 'http://www.indeed.com' + a['href']
            links.append(link)
    return links


def summaryHelper(url):
    try:
        subpage = requests.get(url)
        subsoup = BeautifulSoup(subpage.text, 'html.parser')
        JobDespTab = str(subsoup.find(attrs={"class": "jobsearch-jobDescriptionText"}))
        cleanr = re.compile('<.*?>')

        clean_text = re.sub(cleanr, ' ', JobDespTab)
        return clean_text
    except requests.exceptions.ConnectionError:
        summaryHelper(url)


def scraper_customizat(pages, city, job):
    # function that lets the user determine what jobs the bot scrapes. Can specify the # of pages to scrape for each search, what cities, and what job title.
    job = job.replace(' ', '+')
    customlink = 'https://www.indeed.com/jobs?q=' + job + '&l=' + city
    for i in range(pages):
        page = customlink + '&start=' + str(i);
        print(page)
        scraper_start(page)
        print('page done, Sleeping for 5s to avoid spam block from Indeed')
        sleep(5)


def scraper_start(page):
    pagejson = requests.get(page)
    soup = BeautifulSoup(pagejson.text, 'html.parser')
    summarylist = (extract_summary_from_result(soup))
    # salaryList  = (extract_salary_from_result(soup))  #  SalaryList is out for now due to not every job having a "salary" on indeed.com
    companylist = (extract_company_from_result(soup))
    titlelist = (extract_job_title_from_result(soup))
    locationlist = (extract_location_from_result(soup))
    urlList = (extract_job_link(soup))
    for i in range(9):
        try:
            sql = "REPLACE INTO jobs (job_title,job_company,job_location,job_summary,job_url,url_hash) VALUES (%s,%s,%s,%s,%s,%s)"
            thisCompany = companylist[i]
            thisTitle = titlelist[i]
            thisLocation = locationlist[i]
            thisSummary = summarylist[i]
            thisUrl = urlList[i]
            thisHash = hashlib.sha256(str(thisUrl).encode())
            insert_tuple = (thisTitle, thisCompany, thisLocation, thisSummary, thisUrl, thisHash.hexdigest())
            cursor.execute(sql, insert_tuple)
            # print(insert_tuple)
            mydb.commit()
        except Exception:
            # Vague exception, if had more time would add specific functionality to fix timeout crashes and page not found crashes
            print('timed out')
            continue


def db_test():
    # this is the code that initially populates our database, utilizes Scraper_cusotomization function
    cities = ['Illinois', 'new york', 'Utah', 'Minnesota', 'Nebraska', 'Michigan', 'Florida', 'Massachusetts',
              'maryland', 'Oregon', 'California', 'Virginia', 'Texas', 'Ohio', 'Missouri', 'Georgia', 'Washington']

    search_jobs = ['python', 'financial analyst', 'cybersecurity', 'software developer', 'artificial intelligence'
        , 'web developer', 'Database administrator', 'mySQL', 'java', "angular", ]

    for i in range(len(search_jobs)):
        for j in range(len(cities)):
            # In this loop, 5 species how many pages for each city and job type
            scraper_customizat(5, cities[j], search_jobs[i])


db_test()
