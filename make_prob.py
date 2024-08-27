import cv2
from pytesseract import pytesseract
from PIL import Image
import random
import numpy as np
import re
from pykospacing import Spacing
from bs4 import BeautifulSoup
from pix2tex.cli import LatexOCR
from collections import Counter

custom_config = r'--oem 1 --psm 6'

# 이미지 파일 이진화 작업
image = cv2.imread('image.png')
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
_, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 문제 한글 텍스트 추출
pil_image = Image.fromarray(binary_image)
extracted_text = pytesseract.image_to_string(pil_image, lang='kor', config=custom_config)

# hocr 파일 생성
hocr = pytesseract.image_to_pdf_or_hocr(image, extension='hocr', lang='kor')

with open('output_file.hocr', 'wb') as f:
    f.write(hocr)

with open('output.hocr', 'r', encoding='utf-8') as file:
    hocr_content = file.read()

soup = BeautifulSoup(hocr_content, 'html.parser')

words = soup.find_all('span', class_='ocrx_word')

bounding_boxes = []

for word in words:
    text = word.get_text()
    title = word.get('title', '')
    if 'bbox' in title:
        bbox = title.split(';')[0].split()[1:]
        x1, y1, x2, y2 = map(int, bbox)
        
        # 숫자가 포함된 단어인지 확인
        if re.search(r'\d', text):
            bounding_boxes.append((x1, y1, x2, y2))

# 수식 부분만 crop하기
for idx, bbox in enumerate(bounding_boxes):
    x1, y1, x2, y2 = bbox
    # 이미지 잘라내기
    cropped_image = image[y1:y2, x1:x2]
    
    # 자른 이미지 저장
    cropped_image_path = f'cropped_image.png'
    cv2.imwrite(cropped_image_path, cropped_image)

    cropped_img = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

# cropped image 이진화 작업 
image = cv2.imread('cropped_image.png')
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
_, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 수식 부분 텍스트로 추출
pil_image = Image.fromarray(binary_image)

model = LatexOCR()
extracted_equ = model(pil_image)

# x 또는 y로 변환
def replace_braced_letters(extracted_equ):
    pattern = r'\{([a-zA-Z])\}'
    matches = re.findall(pattern, extracted_equ)

    if len(matches) > 1:
        counter = Counter(matches)
        
        if len(counter) == 1:
            result = re.sub(pattern, '{x}', extracted_equ)
        else:
            unique_symbols = {chr(ord('x') + i) for i in range(len(counter))}
            symbol_map = {char: symbol for char, symbol in zip(counter.keys(), unique_symbols)}

            def replace_match(match):
                char = match.group(1)
                return f'{{{symbol_map[char]}}}'

            result = re.sub(pattern, replace_match, extracted_equ)
    else:
        result = re.sub(pattern, '{x}', extracted_equ)

    return result

extracted_equ = replace_braced_letters(extracted_equ)

# 계수 및 상수 바꾸기
def replace_numbers_in_latex(extracted_equ):
    def replace_with_random(match):
        return str(random.randint(1, 99))
    
    number_pattern = re.compile(r'\d+')
    
    new_equ = number_pattern.sub(replace_with_random, extracted_equ)
    
    return new_equ

new_equ = replace_numbers_in_latex(extracted_equ)

# 최종 출력 전 띄어쓰기 교정
def contains_korean(text):
    pattern = re.compile(r'[ㄱ-ㅎ가-힣]+')
    return bool(re.search(pattern, text))

def remove_spaces(text):
    return ''.join(text.split())

parts = extracted_text.split('\n')

for i in range(len(parts)-1):
    if contains_korean(parts[i]):
        parts[i] = remove_spaces(parts[i])
        spacing = Spacing()
        parts[i] = spacing(parts[i])
        print(parts[i], "\n\n\n")

# HTML로 수식 변환
def convert_latex_to_html(latex_str):
    html_str = latex_str
    html_str = html_str.replace(r'\left(', '(').replace(r'\right)', ')')
    html_str = html_str.replace(r'\mathcal{', '<i>').replace(r'}', '</i>')
    html_str = html_str.replace(r'$', '')  # 제거 LaTeX 수식의 구분 기호
    return html_str

with open('mun.txt', 'w', encoding='utf-8') as file:
    for i in range(len(parts)-1):
        if contains_korean(parts[i]):
            file.write(parts[i] + '\n')
    file.write(convert_latex_to_html(new_equ))
    file.write('\n\n위 문제의 풀이를 알려줘. 알려준 풀이에서 LaTeX 수식 언어로 출력하는 부분은 자연어 수식으로 출력해줘. 컴퓨터 언어 없이 자연어와 수식으로만 구성된 풀이를 출력해야해')

with open('mun.txt', 'r', encoding='utf-8') as file:
    content = file.read()

print(convert_latex_to_html(new_equ))
