from html.parser import HTMLParser
from urllib import parse

class SimpleParser(HTMLParser):

	LINK_START_TAG = "a"
	LINK_TAG = "href"
	cur_links = []
	visited_links = []

	def handle_starttag(self, tag, attrs):
		if tag == self.LINK_START_TAG:
			for attr in attrs:
				if attr[0] == self.LINK_TAG:
					# Encountered link
					# if link is not anchor, append to list
					link = attr[1].lower()
					if "#" not in link:
						self.cur_links.append(link)