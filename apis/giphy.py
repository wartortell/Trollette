import os
import json
import wget
import argparse
import giphypop

from helpers import get_data_folder, get_file_md5, default_logger


class GiphyAPI:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        self.gipher = giphypop.Giphy()

    def search_gifs(self, term, min_width=0, max_width=1000, min_height=0, max_height=1000, max_size=5000000, limit=50):
        gifs = self.gipher.search(term=term, limit=limit)

        gif_urls = list()
        for gif in [x for x in gifs]:
            if (min_width <= gif.width <= max_width) and (min_height <= gif.height <= max_height) and gif.filesize <= max_size:
                if gif.width > gif.height:
                    gif_urls.append(gif.fixed_width.url)
                else:
                    gif_urls.append(gif.fixed_height.url)

        return gif_urls

    def farm_gif_term(self, term, amount=35, threshold=10):
        self.logger("Farming GIFs for %s..." % term)

        gif_dir_path = os.path.join("Gifs", term)
        if not os.path.isdir(gif_dir_path):
            os.mkdir(gif_dir_path)

        if not (term in self.gifs):
            self.gifs[term] = []

        attempt_count = 0
        while (attempt_count < threshold) and (len(self.gifs[term]) < amount):

            image_path = "test.gif"
            try:
                os.remove(image_path)
            except:
                pass

            try:
                img = translate(term)
                wget.download(img.fixed_height.url, image_path)

                image_md5 = get_file_md5(image_path)

                if not (image_md5 in self.gifs[term]):
                    self.gifs[term].append(image_md5)
                    shutil.copy(image_path, os.path.join(gif_dir_path, "%s.gif" % image_md5))
                    self.logger("    GIF saved to archive. %d/%d GIFs." % (len(self.gifs[term]), amount))
                    attempt_count = 0
                else:
                    self.logger("    Already had GIF!")
                    attempt_count += 1
            except:
                self.logger("    Downloading failed")
                attempt_count += 1

        self.logger("Farming of %s GIFs complete, now holding %d GIFs" % (term, len(self.gifs[term])))

        with open(os.path.join("GIFs", "hashes.json"), "w") as f:
            json.dump(self.gifs, f, indent=2)

    def farm_gifs(self, terms, amount=35, threshold=10):
        self.show_gif_counts()

        for term in terms:

            self.logger("Farming GIFs for %s..." % term)

            if not (term in self.gifs):
                self.gifs[term] = []

            self.farm_gif_term(term, amount, threshold)

        self.show_gif_counts()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--term", action="store", required=False, help="Term to search giphy with")
    args = parser.parse_args()

    giph = GiphyAPI()
    if args.term:
        print("\n".join(giph.search_gifs(args.term)))
    else:
        parser.print_help()
