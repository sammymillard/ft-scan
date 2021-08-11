#!/usr/bin/env python

import argparse
import os
from pathlib import Path
import re
import sys
  
sys.path.append('../')

from full_text_scan import Article

def clean_author(names):
    def multiple(names): return " and " in names

    first_surname = names.split(",")[0].strip() if "," in names else names.strip()
    if multiple(names): 
        return first_surname+" et al"
    return first_surname

def clean_title(title):
    return re.sub(r'[^A-Za-z0-9 -]+', '', title).strip()[:40].strip()

def main(bibtex_filename):
    with open(bibtex_filename, encoding='utf-8') as bibtex_file:
        bib = bibtex_file.read()

    old_cwd = os.getcwd()
    p = Path(bibtex_filename)
    os.chdir(p.parent.absolute())

    articles = [Article(article) for article in bib.split("\n}\n")[:-1]]
    print(articles)

    for article in articles:
        print(article.filename)
        if article.filename and article.filename.endswith(".pdf"):
            p = Path(article.filename)
            new_name = " ".join([
                clean_author(article.author),
                str(article.year),
                "-",
                clean_title(article.title)
            ])+".pdf"

            new_filename = str(p.parent.joinpath(new_name))
            article.filename = new_filename
            print(article.filename)
            if p.exists():
                p.rename(new_filename)

    os.chdir(old_cwd)


    with open(bibtex_filename, 'w', encoding='utf-8') as bibtex_file:
        bibtex_file.write("".join(article.as_bibtex() for article in articles))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rename filenames in bibtex."
    )
    parser.add_argument(
        'bibtex',
        metavar='BibTeX input',
        type=str,
        help='BibTex input filename'
    )
    args = parser.parse_args()
    main(bibtex_filename=args.bibtex)
