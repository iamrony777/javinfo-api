"""
fetch trailer/preview from https://www.dmm.co.jp/service/-/html5_player/
"""

from urllib.parse import urljoin
from lxml import html
from src.common._http import CustomSession


def getPreview(code: str):
    session = CustomSession(
        base_url="https://www.dmm.co.jp/service/-/html5_player",
    )
    response = session.get(
        f"/=/cid={code}/mtype=AhRVShI_/service=mono/floor=dvd/mode=/"
    )
    with open("test.html", 'wb') as _f:
        _f.write(response.content)
    page: html.HtmlElement = html.fromstring(
        html=response.content, base_url="https://www.dmm.co.jp"
    )
    return page.cssselect("#dmmvideo-player > video")[0].get("src")


if __name__ == "__main__":
    print(getPreview("mkck275"))
