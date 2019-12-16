from getpass import getpass
import requests
import re
import configparser
import os

home_url = "https://www.pbinfo.ro/"
login_url = "https://www.pbinfo.ro/login.php"


def download_sources(user_data, folder, hw_v):
    if not os.path.exists(folder):
        os.mkdir(folder)
    with requests.Session() as s:
        result = s.get(home_url)

        RC = result.content.decode("utf-8")

        ind = RC.find('<input type="hidden" name="form_token" value="') + 46

        TOKEN = RC[ind: ind + 40: 1]

        values = {
            'form_token': TOKEN,
            'user': user_data['user'],
            'parola': user_data['parola']
        }

        login_response = s.post(login_url, values)

        if login_response.status_code != 200:
            print("Could not log in")
            exit(1)
        else:
            print("Logged in successfully")
        tema = s.get(home_url + "?" + "&".join([str(x) + '=' + str(y) for x, y in hw_v.items()]),
                     cookies=login_response.cookies)
        temaRC = tema.content.decode('utf-8')
        lista = re.findall("<a href=\"/\\?pagina=detalii-evaluare&id=(\\d+)\"", temaRC)
        for id in lista:
            print("Downloading source " + id)
            response = s.get(home_url + 'php/descarca-sursa.php?id=' + id, cookies=login_response.cookies)
            fname = re.findall("filename=(.+)", response.headers['content-disposition'])[0]
            with open(folder + "/" + fname, "w") as f:
                f.write(response.text)
                f.close()
        s.get(home_url + 'logout.php', cookies=login_response.cookies)
        print("Logged out")


if __name__ == '__main__':
    if os.path.exists('user_data.ini'):
        config = configparser.ConfigParser()
        config.read('user_data.ini')
        user_data = config['pbinfo']
    else:
        username = input("Username: ")
        password = getpass()
        user_data = {
            'user': username,
            'parola': password
        }
    id_tema = input("Id tema: ")
    hw_v = {'pagina': 'teme-rezolvare',
            'id': id_tema}
    folder = input("Folder(Lasati gol pentru default): ")
    if len(folder) == 0:
        folder = f"tema{id_tema}"

    download_sources(user_data, folder, hw_v)
