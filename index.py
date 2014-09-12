#!/usr/bin/python26

import web
import urllib
import urllib2
import feedparser
import xml.etree.ElementTree as ET
import xpath
import HTMLParser
import lxml.html
import socket
import sys
from operator import itemgetter
import json
import re

def main():
    #print sys.argv
    query = ''
    for q in range(1, len(sys.argv) - 1):
        query += sys.argv[q] + '+'

    query += sys.argv[len(sys.argv) - 1]
    #print query
    rquery = query.replace('+', ' ')

    #query to CSSeer
    s = "http://csseer.ist.psu.edu/experts/show?query_type=1&q_term=" + rquery
    doc = lxml.html.parse(s)
    timeout = 1000
    socket.setdefaulttimeout(timeout)
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
    s = "http://csxweb01.ist.psu.edu/search?q=" + rquery + "&submit=Search&sort=rlv&t=doc"
    citeseerx = lxml.html.parse(s)
    result_info = citeseerx.xpath("//div[@id='result_info']/strong/text()")
    numFound = int(result_info[1].replace(',', ''))
    result_div = citeseerx.xpath("//div[@class='result']")
    citeseerx_result = []
    for orank,div in enumerate(result_div, 1):
        info = {}
        href = div.xpath("h3/a/@href")
        paper_url = 'http://csxweb01.ist.psu.edu'
        info['href'] = paper_url + ''.join(href)
        doi = re.search(r"\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}", ''.join(href))
        if doi:
            info['doi'] = doi.group()
        else:
            info['doi'] = ''
        info['doi'] = info['doi'] + '&or=' + str(orank)
        title = div.xpath("h3/a//text()")
        title = [s.strip() for s in title]
        title = ' '.join(title)
        info['title'] = title
        abstract = ''.join(div.xpath("div[@class='pubextras']/div[@class='pubabstract']/text()")).strip().replace('<em>','').replace('</em>', '').replace('\n', '')
        info['abstract'] = abstract
        rid = ''.join(div.xpath("div[@class='pubextras']/span/@id")).strip().replace('cmsg_', '')
        info['id'] = rid
        author = ''.join(div.xpath("div[@class='pubinfo']/span[@class='authors']/text()"))
        author = author.replace('\n', '').replace('by', '').strip().split(',')
        info['author'] = author
        info['score'] = 0.0
        author_info = []
        acnt = 0
        ascor = 0.0
        c = 0
        exp = False
        for aut in author:
            aut = aut.strip()
            for a in html:
                if aut == a['author']:
                    acnt += 1
                    c += 1 / acnt
                    author_info.append(a)
                    ascor += a['score'] * 1 / acnt
                    exp = True
            if exp == False:
                ai = {'author':aut}
                author_info.append(ai)
            exp = False
        if c > 0:
            info['score'] += ascor * 1 / (2 * c)
        info['author_info'] = author_info
        citedby = ''.join(div.xpath("div[@class='pubextras']/a[@class='citation remove']/text()"))
        cites = re.search(r"(\d+) \((\d+)", citedby)
        ncites = 0
        scites = 0
        if cites:
            ncites = re.search(r"(\d+) \((\d+)", citedby).group(1)
            scites = re.search(r"(\d+) \((\d+)", citedby).group(2)
        info['ncites'] = int(ncites)
        info['scites'] = int(scites)
        info['incol'] = True
        citeseerx_result.append(info)
    clen = float(len(citeseerx_result))
    cscore = clen
    for n in citeseerx_result:
       n['score'] += cscore / clen
       cscore -= 1
    citeseerx_result = sorted(citeseerx_result, key=itemgetter('score'), reverse=True)
    html = [x for x in html if x['score'] > 0.8]
    #j = json.dumps(citeseerx_result)
    j = json.dumps(csxjson(citeseerx_result, rquery, numFound))
    #outfile = open('citeseerx.json', 'w')
    #with open('citeseerx.json', 'w') as outfile:
    #    json.dump(j, outfile)
    #print >> outfile, j
    #print len(j)
    print j

def csxjson(citeseerx_result, query, numFound):
    csx = {}
    response = {"start":0, "docs":citeseerx_result, "numFound":numFound}
    csx["response"] = response

    params = {}
    params["start"] = 0
    params["q"] = query
    params["wt"] = "json"
    params["qt"] = "dismax"
    params["fq"] = "incol:true"
    params["hl"] = "true"
    params["row"] = "10"
    responseHeader = {"status":0, "QTime":23, "params":params}
    csx["responseHeader"] = responseHeader
    #csxl = [csx]
    return csx

if __name__ == "__main__":
    main()
