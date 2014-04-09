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
        entr.description = entr.description.replace("<em>", " ")
        entr.description = entr.description.replace("</em>", " ")

    #query to CiteSeerx Author
    #s = "http://citeseerx.ist.psu.edu/search?q=" + query + "&submit=Search&uauth=1&sort=ndocs&t=auth"
    #query to CSSeer
    s = "http://csseer.ist.psu.edu/experts/show?query_type=1&q_term=" + query
    doc = lxml.html.parse(s)
    html = []
    for node in doc.xpath("//div[@class='blockhighlight_box']"):
        info = {}
        au_url = 'http://csseer.ist.psu.edu/experts/'
        info['href'] = au_url + ''.join((node.xpath("ul/li/a/@href")))
        info['name'] = ''.join(node.xpath("ul/li/a/text()"))
        #s = ''.join(node.xpath("table[@class='authInfo']/tr[contains(.,'Variations')]/td[2]/text()"))
        #info['Variations'] = s
        info['Affiliations'] = ''.join(node.xpath("ul/li[2]/text()"))
        #s = ''.join(node.xpath("table[@class='authInfo']/tr[contains(.,'Papers')]/td[2]/text()"))
        #info['Papers'] = s
        #s = ''.join(node.xpath("table[@class='authInfo']/tr[contains(.,'Homepage')]/td[2]/a/@href"))
        #info['Homepage'] = s
        html.append(info)
    return self.render.result(rss, html)

class css:
    def GET(self): raise web.seeother("/static/inputcss.css")
if __name__ == "__main__":
  app.run()
