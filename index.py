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

    #query to CiteSeerx
    """
    s = "http://citeseerx.ist.psu.edu/search?q=" + query + "&submit=Search&sort=rlv&t=doc&feed=rss"
    rss = feedparser.parse(s)
    for entr in rss.entries:
        entr.title = entr.title.replace("<em>", " ")
        entr.title = entr.title.replace("</em>", " ")
        entr.description = entr.description.replace("<em>", " ")
        entr.description = entr.description.replace("</em>", " ")
    """
    #query to CSSeer
    s = "http://csseer.ist.psu.edu/experts/show?query_type=1&q_term=" + rquery
    doc = lxml.html.parse(s)
    html = []
    for node in doc.xpath("//div[@class='blockhighlight_box']"):
        info = {}
        au_url = 'http://csseer.ist.psu.edu/experts/'
        info['href'] = au_url + ''.join(node.xpath("ul/li/a/@href"))
        info['author'] = ''.join(node.xpath("ul/li/a/text()"))
        #s = ''.join(node.xpath("table[@class='authInfo']/tr[contains(.,'Variations')]/td[2]/text()"))
        #info['Variations'] = s
        info['Affiliations'] = ''.join(node.xpath("ul/li[2]/text()"))
        #s = ''.join(node.xpath("table[@class='authInfo']/tr[contains(.,'Papers')]/td[2]/text()"))
        #info['Papers'] = s
        #s = ''.join(node.xpath("table[@class='authInfo']/tr[contains(.,'Homepage')]/td[2]/a/@href"))
        #info['Homepage'] = s
        html.append(info)
    cslen = float(len(html))
    csscore = cslen
    for n in html:
        n['score'] = csscore / cslen
        csscore -= 1

    s = "http://citeseerx.ist.psu.edu/search?q=" + rquery + "&submit=Search&sort=rlv&t=doc"
    citeseerx = lxml.html.parse(s)
    result_div = citeseerx.xpath("//div[@class='result']")
    citeseerx_result = []
    for div in result_div:
        info = {}
        paper_url = 'http://citeseerx.ist.psu.edu'
        info['href'] = paper_url + ''.join(div.xpath("h3/a/@href"))
        #title = div.xpath("h3/a//text()").strip().replace('<em>', '').replace('</em>', '').replace('\n', '')
        title = div.xpath("h3/a//text()")
        title = [s.strip() for s in title]
        title = ' '.join(title)
        info['title'] = title
        abstract = ''.join(div.xpath("div[@class='pubextras']/div[@class='pubabstract']/text()")).strip().replace('<em>','').replace('</em>', '').replace('\n', '')
        info['abstract'] = abstract
        author = ''.join(div.xpath("div[@class='pubinfo']/span[@class='authors']/text()"))
        author = author.replace('\n', '').replace('by', '').strip().split(',')
        info['author'] = author
        #for a in html:
        #    print a['author']
        info['score'] = 0.0
        author_info = []
        for aut in author:
            aut = aut.strip()
            #print aut
            for a in html:
                if aut == a['author']:
                #if aut == (a['author'] for a in html):
                    #print a['author'] + '\n'
                    author_info.append(a)
                    info['score'] += a['score']
                    html.remove(a)
        info['author_info'] = author_info
        citedby = ''.join(div.xpath("div[@class='pubextras']/a[@class='citation remove']/text()"))
        info['citedby'] = citedby.replace('Cited by', '')
        citeseerx_result.append(info)
    clen = float(len(citeseerx_result))
    cscore = clen
    for n in citeseerx_result:
       n['score'] += float(cscore / clen)
       cscore -= 1
    citeseerx_result = sorted(citeseerx_result, key=itemgetter('author_info', 'score'), reverse=True)
    html = [x for x in html if x['score'] > 0.85]
#    for n in html:
#        #if n['score'] < 0.5:
#        if n['author'] != '':
#            html.remove(n)
    print html
    #print citeseerx_result
    print query
    return self.render.result(citeseerx_result, html, query)

class css:
    def GET(self): raise web.seeother("/static/inputcss.css")
if __name__ == "__main__":
  app.run()
