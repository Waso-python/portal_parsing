import feedparser
import requests
import lxml
import re
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import OperationalError
import lxml
from my_set import PASSWORD_DB, HOST_DB, PORT_DB, DB_NAME, USER_DB

RSS = "https://zakupki.gov.ru/tinyurl/3769b1ca56c0e0db6fa6e2ccee634ebdf74118ce9a4bf5d3a3ac91914d8e3315"

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

def getRss():
	result = []
	feed = feedparser.parse(RSS)
	for entry in feed.entries:
		result.append(entry.link)
	return result



class Procedure():
	
	def __init__(self):
		self.num_proc:str = ""
		self.link_proc:str = ""
		self.status:str = ""
		self.type_proc:str = ""
		self.subj_proc:str = ""
		self.partner:str = ""
		self.partner_inn:str = ""
		self.summ_proc:str = ""
		self.region:str = ""
		self.law_proc:str = ""
		self.start_date:str = ""
		self.end_date:str = ""
		self.trade_place:str = ""
	def set_num_proc(self, num_proc:str):
		self.num_proc = ''.join(num_proc)
	def set_law_proc(self, law_proc:str):
		self.law_proc = law_proc
	def set_link_proc(self, value:str):
		self.link_proc = value
	def set_status(self, value:str):
		self.status = value
	def set_type_proc(self, value:str):
		self.type_proc = value
	def set_subj_proc(self, value:str):
		self.subj_proc = value
	def set_partner(self, value:str):
		self.partner = value
	def set_partner_inn(self, value:str):
		self.partner_inn = value
	def set_summ_proc(self, value:str):
		self.summ_proc = value
	def set_region(self, value:str):
		self.region = value
	def set_start_date(self, value:str):
		self.start_date = value[0:10]
	def set_end_date(self, value:str):
		self.end_date = value[0:16]
	def set_trade_place(self, value:str):
		self.trade_place = value
	def saveToDb(self, db_con):
		pass
	def __str__(self) -> str:
		return f"Num - {self.num_proc}\nType - {self.type_proc}\n\
Partner - {self.partner}\n\
PartnerINN - {self.partner_inn}\n\
Status - {self.status}\nSubj - {self.subj_proc}\nPrice - {self.summ_proc}\nLink - {self.link_proc}\n\
Region - {self.region}\n\
StartDate - {self.start_date}\n\
EndDate - {self.end_date}\n\
TradePlace - {self.trade_place}\n\
Law - {self.law_proc}\n"

def getINN(href:str):
	result = []
	r = requests.get(href, headers=headers, timeout=4)
	bs = BeautifulSoup(r.text, "lxml")
	apps_cards = bs.find_all("div", class_="registry-entry__body-value")
	for cards in apps_cards:
		result.append(cards.text)
	return result[2]


def getInfo(link: str):
	cur_proc = Procedure()
	r = requests.get(link, headers=headers, timeout=4)
	res:str = ""
	law_type = []
	law_type.append(link)
	cur_proc.set_link_proc(link)
	bs = BeautifulSoup(r.text, "lxml")
	apps_cards = bs.find_all("div", class_="sectionMainInfo__header")
	for cards in apps_cards:
		c_details = cards.find_all("div", class_="cardMainInfo__title")
		for c in c_details:
			res = c.text.rstrip().lstrip().replace('  ','')
			res = res.split('\n')
			llaw = True
			for rr in res:
				if rr:
					law_type.append(rr)
					if llaw:
						cur_proc.set_law_proc(rr)
						llaw = False
					else:
						cur_proc.set_type_proc(rr)
	apps_cards = bs.find_all("div", class_="cardMainInfo__status")
	for cards in apps_cards:
		c_details = cards.find_all("span", class_="cardMainInfo__purchaseLink")
		for c in c_details:
			res = re.findall('\d+', c.text.rstrip().lstrip())
			law_type.append(*res)
			cur_proc.set_num_proc(''.join(*res))
		c_details = cards.find_all("span", class_="cardMainInfo__state")
		for c in c_details:
			res = c.text.rstrip().lstrip()
			law_type.append(res)
			cur_proc.set_status(res)
	org_cards = bs.find_all("div", class_="sectionMainInfo__body")
	for cards in org_cards:
		a = ''
		c_details = cards.find_all("span", class_="cardMainInfo__content")
		for c in c_details:
			try:
				a = c.find('a').get('href')
			except:
				pass
			res = c.text.rstrip().lstrip().replace('  ','')
			law_type.append(res)
			cur_proc.set_partner(res)
		inn = getINN(a)
		law_type.append(inn)
		cur_proc.set_partner_inn(inn)
	price_cards = bs.find_all("div", class_="price")
	for cards in price_cards:
		c_details = cards.find_all("span", class_="cardMainInfo__content cost")
		for c in c_details:
			res = c.text.rstrip().lstrip().replace('  ','')
			law_type.append(''.join(re.findall('[\d]+[.,\d]+',res)))
			cur_proc.set_summ_proc(''.join(re.findall('[\d]+[.,\d]+',res)))
	region_cards = bs.find_all("section", class_="blockInfo__section")
	for cards in region_cards:
		result = ''
		res = cards.find('span', 'section__title')
		if res:
			res = res.text.rstrip().lstrip().replace('  ','')
			if res == 'Регион':
				result = cards.find('span', 'section__info')
				if result:
					law_type.append(result.text.rstrip().lstrip().replace('  ',''))
					cur_proc.set_region(result.text.rstrip().lstrip().replace('  ',''))
			elif res == 'Адрес электронной площадки в информационно-телекоммуникационной сети \"Интернет\"':
				result = cards.find('span', 'section__info')
				if result:
					law_type.append(result.text.rstrip().lstrip().replace('  ',''))
					cur_proc.set_trade_place(result.text.rstrip().lstrip().replace('  ',''))
			elif res == 'Наименование объекта закупки':
				result = cards.find('span', 'section__info')
				if result:
					law_type.append(result.text.rstrip().lstrip().replace('  ',''))
					cur_proc.set_subj_proc(result.text.rstrip().lstrip().replace('  ',''))
			elif res == 'Этап закупки':
				result = cards.find('span', 'section__info')
				if result:
					law_type.append(result.text.rstrip().lstrip().replace('  ',''))
					cur_proc.set_status(result.text.rstrip().lstrip().replace('  ',''))
			elif res == 'Дата и время начала срока подачи заявок':
				result = cards.find('span', 'section__info')
				if result:
					law_type.append(result.text.rstrip().lstrip().replace('  ',''))
					cur_proc.set_start_date(result.text.rstrip().lstrip().replace('  ',''))
			elif res == 'Дата и время окончания срока подачи заявок':
				result = cards.find('span', 'section__info')
				if result:
					law_type.append(result.text.rstrip().lstrip().replace('  ',''))
					cur_proc.set_end_date(result.text.rstrip().lstrip().replace('  ',''))
			
	return cur_proc

def create_connection():
	connection = None
	try:
		connection = psycopg2.connect(
			database=DB_NAME,
			user=USER_DB,
			password=PASSWORD_DB,
			host=HOST_DB,
			port=PORT_DB
		)
		print("Connection to PostgreSQL DB successful")
	except OperationalError as e:
		print(f"The error '{e}' occurred")
	return connection



def execute_query(connection, query):
	connection.autocommit = True
	cursor = connection.cursor()
	try:
		cursor.execute(query)
		print("Query executed successfully")
	except OperationalError as e:
		print(f"The error '{e}' occurred")

def saveToDb(cur_proc, con):
	
	query = f"INSERT INTO public.raw_table\
(num_proc, link_proc, status, type_proc, partner, partner_inn,\
summ_proc, count_order, region, law_proc, subj_proc, complete,\
start_date, end_date, proc_comment)\
VALUES('{cur_proc.num_proc}', '{cur_proc.link_proc}', '{cur_proc.status}',\
'{cur_proc.type_proc}', '{cur_proc.partner}', '{cur_proc.partner_inn}',\
'{cur_proc.summ_proc}', '0', '{cur_proc.region}', '{cur_proc.law_proc}', '{cur_proc.subj_proc}', 0, \
'{cur_proc.start_date}', '{cur_proc.end_date}', '');"
	try:
		execute_query(con, query)
	except Exception as e:
		print(e)



def main():
	con = create_connection()
	feeds = getRss()
	for feed in feeds:
		saveToDb(getInfo(feed),con)

if __name__ == '__main__':
	main()