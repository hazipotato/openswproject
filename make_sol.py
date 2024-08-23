import google.generativeai as genai
import os
import subprocess
from IPython.display import  Markdown
import requests

with open('mun.txt','r',encoding='utf-8') as file:
    content=file.read()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key='AIzaSyBgUbBTUCFh_Ee5ExfhFCoXIZB8YXC8IqA')
model=genai.GenerativeModel('gemini-1.5-flash')
response=model.generate_content(content)



print(Markdown(response.text).data)