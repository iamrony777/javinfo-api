"""
fetch trailer/preview from https://www.dmm.co.jp/service/-/html5_player/
"""

import re
from lxml import html
import requests


def getPreview(code: str):
    response = requests.get(
        f"https://www.dmm.co.jp/service/-/html5_player/=/cid={code}/mtype=AhRVShI_/service=mono/floor=dvd/mode=/",
        allow_redirects=True,
    )

    page: html.HtmlElement = html.fromstring(
        html=response.content, base_url="https://www.dmm.co.jp"
    )
    src = re.findall(
        pattern=r"\"src\":\"(.*?)\"",
        string=page.cssselect("div > script")[0].text,
        flags=re.MULTILINE,
    )

    return (
        "https:" + src[0].replace("\\", "")
        if len(src) > 0 and src[0].endswith(".mp4")
        else None
    )


if __name__ == "__main__":
    print(getPreview("mkck275"))
