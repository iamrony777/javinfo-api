"""
fetch trailer/preview from https://www.dmm.co.jp/service/-/html5_player/
"""

from urllib.parse import urljoin
from lxml import html
from requests import request


def getPreview(code: str):
    return request(
        method="GET",
        url=urljoin(
            base="https://www.dmm.co.jp/service/-/html5_player",
            url=f"/=/cid={code}/mtype=AhRVShI_/service=mono/floor=dvd/mode=/",
        ),
    ).content

if __name__ == "__main__":
    print(getPreview("mkck275"))