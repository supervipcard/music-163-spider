# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime
from scrapy_redis import spiders
from scrapy.mail import MailSender
from scrapy.utils.project import get_project_settings
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..middlewares import CodeError
from ..items import ProjectItem


class SongSpiderMaster(spiders.RedisSpider):
    name = 'song_master'
    # allowed_domains = ['music.163.com']
    # redis_key = 'song:start_urls'

    def __init__(self, *args, **kwargs):
        super(SongSpiderMaster, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        self.mail_to = settings.get('MAIL_TO', ['805071841@qq.com'])
        self.mailer = MailSender.from_settings(settings)
        self.error_count = 0

    def start_requests(self):
        url = 'https://music.163.com/discover/artist/cat?id={id}&initial={initial}'

        id_list = [1001, 1002, 1003, 2001, 2002, 2003, 6001, 6002, 6003, 7001, 7002, 7003, 4001, 4002, 4003]
        initial_list = list(range(65, 91)) + [-1, 0]

        for id in id_list:
            for initial in initial_list:
                yield scrapy.Request(url=url.format(id=id, initial=initial), dont_filter=True, callback=self.api_artist_albums, errback=self.handle_error)

    def api_artist_albums(self, response):
        lines = response.xpath('//ul[@id="m-artist-box"]/li')

        for line in lines:
            singer_id = line.xpath('.//a[contains(@href, "/artist?id=")]/@href').re(r'/artist\?id=(\d+)')[0]

            url = 'https://music.163.com/api/artist/albums/{singer_id}?limit=10000&offset=0'.format(singer_id=singer_id)
            yield scrapy.Request(url=url, callback=self.api_album, errback=self.handle_error)

    def api_album(self, response):
        data = json.loads(response.text)

        for cell in data['hotAlbums']:
            album_id = cell['id']

            url = 'https://music.163.com/api/album/{album_id}'.format(album_id=album_id)
            yield scrapy.Request(url=url, callback=self.api_song_url, errback=self.handle_error)

    def api_song_url(self, response):
        data = json.loads(response.text)

        for cell in data['album']['songs']:
            song_id = cell['id']
            meta_group = {'song_id': song_id, 'info': cell}

            url = 'https://music.163.com/api/song/enhance/player/url?ids=[{song_id}]&br=128000'.format(song_id=song_id)
            yield scrapy.Request(url=url, meta={'meta_group': meta_group}, callback=self.api_song_lyric, errback=self.handle_error)

    def api_song_lyric(self, response):
        player_url_res = json.loads(response.text)

        meta_group = response.meta.get('meta_group')
        meta_group['player_url_res'] = player_url_res

        url = 'https://music.163.com/api/song/lyric?id={song_id}&lv=0&tv=0'.format(song_id=meta_group['song_id'])
        yield scrapy.Request(url=url, meta={'meta_group': meta_group}, callback=self.song_parse, errback=self.handle_error)

    def song_parse(self, response):
        lyric_res = json.loads(response.text)

        meta_group = response.meta.get('meta_group')
        player_url_res = meta_group['player_url_res']
        info = meta_group['info']

        items = ProjectItem()
        items['song_id'] = info['id']
        items['song_name'] = info['name']
        items['song_url'] = player_url_res['data'][0]['url']
        items['singer_id'] = json.dumps([cell['id'] for cell in info['artists']], ensure_ascii=False)
        items['singer_name'] = json.dumps([cell['name'] for cell in info['artists']], ensure_ascii=False)
        items['album_id'] = info['album']['id']
        items['album_name'] = info['album']['name']
        items['album_publish_time'] = datetime.fromtimestamp(info['album']['publishTime'] / 1000) if info['album'].get('publishTime') else None
        items['lyric'] = lyric_res['lrc']['lyric'] if 'lrc' in lyric_res and lyric_res['lrc'].get('lyric') else None
        items['tlyric'] = lyric_res['tlyric']['lyric'] if 'tlyric' in lyric_res and lyric_res['tlyric'].get('lyric') else None
        yield items

    def handle_error(self, failure):
        self.error_count += 1
        self.mailer.send(to=self.mail_to, subject='Requests Error：' + str(failure.request), body=str(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s, status_code is %s', response.url, response.status)

        elif failure.check(CodeError):
            response = failure.value.response
            self.logger.error('CodeError on %s, response is %s', response.url, response.text)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

        else:
            self.logger.error(repr(failure))
