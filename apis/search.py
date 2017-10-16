import os
import re
import html
import json
import argparse
import requests
from urllib.parse import parse_qs, urlparse
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

from helpers import default_logger


class SearchAPI:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        try:
            import configparser
            p = configparser.ConfigParser()
            conf_path = os.environ.get("TROLLETTE_CONFIG", "~/.config/trollette")
            p.read(os.path.expanduser(conf_path))

            self.google_api = p.get("google", "api_key")
            self.google_cse_id = p.get("google", "cse_id")

        except:
            self.google_api = ""
            self.google_cse_id = ""

    def google_basic_search(self, term, amount=50):
        count = 0
        search_links = list()

        while count < amount:
            if not count:
                page = requests.get("http://www.google.de/search?q={}".format(term))
            else:
                page = requests.get("http://www.google.de/search?q={}&start={}".format(term, count))
            soup = BeautifulSoup(page.content, "lxml")
            l = soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)"))
            urls = [parse_qs(urlparse(link["href"]).query)['q'][0] for link in l]
            search_links.extend([url for url in urls if 'webcache' not in url])

            count += 10

        return search_links

    def get_google_links(self, query, amount=50):
        service = build("customsearch", "v1", developerKey=self.google_api)

        links = list()
        while len(links) < amount:
            if len(links):
                res = service.cse().list(q=query, cx=self.google_cse_id, start=len(links)).execute()
            else:
                res = service.cse().list(q=query, cx=self.google_cse_id).execute()

            for item in res['items']:
                links.append(item['link'])

        return links


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topic", action="store", required=False, help="Topic to search wikipedia for")
    args = parser.parse_args()

    sear = SearchAPI()
    if args.topic:
        links = sear.google_basic_search(args.topic)

        print("\n".join(links))
    else:
        parser.print_help()
