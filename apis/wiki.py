import os
import wikipedia
import argparse

from helpers import default_logger


class WikipediaAPI:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        self.twitter_auth = None

    def farm_wikipedia(self, topic):

        content = {"content": list(), "references": list()}

        print(topic)

        # do a wikipedia search for the topic
        topic_results = wikipedia.search(topic)

        self.logger("  Search returned {} articles on {}".format(len(topic_results), topic))
        for i in range(len(topic_results)):
            try:
                self.logger("  Farming topic: {}".format(topic_results[i]))
                page = wikipedia.page(topic_results[i])
                if type(page.content) is str:
                    content["content"].append(page.content)

                content["references"].extend(page.references)
                #self.logger("  Farming references...")
                #for ref in page.references:
                #    self.logger("Farming {}...".format(ref))
                #    if ref.endswith(".pdf"):
                #        content.extend(self.farm_pdf(ref))
                #    else:
                #        content.append(self.farm_website_timeout(ref))

            except:
                pass

        return content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topic", action="store", required=False, help="Topic to search wikipedia for")
    args = parser.parse_args()

    wik = WikipediaAPI()
    if args.topic:
        content = wik.farm_wikipedia(args.topic)

        for con in content["content"]:
            print(con)
        for ref in content["references"]:
            print(ref)
    else:
        parser.print_help()
