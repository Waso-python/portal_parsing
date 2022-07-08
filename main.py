from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import json
from utils import get_inn, only_digit
import logging
from my_set import URL
from bot_mess import add_to_table
import sys

def error_bot(rec):
    rec = [rec, 1, 1]
    add_to_table(rec)

PR_ERROR = 0
PAGE_NUM = 0
COUNT_PAGE = 10

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename="log.log", level=logging.INFO, format=FORMAT)


def loger(type, mess):
    global PR_ERROR
    if type == 'ERROR':
        PR_ERROR +=1
        logging.error(mess)
    else:
        logging.info(mess)

user_agents_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
]


user_agent = user_agents_list[1]
loger('INFO',user_agent)

options = webdriver.FirefoxOptions()
options.set_preference("general.useragent.override", user_agent)

driver = webdriver.Firefox(options=options)

url = URL


orders_dict = dict()

def get_add_info(div_source, ind):
    info_fields = []
    items = div_source.find_all('div', {'class': 'CardStyles__AdditionalInfoContainer-sc-18miw4v-9'})
    for index, item in enumerate(items):
        if index == ind:
            add_items = item.find_all('div', {'class': 'CardStyles__AdditionalInfoHeader-sc-18miw4v-10'})
            for index, item in enumerate(add_items):
                print(item.find('span').text)
                info_fields.append(item.find('span').text.strip())
    return info_fields


def parse_page_data(page_source):
    loger('INFO',"parsing")
    order_rec = dict()
    soup = BeautifulSoup(page_source, 'lxml')
    order_list = soup.find('div', {'class': 'PublicListStyles__PublicListContentContainer-sc-1q0smku-1'})
    items = order_list.find_all('div', {'class': 'CardStyles__MainInfoContainer-sc-18miw4v-1'})
    
    for index, item in enumerate(items):
        order_rec.clear()
        num_order = item.find('span', {'class': 'EllipsedSpan__WordBreakSpan-sc-1fhhmku-0'}).text.strip()
        print(num_order)
        link_order =r'https://zakupki.mos.ru' + item.find('a').get('href')
        order_rec['link_order'] = link_order
        print(link_order)
        order_status = item.find('div', {'class': 'content'}).text.strip()
        order_rec['order_status'] = order_status
        print(order_status)
        order_type = item.find('div', {'class': 'iOqMyw'}).text.strip()
        order_rec['order_type'] = order_type
        print(order_type)
        order_subj = item.find('a', {'class': 'drFPNq'}).text.strip().replace("'","").replace("\"","")
        order_rec['order_subj'] = order_subj
        print(order_subj)
        order_firm = item.find('a', {'class': 'dzCDib'}).text.strip().replace("'","").replace("\"","")
        firm_inn = get_inn(order_firm)[0][5:16] if get_inn(order_firm) else '0000000000'
        order_rec['order_firm'] = order_firm
        print(order_firm)
        try:
            order_price = item.find('div', {'class': 'jzBqrB'}).text.strip()
        except:
            order_price = 'None'
        order_price = only_digit(order_price)
        order_rec['order_price'] = order_price
        print(order_price)
        deal_count = item.find('div', {'class': 'eyTIpk'}).text.strip()
        order_rec['deal_count'] = deal_count
        print(deal_count)
        info_fields = get_add_info(order_list, index)
        c = len(info_fields)
        if c < 4:
            order_region = info_fields[0]
            order_rec['order_region'] = order_region
            order_law = 'No'
            order_rec['order_law'] = order_law
            order_period = info_fields[c - 2]
            order_rec['order_period'] = order_period
            order_comment = info_fields[c - 1]
            order_rec['order_comment'] = order_comment
        else:
            order_region = info_fields[0]
            order_rec['order_region'] = order_region
            order_law = info_fields[1]
            order_rec['order_law'] = order_law
            order_period = info_fields[2]
            order_rec['order_period'] = order_period
            order_comment = info_fields[3]
            order_rec['order_comment'] = order_comment
        # print(order_rec)
        order_start = order_period[2:12]
        order_end = order_period[16:32]
        orders_dict[num_order] = {'link_order': link_order, 'order_status': order_status,
                                  'order_type': order_type, 'order_subj': order_subj, 'order_firm': order_firm,
                                  'firm_inn': firm_inn,
                                  'order_price': order_price, 'deal_count': deal_count,
                                  'order_region': order_region,
                                  'order_law': order_law, 'order_start': order_start, 'order_end': order_end, 
                                  'order_comment': order_comment}


def parse_page(driver):
    global COUNT_PAGE
    page = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[5]/div[2]/div/div/div[1]/div[5]/div[2]/div[1]/div[1]/div/div/div[1]/div/div[1]/div/div/div[2]/div')

    if page.text == 'ПРИЕМ ПРЕДЛОЖЕНИЙ':
        try:
            parse_page_data(driver.page_source)
            # print(orders_dict)
        except Exception as ex:
            error_bot(ex)
            loger('ERROR',ex)
        finally:
            return 1
    else:
        return 0


def get_next_page(driver):
    global PAGE_NUM
    # while parse_page(driver) > 0:
    while PAGE_NUM < COUNT_PAGE:
        try:
            parse_page_data(driver.page_source)
            # print(orders_dict)
        except Exception as ex:
            error_bot(ex)
            loger('ERROR',ex)
        PAGE_NUM += 1
        loger('INFO', f'read a {PAGE_NUM} page')
        res_page = driver.find_element(By.XPATH, '//a[@type="nextItem"]').click()
        time.sleep(4)
    return 1


def driver_get():
    try:
        driver.get(url)
        time.sleep(6)
        driver.find_element(By.XPATH, '//span[text()="Закупки по потребностям"]').click()
        print('get zakupki')
        time.sleep(6)
        driver.find_element(By.XPATH, '//span[text()="Показать фильтры"]').click()
        print('open filter')
        time.sleep(5)
        driver.find_element(By.CLASS_NAME, 'delete').click()
        print('delete filter value')
        time.sleep(4)
        driver.find_element(By.XPATH, '//span[text()="Применить"]').click()
        print('commit ')
        time.sleep(4)
        driver.find_element(By.XPATH, '//span[text()="Скрыть фильтры"]').click()
        print('hide filter window')
        time.sleep(4)
        # with open('main.html', "w") as myfile:
        #     myfile.write(driver.page_source)
        # myfile.close()
        get_next_page(driver)
        time.sleep(5)

    except Exception as ex:
        error_bot(ex)
        loger('ERROR', ex)
    finally:
        with open("order.json", "w", encoding='utf8') as outfile:
            json.dump(orders_dict, outfile, ensure_ascii=False)
        driver.close()
        driver.quit()


if __name__ == '__main__':
    # with open('main.html', "r") as myfile:
    #     parse_page_data(myfile.read())
    loger('INFO',"START PROGRAM")
    try:
        driver_get()
    except Exception as ex:
        error_bot(ex)
        loger('ERROR', ex)
        if PR_ERROR > 0:
            loger('ERROR', f'program has {PR_ERROR} errors')
            error_bot(f'PARSING CRASH with {PR_ERROR} errors')
    finally:
        loger('INFO', f'readed {PAGE_NUM} pages')
        error_bot(f'PARSING ENDED with {PR_ERROR} errors')
       


# See PyCharm help at https://www.jetbrains.com/help/pycharm/