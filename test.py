#!/usr/bin/env python3

import base64
import time

import requests

apikey = "/8MZw6ClhyGEfttDgin2/8amFu5MhEKJJWt+e5qB0jc="

headers = {
    "Authorization": "Bearer " + apikey
}

with open("test-prog/prog", "rb") as f:
    binary = base64.b64encode(f.read()).decode()

r = requests.post("http://localhost:5000/request_decomp", headers=headers, json={"requestor": "test", "binary": binary})
ret = r.json()

id = ret["id"]

while True:
    r = requests.get(f"http://localhost:5000/status/{id}", headers=headers)
    ret = r.json()
    print(ret)
    if ret["analysis_status"] == "completed":
        break
    time.sleep(1)

r = requests.get(f"http://localhost:5000/get_decompilation/{id}", headers=headers)
ret = r.json()

print(base64.b64decode(ret["output"].encode()).decode())
