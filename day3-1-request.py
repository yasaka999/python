import requests
url="http://baidu.com"
result=requests.get(url)
print(result.text)