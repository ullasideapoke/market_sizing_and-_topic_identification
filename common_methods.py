import os
import re
import ast
import random
import logging
import requests
import tldextract
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
import dateutil.parser as parser
from urllib.parse import urlparse
from fake_useragent import UserAgent
from common.headers import headers_lst
from selenium.webdriver.chrome.options import Options
from market_search_db_constants import url_entity_extract_ip_address

ua = UserAgent()


def log_load_info():
    logging.basicConfig(filename='dis_log.log',
                        level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    return logging


def log_load_debug():
    logging.basicConfig(filename='dis_log.log',
                        level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    return logging


logger_info = log_load_info()
logger_bug = log_load_debug()

# user = str(ua.chrome)
# print(user)
# headers = {'user-agent': user}
# print(headers['user-agent'])
# print(headers)
# try:
#     header = {'user-agent': str(ua.chrome)}
# except:
#     pass
# header_lst = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36']
# lst = ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36', 'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36', 'Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36', 'Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36', 'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14']

value = random.choice(headers_lst)
print("value", value)
header = {'user-agent': value}
print(header)
try:
    # print(header)
    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    # getting response object for the request
    # headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; ja-JP) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'}
    souper = ""


    def get_document_google(web_url):
        try:
            page = requests.get(web_url, headers=header, timeout=40)
            souper = BeautifulSoup(page.text, 'html.parser')
            str_unwanted = souper.find_all('script')
            for tag in str_unwanted:
                tag.decompose()
            return souper
        except Exception as exe:
            print('Exception error occurred in get_document_google', exe)
            pass
except Exception as ex:
    print('Exception error occured in scraping (Main method)', ex)

try:
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    # getting response object for the request
    souper = ""


    def get_document(web_url):
        try:
            page = requests.get(web_url, headers=headers, timeout=40)
            souper = BeautifulSoup(page.text, 'html.parser')
            str_unwanted = souper.find_all('script')
            for tag in str_unwanted:
                tag.decompose()
            return souper
        except Exception as exe:
            print('Exception error occurred in get_document', exe)
            pass
except Exception as ex:
    print('Exception error occured in scraping (Main method)', ex)


def get_chrome_driver():
    driver = None
    try:

        options = Options()
        options.headless = True
        options.add_argument('--disable-gpu')
        options.add_argument("--incognito")
        options.add_argument("—disable-gpu")
        options.add_argument(f"user-agent={ua.random}")
        options.add_argument("window-size=1400,600")
        # print(os.getcwd())
        chrome_path = os.getcwd() + "/common/chromedriver"
        driver = webdriver.Chrome(executable_path=chrome_path, options=options)
    except Exception as exe:
        print('Exception occured in get_chrome_driver() ', exe)
    return driver


def remove_header_and_footer(doc):
    try:
        for titletags in doc.find_all('head'):
            titletags.decompose()
        for titletags in doc.find_all('title'):
            titletags.decompose()
        for metatags in doc.find_all('meta'):
            metatags.decompose()
        for footertags in doc.find_all('footer'):
            footertags.decompose()
        for noscripttags in doc.find_all('noscript'):
            noscripttags.decompose()
        for noscripttags in doc.find_all('script'):
            noscripttags.decompose()
        for noscripttags in doc.find_all('style'):
            noscripttags.decompose()
        for navtags in doc.find_all('nav'):
            navtags.decompose()
        for formtags in doc.find_all('form'):
            formtags.decompose()
        for asidetags in doc.find_all('aside'):
            asidetags.decompose()
        for tags in doc.find_all("div", {"class": re.compile(".*footer.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"class": re.compile(".*social.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"class": re.compile(".*cook.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"class": re.compile(".*contact.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"class": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"class": re.compile(".*follow.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"id": re.compile(".*footer.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"id": re.compile(".*social.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"id": re.compile(".*cook.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"id": re.compile(".*contact.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"id": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"id": re.compile(".*follow.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("p", {"id": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("p", {"class": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("ul", {"id": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("ul", {"class": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("section", {"class": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("section", {"id": re.compile(".*breadcrum.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("script", {"class": re.compile(".*cook.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("script", {"src": re.compile(".*cook.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("ul", {"id": re.compile(".*menu.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("ul", {"class": re.compile(".*menu.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"class": re.compile(".*nav.*", re.IGNORECASE)}):
            tags.decompose()
        for tags in doc.find_all("div", {"style": re.compile(".*right.*", re.IGNORECASE)}):
            tags.decompose()
    except Exception as _e:
        print(_e)
    return doc


def rating_mechanism(query, data_str):
    try:
        query = query.replace(",", "")
        query_split = query.split(" ")
        score = 0
        query_str_split_unique = set(query_split)
        if data_str:
            for query_string in query_str_split_unique:
                if query_string.lower() in data_str.lower():
                    score = score + 1
        return score
    except Exception as exp:
        print("Exception in rating_mechanism--->", exp)


def get_year_from_date(date_):
    year = ''
    try:
        if date_ != 'None':
            year = parser.parse(date_).year
        else:
            year = ''
    except Exception as exe:
        print("Exception in get_year_from_date", exe)
    return year


def current_date():
    try:
        today = date.today()
        d1 = today.strftime("%Y/%m/%d")
        return d1
    except Exception as exp:
        print("Exception in current date---> ", exp)


def get_domain_name(website):
    try:
        info = tldextract.extract(website)
        return info.registered_domain

    except Exception as exp:
        print("Exception in get_domain_name--> ", exp)


def get_website_link(url):
    try:
        parsed_uri = urlparse(url)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return result
    except Exception as exp:
        print("Exception in get_website_link--> ", exp)


def get_url_entities_from_content(url_input, title):
    print('url---------', url_input)
    print("title -------", title)
    result_list = []
    try:
        try:
            result_list = []
            url = 'http://' + url_entity_extract_ip_address + '/url_extraction'
            print("3--------")
            post_request = requests.post(
                url,
                data=str({'url': url_input, 'title': title}).encode('utf-8'),
                headers={'Content-Type': "application/json"}
            )
            print("started in post_request")

            result_list = post_request.text
            result_list = ast.literal_eval(result_list)
            print("----", result_list)

        except Exception as exe:
            print("Exception in get_url_entities_from_content() : ", exe)

    except Exception as exe:
        print("Exception in get_url_entities_from_content() : ", exe)
    return result_list

# print(get_document_google("https://pypi.org/project/CurrencyConverter/"))
