import os
import urllib.request
from SimpleParser import SimpleParser
from urllib.parse import urlparse
import networkx as nx
import matplotlib.pyplot as plt
import tldextract

import plotly.plotly as py
import plotly.graph_objs as go

current_domain = ""
visited_links = []
cur_graph = None
cur_file = None
total_pages_crawled = 0
maxdepth = 5
starting_depth = 0

def create_file(name):
	global cur_file
	cur_file = open(name + ".txt", 'w+', buffering=1)


def close_file():
	cur_file.close()


def write_to_file(text, depth):
	for i in range(depth):
		cur_file.write(" ")
	cur_file.write("|- " + text + "\n")


def get_html(url):
	try:
		response = urllib.request.urlopen(url)
		html = response.read()
	except:
		html = ""
	return str(html)


def get_domain(link):
	ext = tldextract.extract(link)
	return ext.registered_domain


def get_domain_deprecated(link):
	parsed_domain = urlparse(link)
	domain = parsed_domain.netloc
	domain_parts = domain.split('.')
	if len(domain_parts) > 2:
		return str('.'.join(domain_parts[-(2 if domain_parts[-1] in {
			'com', 'net', 'org', 'io', 'ly', 'me', 'sh', 'fm', 'us','se', 'uz'} else 3):])).lower()
	return str(domain.lower())


def get_queue():
	temp = open("queue.txt", 'r')
	scrape_queue = temp.read().splitlines()
	temp.close()
	return scrape_queue


def add_nodes(root_node, neighbours):
	cur_graph.add_node(root_node, label=str(root_node))

	for neighbour in neighbours:
		cur_graph.add_edge(root_node, neighbour)


def display_graph():
	print("Displaying graph")
	nx.draw(cur_graph)
	plt.show()


# Plots graph online at plot.ly
def display_advanced_graph():
	pos = nx.random_layout(cur_graph)

	edge_trace = go.Scatter(
		x=[],
		y=[],
		line=dict(width=0.5,color='#888'),
		hoverinfo='none',
		mode='lines')

	for edge in cur_graph.edges():
		x0, y0 = pos[edge[0]][0], pos[edge[0]][1]
		x1, y1 = pos[edge[1]][0], pos[edge[1]][1]
		edge_trace['x'] += tuple([x0, x1, None])
		edge_trace['y'] += tuple([y0, y1, None])

	node_trace = go.Scatter(
		x=[],
		y=[],
		text=[],
		mode='markers',
		hoverinfo='text',
		marker=dict(
			showscale=True,
			colorscale='YlGnBu',
			reversescale=True,
			color=[],
			size=10,
			colorbar=dict(
				thickness=15,
				title='Node Connections',
				xanchor='left',
				titleside='right'
			),
			line=dict(width=2)))

	for node in cur_graph.nodes():
		x, y = pos[node][0], pos[node][1]
		node_trace['x'] += tuple([x])
		node_trace['y'] += tuple([y])

	for node, adjacencies in enumerate(cur_graph.adjacency()):
		node_trace['marker']['color']+=tuple([len(adjacencies[1])])
		node_info = '# of connections: '+str(len(adjacencies[1]))
		node_trace['text'] += tuple([node_info])

	fig = go.Figure(data=[edge_trace, node_trace],
			 layout=go.Layout(
				title='<br>Graph',
				titlefont=dict(size=16),
				showlegend=False,
				hovermode='closest',
				margin=dict(b=20,l=5,r=5,t=40),
				xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
				yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

	py.iplot(fig, filename=str(current_domain))


def format_new_links(links):
	formatted = []
	for link in links:
		link_domain = get_domain(link)
		if link_domain == "":
				link_domain = current_domain
				if link[:1] != "/":
					link = "/" + link
				link = "http://" + current_domain + link
		formatted.append(link)
	return formatted


def handle_links(links, depth, maxdepth):
	global total_pages_crawled
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
		print("Total pages crawled: " + str(total_pages_crawled))
		write_to_file(cur_link, depth)

		# If the current link has not been visited AND it is part of the same website
		# Visit it and parse
		if (current_domain == cur_link_domain):
			cur_link_HTML = get_html(cur_link)
			parser.feed(cur_link_HTML)
			new_links = parser.cur_links

		# Format the gathered links to something that can be connected to
		formatted_new_links = format_new_links(new_links)

		# Add links to graph, add label to each node
		add_nodes(cur_link, formatted_new_links)

		# Add current link to visited
		visited_links.append(cur_link)

		# Call handle links again, with increased depth
		total_pages_crawled += 1
		handle_links(formatted_new_links, depth+1, maxdepth)


if __name__ == "__main__":
	scrape_queue = get_queue()
	parser = SimpleParser()

	for website in scrape_queue:
		total_pages_crawled = 0
		visited_links = []
		cur_graph = nx.Graph()

		# Get current domain and print to terminal
		current_domain = get_domain(website)
		print("\nCurrently crawling: " + current_domain)

		# Create new file for writing to
		create_file(current_domain)
		write_to_file(website, starting_depth)

		# Get html links
		website_HTML = get_html(website)
		parser.cur_links = []
		parser.feed(website_HTML)
		website_links = parser.cur_links
		total_pages_crawled += 1

		visited_links.append(website)
		formatted_website_links = format_new_links(website_links)

		# Add links to graph
		add_nodes(website, formatted_website_links)

		# Handle the parsed links
		handle_links(formatted_website_links, starting_depth, maxdepth)
		close_file()
		display_graph()
		# display_advanced_graph()	# Generates more advanced graph using plot.ly

		print("Done crawling: " + current_domain)