from getpass import getpass
import requests
import re
import configparser
import os
from bs4 import BeautifulSoup

home_url = "https://www.pbinfo.ro/"
login_url = "https://www.pbinfo.ro/login.php"


def download_sources(user_data, folder_path, hw_v):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
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
            print("Could not log in")
            exit(1)
        else:
            print("Logged in successfully")
        tema = s.get(home_url + hw_v['pagina'] + hw_v['id'] + '/' + hw_v['nume'],
                     cookies=login_response.cookies)
        tema_rc = tema.content.decode('utf-8')
        soup = BeautifulSoup(tema_rc, features="lxml")
        lista = soup.find_all('a', href=re.compile("/detalii-evaluare/(\\d+)"))
        for prob in lista:
            prob_id = re.search('/detalii-evaluare/(\\d+)', prob.get('href')).group(1)
            print("Downloading source " + prob_id)
            response = s.get(home_url + 'php/descarca-sursa.php?id=' + prob_id, cookies=login_response.cookies)
            fname = re.findall("filename=(.+)", response.headers['content-disposition'])[0]
            with open(folder_path + "/" + fname, "w") as f:
                f.write(response.text)
                f.close()
        s.get(home_url + 'logout.php', cookies=login_response.cookies)
        print("Logged out")


if __name__ == '__main__':
    if os.path.exists('user_data.ini'):
        config = configparser.ConfigParser()
        config.read('user_data.ini')
        ud = config['pbinfo']
    else:
        username = input("Username: ")
        password = getpass()
        ud = {
            'user': username,
            'parola': password
        }
    id_tema = input("Id tema: ")
    nume_tema = input("Nume tema(exact asa cum apare in link): ")
    hw_v = {'pagina': 'teme/rezolvare/',
            'id': id_tema,
            'nume': nume_tema}
    folder = input("Folder(Lasati gol pentru default): ")
    if len(folder) == 0:
        folder = nume_tema

    download_sources(ud, folder, hw_v)
