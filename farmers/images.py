import os
import re
import json
import shutil
import urllib
import argparse
import urllib.parse

from helpers import default_logger, get_file_md5, get_data_folder, MyOpener


class ImageFarmer:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        self.images_folder_path = get_data_folder("images")
        self.images_hashes_json = os.path.join(self.images_folder_path, "hashes.json")

        if not os.path.isfile(self.images_hashes_json):
            with open(self.images_hashes_json, "w") as f:
                json.dump(dict(), f)

        with open(self.images_hashes_json, "r") as f:
            self.images = json.load(f)

    def farm_image_term(self, term, amount=35, threshold=10):
        self.logger("Farming images for %s..." % term)

        image_term_path = os.path.join(self.images_folder_path, term)
        if not os.path.isdir(image_term_path):
            os.mkdir(image_term_path)

        if not (term in self.images):
            self.images[term] = []

        attempt_count = 0
        while (attempt_count < threshold) and (len(self.images[term]) < amount):
            myopener = MyOpener()
            page = myopener.open('https://www.google.pt/search?q=%s&source=lnms&tbm=isch&sa=X&tbs=isz:l&tbm=isch' % term.replace(" ", "+"))
            html = str(page.read())

            #for match in re.finditer(r'<a href="/imgres\?imgurl=(.*?)&amp;imgrefurl', html, re.IGNORECASE | re.DOTALL | re.MULTILINE):
            for match in re.finditer(r'\"ou\":\"(.*?)\",\"', html, re.IGNORECASE | re.DOTALL | re.MULTILINE):
                if len(self.images[term]) >= amount:
                    break

                try:
                    os.remove("test.img")
                except:
                    pass

                try:
                    image_url = match.group(1)
                    self.logger("  Downloading {}".format(image_url))
                    myopener.retrieve(match.group(1), "test.img")

                    image_md5 = get_file_md5("test.img")

                    if not (image_md5 in self.images[term]):
                        self.images[term].append(image_md5)
                        shutil.copy("test.img", os.path.join(image_term_path, "{}.img".format(image_md5)))
                        os.remove("test.img")
                        self.logger("    Image saved to archive. {}/{} images.".format(len(self.images[term]), amount))
                        attempt_count = 0
                    else:
                        self.logger("    Already had image!")
                        attempt_count += 1

                except Exception as e:
                    self.logger("    Downloading failed: {}".format(e))
                    attempt_count += 1

        self.logger("Farming of {} images complete, now holding {} images".format(term, len(self.images[term])))

        with open(self.images_hashes_json, "w") as f:
            json.dump(self.images, f, indent=2)

    def farm_images(self, terms, amount=25, threshold=10):
        self.show_image_counts()

        for term in terms:
            self.farm_image_term(term, amount, threshold)

        self.show_image_counts()

    def show_image_counts(self):
        self.logger("Current Image Counts:\n-----------------------")
        for s in self.images:
            self.logger("  {}: {}".format(s, len(self.images[s])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--term", action="store", required=False, help="Term to search giphy with")
    args = parser.parse_args()

    imgr = ImageFarmer()
    if args.term:
        imgr.farm_images(args.term.split(","))
    else:
        parser.print_help()
