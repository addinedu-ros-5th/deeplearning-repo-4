import pandas as pd

# 'output_cleaned.txt' 파일 읽기
with open('output_cleaned.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# 텍스트를 줄 단위로 분할하여 리스트로 변환
lines = text.strip().split('\n')

columns = ['품목', '원산지', '검사결과(검사항목: 요오드·세슘)']
data = []

# 인덱스를 통해 데이터 추출
for i in range(6, len(lines), 4):
    item = lines[i+1:i+4]
    data.append(item)

# 데이터프레임 생성
df = pd.DataFrame(data, columns=columns)

print(df)