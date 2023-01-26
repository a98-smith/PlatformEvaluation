


import urllib.request as ul
import validators
from bs4 import BeautifulSoup as soup

# Define URL to scrape
url = ""

# Obtain URL from user if left undefined
while not validators.url(url):
	url = input('Enter the full URL for the webpage you would like to scrape: ')

	if not validators.url(url):
		print('#### The URL you have provided is invalid. Please try again. ####')

print('Scraping '+ url + ', please wait.') 


req = ul.Request(url, headers={'User-Agent':'Mozilla/5.0'}) # Sets headers to prevent getting botted. Simulates a user browsing on Firefox.
client = ul.urlopen(req) # Opens the given URL with the headers provided
htmldata = client.read() # Scrapes the HTML data from the webpage
client.close() # Closes the client

# Create a soup object from the page data for further analysis
pagesoup = soup(htmldata, "html.parser")

### Further analysis to come here ###