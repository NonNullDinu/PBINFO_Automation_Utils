import requests
from bs4 import BeautifulSoup
import os
import configparser
from getpass import getpass

headers = {
	'authority': 'www.pbinfo.ro',
	'accept': '*/*',
	'origin': 'https://www.pbinfo.ro',
	'x-requested-with': 'XMLHttpRequest',
	'sec-fetch-dest': 'empty',
	'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'sec-fetch-site': 'same-origin',
	'sec-fetch-mode': 'cors',
	'accept-language': 'en-US,en;q=0.9'
}

home_url = "https://www.pbinfo.ro/"
login_url = "https://www.pbinfo.ro/login.php"

if __name__ == '__main__':
	if os.path.exists('user_data.ini'):
		config = configparser.ConfigParser()
		config.read('user_data.ini')
		user_data = config['pbinfo']
		del config
	else:
		username = input("Username: ")
		password = getpass()
		user_data = {
			'user': username,
			'parola': password
		}
	with requests.Session() as s:
		result = s.get(home_url)

		rc = result.content.decode("utf-8")

		soup = BeautifulSoup(rc, features="lxml")
		token = soup.find('input', {'type': "hidden", 'name': "form_token"}).get('value')

		values = {
			'form_token': token,
			'user': user_data['user'],
			'parola': user_data['parola']
		}

		login_response = s.post(login_url, values)
		if login_response.status_code != 200:
			print("Nu ne-am putut autentifica")
		nameid = input("Nume/id problema: ")
		prob_statement_response = s.get(home_url+"search.php?search_box=" + nameid)
		rc = prob_statement_response.content.decode('utf-8')
		soup = BeautifulSoup(rc, features="lxml")
		form = soup.find('form', {'id': 'form-incarcare-solutie'})
		submintFormToken = form.find('input', {'name': 'form_token', 'id': 'form_submit_token'}).get('value')
		idprob = form.find('input', {'name': 'id'}).get('value')
		pagina = form.find('input', {'name': 'pagina'}).get('value')
		file = input('Sursa: ')
		with open(file, "r") as f:
			sursa = f.read()
		if file.endswith('.c'):
			lang = 'c'
		elif file.endswith('.cpp'):
			lang = 'cpp'
		elif file.endswith('.php'):
			lang = 'php'
		elif file.endswith('.py'):
			lang = 'py'
		elif file.endswith('.py3'):
			lang = 'py3'
		elif file.endswith('.pas'):
			lang = 'pas'
		elif file.endswith('.java'):
			lang = 'java'
		data = {
			'form_token': submintFormToken,
			'id': idprob,
			'pagina': pagina,
			'limbaj_de_programare': lang,
			'sursa': sursa,
		}
		submit_response = s.post(home_url + 'ajx-module/php-solutie-incarcare.php', headers=headers, data=data)
		with open("local.html", "w") as f:
			f.write(submit_response.content.decode('utf-8'))
