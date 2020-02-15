import os
import requests
import re
from bs4 import BeautifulSoup
import json
import configparser
from getpass import getpass
import subprocess

home_url = "https://www.pbinfo.ro/"
login_url = "https://www.pbinfo.ro/login.php"
browser = 'chromium'

def rezolvat(s, problem_id, prob_nume):
	tmp_result = s.get(home_url + 'probleme/' + problem_id + '/' + prob_nume)
	txt = tmp_result.content.decode('utf-8')
	uid = re.findall('{id_problema : ' + problem_id + ' , id_user : (\\d+)}', txt)[0]
	tmp_result2 = s.get(
		home_url + 'ajx-module/ajx-solutii-lista-json.php?id_user=' + uid + '&id_problema=' + problem_id)
	
	json_data = json.loads(tmp_result2.content.decode('utf-8'))
	for v in json_data['surse']:
		if v['scor'] == '100':
			return {'ans': True,
					'src': v['id']}
	return {'ans': False,
			'src': None}


def notify(id_prob, src_id, prob_name):
	url = home_url + 'probleme/' + id_prob + '/' + prob_name + '/?id_sursa=' + src_id + '#a_editor'
	print(url)
	subprocess.run([browser, url])
	pass


def locate_completed_problems(user_data, hw_v):
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
		tema = s.get(home_url + hw_v['pagina'] + hw_v['id'] + '/' + hw_v['nume'],
					 cookies=login_response.cookies)
		soup = BeautifulSoup(tema.content.decode('utf-8'), features="lxml")
		lista = soup.find_all('a', href=re.compile('/probleme/\\d+/.*'))
		previd = '-1'
		p = 0
		k = 0
		for v in lista:
			capt = re.search('/probleme/(\\d+)/(.*)', v.get('href'))
			prob_id = capt.group(1)
			prob_name = capt.group(2)
			if prob_id != previd:
				p = p + 1
				ret = rezolvat(s, prob_id, prob_name)
				if ret['ans']:
					k = k + 1
					notify(prob_id, ret['src'], prob_name)
			previd = prob_id
		print(f'{k}/{p} probleme rezolvate({100.0 * k / p}%)')
		s.get(home_url + 'logout.php', cookies=login_response.cookies)
		print("Deconectat")


if __name__ == '__main__':
	if os.path.exists('user_data.ini'):
		config = configparser.ConfigParser()
		config.read('user_data.ini')
		ud = config['pbinfo']
		del config
	else:
		username = input("Username: ")
		password = getpass()
		ud = {
			'user': username,
			'parola': password
		}
	tema_id = input("Id tema: ")
	tema_nume = input("Numele temei: ")
	locate_completed_problems(ud, {'pagina': 'teme/rezolvare/', 'nume': tema_nume, 'id': tema_id})
