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

class Render(QWebPage):  
  def __init__(self, url):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  
  
  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    self.app.quit()

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
    s = "http://citeseerx.ist.psu.edu/search?q=" + i.query + "&submit=Search&sort=rlv&t=doc&feed=rss"
    response = urllib2.urlopen(s)
    rss = response.read()
    citeseers_rss = feedparser.parse(s)
    #for entr in citeseers_rss.entries:
      #print entr.title

    s = "http://citeseerx.ist.psu.edu/search?q=" + i.query + "&submit=Search&uauth=1&sort=ndocs&t=auth"
    #html = urllib2.urlopen(s).read()
    #r = soup.findAll("div", { "class" : "result" })
    #rrender = Render(s)
    #html = rrender.frame.toHtml()
    #f = open(i.query + '.html', 'w')
    #f.write(html)
    #f.close()
    doc = lxml.html.parse(s)
    r = doc.xpath('//div/h3/a')
    #for attr in r:
    #  if attr == 'result':
    #    author = doc.xpath('//div/div/h3/a/@href')
    #    print author
    #for ele in r:
    #  print ele.attrib
    #  print ele.text
    return self.render.result(citeseers_rss, r)

if __name__ == "__main__":
  app.run()
