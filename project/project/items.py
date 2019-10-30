# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProjectItem(scrapy.Item):
    # define the fields for your item here like:

    song_id = scrapy.Field()
    song_name = scrapy.Field()
    song_url = scrapy.Field()
    singer_id = scrapy.Field()
    singer_name = scrapy.Field()
    album_id = scrapy.Field()
    album_name = scrapy.Field()
    album_publish_time = scrapy.Field()
    lyric = scrapy.Field()
    tlyric = scrapy.Field()
