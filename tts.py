# coding=utf-8
import sys
import json
import hashlib
import os
import pygame
from pygame.locals import *


# 为字符串计算SHA-256哈希值
def sha256_hash_string(text):
    h = hashlib.sha256()
    h.update(text.encode('utf-8'))
    return h.hexdigest()


def file_exists(file_path):
    return os.path.exists(file_path)


IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib
    from urllib import quote_plus
    from urllib import urlopen
    from urllib import Request
    from urllib import URLError
    from urllib import urlencode

TEXT = "欢迎使用百度语音合成。"

def load_config():
    API_KEY = '3od1ixZqNwLxxxxxxxxxx'
    SECRET_KEY = '27CA1xxxxxxxxxxxxxxxxxxdH0F'
    """
    加载配置文件，优先加载私有配置文件private-config.json
    """
    if file_exists(f"private-config.json"):
        with open(f"private-config.json", 'r') as file:
            config = json.load(file)
    elif file_exists(f"private-config.json"):
        with open(f"private-config.json", 'r') as file:
            config = json.load(file)
    else:
        print("can't load baidu api config!")
        return API_KEY, SECRET_KEY

    return config["baidu-api"]["API_KEY"], config["baidu-api"]["SECRET_KEY"]

# 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
# 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认为度小美
PER = 4
# 语速，取值0-15，默认为5中语速
SPD = 5
# 音调，取值0-15，默认为5中语调
PIT = 5
# 音量，取值0-9，默认为5中音量
VOL = 5
# 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
AUE = 3

FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
FORMAT = FORMATS[AUE]

CUID = "123456PYTHON"

TTS_URL = 'http://tsn.baidu.com/text2audio'


class DemoError(Exception):
    pass


"""  TOKEN start """

TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'
SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选


def fetch_token():
    # 加载密钥
    API_KEY, SECRET_KEY = load_config()

    print(f"fetch token begin {API_KEY},{SECRET_KEY}")
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


"""  TOKEN end """

# 创建一个播放器对象
sound = pygame.mixer

sound_map = {}


def play_mp3_file(file, channel=0):
    if file in sound_map:
        channel1 = sound.Channel(channel)
        channel1.play(sound_map[file])
        return True
    sound_map[file] = pygame.mixer.Sound(file)
    channel1 = sound.Channel(channel)
    channel1.play(sound_map[file])
    return True


def download_tts_file(text, filepath):
    has_error = False

    try:
        token = fetch_token()

        tex = quote_plus(text)  # 此处TEXT需要两次urlencode
        print(tex)
        params = {'tok': token, 'tex': tex, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': AUE, 'cuid': CUID,
                  'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

        data = urlencode(params)
        print('test on Web Browser' + TTS_URL + '?' + data)

        req = Request(TTS_URL, data.encode('utf-8'))

        f = urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
    except URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()
        has_error = True
    except DemoError as err:
        print('except DemoError : ' + str(err))
        result_str = str(err).encode()
        has_error = True

    save_file = "error.txt" if has_error else filepath
    with open(save_file, 'wb') as of:
        of.write(result_str)

    if has_error:
        if (IS_PY3):
            result_str = str(result_str, 'utf-8')
        print("tts api  error:" + result_str)

    print("result saved as :" + save_file)

    if has_error:
        return False

    return True


def say(text):
    """
    TTS播放一个文本语音，该模块通过缓存方式，有解析过直接播放，没有解析过调用API
    :param text: 需要播放的语音文本（短文本）
    """
    # 处理TTS转换，如果存在优先播放本地文档
    filename = f"{sha256_hash_string(text)}.{FORMAT}"
    print(f'tts_play : {text}')

    if file_exists(f"mp3/{filename}"):
        return play_mp3_file(f"mp3/{filename}")

    # download
    if download_tts_file(text, f"mp3/{filename}"):
        return play_mp3_file(f"mp3/{filename}")


if __name__ == '__main__':
    token = fetch_token()
    tex = quote_plus(TEXT)  # 此处TEXT需要两次urlencode
    print(tex)
    params = {'tok': token, 'tex': tex, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': AUE, 'cuid': CUID,
              'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

    data = urlencode(params)
    print('test on Web Browser' + TTS_URL + '?' + data)

    req = Request(TTS_URL, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
    except  URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()
        has_error = True

    save_file = "error.txt" if has_error else 'result.' + FORMAT
    with open(save_file, 'wb') as of:
        of.write(result_str)

    if has_error:
        if (IS_PY3):
            result_str = str(result_str, 'utf-8')
        print("tts api  error:" + result_str)

    print("result saved as :" + save_file)
