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
        '/static/inputcss.css', 'css',
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
    rss = feedparser.parse(s)
    for entr in rss.entries:
        entr.title = entr.title.replace("<em>", " ")
        entr.title = entr.title.replace("</em>", " ")

    #query to CiteSeerx Author
    s = "http://citeseerx.ist.psu.edu/search?q=" + query + "&submit=Search&uauth=1&sort=ndocs&t=auth"
    doc = lxml.html.parse(s)
    href = doc.xpath("//div[@class='result']/h3/a/@href")
    author = doc.xpath("//div[@class='result']/h3/a/text()")
    vari = doc.xpath("//div[@class='result']//table[@class='authInfo']/tr[contains(.,'Variations')]/td[2]/text()")
    affi = doc.xpath("//div[@class='result']//table[@class='authInfo']/tr[contains(.,'Affiliations')]/td[2]/text()")
    paper = doc.xpath("//div[@class='result']//table[@class='authInfo']/tr[contains(.,'Papers')]/td[2]/text()")
    page = doc.xpath("//div[@class='result']//table[@class='authInfo']/tr[contains(.,'Homepage')]/td[2]/a/@href")
    print vari
    html = (author, href, paper)
    return self.render.result(rss, html)

class css:
    def GET(self): raise web.seeother("/static/inputcss.css")
if __name__ == "__main__":
  app.run()
