import os
import re
import json
import shutil
import urllib
import argparse
import urllib.parse

from helpers import default_logger, get_file_md5, get_data_folder, MyOpener


class QuoteFarmer:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        self.quotes_folder_path = get_data_folder("quotes")

        self.quote_authors = dict()
        self.quote_topics = dict()
        self.load_quotes()

    def load_quotes(self):
        for json_file in os.listdir(self.quotes_folder_path):
            json_path = os.path.join(self.quotes_folder_path, json_file)

            with open(json_path, "r") as f:
                j = json.load(f)

            topic = json_file.replace(".json", "").replace("quotes_", "")
            self.quote_topics[topic] = list()

            for quote in j:
                if quote["name"] not in self.quote_authors:
                    self.quote_authors[quote["name"]] = set()

                self.quote_authors[quote["name"]].add(quote["quote"])

                self.quote_topics[topic].append(quote)

    def random_quote(self):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--term", action="store", required=False, help="Term to search giphy with")
    args = parser.parse_args()

    quotr = QuoteFarmer()
    if args.term:
        imgr.farm_images(args.term.split(","))
    else:
        parser.print_help()
