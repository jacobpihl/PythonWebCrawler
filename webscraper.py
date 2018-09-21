import os
from SimpleParser import SimpleParser
from urllib.parse import urlparse
import urllib.request

current_domain = ""
visited_links = []
cur_file = None

def create_file(name):
	file = open(name + ".txt", 'w+', buffering=1)
	return file

def close_file():
	cur_file.close()

def write_to_file(text, depth):
	for i in range(depth):
		cur_file.write(" ")
	cur_file.write("|- " + text + "\n")

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
		return str('.'.join(domain_parts[-(2 if domain_parts[-1] in {
			'com', 'net', 'org', 'io', 'ly', 'me', 'sh', 'fm', 'us','se'} else 3):])).lower()
	return str(domain.lower())

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
		if (cur_link in visited_links):
			continue

		# Write to file with current depth as indent
		write_to_file(cur_link, depth)

		# If the current link has not been visited AND it is part of the same website
		# Visit it and parse
		if (current_domain == cur_link_domain):
			cur_link_HTML = get_html(cur_link)
			parser.feed(cur_link_HTML)
			new_links = parser.cur_links

		# Add current link to visited
		visited_links.append(cur_link)

		# Call handle links again, with increased depth
		handle_links(new_links, depth+1, maxdepth)

if __name__ == "__main__":
	scrape_queue = get_queue()
	parser = SimpleParser()
	maxdepth = 5
	starting_depth = 0

	for website in scrape_queue:
		if website[:7] != "http://":
			website = "http://" + website;
		visited_links = []

		# Get current domain and print to terminal
		current_domain = get_domain(website)
		print("\nCurrently parsing: " + current_domain)

		# Create new file for writing to
		cur_file = create_file(current_domain)
		write_to_file(website, starting_depth)

		# Get html links
		website_HTML = get_html(website)
		parser.cur_links = []
		parser.feed(website_HTML)
		website_links = parser.cur_links

		visited_links.append(website)

		# Handle the parsed links
		handle_links(website_links, starting_depth, maxdepth)

		close_file()
		print("Done parsing: " + current_domain)