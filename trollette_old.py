import os
import re
import wget
import json
import random
import string
import shutil
import hashlib

import unicodedata
import datetime

from urllib.request import FancyURLopener, build_opener
import urllib.parse

import simplejson

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT

from giphypop import translate

from slide_weights import SlideWeights
from content_troll import Face
from data_farmer import DataFarmer

from pymarkovchain import MarkovChain


class MyOpener(FancyURLopener, object):
    version = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"


class Trollette:
    def __init__(self):
        self.presenter = ""
        self.title = ""

        self.slide_count = 0
        self.slide_min = 10
        self.slide_max = 12

        self.console = None
        self.output_dir = ""

        with open("terms.json", "r") as f:
            self.terms = json.load(f)

        # Load up the proverb data
        with open(os.path.join("Proverbs", "facts"), "r") as f:
            self.proverb_lines = f.readlines()
        self.proverbs = map(str.strip, self.proverb_lines)
        self.proverb_markov = MarkovChain("markov.db")
        self.proverb_markov.generateDatabase("".join(self.proverb_lines), n=1)

        # Make the text data
        # self.my_face = comptroller.face(self.title)
        # self.slide_titles = self.my_face.get_titles(50)
        # self.slide_bullets = self.my_face.get_bullets(100)

        self.my_face = Face("")

        self.slide_titles = ["shit", "balls", "butts"]
        self.slide_bullets = ["butts", "do", "stuff", "fucks", "more fucks"]

        self.ppt = Presentation()
        self.slide_weights = SlideWeights()





    def add_term(self, term_type, term):
        if term in self.terms[term_type]:
            return "Term \"%s\" is already in %s!" % (term, term_type)
        else:
            self.terms[term_type].append(term)
            with open("terms.json", "w") as f:
                json.dump(self.terms, f, indent=4)
            return "Term \"%s\" added to %s." % (term, term_type)

    def delete_term(self, term_type, term):
        if not (term in self.terms[term_type]):
            return "Term \"%s\" isn't in %s, can't delete!" % (term, term_type)
        else:
            self.terms[term_type].remove(term)
            with open("terms.json", "w") as f:
                json.dump(self.terms, f, indent=4)
            return "Term \"%s\" removed from %s." % (term, term_type)

    def show_term_counts(self, term_type, term_json):
        log_str = "%s Terms:\n" % term_type
        for term in self.terms[term_type]:
            if term in term_json:
                log_str += "  %s: %d\n" % (term, len(term_json[term]))
            else:
                log_str += "  %s: 0\n" % term
        self.log(log_str)

    def get_file_md5(self, file_path):
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        file_hasher = hashlib.md5()
        file_hasher.update(image_bytes)
        return file_hasher.hexdigest()

    def farm_image_term(self, term, amount=35, threshold=10):
        self.log("Farming images for %s..." % term)

        if not (term in self.images):
            self.images[term] = []

        attempt_count = 0
        while (attempt_count < threshold) and (len(self.images[term]) < amount):
            myopener = MyOpener()
            page = myopener.open('https://www.google.pt/search?q=%s&source=lnms&tbm=isch&sa=X&tbs=isz:l&tbm=isch' % term.replace(" ", "+"))
            html = page.read()

            for match in re.finditer(r'<a href="/imgres\?imgurl=(.*?)&amp;imgrefurl', html, re.IGNORECASE | re.DOTALL | re.MULTILINE):
                if len(self.images[term]) >= amount:
                    break

                try:
                    os.remove("test.img")
                except:
                    pass

                try:
                    path = urllib.parse.urlsplit(match.group(1)).path
                    self.log("  Downloading %s" % match.group(1))
                    myopener.retrieve(match.group(1), "test.img")

                    image_md5 = self.get_file_md5("test.img")

                    if not (image_md5 in self.images[term]):
                        self.images[term].append(image_md5)
                        shutil.copy("test.img", os.path.join("Images", "%s.img" % image_md5))
                        os.remove("test.img")
                        self.log("    Image saved to archive. %d/%d images." % (len(self.images[term]), amount))
                        attempt_count = 0
                    else:
                        self.log("    Already had image!")
                        attempt_count += 1
                except:
                    self.log("    Downloading failed")
                    attempt_count += 1

        self.log("Farming of %s images complete, now holding %d images" % (term, len(self.images[term])))

        with open(os.path.join("Images", "hashes.json"), "w") as f:
            json.dump(self.images, f, indent=2)

    def farm_images(self, amount=25, threshold=10):
        self.show_term_counts("image_searches", self.images)

        all_farm = self.terms["image_searches"]
        all_farm.extend(self.terms["talk_titles"])

        for term in all_farm:
            self.farm_image_term(term, amount, threshold)

    def farm_gif_term(self, term, amount=35, threshold=10):
        self.log("Farming GIFs for %s..." % term)

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

                image_md5 = self.get_file_md5("test.gif")

                if not (image_md5 in self.gifs[term]):
                    self.gifs[term].append(image_md5)
                    shutil.copy(image_path, os.path.join("GIFs", "%s.gif" % image_md5))
                    self.log("    GIF saved to archive. %d/%d GIFs." % (len(self.gifs[term]), amount))
                    attempt_count = 0
                else:
                    self.log("    Already had GIF!")
                    attempt_count += 1
            except:
                self.log("    Downloading failed")
                attempt_count += 1

        self.log("Farming of %s GIFs complete, now holding %d GIFs" % (term, len(self.gifs[term])))

        with open(os.path.join("GIFs", "hashes.json"), "w") as f:
            json.dump(self.gifs, f, indent=2)

    def farm_gifs(self, amount=35, threshold=10):
        self.show_term_counts("giphy_searches", self.gifs)

        all_farm = self.terms["giphy_searches"]
        all_farm.extend(self.terms["talk_titles"])

        for term in all_farm:

            self.log("Farming GIFs for %s..." % term)

            if not (term in self.gifs):
                self.gifs[term] = []

            self.farm_gif_term(term, amount, threshold)

    def farm_content(self, all_content):
        for talk_title in self.terms["talk_titles"]:
            talk_path = os.path.join("Content", "%s.txt" % talk_title)
            # Either we're replacing all content or we're only replacing files that don't exist
            if all_content or (not os.path.exists(talk_path)):
                self.log("Farming data on %s..." % talk_title)
                with open(talk_path, "w") as f:
                    content = self.my_face.fully_research_topic(talk_title, self.log)
                    if type(content) is str:
                        clean_content = content
                    else:
                        clean_content = unicodedata.normalize('NFKD', content).encode('ascii', 'ignore')
                    f.write(clean_content)

    def log_slide_weights(self):
        self.log(self.slide_weights.get_weights_string())

    def log(self, message):
        if self.console:
            self.console(message)
        else:
            print(message)
