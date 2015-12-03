#! /usr/bin/python
# Requires wikipedia.py, wiki2plain.py, and python yaml
import wikipedia
import sys
from random import randint as rand


class Face:
    def __init__(self, topic):
        self.content = ''
        self.topic = topic

        if self.topic:
            self.content = self.get_text()

    def set_topic(self, new_topic):
        self.topic = new_topic
        self.content = self.get_text()

    def get_text(self):

        try:
            # do a wikipedia search for the topic
            topic_results = wikipedia.search(self.topic)

            # pick one of the results and grab the content
            self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content

            # DO IT MORE
            more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
            if more_content not in self.content:
                self.content += more_content
            more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
            if more_content not in self.content:
                self.content += more_content
            more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
        except wikipedia.exceptions.DisambiguationError as e:
            self.content += self.topic + ' can mean many things but to me it is'
        except wikipedia.exceptions.PageError as e:
            self.content += self.topic + ' is sometimes hard to find'

        # if there are more than one word in the topic try to get some more results with the first and last word
        if len(self.topic.split()) > 1:
            try:
                # get more results with less of the topic for some ambiguity
                topic_results = wikipedia.search(self.topic.split()[:1])
                self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                if more_content not in self.content:
                    self.content += more_content
            except wikipedia.exceptions.DisambiguationError as e:
                self.content += self.topic + ' can mean many things but to me it is'
            except wikipedia.exceptions.PageError as e:
                self.content += self.topic + ' is sometimes hard to find'
            try:
                # get even more with the second half of the topic for wierd results maybe
                topic_results = wikipedia.search(self.topic.split()[-1:])
                self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                if more_content not in self.content:
                    self.content += more_content
            except wikipedia.exceptions.DisambiguationError as e:
                self.content += self.topic + ' can mean many things but to me it is'
            except wikipedia.exceptions.PageError as e:
                self.content += self.topic + ' is sometimes hard to find'
        try:
            # do a wikipedia search for the topic
            topic_results = wikipedia.search(self.topic[:len(self.topic) / 2])

            # pick one of the results and grab the self.content
            self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
        except wikipedia.exceptions.DisambiguationError as e:
            self.content += self.topic + ' can mean many things but to me it is'
        except wikipedia.exceptions.PageError as e:
            self.content += self.topic + ' is sometimes hard to find'
        return self.content

    def parse_text(self):
        phrases = []
        words = self.content.split()
        # function to take a blob and parse out apropriately sized snippets
        for index in range(0, len(words) - 1):
            if self.topic.lower()[:len(self.topic) / 4] in words[index].lower() or self.topic.split()[-1].lower() in \
                    words[index].lower():
                cur_word = words[index]
                phrase = ''
                if index > 5:
                    i = index - rand(0, 5)
                else:
                    i = index
                counter = 0
                while cur_word.isalpha() and counter < 6:
                    try:
                        phrase = phrase + words[i].lower() + ' '
                        i += 1
                        cur_word = words[i]
                    except:
                        cur_word = '...'
                    counter += 1
                if len(phrase.split()) > 3:
                    temp = ''
                    for char in phrase:
                        if char.isalpha() or char.isspace():
                            temp += char
                    phrase = temp
                    other_words = ['using only my', 'forever!', 'because', 'for once in your life', 'until',
                                   'Great Job!', ', but in reality', 'is wrong!', 'is #1', 'never dies', 'is really',
                                   'might be', 'or not', 'better known as', 'the worst', 'kinda feels like', ', right?',
                                   '', ', WTF!', ', for realz', ', tru fact', 'in the feels','probably the best','?']
                    phrase += other_words[rand(0, len(other_words) - 1)]
                    phrases.append(phrase)
        phrases = list(set(phrases))
        return phrases

    def parse_bullets(self):
        bullets = []
        sentences = self.content.split('.')
        for ea in sentences:
            if len(ea) in range(50,75) and "\n" not in ea and "=" not in ea:
                bullets.append(ea)
        return bullets

    def get_bullets(self, min_count):
        final_bullets = []
        while len(final_bullets) < min_count:
            self.content += self.get_text()
            bullets = self.parse_bullets()
            for b in bullets:
                final_bullets.append(b.strip())
        return final_bullets

    def get_titles(self, min_count):
        # function to choose short headlines for the top of slides
        headlines = []
        while len(headlines) < min_count:
            self.content += self.get_text()
            phrases = self.parse_text()
            for p in phrases:
                headlines.append(p.strip())
        return headlines
