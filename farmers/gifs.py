import os
import json
import wget
import shutil
import argparse

from apis.giphy import GiphyAPI
from helpers import default_logger, get_data_folder, get_file_md5


class GifFarmer:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        self.gif_folder_path = get_data_folder("gifs")
        self.gif_hashes_json = os.path.join(self.gif_folder_path, "hashes.json")

        if not os.path.isfile(self.gif_hashes_json):
            with open(self.gif_hashes_json, "w") as f:
                json.dump(dict(), f)

        with open(self.gif_hashes_json, "r") as f:
            self.gifs = json.load(f)

        self.giphy = GiphyAPI(self.logger)

    def show_gif_counts(self):
        self.logger("Current GIF Counts:\n-----------------------")
        for s in self.gifs:
            self.logger("  {}: {}".format(s, len(self.gifs[s])))
        self.logger("\n")

    def farm_gif_term(self, term, amount=50):
        self.logger("Farming GIFs for %s..." % term)

        gif_term_dir = os.path.join(self.gif_folder_path, term)
        if not os.path.isdir(gif_term_dir):
            os.mkdir(gif_term_dir)

        if not (term in self.gifs):
            self.gifs[term] = []

        gif_urls = self.giphy.search_gifs(term, limit=amount)

        image_path = "test.gif"
        for url in gif_urls:
            try:
                os.remove(image_path)
            except:
                pass

            try:
                wget.download(url, image_path)
                image_md5 = get_file_md5(image_path)

                if image_md5 not in self.gifs[term]:
                    self.gifs[term].append(image_md5)
                    shutil.copy(image_path, os.path.join(gif_term_dir, "{}.gif".format(image_md5)))
                    self.logger("    {}: GIF saved to archive.".format(image_md5))
                else:
                    self.logger("    {}: Already had GIF!".format(image_md5))
            except:
                self.logger("    Downloading failed: {}".format(url))

        self.logger("Farming of {} GIFs complete, now holding {} GIFs.\n".format(term, len(self.gifs[term])))

        with open(self.gif_hashes_json, "w") as f:
            json.dump(self.gifs, f, indent=2)

    def farm_gifs(self, terms):
        self.show_gif_counts()

        for term in terms:
            self.farm_gif_term(term)

        self.show_gif_counts()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--term", action="store", required=False, help="Term to search giphy with")
    args = parser.parse_args()

    giph = GifFarmer()
    if args.term:
        giph.farm_gifs(args.term.split(","))
    else:
        parser.print_help()
