#!/usr/bin/env python

import re

class Article:
    def __init__(self, text):
        self.__text = text
        self.__author = None
        self.__title = None
        self.__filename = None

    @property
    def author(self):
        def get_author(text):
            try:
                return re.search(
                    r"(?<=author = \{).+?(?=\},)",
                    text
                ).group(0).strip().replace("\n", " ").replace(";", ",")
            except:
                return ""
        if self.__author is None:
            self.__author = get_author(self.__text)
        return self.__author

    @property
    def title(self):
        def get_title(text):
            try:
                return re.search(
                    r"(?<=title = \{).+?(?=\},)",
                    text
                ).group(0).
                strip().
                replace("\n", " ").
                replace(";",",").
                replace("\"","").
                replace("'", "").
                replace("{","").
                replace("}","")
            except:
                return ""
        if self.__title is None:
            self.__title = get_title(self.__text)
        return self.__title

    @property
    def filename(self):
        def get_filename(text):
            try:
                return re.search(
                    r"(?<=file = \{).+?(?=\},)",
                    text
                ).group(0)
            except:
                return ""
        if self.__filename is None:
            self.__filename = get_filename(self.__text)
        return self.__filename


with open("results.csv") as f:
    csv = f.readlines()

with open("/path/to/bibtex.bib") as f:
    bib = f.read()

articles = bib.split("\n}\n")[:-1]

articles = [Article(article) for article in articles]

csv[0] = csv[0][:-1] + ";author;title"

for i, row in enumerate(csv[1:], 1):
    filename = row.split(";")[0][84:]
    found = False
    for article in articles:
        if filename in article.filename:
            found = True
            csv[i] = csv[i][:-1] + ";" + article.author + ";" + article.title
            break

with open("new_results.csv", "w") as f:
    f.write("\n".join(csv))
