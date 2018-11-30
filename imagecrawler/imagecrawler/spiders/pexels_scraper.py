#!/usr/bin/python
import scrapy
import re
from scrapy.linkextractor import LinkExtractor
from scrapy.selector import Selector
import logging
from imagecrawler.items import ImagecrawlerItem
import urllib, cStringIO
from PIL import Image
import requests
from io import BytesIO

class PexelsScraper(scrapy.Spider): 
	name = "pexels" 
	# Define the regex we'll need to filter the returned links 
	url_matcher = re.compile('^https:\/\/www\.skyscanner\.de\/') 
	src_extractor = re.compile('src="([^"]*)"')
	tags_extractor = re.compile('alt="(.*?)"')
	domain_extractor = re.compile('((http[s]?)?:\/\/(www)?\..*?\.[a-z]+)')
	filename_extractor = re.compile('\/(?!.*\/)(.*?)\.(jpg|png)')
	# Create a set that'll keep track of ids we've crawled 
	crawled_urls = set() 
	crawled_images = set()
	start_urls = ''
	# image_height = 0
	# image_width = 0
	
	def __init__(self, *args, **kwargs):
		super(PexelsScraper, self).__init__(*args, **kwargs)
		self.start_urls = [kwargs.get('start_url')] 
	
	def start_requests(self): 
		print self.start_urls[0]
		url = self.start_urls[0]
		yield scrapy.Request(url, self.parse)
				
	def parse(self, response): 
		body = Selector(text=response.body)
		images = body.css('img').extract()
		for image in images:
			image = image.encode("utf-8")
			if PexelsScraper.src_extractor.findall(image):
				img_url = PexelsScraper.src_extractor.findall(image)[0]
				if img_url not in PexelsScraper.crawled_urls:
					if 'http' not in img_url:
						print img_url
						print self.start_urls[0]
						print PexelsScraper.domain_extractor.findall(self.start_urls[0])
						img_url = PexelsScraper.domain_extractor.findall(self.start_urls[0])[0][0] + img_url
						print img_url
					PexelsScraper.crawled_urls.add(img_url)
					tags = ""
					img_name = ""
					img_type = ""
					if PexelsScraper.tags_extractor.findall(image):
						tags = PexelsScraper.tags_extractor.findall(image)[0].replace(',', '').lower()
					print img_url, tags 
					if '/' in img_url and len(PexelsScraper.filename_extractor.findall(img_url)) > 0:
						img_name = PexelsScraper.filename_extractor.findall(img_url)[0][0]
						img_type = PexelsScraper.filename_extractor.findall(img_url)[0][1]
						print img_name
					data = requests.get(img_url).content
					im = Image.open(BytesIO(data))
					width, height = im.size
					# PexelsScraper.image_width = im.size[0]
					# PexelsScraper.image_height = im.size[1]
					img_aspect_ratio = self.calculate_aspect(width, height)
					yield ImagecrawlerItem(source_url=response.url,img_url=img_url, alternate_text=tags, img_width=width, img_height=height, img_name=img_name, img_type=img_type, img_aspect_ratio=img_aspect_ratio)
					
		link_extractor = LinkExtractor()
		next_links = [link.url for link in link_extractor.extract_links(response) if not self.is_extracted(link.url)]
		# Crawl the filtered links 
		for link in next_links: 
			yield scrapy.Request(link, self.parse) 
		
	def is_extracted(self, url): 
		if url not in PexelsScraper.crawled_urls: 
			PexelsScraper.crawled_urls.add(url) 
			return False 
		return True
		
		
	def calculate_aspect(self, width, height):
		def gcd(a, b):
			"""The GCD (greatest common divisor) is the highest number that evenly divides both width and height."""
			return a if b == 0 else gcd(b, a % b)

		r = gcd(width, height)
		x = width / r
		y = height / r
		return str(x) + " : " + str(y)
    