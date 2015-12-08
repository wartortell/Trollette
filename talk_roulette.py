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

from urllib import FancyURLopener
import urlparse

import urllib2
import simplejson

import Tkinter as tk
import ttk

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_PARAGRAPH_ALIGNMENT

from giphypop import translate

from slide_weights import SlideWeights
from content_troll import Face

from pymarkovchain import MarkovChain


class MyOpener(FancyURLopener, object):
    version = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"


class Trollette:
    def __init__(self):
        self.presenter = ""
        self.title = ""

        self.slide_count = 0
        self.slide_min = 15
        self.slide_max = 25

        self.console = None
        self.output_dir = ""

        with open("terms.json", "r") as f:
            self.terms = json.load(f)

        with open(os.path.join("GIFs", "hashes.json"), "r") as f:
            self.gifs = json.load(f)

        with open(os.path.join("Images", "hashes.json"), "r") as f:
            self.images = json.load(f)

        # Load up the proverb data
        with open(os.path.join("Proverbs", "facts"), "r") as f:
            self.proverb_lines = f.readlines()
        self.proverbs = map(string.strip, self.proverb_lines)
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

    def generate_slide_deck(self):
        # Create a place to put data and resources
        self.output_dir = os.path.join("Output", "%s_%s_%s" % (self.title,
                                                               self.presenter,
                                                               datetime.datetime.strftime(datetime.datetime.now(), '%Y_%m_%d_%H_%M_%S')))

        self.resources_dir = os.path.join(self.output_dir, "Resources")

        # Start with a fresh PowerPoint
        self.ppt = Presentation()

        # Make sure the directories exist
        try:
            os.makedirs(self.output_dir)
            os.makedirs(self.resources_dir)
        except:
            self.log("Directory %s already exists, overwriting..." % self.output_dir)

        self.slide_count = random.randint(self.slide_min, self.slide_max)
        self.log("Generating a slide deck of %d slides about %s" % (self.slide_count, self.title))

        try:
            self.log("Getting slide content...")
            self.my_face.set_topic(self.title)

            self.log("Generating slide titles...")
            self.slide_titles = self.my_face.get_titles(self.slide_count)

            self.log("Generating slide bullets...")
            self.slide_bullets = self.my_face.get_bullets(self.slide_count*3)
        except:
            self.log("Problem generating content for a talk on %s, exiting..." % self.title)
            return

        #self.farm_gif_term(self.title)
        #sp = self.title.split(" ")
        #if len(sp) > 1:
        #    for i in range(len(sp)):
        #        if len(sp[i]) > 5:
        #            self.farm_gif_term(sp[i])
        #self.farm_image_term(self.title)

        self.log_slide_weights()

        self.create_title_slide()
        self.create_slides()

        slide_path = os.path.join(self.output_dir, "%s.pptx" % self.title)
        self.ppt.save(slide_path)

        self.log("Successfully generated PPT on %s to %s" % (self.title, slide_path))

    def create_title_slide(self):
        title_slide_layout = self.ppt.slide_layouts[0]
        slide = self.ppt.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]

        title.text = self.title
        subtitle.text = self.presenter

    def create_slides(self):
        for i in range(self.slide_count):
            choice = self.slide_weights.choose_weighted()

            self.log("  Generating slide #%d: %s" % (i+1, choice))

            new_slide_layout = None
            if choice == "Single GIF":
                ns = self.create_gif_slide(random.choice(self.slide_titles), self.get_giphy_search_term(), i)
            elif choice == "Full Slide GIF":
                ns = self.create_full_gif_slide(self.get_giphy_search_term(), i)
            elif choice == "Single Image":
                ns = self.create_image_slide(random.choice(self.slide_titles), self.get_image_search_term(), i)
            elif choice == "Full Slide Image":
                ns = self.create_full_image_slide(self.get_image_search_term(), i)
            elif choice == "Information":
                ns = self.create_info_slide(i)
            elif choice == "Quotation":
                ns = self.create_quote_slide()

    def create_single_full_image_slide(self, image_path):
        blank_slide_layout = self.ppt.slide_layouts[6]
        new_slide = self.ppt.slides.add_slide(blank_slide_layout)

        left = Inches(0)
        top = Inches(0)
        height = Inches(8)
        width = Inches(10)
        pic = new_slide.shapes.add_picture(image_path, left, top, height=height, width=width)
        return new_slide

    def create_single_image_slide(self, slide_title, image_path):

        blank_slide_layout = self.ppt.slide_layouts[1]
        new_slide = self.ppt.slides.add_slide(blank_slide_layout)

        for shape in new_slide.shapes:
            if shape.is_placeholder:
                phf = shape.placeholder_format

                if phf.type == 1:
                    shape.text = slide_title

        left = Inches(1)
        top = Inches(1)
        height = Inches(6)
        width = Inches(8)
        pic = new_slide.shapes.add_picture(image_path, left, top, height=height, width=width)

        return new_slide

    def download_gif(self, term, slide_num):
        # If we have at least 3 local gifs, use one of those
        if (term in self.gifs) and (len(self.gifs[term]) > 3):
            return os.path.join("GIFs", "%s.gif" % random.choice(self.gifs[term]))

        try:
            # Download the gif
            img = translate(term)
            image_path = os.path.join(self.resources_dir, "%d.gif" % slide_num)
            wget.download(img.fixed_height.url, image_path)

            file_hasher = hashlib.md5()
            with open(image_path, "rb") as f:
                file_hasher.update(f.read())
            file_md5 = file_hasher.hexdigest()

            if not (term in self.gifs):
                self.gifs[term] = []

            if not (file_md5 in self.gifs[term]):
                self.gifs[term].append(file_md5)
                shutil.copy(image_path, os.path.join("GIFs", "%s.gif" % file_md5))
                with open(os.path.join("GIFs", "hashes.json"), "w") as f:
                    json.dump(self.gifs, f, indent=2)

            return image_path
        except:
            return None

    def download_image(self, term, slide_num):
        # If we have at least 3 local images, use one of those
        if (term in self.images) and (len(self.images[term]) > 3):
            return os.path.join("Images", "%s.img" % random.choice(self.images[term]))

        try:
            search_term = term
            if (random.randint(0, 100) % 2) == 0:
                search_term = self.title

            download_attempts = 0
            image_bytes = ""
            image_path = ""
            while download_attempts < 10:

                fetcher = urllib2.build_opener()
                start_index = random.randint(0, 50)
                search_url = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s&start=%s" % (search_term, str(start_index))
                f = fetcher.open(search_url)
                deserialized_output = simplejson.load(f)

                image_url = deserialized_output['responseData']['results'][random.randint(0, len(deserialized_output['responseData']['results'])-1)]['unescapedUrl']
                image_path = os.path.join(self.resources_dir, "%d.img" % slide_num)
                wget.download(image_url, image_path)

                with open(image_path, "rb") as f:
                    image_bytes = f.read()

                if (not image_bytes.startswith("<!DOCTYPE html>")) and (not image_bytes.startswith("<html>")):
                    break

                download_attempts += 1
                self.log("    Attempting to download image about %s failed try #%d" % (search_term, download_attempts))

            if image_bytes.startswith("<!DOCTYPE html") or image_bytes.startswith("<html>"):
                return None

            file_hasher = hashlib.md5()
            file_hasher.update(image_bytes)
            file_md5 = file_hasher.hexdigest()

            if not (term in self.images):
                self.images[term] = []

            if not (file_md5 in self.images[term]):
                self.images[term].append(file_md5)
                shutil.copy(image_path, os.path.join("Images", "%s.img" % file_md5))
                with open(os.path.join("Images", "hashes.json"), "w") as f:
                    json.dump(self.images, f, indent=2)

            return image_path
        except:
            return None

    def create_gif_slide(self, slide_title, term, slide_num):
        image_path = self.download_gif(term, slide_num)
        if image_path:
            return self.create_single_image_slide(slide_title, image_path)

    def create_full_gif_slide(self, term, slide_num):
        image_path = self.download_gif(term, slide_num)
        if image_path:
            return self.create_single_full_image_slide(image_path)

    def create_image_slide(self, slide_title, term, slide_num):
        while True:
            try:
                image_path = self.download_image(term, slide_num)
                if image_path:
                    return self.create_single_image_slide(slide_title, image_path)
            except:
                pass

    def create_full_image_slide(self, term, slide_num):
        image_path = self.download_image(term, slide_num)
        if image_path:
            return self.create_single_full_image_slide(image_path)

    def create_info_slide(self, slide_num):
        slide_title_info = random.choice(self.slide_titles)
        slide_title = slide_title_info
        if (random.randint(0, 100) % 3) == 0:
            slide_title = self.get_markov_proverb()

        sb = random.sample(self.slide_bullets, random.randint(1, 4))
        if (random.randint(0, 100) % 4) == 0:
            sb.append(self.get_markov_proverb())

        bullet_slide_layout = self.ppt.slide_layouts[1]
        new_slide = self.ppt.slides.add_slide(bullet_slide_layout)
        shapes = new_slide.shapes

        title_shape = shapes.title
        body_shape = shapes.placeholders[1]
        body_shape.width = Inches(4)
        body_shape.left = Inches(1)
        body_shape.top = Inches(2)

        title_shape.text = slide_title

        tf = body_shape.text_frame
        for b in sb:
            p = tf.add_paragraph()
            #p.text = b

            p.alignment = PP_PARAGRAPH_ALIGNMENT.LEFT
            run1 = p.add_run()
            run1.text = b
            font1 = run1.font
            font1.name = 'Sans Serif'
            font1.size = Pt(20)
            font1.italic = True
            font1.bold = True

        image_path = None
        attempts = 0
        while attempts < 10:
            try:
                tries = 0
                while (not image_path) and (tries < 10):
                    if (random.randint(0, 100) % 2) == 0:
                        search_term = self.get_giphy_search_term()
                        image_path = self.download_gif(search_term, slide_num)
                    else:
                        search_term = self.get_image_search_term()
                        image_path = self.download_image(search_term, slide_num)

                    tries += 1

                if tries < 10:
                    left = Inches(5.5)
                    top = Inches(3)
                    #height = Inches(3)
                    width = Inches(3)
                    pic = new_slide.shapes.add_picture(image_path, left, top, width=width)
                    break
                attempts += 1

            except:
                attempts += 1

        return new_slide

    def create_quote_slide(self):
        # Pick a random quote category and quote
        cat = random.choice(self.terms["quote_categories"])
        with open(os.path.join("Quotes", "quotes_%s.json" % cat)) as f:
            q1 = random.choice(json.load(f))

        cat = random.choice(self.terms["quote_categories"])
        with open(os.path.join("Quotes", "quotes_%s.json" % cat)) as f:
            q2 = random.choice(json.load(f))

        quote_text = "\"%s\"" % q1["quote"]
        if (random.randint(0,100) % 5) == 0:
            quote_text = random.choice(self.proverbs)

        quote_author = "- %s" % q2["name"]

        blank_slide_layout = self.ppt.slide_layouts[2]
        new_slide = self.ppt.slides.add_slide(blank_slide_layout)

        for shape in new_slide.shapes:
            if shape.is_placeholder:
                phf = shape.placeholder_format
                if phf.type == 1:
                    # Put in the quote title
                    shape.text = random.choice(self.terms["quote_titles"])

                elif phf.type == 2:
                    text_frame = shape.text_frame

                    # Create the quote text paragraph
                    p1 = text_frame.paragraphs[0]
                    p1.alignment = PP_PARAGRAPH_ALIGNMENT.LEFT
                    run1 = p1.add_run()
                    run1.text = quote_text
                    font1 = run1.font
                    font1.name = 'Sans Serif'
                    font1.size = Pt(30)
                    font1.italic = True
                    font1.bold = True

                    # Create the Author text paragraph
                    p2 = text_frame.add_paragraph()
                    p2.alignment = PP_PARAGRAPH_ALIGNMENT.RIGHT
                    run2 = p2.add_run()
                    run2.text = quote_author
                    font2 = run2.font
                    font2.name = 'Calibri'
                    font2.size = Pt(24)

        return new_slide

    def get_giphy_search_term(self):
        st = random.choice(self.terms["giphy_searches"])
        if (random.randint(0, 100) % 5) == 0:
            st = self.title
        return st

    def get_image_search_term(self):
        st = random.choice(self.terms["image_searches"])
        if (random.randint(0, 100) % 2) == 0:
            st = self.title
        return st

    def get_proverb(self):
        return random.choice(self.proverb_lines)

    def get_markov_proverb(self, min=5, max=10):
        b = ""

        while True:
            b = self.proverb_markov.generateString()
            s = b.split(" ")
            if min <= len(s) <= max:
                break

        return b

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

    def farm_image_term(self, term, amount=25, threshold=10):
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
                    path = urlparse.urlsplit(match.group(1)).path
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

    def farm_gif_term(self, term, amount=25, threshold=10):
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

    def farm_gifs(self, amount=25, threshold=10):
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
            self.console.config(state=tk.NORMAL)
            self.console.insert(tk.END, "%s\n" % message)
            self.console.see(tk.END)
            self.console.config(state=tk.DISABLED)
            self.console.update()
        else:
            print(message)


class TrolletteApp(tk.Frame):
    ''' An example application for TkInter.  Instantiate
        and call the run method to run. '''
    def __init__(self, master):
        # Initialize window using the parent's constructor
        tk.Frame.__init__(self, master, width=1000, height=800)

        self.master.title("Trollette")

        self.pack_propagate(0)

        self.troll = Trollette()

        # Talk Title and Presenter entries
        tk.Label(master, text="Talk Title", anchor="w").grid(row=0, column=0)
        tk.Label(master, text="Talk Title (Custom)", anchor="w").grid(row=1, column=0)
        tk.Label(master, text="Presenter (Optional)", anchor="w").grid(row=2, column=0)

        self.talk_title_string = tk.StringVar()
        self.talk_title_dropdown = tk.OptionMenu(master, self.talk_title_string, *self.troll.terms["talk_titles"]).grid(row=0, column=1)
        self.talk_title_entry = tk.Entry(master)
        self.talk_title_entry.grid(row=1, column=1)
        self.presenter_entry = tk.Entry(master)
        self.presenter_entry.grid(row=2, column=1)

        ttk.Separator(master, orient=tk.HORIZONTAL).grid(row=3, columnspan=2, sticky="ew")

        # Slide minimum and maximum entries
        tk.Label(master, text="Minimum Slide Count", anchor="w").grid(row=4, column=0)
        tk.Label(master, text="Maximum Slide Count", anchor="w").grid(row=5, column=0)

        self.slide_count_min_entry = tk.Entry(master)
        self.slide_count_min_entry.grid(row=4, column=1)
        self.slide_count_min_entry.insert(0, str(self.troll.slide_min))
        self.slide_count_max_entry = tk.Entry(master)
        self.slide_count_max_entry.grid(row=5, column=1)
        self.slide_count_max_entry.insert(0, str(self.troll.slide_max))

        ttk.Separator(master, orient=tk.HORIZONTAL).grid(row=6, columnspan=2, sticky="ew")

        # Add the options for scaling slide type
        tk.Label(master, text="Slide Type Weights", anchor="w").grid(row=7, column=0)

        self.weights = {}

        r = 8
        for key in self.troll.slide_weights.weights.keys():
            tk.Label(master, text=key, anchor="w").grid(row=r, column=0)
            s = tk.Scale(master, orient=tk.HORIZONTAL, length=150)
            s.grid(row=r, column=1)
            s.set(self.troll.slide_weights.weights[key])
            self.weights[key] = s
            r += 1

        ttk.Separator(master, orient=tk.HORIZONTAL).grid(row=r, columnspan=2, sticky="ew")
        r += 1

        self.show_gif_button = tk.Button(master, text='Show GIF Search Terms', command=self.show_gif_terms)
        self.show_gif_button.grid(row=r, columnspan=2)
        self.add_gif_entry = tk.Entry(master)
        self.add_gif_entry.grid(row=r+1, columnspan=2)
        self.add_gif_button = tk.Button(master, text='Add GIF Term', command=self.add_gif_term)
        self.add_gif_button.grid(row=r+2, column=0)
        self.delete_gif_button = tk.Button(master, text='Delete GIF Term', command=self.delete_gif_term)
        self.delete_gif_button.grid(row=r+2, column=1)
        r += 3

        ttk.Separator(master, orient=tk.HORIZONTAL).grid(row=r, columnspan=2, sticky="ew")
        r += 1

        self.show_image_button = tk.Button(master, text='Show Image Search Terms', command=self.show_image_terms)
        self.show_image_button.grid(row=r, columnspan=2)
        self.add_image_entry = tk.Entry(master)
        self.add_image_entry.grid(row=r+1, columnspan=2)
        self.add_image_button = tk.Button(master, text='Add Image Term', command=self.add_image_term)
        self.add_image_button.grid(row=r+2, column=0)
        self.delete_image_button = tk.Button(master, text='Delete Image Term', command=self.delete_image_term)
        self.delete_image_button.grid(row=r+2, column=1)
        r += 3

        ttk.Separator(master, orient=tk.HORIZONTAL).grid(row=r, columnspan=2, sticky="ew")
        r += 1

        self.farm_gif_button = tk.Button(master, text='Farm GIFs', command=self.farm_gifs)
        self.farm_gif_button.grid(row=r, column=0)

        self.farm_image_button = tk.Button(master, text='Farm Images', command=self.farm_images)
        self.farm_image_button.grid(row=r, column=1)
        r += 1

        self.farm_new_content_button = tk.Button(master, text='Farm New Content', command=self.farm_new_content)
        self.farm_new_content_button.grid(row=r, column=0)

        self.farm_all_content_button = tk.Button(master, text='Farm All Content', command=self.farm_all_content)
        self.farm_all_content_button.grid(row=r, column=1)
        r += 1

        ttk.Separator(master, orient=tk.HORIZONTAL).grid(row=r, columnspan=2, sticky="ew")
        r += 1

        self.go_button = tk.Button(master, text='Trollerate!', command=self.generate_troll)
        self.go_button.grid(row=r, column=0, columnspan=2)
        r += 1

        # Create the output window
        self.trollette_output = tk.Text(master, bd=4, state=tk.DISABLED, width=80, height=40)
        self.trollette_output.config(font=("courier new", 14), background="black", foreground="green")
        self.trollette_output.grid(row=0, rowspan=r, column=2)

        self.trollette_output_scroll = tk.Scrollbar(master, command=self.trollette_output.yview)
        self.trollette_output_scroll.grid(row=0, rowspan=r, column=3, sticky='nsew')
        self.trollette_output['yscrollcommand'] = self.trollette_output_scroll.set

        self.troll.console = self.trollette_output

    def show_gif_terms(self):
        self.troll.log("GIF Search Terms:\n%s" % json.dumps(self.troll.terms["giphy_searches"], indent=4))

    def add_gif_term(self):
        self.troll.log(self.troll.add_term("giphy_searches", self.add_gif_entry.get()))

    def delete_gif_term(self):
        self.troll.log(self.troll.delete_term("giphy_searches", self.add_gif_entry.get()))

    def show_image_terms(self):
        self.troll.log("Image Search Terms:\n%s" % json.dumps(self.troll.terms["image_searches"], indent=4))

    def add_image_term(self):
        self.troll.log(self.troll.add_term("image_searches", self.add_image_entry.get()))

    def delete_image_term(self):
        self.troll.log(self.troll.delete_term("image_searches", self.add_image_entry.get()))

    def farm_gifs(self):
        self.troll.farm_gifs()

    def farm_images(self):
        self.troll.farm_images()

    def farm_new_content(self):
        self.troll.farm_content(all_content=False)

    def farm_all_content(self):
        self.troll.farm_content(all_content=True)

    def generate_troll(self):
        if (self.talk_title_entry.get() == "") and (self.talk_title_string.get() == ""):
            self.troll.log("You must choose a talk title or enter one before generating a Powerpoint!")
            return

        if not (self.talk_title_entry.get() == ""):
            self.troll.title = self.talk_title_entry.get()
        else:
            self.troll.title = self.talk_title_string.get()
        self.troll.presenter = self.presenter_entry.get()

        try:
            self.troll.slide_min = int(self.slide_count_min_entry.get())
            self.troll.slide_max = int(self.slide_count_max_entry.get())
        except:
            self.troll.log("You must use integers for slide min and max!")
            return

        for key in self.weights.keys():
            self.troll.slide_weights.set_weight(key, int(self.weights[key].get()))

        self.troll.generate_slide_deck()

    def run(self):
        ''' Run the app '''
        self.mainloop()


class TrolletteGUI(tk.Frame):
    ''' An example application for TkInter.  Instantiate
        and call the run method to run. '''
    def __init__(self, master):
        # Initialize window using the parent's constructor
        tk.Frame.__init__(self, master, width=1000, height=800, background="black")

        self.master.title("Trollette")
        self.master.configure(background="black")

        self.pack_propagate(0)

        self.troll = Trollette()

        self.style = ttk.Style()
        self.create_styles()

        ### CREATE ALL THE PANES

        # Main Window Pane

        self.pane_main = ttk.PanedWindow(orient=tk.VERTICAL)
        self.pane_main.pack(fill=tk.BOTH, expand=1)

        # Options Pane
        self.pane_top = ttk.PanedWindow(self.pane_main, orient=tk.HORIZONTAL)
        self.pane_top.pack(fill=tk.BOTH, expand=1)
        self.pane_main.add(self.pane_top)

        # Title, Presenter, Trollerate Pane
        self.pane_trollerate = ttk.PanedWindow(self.pane_top, orient=tk.VERTICAL)
        self.pane_trollerate.pack(fill=tk.BOTH, expand=1)
        self.pane_top.add(self.pane_trollerate)

        # Output Pane
        self.pane_bottom = ttk.PanedWindow(self.pane_main, orient=tk.HORIZONTAL)
        self.pane_bottom.pack(fill=tk.BOTH, expand=1)
        self.pane_main.add(self.pane_bottom)

        self.trollette_output = tk.Text(self.pane_bottom, bd=4, state=tk.DISABLED, width=80, height=40)
        self.trollette_output.config(font=("courier new", 16), background="black", foreground="green")
        self.trollette_output.pack(fill=tk.BOTH, expand=1)
        self.trollette_output.grid(row=0, column=0)
        self.troll.console = self.trollette_output
        self.pane_bottom.add(self.trollette_output)

        self.trollette_output_scroll = ttk.Scrollbar(self.trollette_output, command=self.trollette_output.yview)
        self.trollette_output['yscrollcommand'] = self.trollette_output_scroll.set
        #self.pane_bottom.add(self.trollette_output_scroll)

        # Create the Notebook for Options
        self.notebook = ttk.Notebook(self.pane_top)
        self.frame_slide_weights = ttk.Frame(self.notebook)   # first page, which would get widgets gridded into it
        self.frame_terms = ttk.Frame(self.notebook)   # first page, which would get widgets gridded into it
        self.frame_farming = ttk.Frame(self.notebook)   # first page, which would get widgets gridded into it
        self.notebook.add(self.frame_slide_weights, text='Slide Weights')
        self.notebook.add(self.frame_terms, text='Search Terms')
        self.notebook.add(self.frame_farming, text='Data Farming')
        self.pane_top.add(self.notebook)

        # Add the Title, Presenter, Slide Counts, and Trollerate
        ttk.Label(self.pane_trollerate, text="Talk Title", anchor="w").grid(row=0, column=0, columnspan=2)
        ttk.Label(self.pane_trollerate, text="Presenter", anchor="w").grid(row=1, column=0, columnspan=2)

        self.string_talk_title = tk.StringVar()
        self.dropdown_talk_title = ttk.OptionMenu(self.pane_trollerate, self.string_talk_title, *self.troll.terms["talk_titles"])
        self.dropdown_talk_title.grid(row=0, column=2, columnspan=2)
        self.entry_presenter = ttk.Entry(self.pane_trollerate)
        self.entry_presenter.grid(row=1, column=2, columnspan=2)

        ttk.Label(self.pane_trollerate, text="Slide Min", anchor="w").grid(row=2, column=0)
        ttk.Label(self.pane_trollerate, text="Slide Max", anchor="w").grid(row=2, column=2)
        self.slide_count_min_entry = ttk.Entry(self.pane_trollerate, width=5)
        self.slide_count_min_entry.grid(row=2, column=1)
        self.slide_count_min_entry.insert(0, str(self.troll.slide_min))
        self.slide_count_max_entry = ttk.Entry(self.pane_trollerate, width=5)
        self.slide_count_max_entry.grid(row=2, column=3)
        self.slide_count_max_entry.insert(0, str(self.troll.slide_max))

        self.image_trollerate = tk.PhotoImage(file=os.path.join("Resources", "trollerate.gif"), width=300, height=280)
        self.go_button = ttk.Button(self.pane_trollerate, command=self.generate_troll, image=self.image_trollerate, style="Troll.TButton")

        self.go_button.grid(row=3, column=0, columnspan=4)

        # Add the Slide options
        self.weights = {}

        r = 0
        for key in self.troll.slide_weights.weights.keys():
            ttk.Label(self.frame_slide_weights, text=key, anchor="w").grid(row=r, column=0)
            s = ttk.Scale(self.frame_slide_weights, from_=0, to=100, orient=tk.HORIZONTAL, length=250)
            s.grid(row=r, column=1)
            s.set(self.troll.slide_weights.weights[key])
            self.weights[key] = s
            r += 1

        # Add the Terms Options

        self.show_title_button = ttk.Button(self.frame_terms, text='Show Talk Titles', command=self.show_titles)
        self.show_title_button.grid(row=0, column=0)
        self.add_title_entry = ttk.Entry(self.frame_terms)
        self.add_title_entry.grid(row=1, column=0)
        self.add_title_button = ttk.Button(self.frame_terms, text='Add Title', command=self.add_title)
        self.add_title_button.grid(row=2, column=0)
        self.delete_title_button = ttk.Button(self.frame_terms, text='Delete Title', command=self.delete_title)
        self.delete_title_button.grid(row=3, column=0)

        ttk.Separator(self.frame_terms, orient=tk.VERTICAL).grid(row=0, column=1, rowspan=4, sticky="ns")

        self.show_image_button = ttk.Button(self.frame_terms, text='Show Image Search Terms', command=self.show_image_terms)
        self.show_image_button.grid(row=0, column=2)
        self.add_image_entry = ttk.Entry(self.frame_terms)
        self.add_image_entry.grid(row=1, column=2)
        self.add_image_button = ttk.Button(self.frame_terms, text='Add Image Term', command=self.add_image_term)
        self.add_image_button.grid(row=2, column=2)
        self.delete_image_button = ttk.Button(self.frame_terms, text='Delete Image Term', command=self.delete_image_term)
        self.delete_image_button.grid(row=3, column=2)

        ttk.Separator(self.frame_terms, orient=tk.VERTICAL).grid(row=0, column=3, rowspan=4, sticky="ns")

        self.show_gif_button = ttk.Button(self.frame_terms, text='Show GIF Search Terms', command=self.show_gif_terms)
        self.show_gif_button.grid(row=0, column=4)
        self.add_gif_entry = ttk.Entry(self.frame_terms)
        self.add_gif_entry.grid(row=1, column=4)
        self.add_gif_button = ttk.Button(self.frame_terms, text='Add GIF Term', command=self.add_gif_term)
        self.add_gif_button.grid(row=2, column=4)
        self.delete_gif_button = ttk.Button(self.frame_terms, text='Delete GIF Term', command=self.delete_gif_term)
        self.delete_gif_button.grid(row=3, column=4)

        # Add the farming buttons
        self.farm_gif_button = ttk.Button(self.frame_farming, text='Farm GIFs', command=self.farm_gifs)
        self.farm_gif_button.grid(row=0, column=0)

        self.farm_image_button = ttk.Button(self.frame_farming, text='Farm Images', command=self.farm_images)
        self.farm_image_button.grid(row=1, column=0)

        self.farm_new_content_button = ttk.Button(self.frame_farming, text='Farm New Content', command=self.farm_new_content)
        self.farm_new_content_button.grid(row=2, column=0)

        self.farm_all_content_button = ttk.Button(self.frame_farming, text='Farm All Content', command=self.farm_all_content)
        self.farm_all_content_button.grid(row=3, column=0)


    def create_styles(self):
        self.style.configure("Troll.TButton", bd=0)
        self.style.configure("TPanedWindow", font="courier 20", background="black")
        self.style.configure("TText", font="courier 20", background="black")
        self.style.configure("TScale", font="courier 20", background="black")
        self.style.configure("TEntry", font="courier 20")
        self.style.configure("TLabel", font="courier 20", background="black")
        self.style.configure("TOptionMenu", font="courier 20", background="black")
        self.style.configure("TNotebook", font="courier 20", background="black")
        self.style.configure("TSeparator", padding=20)


    def show_gif_terms(self):
        self.troll.log("GIF Search Terms:\n%s" % json.dumps(self.troll.terms["giphy_searches"], indent=4))

    def add_gif_term(self):
        self.troll.log(self.troll.add_term("giphy_searches", self.add_gif_entry.get()))

    def delete_gif_term(self):
        self.troll.log(self.troll.delete_term("giphy_searches", self.add_gif_entry.get()))

    def show_titles(self):
        self.troll.log("GIF Search Terms:\n%s" % json.dumps(self.troll.terms["talk_titles"], indent=4))

    def add_title(self):
        self.troll.log(self.troll.add_term("talk_titles", self.add_title_entry.get()))

    def delete_title(self):
        self.troll.log(self.troll.delete_term("talk_titles", self.add_title_entry.get()))

    def show_image_terms(self):
        self.troll.log("Image Search Terms:\n%s" % json.dumps(self.troll.terms["image_searches"], indent=4))

    def add_image_term(self):
        self.troll.log(self.troll.add_term("image_searches", self.add_image_entry.get()))

    def delete_image_term(self):
        self.troll.log(self.troll.delete_term("image_searches", self.add_image_entry.get()))

    def farm_gifs(self):
        self.troll.farm_gifs()

    def farm_images(self):
        self.troll.farm_images()

    def farm_new_content(self):
        self.troll.farm_content(all_content=False)

    def farm_all_content(self):
        self.troll.farm_content(all_content=True)

    def generate_troll(self):
        if self.string_talk_title.get() == "":
            self.troll.log("You must choose a talk title or enter one before generating a Powerpoint!")
            return

        self.troll.title = self.string_talk_title.get()
        self.troll.presenter = self.entry_presenter.get()

        try:
            self.troll.slide_min = int(self.slide_count_min_entry.get())
            self.troll.slide_max = int(self.slide_count_max_entry.get())
        except:
            self.troll.log("You must use integers for slide min and max!")
            return

        for key in self.weights.keys():
            self.troll.slide_weights.set_weight(key, int(self.weights[key].get()))

        self.troll.generate_slide_deck()

    def run(self):
        ''' Run the app '''
        self.mainloop()


def main():
    app = TrolletteGUI(tk.Tk())
    app.run()

if __name__ == "__main__":
    main()

__author__ = 'wartortell'