from PIL import Image
import pytesseract

# Tesseract OCR 실행 파일의 경로 지정

# Define the path to your image
path = '/home/hj/Downloads/reseet.jpeg'

# Open the image file
image = Image.open(path)

# print(pytesseract.get_languages(config=''))

# Perform OCR on the image
text = pytesseract.image_to_string(image, lang='kor')

print(text)