import os
from SimpleParser import SimpleParser

def get_queue():
	temp = open("queue.txt", 'r')
	scrape_queue = temp.read().splitlines()
	temp.close()
	return scrape_queue

if __name__ == "__main__":
	scrape_queue = get_queue()

	for website in scrape_queue:
		# Create text file for tree view
		# Create empty completed list for already visited links