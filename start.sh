#!/bin/bash
source /home/user/portal_parsing/venv/bin/activate
python3 /home/user/portal_parsing/main.py
python3 /home/user/portal_parsing/json_to_db.py
python3 /home/user/portal_parsing/rss_parse.py
