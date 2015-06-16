# -*- coding: utf-8 -*-

# Scrapy settings for play project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'play'

SPIDER_MODULES = ['play.spiders']
NEWSPIDER_MODULE = 'play.spiders'

LOG_LEVEL = 'INFO'
JOBDIR = 'jobs/play'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'play (+http://www.yourdomain.com)'
