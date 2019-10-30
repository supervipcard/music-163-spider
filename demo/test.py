import requests
import json

headers = {
    'Referer': 'https://music.163.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
}
# response = requests.get(url='https://music.163.com/api/artist/10559', headers=headers)
# print(response.text)


# response = requests.get(url='https://music.163.com/api/album/2696067', headers=headers)
# print(response.text)


# response = requests.get(url='https://music.163.com/api/artist/albums/10559?limit=10000&offset=0', headers=headers)
# print(response.text)


# response = requests.get(url='https://music.163.com/api/song/detail?ids=[551816010]', headers=headers)
# print(response.text)


# response = requests.get(url='https://music.163.com/api/song/enhance/player/url?ids=[561307346]&br=128000', headers=headers)
# print(json.loads(response.text))


# response = requests.get(url='https://music.163.com/api/song/lyric?id=1318089156&lv=0&tv=0', headers=headers)
# print(response.text)
