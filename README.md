# portal_parsing

pip install virtualenv
python3 -m venv env
source venv/bin/activate 

pip3 install -r requirements.txt
pip3 freeze > requirements.txt

need file my_set.py with db config:
DB_NAME = ''
USER_DB = ''
URL = 'https://zakupki.mos.ru/purchase/list'
PASSWORD_DB = ''
HOST_DB = ''
PORT_DB = ''

main.py - start parsing and save result in order.json
json_to_db.py - from order.json to table raw_data in database


