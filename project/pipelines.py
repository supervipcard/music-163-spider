# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymysql
from twisted.enterprise import adbapi


class SqlPipeline(object):
    def __init__(self, pool):
        self.db_conn = pool
        self.sql = 'insert ignore into 163_music (song_id, song_name, song_url, singer_id, singer_name, album_id, album_name, album_publish_time, lyric, tlyric) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

    @classmethod
    def from_settings(cls, settings):
        pool = adbapi.ConnectionPool('pymysql', host=settings['MYSQL_HOST'], port=settings['MYSQL_PORT'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASSWD'], db=settings['MYSQL_DB'], charset='utf8')
        return cls(pool)

    def process_item(self, item, spider):
        query = self.db_conn.runInteraction(self.go_insert, item)   # 数据插入
        query.addErrback(self.handle_error, item, spider)   # 异常检测
        return item

    def go_insert(self, cursor, item):
        cursor.execute(self.sql, [item['song_id'], item['song_name'], item['song_url'], item['singer_id'], item['singer_name'], item['album_id'], item['album_name'], item['album_publish_time'], item['lyric'], item['tlyric']])

    def handle_error(self, failure, item, spider):
        spider.logger.error(failure)
