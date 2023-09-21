"""
fetch trailer/preview from https://www.dmm.co.jp/service/-/html5_player/
"""

from urllib.parse import urljoin
from lxml import html
from src.common.http import CustomSession


def getPreview(code: str):
    session = CustomSession(
        base_url="https://www.dmm.co.jp/service/-/html5_player",
    )
    return session.get(f"/=/cid={code}/mtype=AhRVShI_/service=mono/floor=dvd/mode=/")


if __name__ == "__main__":
    print(getPreview("mkck275"))
