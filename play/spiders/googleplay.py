# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from play.items import PlayItem
from contextlib import closing
from operator import itemgetter
import sqlite3
import re

dbname = 'googleplay.db'
re_pkg = re.compile(r'id=(.*?)(?:$|&)')
re_float = re.compile(r'\d+\.\d+')
insertgetter = itemgetter('pkg', 'url', 'title', 'author', 'stars',
                          'published', 'size', 'downloads', 'version', 'os')

def text(el):
    try: return ''.join(el.css('*::text').extract()).strip()
    except: return None

def regex(reg, text):
    try: return reg.findall(text)[0]
    except: return None

def dosql(sql, *args, **kwargs):
    with sqlite3.connect(dbname) as db:
        with closing(db.cursor()) as cursor:
            cursor.execute(sql, *args, **kwargs)

def insert_app(item):
    dosql('INSERT OR IGNORE INTO app VALUES (?,?,?,?,?,?,?,?,?,?)', insertgetter(item))

dosql('CREATE TABLE IF NOT EXISTS app(pkg TEXT NOT NULL PRIMARY KEY,'
      'url TEXT NOT NULL, title TEXT, author TEXT, stars TEXT,'
      'published TEXT, size TEXT, downloads TEXT, version TEXT, os TEXT)')

class GoogleplaySpider(CrawlSpider):
    name = 'googleplay'
    allowed_domains = ['play.google.com']
    start_urls = ['https://play.google.com/store/apps/collection/topselling_free']
    rules = [Rule(SgmlLinkExtractor(allow=('/store/apps/details')), follow=True, callback='parse_app'),
             Rule(SgmlLinkExtractor(allow=('/store/apps/')), follow=True)]

    def parse_app(self, res):
        item = PlayItem()
        item['pkg'] = regex(re_pkg, res.url)
        item['url'] = res.url
        item['title'] = text(res.css('.document-title'))
        item['author'] = text(res.css('[itemprop=author] [itemprop=name]'))
        item['stars'] = regex(re_float, text(res.css('.stars-count')))
        item['published'] = text(res.css('[itemprop=datePublished]'))
        item['size'] = text(res.css('[itemprop=fileSize]'))
        item['downloads'] = text(res.css('[itemprop=numDownloads]'))
        item['version'] = text(res.css('[itemprop=softwareVersion]'))
        item['os'] = text(res.css('[itemprop=operatingSystems]'))
        insert_app(item)
        yield item

