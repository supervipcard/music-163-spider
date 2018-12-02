import requests
import execjs
import json
import time
import aiohttp
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
}

with open('core.js', 'r', encoding='utf-8') as f:
    source = f.read()


class MusicSpider(object):
    def __init__(self):
        node = execjs.get('Node')
        self.getpass = node.compile(source)

        self.thread = ThreadPoolExecutor(10)

    def collect(self, ids):
        t = time.time()

        tasks = []
        for id in ids:
            task = self.thread.submit(self._download, id=str(id))
            tasks.append(task)

        for cell in tasks:
            print(cell.result())

        print(time.time() - t)

    async def _fetch(self, data, url):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url=url, data=data) as response:
                return await response.text()

    def _download(self, id):
        home_url = 'https://music.163.com/song?id={id}'.format(id=id)
        response = requests.get(url=home_url, headers=headers)
        if '很抱歉，你要查找的网页找不到' in response.text:
            return
        else:
            url_list = ['https://music.163.com/weapi/song/enhance/player/url?csrf_token=', 'https://music.163.com/weapi/v3/song/detail?csrf_token=', 'https://music.163.com/weapi/song/lyric?csrf_token=']
            data_dict = self.getpass.call('get_data', id)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [asyncio.ensure_future(self._fetch(data_dict[url], url)) for url in url_list]
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()

            result = [json.loads(task.result()) for task in tasks]
            return result


if __name__ == '__main__':
    spider = MusicSpider()
    spider.collect(iter(range(0, 100)))
