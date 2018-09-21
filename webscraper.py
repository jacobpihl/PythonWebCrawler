import os
from SimpleParser import SimpleParser
from urllib.parse import urlparse
import urllib.request

current_domain = ""

def get_html(url):
	if url[:7] != "http://":
		url = "http://" + url;
	try:
		response = urllib.request.urlopen(url)
		html = response.read()
	except:
		html = ""
	return str(html)

def get_domain(link):
	parsed_domain = urlparse(link)
	domain = parsed_domain.netloc or parsed_domain.path # Just in case, for urls without scheme
	domain_parts = domain.split('.')
	if len(domain_parts) > 2:
		return '.'.join(domain_parts[-(2 if domain_parts[-1] in {
			'com', 'net', 'org', 'io', 'ly', 'me', 'sh', 'fm', 'us','se'} else 3):])
	return domain.lower()

def get_queue():
	temp = open("queue.txt", 'r')
	scrape_queue = temp.read().splitlines()
	temp.close()
	return scrape_queue

def handle_links(links, depth, maxdepth):
	# Stop printing stuff when we reach maxdepth
	if depth > maxdepth:
		return

	for cur_link in links:
		cur_link_domain = get_domain(cur_link)
		parser.cur_links = []
		new_links = []

		# If the current link is not the same domain as the website -> end
		if (cur_link in parser.visited_links):
			continue

		# Print to terminal or file with current depth as indent
		for i in range(depth):
			print('  ', end='', flush=True)
		print("|-" + cur_link)

		# If the current link has not been visited AND it is part of the same website
		# Visit it and parse
		if (current_domain == cur_link_domain):
			cur_link_HTML = get_html(cur_link)
			parser.feed(cur_link_HTML)
			new_links = parser.cur_links

		# Add current link to visited
		parser.visited_links.append(cur_link)

		# Call handle links again, with increased depth
		handle_links(new_links, depth+1, maxdepth)

if __name__ == "__main__":
	scrape_queue = get_queue()
	parser = SimpleParser()
	maxdepth = 5

	for website in scrape_queue:
		parser.visited_links = []

		# Get current domain and print to terminal
		current_domain = get_domain(website)
		print("\nCurrently parsing: " + current_domain)

		# Print to terminal or file with depth 0
		#print("" + website)

		# Get html links
		website_HTML = get_html(website)
		parser.cur_links = []
		parser.feed(website_HTML)
		website_links = parser.cur_links

		# Handle the parsed links
		handle_links(website_links, 0, maxdepth)