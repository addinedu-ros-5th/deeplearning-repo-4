from PIL import Image
import pytesseract

# Tesseract OCR 실행 파일의 경로 지정

# Define the path to your image
path = '/home/hj/Downloads/radi.jpg'

# Open the image file
image = Image.open(path)

# print(pytesseract.get_languages(config=''))

# Perform OCR on the image
text = pytesseract.image_to_string(image, lang='kor')

# Save the text to a file
with open('output_pytesseract.txt', 'w', encoding='utf-8') as file:
    file.write(text)

print("OCR 결과가 output_pytesseract.txt 파일에 저장되었습니다.")