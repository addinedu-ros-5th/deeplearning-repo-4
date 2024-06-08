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

# 2024.06.08 code
response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

for i in response.json()['images'][0]['fields']:
    text = i['inferText']
    print(text)


# # 2024.06.08 ChatGPT
# response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
# response_data = response.json()

# extracted_text = "\n".join([i['inferText'] for i in response_data['images'][0]['fields']])
# print(extracted_text)

# lines = extracted_text.split('\n')
# details_start_index = lines.index('품목별 상세 내역') + 2
# data = []

# for line in lines[details_start_index:]:
#     if '부적합 의심' in line:
#         break
#     parts = line.split()
#     if len(parts) == 4:
#         data.append(parts[1:])
#     elif len(parts) > 4:
#         combined_parts = [' '.join(parts[1:2]), parts[2], parts[3]]
#         data.append(combined_parts)

# df = pd.DataFrame(data, columns=['품목', '원산지', '검사결과'])
# print(df)