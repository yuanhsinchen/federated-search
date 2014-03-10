import web
import urllib
import urllib2
import feedparser
import xml.etree.ElementTree as ET
import xpath
import HTMLParser
from bs4 import BeautifulSoup
import lxml.html
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *
import sys

urls = (
	'/', 'index',
	'/result', 'result',
	)

app = web.application(urls, globals())

class index:
  def __init__(self):
    self.render = web.template.render('template')

  def GET(self, name=None):
    return self.render.input("a")

  def POST(self, name):
    return "post"

class result:
  def __init__(self):
    self.render = web.template.render('template')

  def GET(self, name=None):
    i = web.input(query=None)
    query = i.query.replace(" ", "+")

    #query to CiteSeerx
    s = "http://citeseerx.ist.psu.edu/search?q=" + query + "&submit=Search&sort=rlv&t=doc&feed=rss"
    citeseers_rss = feedparser.parse(s)

    #query to CiteSeerx Author
    s = "http://citeseerx.ist.psu.edu/search?q=" + query + "&submit=Search&uauth=1&sort=ndocs&t=auth"
    doc = lxml.html.parse(s)
    r = doc.xpath('//div/h3/a')
    return self.render.result(citeseers_rss, r)

if __name__ == "__main__":
  app.run()
