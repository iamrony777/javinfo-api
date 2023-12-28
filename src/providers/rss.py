from datetime import datetime, timezone
from enum import Enum
from os import getenv
import re
from urllib.parse import urljoin
from lxml import etree, html
import logging
from os.path import basename, splitext
from cloudscraper import create_scraper


class Providers(str, Enum):
    """
    Enumeration of providers for the API.

    This class represents the available providers for the API. Each provider has a unique value
    that can be used to identify it.
    """

    r18 = "r18"
    jvdtbs = "jvdtbs"
    jvlib = "jvlib"
    javdb = "javdb"
    all = "all"


class RSS:
    def __init__(self) -> None:
        __handler = logging.StreamHandler()
        __handler.setLevel(logging.DEBUG)
        __handler.setFormatter(
            logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        )
        self.parser = html.HTMLParser(encoding="utf-8")
        self.rss: etree._Element = etree.Element(
            "rss", version="2.0", nsmap={"atom": "http://www.w3.org/2005/Atom"}
        )
        # self.provider = provider
        self.logger = logging.getLogger(splitext(basename(__file__))[0])
        self.logger.addHandler(__handler)
        self.logger.setLevel(logging.DEBUG)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
            "Accept": "*/*",
        }
        self.client = create_scraper(
            browser={"browser": "chrome", "platform": "linux", "desktop": True},
        )
        # javdatabase - init
        self.javdatabase_base_url = "https://javdatabase.com/"

    def generate_channel(self) -> etree._Element:
        channel: etree._Element = etree.SubElement(self.rss, "channel")

        # channel.title
        etree.SubElement(channel, "title").text = "NSFW API - JAV RSS"

        # channel.description
        etree.SubElement(
            channel, "description"
        ).text = "A rss endpoint to list latest javs"

        # channel.link
        etree.SubElement(channel, "link").text = "https:/nsfw-api.eu.org"

        # channel.logo
        etree.SubElement(channel, "icon").text = "image"
        gen = etree.SubElement(
            channel,
            "generator",
            uri="https://github.com/iamrony777/nsfw-api",
            version="3.0.0",
        )
        gen.text = "RSS Generator by NSFW API"

        updated = etree.SubElement(channel, "pubDate")
        updated.text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")

        # rss.atom
        etree.SubElement(
            channel,
            etree.QName("http://www.w3.org/2005/Atom", "link"),
            attrib={
                # "href": getenv("VERCEL_URL") + el_title.replace("r/", "/r/"),
                "rel": "self",
                "type": "application/rss+xml",
            },
        )

        return channel

    def generate_entries(self, provider: Providers) -> etree._Element:
        channel = self.generate_channel()
        if provider == Providers.jvdtbs:
            return self.generate_jvdtbs_entries(channel)
        # if provider == Providers.jvlib:
        #     return self.generate_jvlib_entries()


    def generate_jvdtbs_entries(self, channel: etree._Element) -> etree._Element | None:
        resp = self.client.get(
            url=urljoin(self.javdatabase_base_url, "/movies"),
            allow_redirects=True,
        )

        if not resp.ok:
            self.logger.debug("search:code:status: %s", resp.status_code)
            return None

        data_collumn = html.fromstring(
            resp.content, self.javdatabase_base_url, self.parser
        )

        for element in data_collumn.xpath('(//div[@class="row"])[2]')[0]:
            item = etree.SubElement(channel, "item")
            title = etree.SubElement(item, "title")
            description = etree.Element("div", attrib={"class": "col-md-9"})

            for child in element.find("div/div").iterchildren():
                if child.tag == "p":
                    title.text = f"[{child.find('a').text.strip()}] "
                    # etree.SubElement(item, "title").text = child.find("a").text.strip()
                    etree.SubElement(item, "link").text = child.find("a").get("href")
                if (
                    child.tag == "div"
                    and child.attrib.get("class") == "movie-cover-thumb"
                ):
                    etree.SubElement(
                        etree.SubElement(
                            description,
                            "a",
                            attrib={
                                "referrerpolicy": "no-referrer",
                                "class": "bigImage",
                                "title": child.find("a/img").get("alt"),
                            },
                        ),
                        "img",
                        attrib={
                            "src": child.find("a/img").get("data-src"),
                            "alt": child.find("a/img").get("alt"),
                        },
                    )
                    etree.SubElement(item, "description").text = etree.CDATA(
                        html.tostring(description, encoding="unicode", method="xml")
                    )

                if (child.tag == 'div' and child.attrib.get("class") == "mt-auto"):
                    title.text += child.find('a').text.strip()
                    # etree.SubElement(item, 'title').text = title


        return item

    def generate_jvlib_entries(self, channel: etree._Element) -> etree._Element | None:
        pass

if __name__ == "__main__":
    rss = RSS()
    rss.generate_entries(Providers.jvdtbs)
    print(
        etree.tostring(
            rss.rss,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
            standalone=True,
        ).decode("utf-8")
    )
