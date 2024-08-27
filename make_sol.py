import google.generativeai as genai
import os
import subprocess
from IPython.display import Markdown
import requests
import re

# 'mun.txt' 파일을 읽음
with open('mun.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Google Generative AI 구성
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key='AIzaSyBgUbBTUCFh_Ee5ExfhFCoXIZB8YXC8IqA')

# 모델 설정
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(content)

# HTML 태그 없이 출력하기 위해 태그를 제거하는 함수
def remove_html_tags(text):
    text = re.sub(r'</?i>', '', text)  # <i>와 </i> 태그를 제거
    return text

# 출력 결과에서 HTML 태그를 제거한 텍스트를 출력
output_text = remove_html_tags(response.text)
print(output_text)
