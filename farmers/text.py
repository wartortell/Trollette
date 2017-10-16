import os
import re
import bs4
import json
import requests
import multiprocessing
import urllib.parse
import urllib.request


from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter

from farmers import DataFarmer
from apis import SearchAPI, WikipediaAPI, TwitterAPI


class TextFarmer(DataFarmer):

    def initialize_apis(self):
        self.searcher = SearchAPI()
        self.wiki_searcher = WikipediaAPI()
        self.twit_searcher = TwitterAPI()

    def initialize_paths(self):
        pass

    def farm_all_text(self, term):
        # Get all of the links to farm from google
        links = self.searcher.google_basic_search(term, 10)

        # Get the wikipedia data
        w = self.wiki_searcher.farm_wikipedia(term)

        # Get twitter content
        t = self.twit_searcher.farm_tweets(term)

        # Farm all of the links for daterz
        text_data = list()
        for link in links:
            text_data.append(self.farm_website_timeout(link))

        return text_data

    @staticmethod
    def filter_visible_elements(element):

        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('.*<!--.*-->.*', element, re.DOTALL):
            return False
        return True

    def farm_website_timeout(self, url, timeout=10):
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=self.farm_website, args=(url, return_dict))
        p.start()

        # Wait for timeout seconds or until process finishes
        p.join(timeout)

        # If thread is still active
        if p.is_alive():
            self.logger("    Killing web query that's been running too long...")

            # Terminate
            p.terminate()
            p.join()

        if "content" in return_dict:
            return return_dict["content"]

        return ""

    def farm_website(self, url, return_dict):
        """
        Description:
            Download a website and pull the visible content.

        :param url: str: url of the website to download
        :return:
        """

        try:
            agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"
            headers = {"User-Agent": agent}
            r = requests.get(url, headers=headers)
            #webpage = urllib.request.urlopen(url).read()
            webpage = r.content

            soup = bs4.BeautifulSoup(webpage, "lxml")
            texts = soup.findAll(text=True)

            visible_texts = filter(self.filter_visible_elements, texts)
            ret = ""
            for text in visible_texts:
                if text.strip():
                    ret += "%s\n" % text.strip()

            return_dict["content"] = ret

        except Exception as e:
            self.logger("    Exception when farming website: {}".format(url))
            self.logger(str(e))
            return_dict["content"] = ""

    def farm_pdf(self, pdf_url):
        """
        Description:
            Download a PDF and parse all the text from it.

        :param pdf_url: str: URL of the pdf you want to parse
        :return: list: list of strings from the pdf
        """

        self.logger("Downloading {}...\n".format(pdf_url))
        urllib.request.urlretrieve(pdf_url, "temp.pdf")

        self.logger("Farming text from {}...\n".format(pdf_url))
        with open("temp_pdf.txt", "w") as f:
            rsrcmgr = PDFResourceManager(caching=True)
            device = TextConverter(rsrcmgr, f, codec='utf-8', laparams=LAParams(), imagewriter=None)
            fp = open("temp.pdf", 'rb')
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.get_pages(fp, set(), maxpages=0, password="", caching=True, check_extractable=True):
                page.rotate = (page.rotate+0) % 360
                interpreter.process_page(page)
            fp.close()

        with open("temp_pdf.txt", "r") as f:
            text = f.read()

        os.remove("temp.pdf")
        os.remove("temp_pdf.txt")

        data = text.split("\n\n")

        farmed_pdf_text = []
        for line in data:
            farmed_pdf_text.append(line.replace("\n", " "))

        return farmed_pdf_text


if __name__ == "__main__":
    tf = TextFarmer()

    print(tf.farm_all_text("dicks"))


