import requests

payload = {'key1': 'value1', 'key2[]': ['value2', 'value3']}
r = requests.post("controller/")