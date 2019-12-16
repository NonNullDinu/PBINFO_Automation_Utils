import os
import requests
import re
from bs4 import BeautifulSoup
import json
import configparser
from getpass import getpass

home_url = "https://www.pbinfo.ro/"
login_url = "https://www.pbinfo.ro/login.php"


def rezolvat(s, problem_id):
    tmp_result = s.get(home_url + '?pagina=probleme&id=' + problem_id)
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


def notify(id, src_id):
    print(home_url + '?pagina=probleme&id=' + id + '&id_sursa=' + src_id +
          '#a_editor')
    pass


def locate_completed_problems(user_data, hw_v):
    with requests.Session() as s:
        result = s.get(home_url)

        rc = result.content.decode("utf-8")

        ind = rc.find('<input type="hidden" name="form_token" value="') + 46

        token = rc[ind: ind + 40: 1]

        values = {
            'form_token': token,
            'user': user_data['user'],
            'parola': user_data['parola']
        }

        login_response = s.post(login_url, values)

        if login_response.status_code != 200:
            print("Nu ne-am putut autentifica")
        tema = s.get(home_url + "?" + "&".join([str(x) + '=' + str(y) for x, y in hw_v.items()]),
                     cookies=login_response.cookies)
        soup = BeautifulSoup(tema.content.decode('utf-8'), features="lxml")
        lista = soup.find_all('a', href=re.compile('/\\?pagina=probleme&id=\\d+'))
        previd = '-1'
        p = 0
        k = 0
        for v in lista:
            id = re.findall('/\\?pagina=probleme&id=(\\d+)', v.get('href'))[0]
            if id != previd:
                p = p + 1
                ret = rezolvat(s, id)
                if ret['ans']:
                    k = k + 1
                    notify(id, ret['src'])
            previd = id
        print(f'{k}/{p} probleme rezolvate({100.0 * k / p}%)')
        s.get(home_url + 'logout.php', cookies=login_response.cookies)
        print("Deconectat")


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
    tema_id = input("Id tema: ")
    locate_completed_problems(user_data, {'pagina': 'teme-rezolvare', 'id': tema_id})
