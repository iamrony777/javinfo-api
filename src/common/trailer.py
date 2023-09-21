"""
fetch trailer/preview from https://www.dmm.co.jp/service/-/html5_player/
"""

import re
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

    page: html.HtmlElement = html.fromstring(
        html=response.content, base_url="https://www.dmm.co.jp"
    )
    src = re.search(
        pattern=r"\"src\":\"(.*?)\"", string=page.cssselect("div > script")[0].text, flags="gm"
    )

    return src

if __name__ == "__main__":
    print(getPreview("mkck275"))
