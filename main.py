from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

user_agents_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
]


user_agent = user_agents_list[1]
print(user_agent)

options = webdriver.FirefoxOptions()
options.set_preference("general.useragent.override", user_agent)

driver = webdriver.Firefox(options=options)

url = 'https://zakupki.mos.ru/purchase/list?page=1&perPage=50&sortField=relevance&sortDesc=true&filter=%7B%22auctionSpecificFilter%22%3A%7B%22stateIdIn%22%3A%5B19000002%2C19000005%2C19000003%2C19000004%2C19000008%5D%7D%2C%22needSpecificFilter%22%3A%7B%7D%2C%22tenderSpecificFilter%22%3A%7B%7D%7D&state=%7B%22currentTab%22%3A1%7D'
# url = 'https://www.whatismybrowser.com/detect/what-is-my-user-agent/'

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
    order_rec = dict()
    soup = BeautifulSoup(page_source, 'lxml')
    order_list = soup.find('div', {'class': 'PublicListStyles__PublicListContentContainer-sc-1q0smku-1'})
    items = order_list.find_all('div', {'class': 'CardStyles__MainInfoContainer-sc-18miw4v-1'})
    for index, item in enumerate(items):
        order_rec.clear()
        num_order = item.find('span', {'class': 'EllipsedSpan__WordBreakSpan-sc-1fhhmku-0'}).text.strip()
        print(num_order)
        link_order = item.find('a').get('href')
        order_rec['link_order'] = link_order
        print(link_order)
        order_status = item.find('div', {'class': 'content'}).text.strip()
        order_rec['order_status'] = order_status
        print(order_status)
        order_type = item.find('div', {'class': 'iOqMyw'}).text.strip()
        order_rec['order_type'] = order_type
        print(order_type)
        order_subj = item.find('a', {'class': 'drFPNq'}).text.strip()
        order_rec['order_subj'] = order_subj
        print(order_subj)
        order_firm = item.find('a', {'class': 'dzCDib'}).text.strip()
        order_rec['order_firm'] = order_firm
        print(order_firm)
        try:
            order_price = item.find('div', {'class': 'jzBqrB'}).text.strip()
        except:
            order_price = 'None'
        order_rec['order_price'] = order_price
        print(order_price)
        deal_count = item.find('div', {'class': 'eyTIpk'}).text.strip()
        order_rec['deal_count'] = deal_count
        print(deal_count)
        info_fields = get_add_info(order_list, index)
        order_region = info_fields[0]
        order_rec['order_region'] = order_region
        order_law = info_fields[1]
        order_rec['order_law'] = order_law
        order_period = info_fields[2]
        order_rec['order_period'] = order_period
        order_comment = info_fields[3]
        order_rec['order_comment'] = order_comment
        print(order_rec)
        # orders_dict[num_order] = order_rec


def parse_page(driver):
    page = driver.find_element(By.CSS_SELECTOR, '.PublicListStyles__PublicListContentContainer-sc-1q0smku-1 > div:nth-child(49) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)')
    if page.text == 'ПРИЕМ ПРЕДЛОЖЕНИЙ':
        try:
            parse_page_data(driver.page_source)
            print(orders_dict)
        except:
            print('error')
        finally:
            return 1
    else:
        return 0


def get_next_page(driver):
    while parse_page(driver) > 0:
        res_page = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[5]/div[2]/div/div/div[1]/div[5]/div[3]/div/div[1]/div/a[9]').click()
        time.sleep(4)
    return 1


def driver_get():
    try:
        driver.get(url)
        time.sleep(3)
        driver.find_element(By.XPATH, '/html/body/div[3]/div/div[5]/div[2]/div/div/div[1]/div[2]/div/div[1]/div[3]/span').click()
        print('get zakupki')
        time.sleep(4)
        driver.find_element(By.XPATH, '/html/body/div[3]/div/div[5]/div[2]/div/div/div[1]/div[3]/div/div/div[2]/div/i').click()
        print('open filter')
        time.sleep(4)
        driver.find_element(By.XPATH, '/html/body/div[3]/div/div[5]/div[2]/div/div/div[1]/div[4]/div/div/form/div/div[1]/div[1]/div/div/i[2]').click()
        print('delete filter value')
        time.sleep(4)
        driver.find_element(By.XPATH, '/html/body/div[3]/div/div[5]/div[2]/div/div/div[1]/div[4]/div/div/form/div/div[6]/div/button[2]').click()
        print('commit ')
        time.sleep(4)
        driver.find_element(By.CSS_SELECTOR, '.PublicListHeaderActionsStyles__ShowFilterButton-sc-yl44rw-6 > i:nth-child(2)').click()
        print('hide filter window')
        time.sleep(4)
        # with open('main.html', "w") as myfile:
        #     myfile.write(driver.page_source)
        # myfile.close()
        get_next_page(driver)
        time.sleep(5)

    except Exception as ex:
        print(ex)
    finally:
        pass
        # print(driver.page_source)
        # driver.close()
        # driver.quit()


if __name__ == '__main__':
    # with open('main.html', "r") as myfile:
    #     parse_page_data(myfile.read())
    driver_get()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
