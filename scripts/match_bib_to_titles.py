#!/usr/bin/env python

import re
from rapidfuzz import fuzz, process

def has_file(article):
    return "file = {" in article

def has_author(article):
    return "author = {" in article

with open("maybe_titles.txt") as f:
    titles = f.read().split("\n")[:-1]

count = dict()
for title in titles:
    count[title] = list()

with open("toomany.bib") as f:
    bib = f.read()

articles = bib.split("\n}\n")[:-1]

for article in articles:
    try:
        title = re.search(
            r"(?<=title = \{\{).+?(?=\}\},)",
            article
        ).group(0)
        match = process.extractOne(title, titles, scorer=fuzz.ratio)
        if match[1] >= 95.0:
            count[match[0]].append(article)
        else:
            pass
    except:
        pass


cleaned_result = []
for key, value in count.items():
    if len(value) > 1:
        chosen_article = False
        for article in value:
            if has_file(article) and has_author(article):
                chosen_article = True
                cleaned_result.append(article)
                break
        if not chosen_article:
            exit(f"Cannot choose between multiple articles for {key}")
    elif len(value) == 1:
        cleaned_result.append(value[0])
print("\n}\n".join(cleaned_result)+"\n}")
