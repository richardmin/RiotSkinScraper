'''
Author: Richard Min (richardmin97@gmail.com)
Uses httplib2 and BeautifulSoup to prase the riot skins sales webpage, reading what it has already found from a text file and comparing that
to what is new on the page, printing that out and updating the text file
This code is licensed under MIT creative license.
'''

#!/usr/bin/env python
import httplib2
from BeautifulSoup import BeautifulSoup

class PageNotFound(RuntimeError): pass


class RiotSalesScraper(object):
	def __init__(self, url="http://na.leagueoflegends.com/en/news/store/sales", timeout=15):
		self.url, self.timeout = url, int(timeout)

	def fetch_sales(self):
		http = httplib2.Http(timeout=self.timeout)
		headers, content = http.request(self.url)

		if not headers.get('status') == '200':
			raise PageNotFound("Could not fetch page from '%s'. Got %s." % (self.url, headers['status']))

		return content

	def parse_sales(self, content):
		soup = BeautifulSoup(content)
		raw = soup.findAll("a" , { "class" : "lol-core-file-formatter" })
		processed = []
		for line in raw:
			if len(line['title']) < 24:
				continue
			if not line['title'][:24] == "Champion and skin sale: ":
				continue
			processed.append(str(line['href']))
		return processed

	def get_sales(self):
		content = self.fetch_sales()
		return self.parse_sales(content)

	def newSales(self):
		releases = self.get_sales()
		
		text_file = open('alreadyfound.txt', 'r')
		rawlines = text_file.readlines()
		lines = []
		for rawline in rawlines:
			lines.append(rawline[:-1])
		diff = []
		for release in releases:
			if not release in lines:
				diff.append(release)
			
		return diff
		
	def fetch_salepage(self, url):
		http = httplib2.Http(timeout=self.timeout)
		headers, content = http.request('http://na.leagueoflegends.com'+url)

		if not headers.get('status') == '200':
			raise PageNotFound("Could not fetch page from '%s'. Got %s." % ('http://na.leagueoflegends.com'+url, headers['status']))

		return content
		
	def parse_salepage(self, content):
		soup = BeautifulSoup(content)
		
#		rawprices = soup.findAll("strike")
		raw = soup.findAll("h4")
		#raw = []
		skinsales = []
		
		skinsales.append(str(raw[1].contents[0]))
		skinsales.append(str(raw[2].contents[0]))
		skinsales.append(str(raw[3].contents[0]))
		
		champsales = []
		
		champsales.append(str(raw[5].find('a').contents[0].strip()))
		champsales.append(str(raw[6].find('a').contents[0].strip()))
		champsales.append(str(raw[7].find('a').contents[0].strip()))

		rawprices = soup.findAll("strike")
		prices = []
		for rawprice in rawprices:
			prices.append(int(rawprice.contents[0])/2)
		return skinsales+champsales+prices
		
	def get_salepage(self, url):
		content = self.fetch_salepage(url)
		return self.parse_salepage(content)
		
	def processSales(self): 
		urls = self.newSales()
		prepend = ''
		
		for url in urls:
			print self.get_salepage(url)
			prepend = prepend + url +'\n'
		with file('alreadyfound.txt', 'r') as original: data = original.read()
		with file('alreadyfound.txt', 'w') as modified: modified.write(prepend + data)

			
if __name__ == '__main__':
	scraper = RiotSalesScraper()
	releases = scraper.get_sales()
	scraper.processSales()