import requests
import uuid
import time
import json
import pandas as pd
import OCRv2_APIinfo as API

api_url = API.api_url
secret_key = API.secret_key
image_file = API.image_file

request_json = {
    'images': [
        {
            'format': 'jpg',
            'name': 'demo'
        }
    ],
    'requestId': str(uuid.uuid4()),
    'version': 'V2',
    'timestamp': int(round(time.time() * 1000))
}

payload = {'message': json.dumps(request_json).encode('UTF-8')}
files = [
  ('file', open(image_file,'rb'))
]
headers = {
  'X-OCR-SECRET': secret_key
}

response = requests.request("POST", api_url, headers=headers, data=payload, files=files)

text = ""
for i in response.json()['images'][0]['fields']:
    text += i['inferText'] + '\n'

with open('output.txt', 'w', encoding='utf-8') as file:
    file.write(text)

print("텍스트를 'output.txt' 파일에 저장했습니다.")