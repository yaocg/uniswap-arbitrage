import requests
import json
import traceback

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def url_post(url, post_data, headers={'content-type': 'application/json;'}, timeout=(180,180)):
    # 请求数据
    try:
        req = requests.post(url, headers=headers, data=json.dumps(post_data), timeout=timeout)
        return req.text
    except Exception:
        print("url:{0}, ERROR:{1}".format(url, traceback.format_exc()))

    return None

def url_get(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        req = requests.get(url=url, headers=headers, timeout=(30,30))
        return req.text
    except Exception:
        print("url:{0}, ERROR:{1}".format(url, traceback.format_exc()))

    return None


def url_websocket(earn_url):
    try:
        ws = create_connection(earn_url,timeout=5)
        if ws.connected:
            return True, ws.recv()
        return False, None
    except Exception as e:
        return False, str(e)
    finally:
        ws.close()
