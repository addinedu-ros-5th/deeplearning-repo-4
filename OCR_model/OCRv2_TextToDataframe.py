import pandas as pd
import mysql.connector
import OCRv2_DB_Info as DB
import os

# 'output_cleaned.txt' 파일 읽기
with open('output_cleaned.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# 텍스트를 줄 단위로 분할하여 리스트로 변환
lines = text.strip().split('\n')

columns = ['연번', '품목', '원산지', '검사결과(검사항목: 요오드·세슘)']
data = []

# 인덱스를 통해 데이터 추출
for i in range(6, len(lines), 4):
    item = lines[i:i+4]
    data.append(item)

# 데이터프레임 생성
df = pd.DataFrame(data, columns=columns)
df.to_csv("output.csv", index=False)
print(df)

# 데이터베이스 연결 설정
dldb = mysql.connector.connect(
    host=DB.host,
    port=DB.port,
    user=DB.user,
    password=DB.password,
    database=DB.database,
    charset='utf8mb4',
    use_unicode=True
)

cursor = dldb.cursor()

# 테이블 생성 쿼리
create_table_query = """
CREATE TABLE IF NOT EXISTS radioactivity_pollution (
    No VARCHAR(16),
    Item VARCHAR(16),
    Origin VARCHAR(16),
    Test_Result_Iodine_Cesium VARCHAR(16)
) CHARACTER SET utf8mb4
"""
cursor.execute(create_table_query)

# CSV 파일 경로 출력
print(DB.csv_file_path)

# CSV 파일이 존재하면 데이터 삽입
if os.path.exists(DB.csv_file_path):
    try:
        df = pd.read_csv(DB.csv_file_path, encoding='utf-8')
        df.columns = ['No', 'Item', 'Origin', 'Test_Result_Iodine_Cesium']
        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO radioactivity_pollution (No, Item, Origin, Test_Result_Iodine_Cesium)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, tuple(row))
        dldb.commit()
    except Exception as e:
        print(f"Error: {e}")

cursor.close()
dldb.close()