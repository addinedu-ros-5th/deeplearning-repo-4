# output.txt 파일 읽기
with open('output.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# '연번'부터 '부적합 의심'까지의 텍스트 추출
start_index = text.find('연번')
end_index = text.find('부적합 의심')

if start_index != -1 and end_index != -1:
    extracted_text = text[start_index:end_index]
    print(extracted_text)

    # 'output_cleaned.txt' 파일에 추출된 텍스트 저장
    with open('output_cleaned.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(extracted_text)
else:
    print("텍스트에서 '연번' 또는 '부적합 의심'을 찾을 수 없습니다.")
