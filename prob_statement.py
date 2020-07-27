#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests
from os import sys

home_url = "https://www.pbinfo.ro/"


def full_problem_statement(session, id_nume):
	answer = session.get(home_url + 'search.php?search_box=' + id_nume.replace(' ', '+').lower())
	if answer.status_code != 200:
		print("Am avut o problema si serverul a returnat " + answer.status_code)
		return None

	bs = BeautifulSoup(answer.content.decode('utf-8'), features='lxml')
	statement = bs.find('article', id='enunt')
	table = bs.find('table', {'class': ['table', 'table-borded']})
	for ad in statement.find_all("ins", {'class': 'adsbygoogle'}):
		ad.decompose()
	for script in statement.find_all("script"):
		script.decompose()
	for img in statement.find_all("img"):
		if img.get('src')[0] == '/':
			img['src'] = home_url + img['src'][1:]
	return str(table) + '\n' + str(statement)

if __name__ == "__main__":
	print("Id/nume: ", file=sys.stderr, end="")
	id_nume = input('')
	with requests.Session() as s:
		print(full_problem_statement(s, id_nume))