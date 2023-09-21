"""
fetch trailer/preview from https://www.dmm.co.jp/service/-/html5_player/
"""

from urllib.parse import urljoin
from pyjsparser import parse
from lxml import html
import requests
import json

def getPreview(code: str):
    response = requests.get(
        f"https://www.dmm.co.jp/service/-/html5_player/=/cid={code}/mtype=AhRVShI_/service=mono/floor=dvd/mode=/",
        allow_redirects=True,
    )
    with open("test.html", "wb") as _f:
        _f.write(response.content)
    page: html.HtmlElement = html.fromstring(
        html=response.content, base_url="https://www.dmm.co.jp"
    )
    js = parse(page.cssselect("div > script")[0].text)

    return json.dumps(js, indent=2)

if __name__ == "__main__":
    print(getPreview("mkck275"))
