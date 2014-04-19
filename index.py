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
from operator import itemgetter

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
    query = i.query
    rquery = query.replace(" ", "+")

    #query to CSSeer
    s = "http://csseer.ist.psu.edu/experts/show?query_type=1&q_term=" + rquery
    doc = lxml.html.parse(s)
    html = []
    for node in doc.xpath("//div[@class='blockhighlight_box']"):
        info = {}
        au_url = 'http://csseer.ist.psu.edu/experts/'
        info['href'] = au_url + ''.join(node.xpath("ul/li/a/@href"))
        info['author'] = ''.join(node.xpath("ul/li/a/text()"))
        info['Affiliations'] = ''.join(node.xpath("ul/li[2]/text()"))
        html.append(info)
    cslen = float(len(html))
    csscore = cslen
    for n in html:
        n['score'] = csscore / cslen
        csscore -= 1

    #query to CiteSeerx
    s = "http://citeseerx.ist.psu.edu/search?q=" + rquery + "&submit=Search&sort=rlv&t=doc"
    citeseerx = lxml.html.parse(s)
    result_div = citeseerx.xpath("//div[@class='result']")
    citeseerx_result = []
    for div in result_div:
        info = {}
        paper_url = 'http://citeseerx.ist.psu.edu'
        info['href'] = paper_url + ''.join(div.xpath("h3/a/@href"))
        title = div.xpath("h3/a//text()")
        title = [s.strip() for s in title]
        title = ' '.join(title)
        info['title'] = title
        abstract = ''.join(div.xpath("div[@class='pubextras']/div[@class='pubabstract']/text()")).strip().replace('<em>','').replace('</em>', '').replace('\n', '')
        info['abstract'] = abstract
        author = ''.join(div.xpath("div[@class='pubinfo']/span[@class='authors']/text()"))
        author = author.replace('\n', '').replace('by', '').strip().split(',')
        info['author'] = author
        info['score'] = 0.0
        author_info = []
        acnt = 0
        ascor = 0.0
        c = 0
        for aut in author:
            aut = aut.strip()
            for a in html:
                if aut == a['author']:
                    acnt += 1
                    c += 1 / acnt
                    author_info.append(a)
                    ascor += a['score'] * 1 / acnt
        if c > 0:
            info['score'] += ascor * 1 / (2 * c)
        print info['score']
        info['author_info'] = author_info
        citedby = ''.join(div.xpath("div[@class='pubextras']/a[@class='citation remove']/text()"))
        info['citedby'] = citedby.replace('Cited by', '')
        citeseerx_result.append(info)
    clen = float(len(citeseerx_result))
    cscore = clen
    for n in citeseerx_result:
       print "citeseer_before " + str(n['score'])
       n['score'] += cscore / clen
       cscore -= 1
       print "citeseer " + str(n['score'])
    citeseerx_result = sorted(citeseerx_result, key=itemgetter('score'), reverse=True)
    html = [x for x in html if x['score'] > 0.8]
    #print citeseerx_result
    return self.render.result(citeseerx_result, html, query)

class css:
    def GET(self): raise web.seeother("/static/inputcss.css")
if __name__ == "__main__":
  app.run()
