import json
import requests

api_url = 'http://127.0.0.1:5000' # change if required
register = False

with requests.Session() as s:
    name, password = input("name>"), input("password>")

    if register:
        s.post(f'{api_url}/register', data={'name': name, 'password': password})
    else:
        s.post(f'{api_url}/login', data={'name': name, 'password': password})

    res = s.get(f'{api_url}/api')
    res = json.loads(res.text)
    print('name:', res['name'])
    print('discriminator:', res['discriminator'])