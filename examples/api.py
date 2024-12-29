import json
import requests

register = False

with requests.Session() as s:
    name, password = input("name>"), input("password>")

    if register:
        s.post('http://127.0.0.1:5000/register', data={'name': name, 'password': password})
    else:
        s.post('http://127.0.0.1:5000/login', data={'name': name, 'password': password})

    res = s.get('http://127.0.0.1:5000/api')
    res = json.loads(res.text)
    print('name:', res['name'])
    print('discriminator:', res['discriminator'])