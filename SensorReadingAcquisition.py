

import urllib.request as request
from bs4 import BeautifulSoup as BS




url = 'http://192.168.4.1'
req = request.Request(url)
client = request.urlopen(req)
htmldata = client.read()

print(htmldata)



