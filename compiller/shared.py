from bs4 import BeautifulSoup

class HtmlpException(Exception):
	pass

def htmlBeautifulSoup(data: str) -> BeautifulSoup:
	return BeautifulSoup(data, 'html.parser', multi_valued_attributes=None)
