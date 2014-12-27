#! /usr/bin/env python26

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

def build_query():
    #print sys.argv
    query = ''
    for q in range(1, len(sys.argv) - 1):
        query += sys.argv[q] + '+'

    query += sys.argv[len(sys.argv) - 1]
    #print query
    return query.replace('+', ' ')

def query_csseer(query):
    #query to CSSeer
    s = "http://csseer.ist.psu.edu/experts/show?query_type=1&q_term=" + query
    htmldoc = lxml.html.parse(s)
    timeout = 1000
    socket.setdefaulttimeout(timeout)

    cs_authors = []
    for node in htmldoc.xpath("//div[@class='blockhighlight_box']"):
        author = {}
        au_url = 'http://csseer.ist.psu.edu/experts/'
        author['href'] = au_url + ''.join(node.xpath("ul/li/a/@href"))
        author['author'] = ''.join(node.xpath("ul/li/a/text()"))
        author['Affiliations'] = ''.join(node.xpath("ul/li[2]/text()"))
        cs_authors.append(author)
    cslen = float(len(cs_authors))
    csscore = cslen
    for n in cs_authors:
        n['score'] = csscore / cslen
        csscore -= 1

    return cs_authors

def query_citeseerx(query, cs_authors):
    #query to CiteSeerx
    s = "http://localhost:8080/search?q=" + query + "&submit=Search&sort=rlv&t=doc"
    htmldoc = lxml.html.parse(s)

    result_info = htmldoc.xpath("//div[@id='result_info']/strong/text()")
    numFound = int(result_info[1].replace(',', ''))

    result_div = htmldoc.xpath("//div[@class='result']")
    docs = []
    for orank,div in enumerate(result_div, 1):
        doc = {}
        href = div.xpath("h3/a/@href")

        paper_url = 'http://csxweb04.ist.psu.edu'
        doc['href'] = paper_url + ''.join(href)

        doi = re.search(r"\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}", ''.join(href))
        if doi:
            doc['doi'] = doi.group()
        else:
            doc['doi'] = ''
        doc['doi'] = doc['doi'] + '&or=' + str(orank)

        title = div.xpath("h3/a//text()")
        title = [s.strip() for s in title]
        title = ' '.join(title)
        doc['title'] = title

        abstract = ''.join(div.xpath("div[@class='pubextras']/div[@class='pubabstract']/text()")).strip().replace('<em>','').replace('</em>', '').replace('\n', '')
        doc['abstract'] = abstract

        rid = ''.join(div.xpath("div[@class='pubextras']/span/@id")).strip().replace('cmsg_', '')
        doc['id'] = rid

        authors = []
        authors_span = div.xpath("div[@class='authors']/span[@class='author']")
        for au in authors_span:
            authors.append(''.join(au.xpath("text()")).strip())
        kauthors_span = div.xpath("div[@class='authors']/div[@class='kauthors']/span[@class='author']")
        for au in kauthors_span:
            authors.append(''.join(au.xpath("text()")).strip())
        doc['author'] = authors

        doc['score'] = 0.0

        author_info = []
        acnt = 0
        ascore = 0.0
        c = 0
        for author in authors:
            found = False
            author = author.strip()
            for cs_author in cs_authors:
                if author == cs_author['author']:
                    acnt += 1
                    c += 1 / acnt
                    author_info.append(cs_author)
                    ascore += cs_author['score'] * 1 / acnt
                    found = True
                    break

            if not found:
                ai = {'author':author}
                author_info.append(ai)

        if acnt > 0:
            doc['score'] += ascore * 1 / (2 * c)

        doc['author_info'] = author_info

        citedby = ''.join(div.xpath("div[@class='pubextras']/a[@class='citation remove']/text()"))
        cites = re.search(r"(\d+) \((\d+)", citedby)
        ncites = 0
        scites = 0
        if cites:
            ncites = re.search(r"(\d+) \((\d+)", citedby).group(1)
            scites = re.search(r"(\d+) \((\d+)", citedby).group(2)
        doc['ncites'] = int(ncites)
        doc['scites'] = int(scites)

        doc['incol'] = True
        docs.append(doc)

    clen = float(len(docs))
    cscore = clen
    for n in docs:
       n['score'] += cscore / clen
       cscore -= 1

    return numFound, sorted(docs, key=itemgetter('score'), reverse=True)

def build_solr_json(docs, query, numFound, cs_authors):
    params = {}
    params["start"] = 0
    params["q"] = query
    params["wt"] = "json"
    params["qt"] = "dismax"
    params["fq"] = "incol:true"
    params["hl"] = "true"
    params["row"] = "10"

    responseHeader = {}
    responseHeader["status"] = 0
    responseHeader["QTime"] = 23
    responseHeader["params"] = params

    response = {}
    response["start"] = 0
    response["docs"] = docs
    response["numFound"] = numFound
    response["experts"] = cs_authors

    output = {}
    output["responseHeader"] = responseHeader
    output["response"] = response

    return output

def main():
    query = build_query()
    cs_authors = query_csseer(query)
    numFound, docs = query_citeseerx(query, cs_authors)

    output = build_solr_json(docs, query, numFound, cs_authors)
    print json.dumps(output)

if __name__ == "__main__":
    main()
